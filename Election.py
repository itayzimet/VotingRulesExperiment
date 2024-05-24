#!/usr/bin/python
#-*- coding: utf-8 -*-

class Election:
    def __init__(self):
        self.voters = list()
        self.candidates = []
        self.numberOfVoters = 0
        self.numberOfCandidates = 0
    def __init__(self, candidates, voters):
        self.voters = voters
        self.candidates = candidates
        self.numberOfVoters = len(voters)
        self.numberOfCandidates = len(candidates)

    def getVoter(self, voterID):
        return self.voters[voterID]
    def getVoters(self, ):
        return self.voters

    def getCandidates(self, ):
        return self.candidates

    def getNumberOfVoters(self, ):
        return self.numberOfVoters

    def getNumberOfCandidates(self, ):
        return self.numberOfCandidates

    def reset(self, ):
        for voter in self.voters:
            voter.reset()
        return None
