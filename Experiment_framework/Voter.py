#!/usr/bin/python
# -*- coding: utf-8 -*-

class Voter:
    """
    A class to represent a voter with ordinal preferences.

    Attributes:
        OrdinalPreferences : list[int]
            List of integers representing the ordinal preferences of the voter.

    Methods:
        get_preferences()
            Get the ordinal preferences of the voter.
        get_preference(index: int)
            Get the candidate at the given index in the voter's ordinal preferences.
        split_candidates(candidates: list[int])
            Split the candidates evenly into those preferred and not preferred by the voter.
        general_bucket_question(candidates: list[int], question: list[int])
            Split the candidates into buckets based on the voter's answers to the general bucket question.
        __str__()
            Return a string representation of the voter.
    """

    def __init__(self, preferences: list[int]) -> None:
        """
        Initialize the voter with ordinal preferences.
        :param preferences: list of integers representing the ordinal preferences of the voter.
        """
        self.OrdinalPreferences = preferences

    def split_candidates(self, candidates: list[int]) -> list[list[int]]:
        """
        Split the candidates evenly into those preferred and not preferred by the voter.
        :param candidates: the list of candidates to split.
        :return: a tuple containing the preferred and not preferred candidates.
        """
        return self.general_bucket_question(candidates, [0.5, 0.5])

    def general_bucket_question(self, candidates: list[int], question: list[float]) -> list[list[int]]:
        """
        Split the given candidates into buckets based on the voter's preferences.
        :param candidates: the list of candidates to split.
        :param question: the bucket ratios for the question.
        :return: a list of candidates in each bucket where the first bucket is the most preferred and
        the last is the least preferred.
        """
        buckets = [[] for _ in question]
        candidates = set(candidates)
        temp = len(candidates)
        for i, bucket in enumerate(question):
            bucket = int(bucket*len(candidates))
            temp -= bucket
            question[i] = bucket
        question[-1] += temp
        left_to_fill = question[0]
        current_bucket = 0
        for candidate in self.OrdinalPreferences:
            if candidate in candidates:
                buckets[current_bucket].append(candidate)
                candidates.discard(candidate)
                left_to_fill -= 1
                if left_to_fill == 0:
                    current_bucket += 1
                    if current_bucket == len(question):
                        break
                    left_to_fill = question[current_bucket]
        return buckets

    def __str__(self):
        """
        Return a string representation of the voter.
        :return: a string representation of the voter.
        """
        return f"Voter with ordinal preferences: {self.OrdinalPreferences}"
