#!/usr/bin/python
# -*- coding: utf-8 -*-

class Voter:
    """
    A class to represent a voter with ordinal preferences.

    Attributes:
        OrdinalPreferences : list[int]
            List of integers representing the ordinal preferences of the voter.

    Methods:
        get_preferences() -> list[int]:
            Returns the ordinal preferences of the voter.
        get_preference(index: int) -> int:
            Returns the candidate at the given index in the voter's ordinal preferences.
        __init__(preferences: list[int]) -> None:
            Initializes the voter with ordinal preferences.
        __str__() -> str:
            Returns a string representation of the voter.
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
        # Every candidate is in the voter's preferences so the criteria is if half or more of the candidates are worse than the candidate in question, the candidate is preferred
        preferred_candidates = []
        not_preferred_candidates = []
        for candidate in candidates:
            if sum([candidate < candidate2 for candidate2 in self.OrdinalPreferences]) >= len(candidates) // 2:
                preferred_candidates.append(candidate)
            else:
                not_preferred_candidates.append(candidate)
        return preferred_candidates, not_preferred_candidates


    def pairwise_comparison(self, candidate1: int, candidate2: int) -> int:
        """
        Returns 1 if the voter prefers candidate1 over candidate2 and -1 if the voter prefers candidate2 over candidate1.
        :param candidate1: the first candidate to compare.
        :param candidate2: the second candidate to compare.
        :return: 1 if the voter prefers candidate1 over candidate2, -1 if the voter prefers candidate2 over candidate1.
        """
        if self.OrdinalPreferences.index(candidate1) < self.OrdinalPreferences.index(candidate2):
            return 1
        else:
            return -1

    def __str__(self):
        return f"Voter with ordinal preferences: {self.OrdinalPreferences}"
