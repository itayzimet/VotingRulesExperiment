import math
import os
import random

import bottleneck as bn
from dotenv import load_dotenv
import numpy as np
import requests
from tqdm.contrib.telegram import trange

from Experiment_framework import Experiment_helper
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaBucket import KbordaBucket


def send_message(message: str):
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data = {"chat_id": chat_id, "text": message})
    print(message)


def softmax(x: list):
    """Compute the softmax of vector x."""
    # all output values should be between 0 and 1
    # the sum of all output values should be 1
    # filter out the values that are less than 1/1000 they are considered to be 0 and should be removed
    e_x = np.exp(np.array(x) - np.max(x))
    e_x = e_x[e_x > 1e-3]
    return e_x / e_x.sum()


def random_function(min_size = 1, max_size = 10):
    """Generate a random function structure with variable output size."""
    
    operations = ['+', '-', '*', '/', '%', '**']
    inputs = ['winners', 'candidates', 'voters', 'budget']
    constants = [str(x) for x in [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
    
    def generate_expr():
        if random.random() < 0.1:
            return f"{random.choice(constants)}"
        elif random.random() < 0.6:
            return f"{random.choice(inputs)}"
        else:
            return f"({generate_expr()} {random.choice(operations)} {generate_expr()})"
    
    size = random.randint(min_size, max_size)
    return [generate_expr() for _ in range(size)]


def mutate_function(func):
    """Mutate the given function slightly."""
    if random.random() < 0.7 and len(func) > 1:
        # Modify an existing expression
        index = random.randint(0, len(func) - 1)
        func[index] = random_function(1, 1)[0]
    elif random.random() < 0.5 and len(func) > 1:
        # Remove an expression
        index = random.randint(0, len(func) - 1)
        func.pop(index)
    else:
        # Add a new expression
        func.append(random_function(1, 1)[0])
    return func


def evaluate_function(func: list, num_tests = 10, num_winners = 50, num_candidates = 100, num_voters = 100,
                      max_budget = 10000):
    """Evaluate the function with the given parameters."""
    
    def execute(expression, _num_winners: int, _num_candidates: int, _num_voters: int, _budget: int):
        winners = _num_winners
        candidates = _num_candidates
        voters = _num_voters
        budget = _budget
        return eval(expression)
    
    total_error = 0
    for _ in range(num_tests):
        budget = random.randint(0, max_budget)
        try:
            # Generate a question type
            question = [execute(expression, num_winners, num_candidates, num_voters, budget) for expression in func]
            question = softmax(question)
            sum_question = sum(question)
            if sum_question > 1:
                # Normalize the question type
                question = [q / sum_question for q in question]
                # Add a final bucket to make it sum to 1
                question.append(1 - sum_question)
            else:
                if sum_question != 1:
                    # Add a final bucket to make it sum to 1
                    question.append(1 - sum_question)
            
            # Generate an election based on the parameters
            election = Experiment_helper.fabricate_election(num_candidates, num_voters)
            # experiment = Experiment(num_winners, election, Kborda, KbordaBucket, [budget], question)
            true_scores = Kborda.calculate_scores(election)
            true_scores = np.array(true_scores)
            committee_scores = KbordaBucket(question).calculate_scores(election, budget)
            committee_scores = np.array(committee_scores)
            
            true_winners = bn.argpartition(true_scores, num_winners)[-num_winners:]
            committee_winners = bn.argpartition(committee_scores, num_winners)[-num_winners:]
            
            symmetric_difference = len(set(true_winners) ^ set(committee_winners))
            mean_squared_error = np.mean((true_scores - committee_scores) ** 2)
            
            error = symmetric_difference
            total_error += error
        except:
            total_error += 1000000
    return total_error / num_tests


def simulated_annealing(t, _alpha, _max_iter):
    load_dotenv()
    """Perform simulated annealing to find the best function."""
    # Generate a random function
    current_function = random_function()
    current_score = evaluate_function(current_function)
    _best_function = current_function.copy()
    _best_score = current_score
    
    iterations = trange(_max_iter, desc = "Simulated Annealing",
                        token = os.getenv("TELEGRAM_TOKEN"), chat_id = os.getenv("CHAT_ID"))
    
    for _ in iterations:
        t *= _alpha
        neighbour_function = mutate_function(current_function.copy())
        neighbour_score = evaluate_function(neighbour_function)
        if neighbour_score < current_score:
            current_score = neighbour_score
            current_function = neighbour_function
            if neighbour_score < _best_score:
                _best_score = neighbour_score
                _best_function = neighbour_function.copy()
                iterations.postfix = f"Best score: {neighbour_score:.2f}"
        else:
            p = math.exp((current_score - neighbour_score) / t)
            if random.random() < p:
                current_score = neighbour_score
                current_function = neighbour_function
            iterations.postfix = f"Best score: {_best_score:.2f}"
        if _best_score < 0.01:
            break
    return _best_function, _best_score


# Test the best function
def test_best_function(func):
    def execute(expression, _num_winners: int, _num_candidates: int, _num_voters: int, _budget: int):
        winners = _num_winners
        candidates = _num_candidates
        voters = _num_voters
        budget = _budget
        return eval(expression)
    
    for _ in range(10):
        x1, x2, x3, x4 = random.randint(1, 50), random.randint(1, 100), random.randint(1, 100), random.randint(1,
                                                                                                               150000)
        try:
            result = [execute(expression, x1, x2, x3, x4) for expression in func]
            normalized_result = softmax(result)
        except ZeroDivisionError:
            result = [0]
            normalized_result = [1]
        send_message(f"""Inputs:
        num winners: {x1}
        num candidates: {x2}
        num voters: {x3}
        budget: {x4}""")
        send_message(f"Output (size {len(result)}): {[f'{x:.6f}' for x in result]}")
        send_message(f"Sum: {sum(result):.6f}")
        send_message(f"Normalized: {[f'{x:.6f}' for x in normalized_result]}")
        send_message(f"Sum of normalized: {sum([x / sum(result) for x in result]):.6f}")
        send_message(f"Error: {evaluate_function(func)}")
        send_message("\n")


def main():
    """
    Main function to run the annealing AI
    :return: None
    """
    T = 1
    alpha = 0.999999995
    max_iter = 1000
    
    best_function, best_score = simulated_annealing(T, alpha, max_iter)
    send_message(f"Best function (vector size: {len(best_function)}):")
    for expr in best_function:
        print(expr)
    send_message(f"Best score (average error): {best_score}")
    
    send_message("\nTesting the best function:")
    test_best_function(best_function)


if __name__ == '__main__':
    main()
