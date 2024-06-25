def get_price(question: list[int]):
    """
    Get the price of the question.
    :param question: the question to get the price of.
    :return: the price of the question.
    """
    return 1
    # for example, if the question is [1,19] the price will be (1)*1 = 1
    # if the question is [10,10] the price will be (10)*1 = 10
    # if the question is [10,10,10] the price will be (10+10)*2 = 40
    # if the question is [20,10,20] the price will be (20+10)*2 = 60
