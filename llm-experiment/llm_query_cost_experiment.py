"""
llm_query_cost_experiment.py

Measures the *computational* cost (in LLM thinking/completion tokens) of
asking an LLM voter to answer a refinement query Q = (C', B), as a
candidate cost function for the query-based committee selection paper.

This lets us empirically test, for one or more LLMs, whether token cost:
  (1) grows with |C'|             (multiple monotonicity)
  (2) grows with |B|              (prefix monotonicity)
  (3) grows with Var(B)           (variance monotonicity)
  (4) depends on bucket ORDERING  (exploratory: does it matter whether the
                                    large/small bucket comes first?)

Usage
-----
1. Fill in MODELS below with the model strings (and any extra LiteLLM
   kwargs, e.g. reasoning/thinking params) you want to test.
2. `pip install litellm pandas --break-system-packages`
3. Set any required API keys as environment variables (per LiteLLM docs).
4. python3 llm_query_cost_experiment.py

Output: a long-format CSV (one row per individual LLM call) and a
grouped-summary CSV (mean/std per config) written next to this script.
"""

from __future__ import annotations

import ast
import csv
import os

import math
import json
import random
import time
import itertools
import dataclasses
from pathlib import Path
from typing import Optional

import litellm
import re
import pandas as pd
import matplotlib.pyplot as plt
import argparse

# --------------------------------------------------------------------------
# 1. CONFIG -- fill this in
# --------------------------------------------------------------------------

# Each entry: model string LiteLLM understands, plus optional extra kwargs
# (useful for reasoning-effort / extended-thinking params, which differ by
# provider). Leave litellm_kwargs={} for plain models.
MODELS = [
    # {"name": "claude-sonnet-4-6", "litellm_kwargs": {}},
    {"name": "gpt-5.4-mini", "litellm_kwargs": {"reasoning_effort": "low"}},
    # {"name": "gpt-4o", "litellm_kwargs": {}},
    # {"name": "mistral/mistral-small-latest", "litellm_kwargs": {}},
    # {"name": "gemini/gemini-3.1-flash-lite", "litellm_kwargs": {}},
    # {"name": "groq/meta-llama/llama-3.1-8b-instant", "litellm_kwargs": {}}
]

N_REPEATS = 10  # number of repeated calls averaged per (model, config)
TEMPERATURE = 1  # lower temperature (still non-deterministic); CLI --temperature overrides this
PROMPT_TEMPLATE_PATH = Path("prompt_template.txt")
OUTPUT_DIR = Path("outputs")
RANDOM_SEED = 0

random.seed(RANDOM_SEED)



# --------------------------------------------------------------------------
# 2. Refinement query construction
# --------------------------------------------------------------------------

def candidate_names(c_size: int) -> list[str]:
    """Synthetic, content-free candidate labels (Candidate_1, ...)."""
    return [f"Candidate_{i+1}" for i in range(c_size)]


def generate_random_candidate_names(c_size: int, seed: Optional[int] = None) -> list[str]:
    """
    Generate randomized candidate names by shuffling the base candidate list.
    This provides variety across different runs while remaining deterministic.
    
    If seed is provided, temporarily seed the RNG for reproducibility.
    """
    saved_state = None
    if seed is not None:
        saved_state = random.getstate()
        random.seed(seed)
    
    try:
        # Start with base names and shuffle them
        names = candidate_names(c_size)
        random.shuffle(names)
        return names
    finally:
        if saved_state is not None:
            random.setstate(saved_state)


def generate_random_preferences(candidates: list[str], seed: Optional[int] = None) -> str:
    """
    Generate a random total order (preference ranking) over candidates.
    Returns a formatted preference string suitable for the system prompt.
    
    If seed is provided, temporarily seed the RNG for reproducibility.
    """
    saved_state = None
    if seed is not None:
        saved_state = random.getstate()
        random.seed(seed)
    
    try:
        # Shuffle a copy of the candidates list to get a random ranking
        ranked = candidates[:]
        random.shuffle(ranked)
        # Format as numbered list
        pref_lines = [f"{i + 1}. {c}" for i, c in enumerate(ranked)]
        return "\n".join(pref_lines)
    finally:
        if saved_state is not None:
            random.setstate(saved_state)


