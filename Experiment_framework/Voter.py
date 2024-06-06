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
        pairwise_comparison(candidate1: int, candidate2: int)
            Returns 1 if the voter prefers candidate1 over candidate2 and -1 if the voter prefers candidate2 over candidate1.
        __str__()
            Return a string representation of the voter.
    """

    def __init__(self, preferences: list[int]) -> None:
        """
        Initialize the voter with ordinal preferences.
        :param preferences: list of integers representing the ordinal preferences of the voter.
        """
        self.OrdinalPreferences = preferences

    def get_preferences(self, ) -> list[int]:
        """
        Get the ordinal preferences of the voter.
        :return: the ordinal preferences of the voter.
        """
        return self.OrdinalPreferences

    def get_preference(self, index: int) -> int:
        """
        Get the candidate at the given index in the voter's ordinal preferences.
        :param index: the index of the preference to get.
        :return: the ordinal preference of the voter at the given index.
        """
        return self.OrdinalPreferences[index]

    def split_candidates(self, candidates: list[int]) -> tuple[list[int], list[int]]:
        """
        Split the candidates evenly into those preferred and not preferred by the voter.
        :param candidates: the list of candidates to split.
        :return: a tuple containing the preferred and not preferred candidates.
        """
        # Every candidate is in the voter's preferences so the criteria is if half or more of the candidates are
        # worse than the candidate in question, the candidate is preferred
        need_to_find = len(candidates) // 2
        candidates = set(candidates)
        preferred_candidate = []
        for candidate in self.OrdinalPreferences:
            if need_to_find == 0:
                return preferred_candidate, list(candidates)
            if candidate in candidates:
                preferred_candidate.append(candidate)
                candidates.discard(candidate)
                need_to_find -= 1



    def pairwise_comparison(self, candidate1: int, candidate2: int) -> int:
        """
        Returns 1 if the voter prefers candidate1 over candidate2 and -1 if the voter prefers candidate2 over candidate1.
        :param candidate1: the first candidate to compare.
        :param candidate2: the second candidate to compare.
        :return: 1 if the voter prefers candidate1 over candidate2, -1 if the voter prefers candidate2 over candidate1.
        """
        i = 0
        while i < len(self.OrdinalPreferences):
            if self.OrdinalPreferences[i] == candidate1:
                return 1
            if self.OrdinalPreferences[i] == candidate2:
                return -1
            i += 1

    def __str__(self):
        """
        Return a string representation of the voter.
        :return: a string representation of the voter.
        """
        return f"Voter with ordinal preferences: {self.OrdinalPreferences}"
