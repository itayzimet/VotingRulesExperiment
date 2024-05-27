#!/usr/bin/python
# -*- coding: utf-8 -*-

class Voter:
    """
    A class to represent a voter with ordinal preferences.

    Attributes:
        OrdinalPreferences : list[int]
            List of integers representing the ordinal preferences of the voter.

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

    def __str__(self):
        return f"Voter with ordinal preferences: {self.OrdinalPreferences}"