def bucket_sizes_from_B(c_size: int, B: list[float]) -> list[int]:
    """
    Convert bucket proportions B into integer bucket sizes summing to
    c_size, using the largest-remainder method. This satisfies the paper's
    rounding constraint | |C'_j| - b_j*|C'| | < 1 for all j.
    """
    raw = [b * c_size for b in B]
    floors = [math.floor(r) for r in raw]
    remainder = c_size - sum(floors)
    fracs = sorted(range(len(B)), key=lambda i: raw[i] - floors[i], reverse=True)
    sizes = floors[:]
    for i in range(remainder):
        sizes[fracs[i]] += 1
    assert sum(sizes) == c_size
    return sizes


def variance(B: list[float]) -> float:
    """Var(B) as defined in the paper (Definition: variance in bucket ratios)."""
    ell = len(B)
    if ell <= 1:
        return 0.0
    mean = 1.0 / ell
    return sum((b - mean) ** 2 for b in B) / ell


@dataclasses.dataclass
class QueryConfig:
    sweep: str          # which sweep this config belongs to
    sweep_value: float  # the swept independent variable, for plotting
    c_size: int
    B: list[float]
    bucket_order_id: int = 0  # disambiguates permutations with same B multiset

    @property
    def num_buckets(self) -> int:
        return len(self.B)

    @property
    def var_B(self) -> float:
        return variance(self.B)

    def label(self) -> str:
        return f"{self.sweep}|C'|={self.c_size}|B|={self.B}|ord={self.bucket_order_id}"


# --------------------------------------------------------------------------
# 3. Prompt construction
# --------------------------------------------------------------------------

def load_template(path: Path) -> tuple[str, str]:
    raw = path.read_text()
    if "---SYSTEM---" not in raw or "---USER---" not in raw:
        raise ValueError("Prompt template must contain ---SYSTEM--- and ---USER--- delimiters")
    system_part = raw.split("---SYSTEM---", 1)[1].split("---USER---", 1)[0].strip()
    user_part = raw.split("---USER---", 1)[1].strip()
    return system_part, user_part


def fill_template(template: str, values: dict[str, str]) -> str:
    out = template
    for key, val in values.items():
        out = out.replace("{{" + key + "}}", val)
    return out


def build_messages(system_template: str, user_template: str, cfg: QueryConfig, repeat_idx: int = 0) -> list[dict]:
    sizes = bucket_sizes_from_B(cfg.c_size, cfg.B)
    # Generate deterministic randomization seeds based on config and repeat index
    config_hash = hash((cfg.sweep, cfg.c_size, tuple(cfg.B), cfg.bucket_order_id))
    base_seed = (config_hash + repeat_idx) % (2 ** 31)  # keep seed within 32-bit range
    
    # Generate randomized candidates with one seed offset
    candidates = generate_random_candidate_names(cfg.c_size, seed=base_seed)
    
    # Generate random preferences with a different seed offset to ensure independence
    prefs = generate_random_preferences(candidates, seed=(base_seed + 1) % (2 ** 31))
    
    values = {
        "CANDIDATE_LIST": ", ".join(candidates),
        "NUM_CANDIDATES": str(cfg.c_size),
        "NUM_BUCKETS": str(cfg.num_buckets),
        "BUCKET_SIZES": ", ".join(str(s) for s in sizes),
        "VOTER_PREFERENCES": prefs,
    }
    system = fill_template(system_template, values)
    user = fill_template(user_template, values)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


# --------------------------------------------------------------------------
# 4. Querying the LLM and extracting token costs
# --------------------------------------------------------------------------

def extract_token_counts(response) -> dict:
    """
    Pull completion / reasoning / total tokens out of a LiteLLM response in
    a provider-agnostic way. Different providers expose "thinking" cost
    under different field names, so we check several known locations and
    fall back gracefully.
    """
    usage = getattr(response, "usage", None) or {}
    if not isinstance(usage, dict):
        usage = usage.model_dump() if hasattr(usage, "model_dump") else dict(usage)

    completion_tokens = usage.get("completion_tokens", 0) or 0
    prompt_tokens = usage.get("prompt_tokens", 0) or 0
    total_tokens = usage.get("total_tokens", completion_tokens + prompt_tokens)

    reasoning_tokens = 0
    details = usage.get("completion_tokens_details")
    if details:
        if not isinstance(details, dict):
            details = details.model_dump() if hasattr(details, "model_dump") else dict(details)
        reasoning_tokens = details.get("reasoning_tokens", 0) or 0

    # Anthropic extended thinking: thinking content is billed as part of
    # completion_tokens already, but some LiteLLM versions also surface a
    # separate field -- check defensively.
    reasoning_tokens = reasoning_tokens or usage.get("reasoning_tokens", 0) or 0

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": total_tokens,
    }


