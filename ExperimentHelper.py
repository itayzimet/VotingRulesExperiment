#!/usr/bin/python
#-*- coding: utf-8 -*-
import random

from Election import Election
from Voter import Voter

class ExperimentHelper:
    def __init__(self):
        pass

    
    def fabricateElection(numberOfCandidates, numberOfVoters):
        candidates = []
        for i in range(numberOfCandidates):
            candidates.append(i)
        voters = list()
        for i in range(numberOfVoters):
            voterOrdinalPrefrences = random.sample(candidates, numberOfCandidates)
            voter = Voter(voterOrdinalPrefrences)
            voters.append(voter)
        return Election(candidates, voters)

    def committeeDistance(committee1, committee2):
        return len(set(committee1).symmetric_difference(set(committee2)))

