"""
This module is a helper module for the main part of the experiment

It contains the following functions:
    - run_experiment(target_committee_size: int, num_candidates: int, num_voters: int, voting_rule,
    constrained_voting_rule, number_of_questions: list[int]) -> list[int]
    - run_experiment_wrapper(args) -> list[int]
"""
import json
import os
import pickle
import random
from multiprocessing import Pool
from typing import Any, Dict, Tuple

import matplotlib
import plotly.express as px
import requests
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from tqdm import tqdm, trange

from Experiment_framework.Experiment import Experiment
from Experiment_framework.Experiment_helper import fabricate_election


def run_experiment(
		target_committee_size: int, num_candidates: int, num_voters: int, voting_rule, constrained_voting_rule,
		number_of_questions: list[int]) -> list[int]:
	"""
	Run the experiment a single time with one fabricated election and return the distances between the committees for
	that election and the given numbers of questions
	:param target_committee_size: the size of the committee to be found
	:param num_candidates: the number of candidates in the election
	:param num_voters: the number of voters in the election
	:param voting_rule: the voting rule to find the committee with
	:param constrained_voting_rule: the constrained voting rule to find the committee with
	:param number_of_questions: the number of questions all voters can answer for the constrained voting rule
	:return: list of distances between all the committees
	"""
	# Fabricate an election with num_candidates candidates and num_voters voters
	election = fabricate_election(num_candidates, num_voters)
	# Run the experiment
	experiment = Experiment(target_committee_size, election, voting_rule, constrained_voting_rule, number_of_questions)
	# Return the distance between the two committees
	return experiment.committeeDistance


def run_experiment_wrapper(args):
	"""
	Wrapper function for the run_experiment function to allow for the use of the Pool class
	:param args: the arguments for the run_experiment function
	:return: the result of the run_experiment function
	"""
	return run_experiment(*args)


def run_test(params: dict[str, any]) -> dict[Any, list[int]]:
	"""
	Run the experiment multiple times and return the average differences between the committees

	:param params: the parameters of the test
	:return: the average differences between the committees
	"""
	target_committee_size = params['target_committee_size']
	num_candidates = params['num_candidates']
	num_voters = params['num_voters']
	voting_rule = params['voting_rule']
	constrained_voting_rules = params['constrained_voting_rule']
	number_of_questions = params['number_of_questions']
	number_of_runs = params['number_of_runs']
	multithreaded = params['multithreaded']
	averages = {}
	load_dotenv()
	for rule in constrained_voting_rules:
		if multithreaded:
			with Pool() as pool:
				differences = list(tqdm(pool.imap(run_experiment_wrapper, [
						(target_committee_size, num_candidates, num_voters, voting_rule, rule, number_of_questions) for
						_ in range(number_of_runs)]), total = number_of_runs,
				                        desc = f'Running experiments: {rule.__str__()}', ))
		else:
			differences = []
			for _ in trange(number_of_runs, desc = f'Running experiments: {rule.__str__()}', total = number_of_runs, ):
				differences.append(run_experiment(target_committee_size, num_candidates, num_voters, voting_rule, rule,
				                                  number_of_questions))
		average_differences = [0] * len(number_of_questions)
		# Average the results from the different runs
		for difference in differences:
			for i in range(len(difference)):
				average_differences[i] += difference[i]
		for i in range(len(average_differences)):
			average_differences[i] /= number_of_runs
		averages[rule.__str__()] = average_differences
	return averages


