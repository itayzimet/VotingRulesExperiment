import os

from dotenv import load_dotenv
import torch
import torch.optim as optim
from tqdm.contrib.telegram import trange

from ai_framework import evaluate_function, test_best_function
from Experiment_framework.main_helper import send_message
from QuestionGenerator import QuestionGenerator


def train_model(_model, num_epochs = 100, learning_rate = 0.001):
    optimizer = optim.Adam(_model.parameters(), lr = learning_rate)
    
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    
    for epoch in trange(num_epochs, desc = "Training model", unit = "epoch", chat_id = chat_id, token = token,
                        leave = True):
        loss_float = evaluate_function(_model)
        loss = torch.tensor(loss_float, dtype = torch.float32, requires_grad = True)
        loss.backward()
        optimizer.step()
    return _model


def main():
    # Create and train the model
    model = QuestionGenerator()
    trained_model = train_model(model)
    
    training_summary = f"Training complete."
    
    # Evaluate the trained model
    final_error = evaluate_function(trained_model)
    training_summary += f"Final average error: {final_error}"
    send_message(training_summary)
    test_best_function(trained_model)


if __name__ == '__main__':
    main()