def _sanitize_filename(s: str) -> str:
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^A-Za-z0-9_.-]", "_", s)
    return s


def _dump_response(response, path: Path) -> None:
    """Attempt to serialize the full response to JSON; fall back to str()."""
    path.parent.mkdir(parents=True, exist_ok=True)
    out = None
    try:
        if hasattr(response, "model_dump"):
            out = response.model_dump()
        else:
            # try mapping-like
            out = dict(response)
    except Exception:
        try:
            out = repr(response)
        except Exception:
            out = "<unserializable response>"

    # Write JSON if we have a mapping-like structure, else write text
    try:
        if isinstance(out, (dict, list)):
            with path.open("w") as f:
                json.dump(out, f, indent=2)
        else:
            with path.open("w") as f:
                f.write(str(out))
    except Exception:
        # best-effort: write repr
        with path.open("w") as f:
            f.write(repr(out))


def query_single(model_name: str, messages: list[dict],
                 litellm_kwargs: Optional[dict] = None, max_retries: int = 3) -> dict:
    """
    Calls `model_name` once with the given messages and returns
    a dict with token counts and the full response.
    """
    litellm_kwargs = litellm_kwargs or {}
    for attempt in range(max_retries):
        try:
            response = litellm.completion(
                model=model_name,
                messages=messages,
                # temperature=TEMPERATURE,
                **litellm_kwargs,
            )
            return {"tokens": extract_token_counts(response), "response": response}
        except Exception as e:  # noqa: BLE001 -- log and retry
            # Detect rate-limit-like errors and back off more aggressively.
            def _is_rate_limit(err) -> bool:
                msg = str(err).lower()
                # common textual indicators of rate limiting
                if "rate limit" in msg or "rate_limit" in msg or "too many" in msg or "429" in msg:
                    return True
                # some libraries expose numeric status/code fields
                code = getattr(err, "status_code", None) or getattr(err, "status", None) or getattr(err, "code", None)
                try:
                    if code is not None and int(code) == 429:
                        return True
                except Exception:
                    pass
                return False

            is_rate_limit = _is_rate_limit(e)
            base_wait = 1.0
            # standard exponential backoff
            wait = base_wait * (2 ** attempt)
            if is_rate_limit:
                # when rate-limited, increase backoff more quickly and add jitter
                wait = min(120.0, wait * 8)
            else:
                # small jitter for non-rate-limit errors to avoid thundering retries
                wait = min(30.0, wait + random.random())

            kind = "rate-limit" if is_rate_limit else "error"
            print(f"  [warn] {model_name} call failed ({e}); {kind} - retrying in {wait:.1f}s")
            time.sleep(wait)
    else:
        print(f"  [error] {model_name} call failed after {max_retries} attempts; skipping")
        return {"tokens": {}, "response": None}


# --------------------------------------------------------------------------
# 5. Sweep definitions
# --------------------------------------------------------------------------

def sweep_candidate_count(c_sizes=(4, 8, 16, 32, 64, 128)) -> list[QueryConfig]:
    """Fix B (uniform 50/50 split), vary |C'| -> tests multiple monotonicity."""
    B = [0.5, 0.5]
    return [QueryConfig(sweep="candidate_count", sweep_value=c, c_size=c, B=B) for c in c_sizes]


def sweep_bucket_count(c_size=32, bucket_counts=(1, 2, 3, 4, 6, 8)) -> list[QueryConfig]:
    """Fix |C'|, vary |B| (always uniform proportions, Var(B)=0) -> tests prefix monotonicity."""
    configs = []
    for ell in bucket_counts:
        B = [1.0 / ell] * ell
        configs.append(QueryConfig(sweep="bucket_count", sweep_value=ell, c_size=c_size, B=B))
    return configs


