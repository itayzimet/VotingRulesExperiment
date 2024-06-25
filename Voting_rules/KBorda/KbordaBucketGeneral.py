import numpy as np

from Experiment_framework.Election import Election
from Experiment_framework.Voter import Voter
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
from Voting_rules import questionPrice
import bottleneck as bn


class Node:
    def __init__(self, sons: list, value) -> None:
        self.sons = sons
        self.value = value


class KbordaBucketGeneral(VotingRuleConstrained):
    questions = []

    def find_winners(self, election: Election, num_winners: int, question_limit: int) -> list[int]:
        voters = election.voters
        candidates = election.candidates
        num_candidates = election.numberOfCandidates
        scores = np.zeros(num_candidates, dtype=int)
        self.questions = [question_limit // len(voters)] * len(voters)
        for i, voter in enumerate(voters):
            if self.questions[i] == 0:
                break
            root_node = Node([], candidates)
            self.__fill_tree(i, voter, root_node, [num_candidates // 2] * 2)
            rank = num_candidates
            self.__score_candidates(root_node, scores, rank)
        return bn.argpartition(scores, num_winners)[-num_winners:]

    def __fill_tree(self, voter_index: int, voter: Voter, node: Node, question_type: list[int]) -> None:
        if self.questions[voter_index] <= 0 or len(node.value) == 1:
            return
        self.questions[voter_index] -= 1
        buckets = voter.general_bucket_question(node.value, question_type)

        for bucket in buckets:
            node.sons.append(Node([], bucket))
            next_question_type = [len(bucket) - len(bucket) // 2, len(bucket) // 2]
            self.__fill_tree(voter_index, voter, node.sons[-1], next_question_type)

    def __score_candidates(self, node: Node, scores: np.ndarray, rank: int) -> None:
        if len(node.sons) == 0:  # node is a leaf
            # score them all based on the position of the leaf regardless of the order in the leaf
            for candidate in node.value:
                scores[candidate] += rank - (len(node.value) // 2)
            return
        for i, son in enumerate(node.sons):
            self.__score_candidates(son, scores, rank - (len(node.sons[i - 1].value) // 2))
            rank -= len(son.value)

    @staticmethod
    def __str__():
        return "K-Borda Bucket General as split"
