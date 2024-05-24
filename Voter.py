#!/usr/bin/python
#-*- coding: utf-8 -*-

class Voter:
    def __init__(self):
        self.OrdinalPrefrences = []
        self.nextPrefrence = 0
    def __init__(self, prefrences):
        self.OrdinalPrefrences = prefrences
        self.nextPrefrence = 0

    def getNextPrefrence(self, ):
        if self.nextPrefrence < len(self.OrdinalPrefrences):
            self.nextPrefrence += 1
            return self.OrdinalPrefrences[self.nextPrefrence - 1]
        else:
            return None

    def getPrefrences(self, ):
        return self.OrdinalPrefrences
    
    def reset(self, ):
        self.nextPrefrence = 0
        return None