def sweep_variance(c_size=32, skews=(0.0, 0.1, 0.2, 0.3, 0.4)) -> list[QueryConfig]:
    """
    Fix |C'| and |B|=2, vary how unbalanced the split is
    (skew=0 -> (0.5,0.5), skew=0.4 -> (0.1,0.9)) -> tests variance monotonicity.
    """
    configs = []
    for skew in skews:
        B = [0.5 - skew, 0.5 + skew]
        configs.append(QueryConfig(sweep="variance", sweep_value=variance(B), c_size=c_size, B=B))
    return configs


def sweep_bucket_ordering(c_size=30, proportions=(0.2, 0.3, 0.5)) -> list[QueryConfig]:
    """
    Fix |C'|, |B|, and the MULTISET of bucket proportions (so Var(B) is
    identical across all configs here) but vary the ORDER in which the
    bucket sizes are presented (which one is "most preferred"/listed
    first). Exploratory: tests whether positioning affects token cost
    independent of variance.
    """
    configs = []
    for i, perm in enumerate(set(itertools.permutations(proportions))):
        configs.append(
            QueryConfig(
                sweep="bucket_ordering",
                sweep_value=i,  # purely an index; not a meaningful numeric x-axis
                c_size=c_size,
                B=list(perm),
                bucket_order_id=i,
            )
        )
    return configs


ALL_SWEEPS = {
    "candidate_count": sweep_candidate_count,
    "bucket_count": sweep_bucket_count,
    "variance": sweep_variance,
    "bucket_ordering": sweep_bucket_ordering,
}


# --------------------------------------------------------------------------
# 6. Runner
# --------------------------------------------------------------------------

def run_all(models=MODELS, sweeps=ALL_SWEEPS, n_repeats=N_REPEATS, existing_rows: Optional[list[dict]] = None, temperature: float = TEMPERATURE) -> list[dict]:
    system_template, user_template = load_template(PROMPT_TEMPLATE_PATH)
    rows = []

    # Compute starting repeat index for each (sweep,c_size,B,order,model) key so
    # appended runs continue where previous ones left off instead of clobbering
    # or duplicating repeat_idx values.
    start_repeat = {}
    if existing_rows:
        from collections import defaultdict
        max_idx = defaultdict(lambda: -1)
        for r in existing_rows:
            key = (
                r.get("sweep"),
                r.get("c_size"),
                r.get("B"),
                int(r.get("bucket_order_id", 0)),
                r.get("model"),
            )
            try:
                ri = int(r.get("repeat_idx", -1))
            except Exception:
                ri = -1
            if ri > max_idx[key]:
                max_idx[key] = ri
        for k, v in max_idx.items():
            start_repeat[k] = v + 1

    for sweep_name, sweep_fn in sweeps.items():
        configs = sweep_fn()
        print(f"\n=== Sweep: {sweep_name} ({len(configs)} configs) ===")
        for cfg in configs:
            for model_entry in models:
                # copy model-specific litellm kwargs and ensure temperature is set
                base_kwargs = dict(model_entry.get("litellm_kwargs", {}) or {})
                if "temperature" not in base_kwargs:
                    base_kwargs["temperature"] = float(temperature)
                kwargs = base_kwargs
                model_name = model_entry["name"]
                print(f"  {cfg.label()}  model={model_name}  temp={kwargs.get('temperature')}")

                # Determine the starting repeat index for this specific config+model
                key = (cfg.sweep, cfg.c_size, json.dumps(cfg.B), cfg.bucket_order_id, model_name)
                start = start_repeat.get(key, 0)

                # Make n_repeats calls, each with different random preferences
                for i in range(n_repeats):
                    repeat_idx = start + i
                    messages = build_messages(system_template, user_template, cfg, repeat_idx=repeat_idx)
                    data = query_single(model_name, messages, litellm_kwargs=kwargs)
                    tok = data.get("tokens", {})
                    response = data.get("response")
                    # save full response/thinking chain for later inspection
                    resp_dir = OUTPUT_DIR / "responses"
                    label = f"{cfg.sweep}_{cfg.c_size}_{cfg.num_buckets}_{cfg.bucket_order_id}_{model_name}_{repeat_idx}"
                    fname = _sanitize_filename(label) + ".json"
                    resp_path = resp_dir / fname
                    try:
                        _dump_response(response, resp_path)
                        resp_path_str = str(resp_path)
                    except Exception:
                        resp_path_str = ""

                    rows.append({
                        "sweep": cfg.sweep,
                        "sweep_value": cfg.sweep_value,
                        "model": model_name + "-" + repr(kwargs["reasoning_effort"]),
                        "c_size": cfg.c_size,
                        "num_buckets": cfg.num_buckets,
                        "B": json.dumps(cfg.B),
                        "var_B": cfg.var_B,
                        "bucket_order_id": cfg.bucket_order_id,
                        "repeat_idx": repeat_idx,
                        "response_path": resp_path_str,
                        **tok,
                    })
    return rows


