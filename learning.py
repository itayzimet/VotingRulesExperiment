import random

import bottleneck as bn
import torch
import torch.nn as nn
import torch.optim as optim

from Experiment_framework.Experiment_helper import fabricate_election
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaBucket import KbordaBucket


class QuestionGenerator(nn.Module):
    def __init__(self, input_size = 4, hidden_size = 64, output_size = 10):
        super(QuestionGenerator, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
        )
    
    def forward(self, x, temperature = 1.0):
        temp = self.network(x)
        probabilities = torch.softmax(temp / temperature, dim = 1).squeeze()
        return probabilities


def train_model(_model, num_epochs = 100, learning_rate = 0.001):
    optimizer = optim.Adam(_model.parameters(), lr = learning_rate)
    criterion = nn.MSELoss()
    
    for epoch in range(num_epochs):
        num_winners = 50
        num_candidates = 100
        num_voters = 100
        budget = random.randint(1, 150000)
        
        input_tensor = torch.tensor([num_winners, num_candidates, num_voters, budget], dtype = torch.float32).unsqueeze(
            0)
        
        optimizer.zero_grad()
        question = _model(input_tensor).squeeze()
        
        election = fabricate_election(num_candidates, num_voters)
        true_scores = Kborda.calculate_scores(election)
        true_winners = bn.argpartition(true_scores, num_winners)[-num_winners:]
        
        kborda_bucket = KbordaBucket(question.tolist())
        test_scores = kborda_bucket.calculate_scores(election, budget)
        test_winners = bn.argpartition(test_scores, num_winners)[-num_winners:]
        
        symmetric_difference = len(set(true_winners) ^ set(test_winners))
        
        loss = symmetric_difference / num_winners + criterion(torch.tensor(true_scores, dtype = torch.float32),
                                                              torch.tensor(test_scores, dtype = torch.float32))
        
        # Add the differentiable connection to the loss
        loss = loss * question.sum()
        
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item()}")
            print(f"Question: {question.tolist()}")
            print(f"Symmetric difference: {symmetric_difference}")
    
    return _model


def evaluate_model(model, num_tests = 10000):
    total_error = 0
    criterion = nn.MSELoss()
    
    for _ in range(num_tests):
        num_candidates = random.randint(1, 100)
        num_winners = random.randint(1, num_candidates//2)
        num_voters = random.randint(1, 100)
        budget = random.randint(1, 150000)
        
        input_tensor = torch.tensor([num_winners, num_candidates, num_voters, budget], dtype = torch.float32).unsqueeze(
            0)
        
        with torch.no_grad():
            question = model(input_tensor).squeeze()
        
        election = fabricate_election(num_candidates, num_voters)
        kborda_bucket = KbordaBucket(list(question.numpy()))
        # true_scores = torch.tensor(Kborda.calculate_scores(election), dtype = torch.float32)
        # true_scores = true_scores / true_scores.sum()
        #
        # test_scores = torch.tensor(kborda_bucket.calculate_scores(election, budget), dtype = torch.float32)
        # test_scores = test_scores / test_scores.sum()
        
        true_winners = kborda_bucket.find_winners(election, num_winners, budget)
        test_winners = KbordaBucket(question.tolist()).find_winners(election, num_winners, budget)
        
        symmetric_difference = len(set(true_winners) ^ set(test_winners))
        
        error = symmetric_difference
        error = error * question.sum()
        total_error += error
    
    return total_error / num_tests


# Create and train the model
model = QuestionGenerator()
trained_model = train_model(model)

# Evaluate the trained model
final_error = evaluate_model(trained_model)
print(f"Final average error: {final_error}")


# Test the trained model
def test_model(model):
    for _ in range(10):
        num_winners = random.randint(1, 50)
        num_candidates = random.randint(1, 100)
        num_voters = random.randint(1, 100)
        budget = random.randint(1000, 150000)
        
        input_tensor = torch.tensor([num_winners, num_candidates, num_voters, budget], dtype = torch.float32).unsqueeze(
            0)
        
        with torch.no_grad():
            question = model(input_tensor).squeeze().tolist()
        
        print(f"""Inputs:
        num winners: {num_winners}
        num candidates: {num_candidates}
        num voters: {num_voters}
        budget: {budget}""")
        print(f"Output: {[f'{x:.6f}' for x in question]}")
        print(f"Sum: {sum(question):.6f}")
        print()


print("\nTesting the trained model:")
test_model(trained_model)
