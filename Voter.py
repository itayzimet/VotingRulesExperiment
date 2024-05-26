#!/usr/bin/python
# -*- coding: utf-8 -*-

class Voter:
    """
    A class to represent a voter with ordinal preferences.

    Attributes:
        OrdinalPreferences : list[int]
            List of integers representing the ordinal preferences of the voter.
        nextPreference : int
            The index of the next preference to be considered.

    Methods:
        get_next_preference() -> int | None:
            Returns the next preference of the voter.
        get_preferences() -> list[int]:
            Returns the ordinal preferences of the voter.
        reset() -> None:
            Resets the voter to the first preference.
    """

    def __init__(self, preferences: list[int]) -> None:
        """
        Initialize the voter with ordinal preferences.
        :param preferences: list of integers representing the ordinal preferences of the voter.
        """
        self.OrdinalPreferences = preferences
        self.nextPreference = 0

    def get_next_preference(self, ) -> int | None:
        """
        Get the next preference of the voter.
        :return: the next preference of the voter.
        """
        if self.nextPreference < len(self.OrdinalPreferences):
            self.nextPreference += 1
            return self.OrdinalPreferences[self.nextPreference - 1]
        else:
            return None

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

    def get_candidate_index(self, candidate: int) -> int:
        """
        Get the index of the given candidate in the voter's ordinal preferences.
        :param candidate: the candidate to find the index of.
        :return: the index of the candidate in the voter's ordinal preferences.
        """
        return self.OrdinalPreferences.index(candidate)
    def reset(self, ) -> None:
        """
        Reset the voter to the first preference.
        """
        self.nextPreference = 0

    def __str__(self):
        return f"Voter with ordinal preferences: {self.OrdinalPreferences}"
