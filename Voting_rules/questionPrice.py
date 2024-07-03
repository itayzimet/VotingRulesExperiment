# %%
def get_price(candidates: list[int], buckets: list[float]) -> float:
    """
    Get the price of the question.
    :param candidates: list of candidates
    :param buckets: list of bucket ratios
    :return: the price of the question
    """
    return len(candidates) * (1 - get_variance(buckets)) ** 10


def get_variance(buckets: list[float]) -> float:
    """
    Get the variance of the buckets
    :param buckets: list of bucket ratios
    :return: the variance of the buckets
    """
    temp = 0
    for bucket in buckets:
        temp += (bucket - (1 / len(buckets))) ** 2
    return temp / len(buckets)