def summarize(rows: list[dict], winsorize_frac: float = 0.0) -> list[dict]:
    """Group by (sweep, model, c_size, B, bucket_order_id) and compute mean/std.

    Also aggregate mean/std for prompt tokens so plots can reflect the queries
    (prompt length) alongside completion cost. Optionally winsorize per-config
    samples when winsorize_frac > 0 (fraction trimmed from each tail) — the
    raw rows remain unchanged.
    """
    from collections import defaultdict

    def _winsorize_list(lst: list[float], frac: float) -> list[float]:
        if not lst or not frac or frac <= 0.0:
            return lst[:]
        n = len(lst)
        if n == 0:
            return []
        s = sorted(lst)
        # Trim frac from each tail: keep elements from index ceil(frac*n) to floor((1-frac)*n)-1
        lower_idx = int(math.ceil(frac * n))
        upper_idx = int(math.floor((1.0 - frac) * n)) - 1
        lower_idx = max(0, min(lower_idx, n - 1))
        upper_idx = max(lower_idx, min(upper_idx, n - 1))
        low_val = s[lower_idx]
        high_val = s[upper_idx]
        return [min(max(x, low_val), high_val) for x in lst]

    groups = defaultdict(lambda: {"completion": [], "prompt": [], "reasoning": [], "total": [], "example_path": ""})
    for r in rows:
        key = (r["sweep"], r["model"], r["c_size"], r["B"], r["bucket_order_id"], r["sweep_value"])
        groups[key]["completion"].append(r.get("completion_tokens", 0) or 0)
        groups[key]["prompt"].append(r.get("prompt_tokens", 0) or 0)
        groups[key]["reasoning"].append(r.get("reasoning_tokens", 0) or 0)
        groups[key]["total"].append(r.get("total_tokens", 0) or 0)
        if not groups[key]["example_path"] and r.get("response_path"):
            groups[key]["example_path"] = r.get("response_path")

    summary = []
    for (sweep, model, c_size, B, order_id, sweep_value), vals in groups.items():
        def _mean_std(lst):
            n = len(lst)
            if n == 0:
                return 0.0, 0.0
            mean = sum(lst) / n
            var = sum((v - mean) ** 2 for v in lst) / n if n > 1 else 0.0
            return mean, var ** 0.5

        comp_vals = _winsorize_list(vals["completion"], winsorize_frac)
        prompt_vals = _winsorize_list(vals["prompt"], winsorize_frac)
        reason_vals = _winsorize_list(vals["reasoning"], winsorize_frac)
        total_vals = _winsorize_list(vals["total"], winsorize_frac)

        mean_comp, std_comp = _mean_std(comp_vals)
        mean_prompt, std_prompt = _mean_std(prompt_vals)
        mean_reason, std_reason = _mean_std(reason_vals)
        mean_total, std_total = _mean_std(total_vals)

        summary.append({
            "sweep": sweep,
            "model": model,
            "c_size": c_size,
            "B": B,
            "bucket_order_id": order_id,
            "sweep_value": sweep_value,
            "n": len(comp_vals),
            "mean_completion_tokens": mean_comp,
            "std_completion_tokens": std_comp,
            "mean_prompt_tokens": mean_prompt,
            "std_prompt_tokens": std_prompt,
            "mean_reasoning_tokens": mean_reason,
            "std_reasoning_tokens": std_reason,
            "mean_total_tokens": mean_total,
            "std_total_tokens": std_total,
            "example_response_path": vals["example_path"],
        })
    return summary


