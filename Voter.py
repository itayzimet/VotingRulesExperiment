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

    def reset(self, ) -> None:
        """
        Reset the voter to the first preference.
        """
        self.nextPreference = 0
