#!/usr/bin/python
#-*- coding: utf-8 -*-

from VotingRuleConstrained import VotingRuleConstrained

class SNTV_constrained(VotingRuleConstrained):
    def __init__(self):
        pass

    def findWinners(election, numWinners, questionLimit):
        noOfVoters = election.getNumberOfVoters()
        candidates = election.getCandidates().copy()
        candidatesScores = [0] * len(candidates)
        for voter in range(noOfVoters):
            if questionLimit == 0:
                break
            candidatesScores[election.voters[voter].getNextPrefrence()] += 1
            questionLimit -= 1
        candidates.sort(reverse = True, key = lambda x: candidatesScores[x])
        return candidates[:numWinners]