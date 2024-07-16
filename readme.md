# voting experiment

This is a simple voting experiment to test different voting system.

## Table of contents

- [Installation and usage](#installation-and-usage)
- [Experimental protocol](#experimental-protocol)
    - [Experiment control parameters](#experiment-control-parameters)
    - [Data fabrication](#data-fabrication)
    - [Experiment procedure](#experiment-procedure)
    - [Voting systems](#voting-systems)
    - [Question types](#question-types)
    - [Distance metric](#distance-metric)
- [todo](#todo)

## Installation and usage

clone the repository and change main.py to your liking. Then run the following commands to create a virtual environment
and install the required packages.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

or if you are using windows

```bash
python -m venv venv
venv\Scripts\activate.ps1
pip install -r requirements.txt
```

Then run the following command to run the experiment

```bash
python main.py
```

## Experimental protocol

### Experiment control parameters

- Number of voters: 100
- Number of candidates: 100
- Target committee size: 50
- Question budgets: 1 - 150000 (jumps of 1000)
- Number of runs: 20
- Voting system: Kborda
- Question type: Next, Last, Split, SplitTrinary - all using the refinement query syntax
- Distance metric: size of the symmetric difference between the approximation and the committee

### Data fabrication

- Generate candidates labeled 0-number of candidates - 1
- Generate voters with random preferences by shuffling the candidates list for each voter

### Experiment procedure

1. For each run:
    1. Generate candidates and voters
    2. For each voting system
        1. generate a committee of size target committee size using the voting system
        2. For each approximation of the voting system
            1. For each number of questions
                1. generate an approximation of the committee using the approximation of the voting system
                2. calculate the distance between the approximation and the committee
                3. store the distance in a list
2. calculate the average distances from the different runs for each voting system and approximation for all number of
   questions
3. plot the average distances for each voting system and approximation for all number of questions
4. save the plot
5. repeat for all voting systems and approximations

### Voting systems

- Kborda: Select the top k candidates with the highest borda score
    - KbordaBucketSplit: approximate the voters preferences by asking the voter to split the candidates into two sets,
      the first set containing the candidates he prefers over the second set. Then select the top k candidates with the
      highest borda score. Budget is distributed evenly between the voters.
    - KbordaBucketTrinary: same as KbordaBucketSplit but the voter is asked to split the candidates into three sets
      instead of two
    - KbordaNextEq: approximate the voters preferences by asking the voter for the next best candidate in his preference
      list. Then select the top k candidates with the highest borda score. Budget is distributed evenly between the
      voters.
    - KbordaLastEq: same as KbordaNextEq but the voter is asked for the next worst candidate in his preference list
    - KbordaNextLastEq: same as KbordaNextEq but the voter is asked for the next best and worst candidate in his
      preference list
    - KbordaNextFCFS: same as KbordaNextEq but the budget is distributed first come first serve
    - KbordaLastFCFS: same as KbordaLastEq but the budget is distributed first come first serve
    - KbordaNextLastFCFS: same as KbordaNextLastEq but the budget is distributed first come first serve
- Random: Select k candidates at random

### Question types

- Next: Ask the voter for the next best candidate in his preference list
- Last: Ask the voter for the next worst candidate in his preference list
- Split: Ask the voter to halve the set of candidates provided into two sets, the first set containing the candidates he
  prefers over the second set
- SplitTrinary: Ask the voter to split the set of candidates provided into three sets, the first set containing the
  candidates he prefers over the second set, and the second set containing the candidates he prefers over the third set
- All question types use the refinement query syntax described in the latex document

### Distance metric

- The only metric currently implemented is the size of the symmetric difference between the approximation and the
  committee

## todo

- [ ] fix Deep leaning
