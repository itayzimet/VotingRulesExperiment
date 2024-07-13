# %%
def get_price(candidates: list[int], buckets: list[float]) -> float:
    """
    Get the price of the question.
    :param candidates: list of candidates
    :param buckets: list of bucket ratios
    :return: the price of the question
    """
    return len(candidates) * len(buckets) * (1 - get_variance(buckets))


def get_variance(buckets: list[float]) -> float:
    """
    Get the variance of the buckets
    :param buckets: list of bucket ratios
    :return: the variance of the buckets
    """
    if len(buckets) < 2:
        return 0
    return (sum([(b - 1 / len(buckets)) ** 2 for b in buckets]) / len(buckets)) * 4