def plot_summary(summary_rows: list[dict], out_dir: Path, show_errorbars: bool = True, fmt: str = "png") -> None:
    """Create simple plots (mean +/- std) per sweep, grouped by model.

    Simplified plotting: each model is a single line (mean), optional error bars.
    Annotates points with a short label; annotation font size encodes mean_prompt_tokens.
    """
    if not summary_rows:
        print("[warn] no summary rows to plot")
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(summary_rows)
    df["sweep_value_num"] = pd.to_numeric(df["sweep_value"], errors="coerce")

    # baseline for prompt-token encoding
    if "mean_prompt_tokens" not in df.columns:
        df["mean_prompt_tokens"] = pd.NA
    median_prompt = df["mean_prompt_tokens"].median(skipna=True)
    median_prompt = float(median_prompt) if not pd.isna(median_prompt) and median_prompt > 0 else 1.0

    for sweep in df["sweep"].unique():
        dfs = df[df["sweep"] == sweep]
        fig, ax = plt.subplots(figsize=(8, 5))

        for model in dfs["model"].unique():
            sub = dfs[dfs["model"] == model]
            x = sub["sweep_value_num"]
            if x.isna().all():
                x = range(len(sub))
            y = sub["mean_completion_tokens"]
            yerr = sub.get("std_completion_tokens", None) if show_errorbars else None

            if show_errorbars:
                ax.errorbar(x, y, yerr=yerr, label=model, marker="o", capsize=3)
            else:
                ax.plot(x, y, label=model, marker="o")

            # annotation font size encoding based on mean_prompt_tokens
            prompt_vals = pd.to_numeric(sub.get("mean_prompt_tokens", pd.Series([median_prompt] * len(sub))), errors="coerce").fillna(median_prompt)
            # scale font sizes between 6 and 12
            norms = (prompt_vals / median_prompt)
            font_sizes = (6 + (norms - 1.0) * 4).clip(lower=6, upper=12)

            # compute small offset in data coordinates (2% of axis range)
            # derive from this sub's x and y ranges
            x_vals = pd.to_numeric(sub.get("sweep_value_num", pd.Series(list(x))), errors="coerce").fillna(0.0)
            if x_vals.empty:
                x_min, x_max = 0.0, 1.0
            else:
                x_min, x_max = float(x_vals.min()), float(x_vals.max())
            x_range = x_max - x_min if (x_max - x_min) > 0 else 1.0
            offset_x = 0.02 * x_range

            y_vals = pd.to_numeric(sub.get("mean_completion_tokens", pd.Series(list(y))), errors="coerce").fillna(0.0)
            if y_vals.empty:
                y_min, y_max = 0.0, 1.0
            else:
                y_min, y_max = float(y_vals.min()), float(y_vals.max())
            y_range = y_max - y_min if (y_max - y_min) > 0 else 1.0
            offset_y = 0.02 * y_range

            for xi, yi, bstr, csize, fs in zip(x, y, sub.get("B", []), sub.get("c_size", []), font_sizes):
                label = f"|C|={int(csize)},B={bstr}" if isinstance(bstr, str) and len(bstr) < 20 else f"|C|={int(csize)},|B|={len(ast.literal_eval(bstr))}"
                xi_f = float(xi)
                yi_f = float(yi)
                ax.text(xi_f + offset_x, yi_f + offset_y, label, fontsize=float(fs), va='bottom', ha='left')

        ax.set_xlabel("sweep_value")
        ax.set_ylabel("mean_completion_tokens")
        ax.set_title(f"Sweep: {sweep}")
        ax.legend(framealpha=1.0)
        ax.grid()

        out_path = out_dir / f"{_sanitize_filename(sweep)}.{fmt}"
        fig.tight_layout()
        # Force renderer draw (helps with some backends producing empty vector files)
        try:
            fig.canvas.draw()
        except Exception:
            pass

        try:
            fig.savefig(out_path, format=fmt, bbox_inches='tight', transparent=False)
            plt.close(fig)
            print(f"Wrote plot -> {out_path}")
        except Exception as e:
            try:
                png_path = out_dir / f"{_sanitize_filename(sweep)}.png"
                # Ensure the figure is drawn before saving PNG fallback
                try:
                    fig.canvas.draw()
                except Exception:
                    pass
                fig.savefig(png_path, format="png", bbox_inches='tight')
                plt.close(fig)
                print(f"Wrote PNG fallback -> {png_path}; failed to produce {out_path}: {e}")
            except Exception as e2:
                print(f"[error] Failed to save plot in any format: {e}; {e2}")



