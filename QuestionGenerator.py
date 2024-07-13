import torch
from torch import nn as nn


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
