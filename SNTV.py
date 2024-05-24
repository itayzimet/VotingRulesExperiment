#!/usr/bin/python
#-*- coding: utf-8 -*-

from VotingRule import VotingRule

class SNTV(VotingRule):
    def __init__(self):
        pass

    def findWinners(election, numWinners):
        noOfVoters = election.getNumberOfVoters()
        candidates = election.getCandidates().copy()
        candidatesScores = [0] * len(candidates)
        for voter in range(noOfVoters):
            candidatesScores[election.voters[voter].getNextPrefrence()] += 1
        candidates.sort(reverse = True, key = lambda x: candidatesScores[x])
        election.reset()
        return candidates[:numWinners]