def load_raw_rows(path: Path) -> list[dict]:
    """Load raw per-call rows from a CSV written by write_csv.

    Returns a list of dicts where numeric token/count fields are converted
    to numbers where possible so `summarize()` works correctly.
    """
    if not path.exists():
        raise FileNotFoundError(f"Raw CSV not found: {path}")
    df = pd.read_csv(path)
    # Convert typical numeric fields
    for col in ("completion_tokens", "prompt_tokens", "reasoning_tokens", "total_tokens", "c_size", "num_buckets", "bucket_order_id", "repeat_idx"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Keep sweep_value as-is (string or numeric); no coercion here
    rows = df.fillna("").to_dict(orient="records")
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        print(f"[warn] no rows to write for {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {path}")


def main():
    parser = argparse.ArgumentParser(description="LLM query cost experiment runner")
    parser.add_argument("--mode", choices=("run", "summarize"), default="run",
                        help="'run' to execute LLM calls, 'summarize' to read existing raw CSV and summarize/plot")
    parser.add_argument("--raw-csv", type=Path, default=OUTPUT_DIR / "llm_query_cost_raw.csv",
                        help="Path to raw CSV produced by a previous run (used with --mode summarize)")
    parser.add_argument("--append", action="store_true",
                        help="When set in run mode, append new results to existing raw CSV instead of overwriting")
    parser.add_argument("--merge-summary", action="store_true",
                        help="When set with --append, update the existing summary by merging new samples into the prior summary instead of appending raw rows.")
    parser.add_argument("--n-repeats", type=int, default=N_REPEATS,
                        help="Number of repeats to perform per config for this invocation. When used with --append, these repeats are appended to existing data.")
    parser.add_argument("--temperature", type=float, default=TEMPERATURE,
                        help="Sampling temperature to use for LLM calls (0 = deterministic). Lower reduces variance; keep >0 for stochasticity.")
    parser.add_argument("--winsorize", type=float, default=0.0,
                        help="Fraction to winsorize from each tail when summarizing (e.g., 0.05). 0 disables winsorization. Raw data is not modified.")
    parser.add_argument("--models", nargs="+",
                        help="List of model names to include in summarize/plot. If omitted, include all models.")
    parser.add_argument("--no-errorbars", action="store_true",
                        help="When plotting, omit error bars (show only means).")
    parser.add_argument("--plot-format", type=str, default="png",
                        choices=["png","pdf","svg","eps","jpg","jpeg","tiff"],
                        help="File format to save plots in (default: png)")
    args = parser.parse_args()

    if args.mode == "summarize":
        # Load existing raw rows and produce summary + plots only
        try:
            rows = load_raw_rows(args.raw_csv)
        except FileNotFoundError as e:
            raise SystemExit(str(e))
        summary = summarize(rows, winsorize_frac=args.winsorize)
        if args.models:
            models_set = set(args.models)
            summary = [r for r in summary if r.get("model") in models_set]
        write_csv(summary, OUTPUT_DIR / "llm_query_cost_summary.csv")
        plot_summary(summary, OUTPUT_DIR / "plots", show_errorbars=not args.no_errorbars, fmt=args.plot_format)
        print("Summarize-only mode complete.")
        return

    # mode == run
    if not MODELS:
        raise SystemExit(
            "MODELS is empty -- fill in the MODELS list at the top of this "
            "script with the model strings you want to test, then re-run."
        )

    existing_rows = None
    if args.append and args.raw_csv.exists():
        try:
            existing_rows = load_raw_rows(args.raw_csv)
            print(f"Loaded {len(existing_rows)} existing rows from {args.raw_csv}; appending {args.n_repeats} repeats per config.")
        except FileNotFoundError:
            existing_rows = None
            print(f"No existing raw CSV found at {args.raw_csv}; running fresh and creating new file.")

    # If merging summaries, load prior summary if available
    prior_summary = None
    summary_path = OUTPUT_DIR / "llm_query_cost_summary.csv"
    if args.merge_summary and summary_path.exists():
        try:
            df_prior = pd.read_csv(summary_path)
            prior_summary = df_prior.to_dict(orient="records")
            print(f"Loaded prior summary with {len(prior_summary)} rows from {summary_path}; will merge new samples into these aggregates.")
        except Exception:
            prior_summary = None
            print(f"Failed to load prior summary from {summary_path}; proceeding without merging.")

    new_rows = run_all(n_repeats=args.n_repeats, existing_rows=existing_rows, temperature=args.temperature)

    if args.merge_summary and prior_summary:
        # Build maps for prior summary and new summary keyed by (sweep, model, c_size, B, bucket_order_id, sweep_value)
        def _key(r):
            return (r["sweep"], r["model"], int(r["c_size"]), r["B"], int(r["bucket_order_id"]), r.get("sweep_value"))

        prior_map = {}
        for r in prior_summary:
            try:
                n1 = int(r.get("n", 0))
                mean1 = float(r.get("mean_completion_tokens", 0.0))
                std1 = float(r.get("std_completion_tokens", 0.0))
            except Exception:
                continue
            var1 = std1 ** 2
            sum1 = mean1 * n1
            sumsq1 = n1 * (var1 + mean1 * mean1)
            prior_map[_key(r)] = {"n": n1, "sum": sum1, "sumsq": sumsq1, "sweep": r["sweep"], "model": r["model"], "c_size": int(r["c_size"]), "B": r["B"], "bucket_order_id": int(r["bucket_order_id"]), "sweep_value": r.get("sweep_value")}

        new_summary_rows = summarize(new_rows, winsorize_frac=args.winsorize)
        new_map = {}
        for r in new_summary_rows:
            k = _key(r)
            n2 = int(r.get("n", 0))
            mean2 = float(r.get("mean_completion_tokens", 0.0))
            var2 = float(r.get("std_completion_tokens", 0.0)) ** 2
            sum2 = mean2 * n2
            sumsq2 = n2 * (var2 + mean2 * mean2)
            new_map[k] = {"n": n2, "sum": sum2, "sumsq": sumsq2, "sweep": r["sweep"], "model": r["model"], "c_size": r["c_size"], "B": r["B"], "bucket_order_id": r["bucket_order_id"], "sweep_value": r.get("sweep_value")}

        # Combine maps
        keys = set(prior_map.keys()) | set(new_map.keys())
        combined_summary_rows = []
        for k in keys:
            p = prior_map.get(k)
            n1 = p["n"] if p else 0
            sum1 = p["sum"] if p else 0.0
            sumsq1 = p["sumsq"] if p else 0.0
            q = new_map.get(k)
            n2 = q["n"] if q else 0
            sum2 = q["sum"] if q else 0.0
            sumsq2 = q["sumsq"] if q else 0.0
            n_tot = n1 + n2
            if n_tot == 0:
                continue
            sum_tot = sum1 + sum2
            sumsq_tot = sumsq1 + sumsq2
            mean_tot = sum_tot / n_tot
            var_tot = max(0.0, (sumsq_tot / n_tot) - (mean_tot * mean_tot))
            std_tot = math.sqrt(var_tot)
            # reuse metadata from available map
            meta = p or q
            combined_summary_rows.append({
                "sweep": meta["sweep"],
                "model": meta["model"],
                "c_size": meta["c_size"],
                "B": meta["B"],
                "bucket_order_id": meta["bucket_order_id"],
                "sweep_value": meta.get("sweep_value"),
                "n": n_tot,
                "mean_completion_tokens": mean_tot,
                "std_completion_tokens": std_tot,
            })

        # Write combined summary but do NOT modify the raw CSV (user requested no new raw rows)
        filtered = combined_summary_rows
        if args.models:
            models_set = set(args.models)
            filtered = [r for r in combined_summary_rows if r.get("model") in models_set]
        write_csv(filtered, summary_path)
        plot_summary(filtered, OUTPUT_DIR / "plots", show_errorbars=not args.no_errorbars, fmt=args.plot_format)
        print("Merged new samples into existing summary (raw CSV left unchanged).")
        return

    # fallback: append raw rows or overwrite
    if args.append and existing_rows:
        combined = existing_rows + new_rows
    else:
        combined = new_rows

    write_csv(combined, args.raw_csv)
    summary = summarize(combined, winsorize_frac=args.winsorize)
    if args.models:
        models_set = set(args.models)
        summary = [r for r in summary if r.get("model") in models_set]
    write_csv(summary, OUTPUT_DIR / "llm_query_cost_summary.csv")
    # produce plots and save response artifacts
    plot_summary(summary, OUTPUT_DIR / "plots", show_errorbars=not args.no_errorbars, fmt=args.plot_format)


if __name__ == "__main__":
    main()