def plot_graph(test_params: dict[str, any], averages: dict[Any, list[int]], file_name = "graph", latex = True) -> str:
	"""
	Plots the graph for the experiment
	:param test_params: the parameters of the test
	:param averages: the average differences between the committees for the different constrained voting rules
	:param file_name: the name of the file to save the graph to
	:param latex: whether to use latex for the graph
	:return: None

	"""
	if not latex:
		# make it a scatter plot
		fig = px.scatter()
		for rule, average in averages.items():
			fig.add_scatter(x = list(test_params['number_of_questions']), y = average, mode = 'markers',
			                name = rule.__str__())
		fig.update_layout(
				title = f"{test_params['voting_rule'].__str__()}: {test_params['target_committee_size']} committee "
				        f"members, "
				        f"{test_params['num_candidates']} candidates, {test_params['num_voters']} "
				        f"voters, {test_params['number_of_runs']} runs", xaxis_title = 'Number of questions',
				yaxis_title = 'Distance between the committees')

		fig.show()
		fig.write_html(file_name + ".html")
		return file_name + ".html"
	else:
		# matplotlib.use("pgf")
		# matplotlib.rcParams.update(
		# 		{"pgf.texsystem": "pdflatex", 'font.family': 'serif', 'text.usetex': True, 'pgf.rcfonts': False, })
		plt.figure()
		fig, ax = plt.subplots()
		plt.rcParams["figure.autolayout"] = True
		plt.title(f"{test_params['voting_rule'].__str__()}: {test_params['target_committee_size']} committee members, "
		          f"{test_params['num_candidates']} candidates, {test_params['num_voters']} "
		          f"voters, {test_params['number_of_runs']} runs")
		x = list(test_params['number_of_questions'])
		colors = plt.cm.get_cmap('tab10', len(averages))  # Use a colormap with distinct colors
		for i, (rule, average) in enumerate(averages.items()):
			plt.plot(x, average, label=rule.__str__(), color=colors(i))
		plt.xlabel('Number of questions')
		plt.ylabel('Distance between the committees')
		plt.legend(bbox_to_anchor=(0.5, -0.1), loc="upper center", ncol=len(averages)//4)
		plt.savefig(file_name + ".svg", bbox_inches='tight')
		return file_name + ".svg"


def write_averages_to_file(averages, test_parameters):
	if os.path.exists('averages.pickle'):
		os.remove('averages.pickle')
	with open('averages.pickle', 'wb') as f:
		# add the averages to a new pickle file
		data = [averages, int(test_parameters['number_of_runs'])]
		pickle.dump(data, f)


def combine_saved_current(
		averages: dict[Any, list[int]], no_of_saved_runs: int, saved_averages: dict, test_parameters: dict) -> Tuple[
	dict, dict]:
	if saved_averages != {}:
		for key in averages:
			if key in saved_averages:
				for i, average in enumerate(averages[key]):
					averages[key][i] = (((averages[key][i] * test_parameters['number_of_runs'] + saved_averages[key][
						i] * no_of_saved_runs)) / (test_parameters['number_of_runs'] + no_of_saved_runs))
		no_runs = int(no_of_saved_runs) + int(test_parameters['number_of_runs'])
		test_parameters['number_of_runs'] = no_runs
		return averages, test_parameters
	return averages, test_parameters


def extract_saved_averages(file: str = 'averages.pickle') -> Tuple[int, Dict]:
	saved_averages = {}
	try:
		with open(file, 'rb') as f:
			saved_averages = pickle.load(f)
			no_of_saved_runs = int(saved_averages[1])
			saved_averages = saved_averages[0]
			return no_of_saved_runs, saved_averages
	except:
		return 0, saved_averages


def send_message(message: str):
	load_dotenv()
	token = os.getenv("TELEGRAM_TOKEN")
	chat_id = os.getenv("CHAT_ID")
	requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data = {"chat_id": chat_id, "text": message})
	print(message)


def send_file(file: str) -> dict[str, any]:
	load_dotenv()
	token = os.getenv("TELEGRAM_TOKEN")
	chat_id = os.getenv("CHAT_ID")
	file = open(file, 'rb')
	url = f"https://api.telegram.org/bot{token}/sendDocument"
	files = {'document': file}
	data = {'chat_id': chat_id}
	response = requests.post(url, files = files, data = data)
	content = response.content.decode("utf8")
	js = json.loads(content)
	file.close()
	return js


def send_files(files: list[str]):
	for file in files:
		send_file(file)


def send_plot(test_parameters: dict[str, any], averages: dict[Any, list[int]]):
	temp_file_name = random.randint(0, 1000000).__str__()
	filename = plot_graph(test_parameters, averages, temp_file_name)
	send_file(filename)
	# os.remove(filename)
