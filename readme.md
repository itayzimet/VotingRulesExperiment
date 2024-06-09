# voting experiment

This is a simple voting experiment to test different voting system.

## Table of contents
- [Installation and usage](#installation-and-usage)
- [Experimental protocol](#experimental-protocol)
  - [Experiment control parameters](#experiment-control-parameters)
  - [Data fabrication](#data-fabrication)
  - [Experiment procedure](#experiment-procedure)
  - [Voting systems](#voting-systems)
  - [Question types](#question-types)
  - [Distance metric](#distance-metric)
- [todo](#todo)

## Installation and usage

clone the repository and change main.py to your liking. Then run the following commands to create a virtual environment and install the required packages.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
or if you are using windows
```bash
python -m venv venv
venv\Scripts\activate.ps1
pip install -r requirements.txt
```

Then run the following command to run the experiment
```bash
python main.py
```
## Experimental protocol
### Experiment control parameters
- Number of voters: 10
- Number of candidates: 100
- Target committee size: 50
- Number of questions: 1-1000 (increment by 1)
- Number of runs: 20
- Voting system: Kborda, SNTV
- Question type: Next best candidate (Next), halve set of candidates (Split)
- Voting system parameters: None

### Data fabrication
- Generate candidates labeled 0-number of candidates - 1
- Generate voters with random preferences by shuffling the candidates list for each voter

### Experiment procedure
1. For each run:
   1. Generate candidates and voters
   2. For each voting system
      1. generate a committee of size target committee size using the voting system
      2. For each approximation of the voting system
         1. For each number of questions
            1. generate an approximation of the committee using the approximation of the voting system
            2. calculate the distance between the approximation and the committee
            3. store the distance in a list
2. calculate the average distances from the different runs for each voting system and approximation for all number of questions
3. plot the average distances for each voting system and approximation for all number of questions
4. save the plot
5. repeat for all voting systems and approximations

### Voting systems
- Kborda: Select the top k candidates with the highest borda score
  - KbordaNextEq: use the (next) question to select the top k candidates with the highest borda score under a question number constraint while maintaining the same number of questions for all voters
  - KbordaNextFCFS: same as KbordaNextEq but instead of maintaining the same number of questions for all voters, first use all questions you can for the first voter, then use all questions you can for the second voter, and so on
  - KbordaSplitEq: use the (split) question to select the top k candidates with the highest borda score under a question number constraint while maintaining the same number of questions for all voters. works by recursively splitting the set of candidates in half for each voter to get an approximation of his ordinal preferences.
  - KbordaSplitFCFS: same as KbordaSplitEq but instead of maintaining the same number of questions for all voters, first use all questions you can for the first voter, then use all questions you can for the second voter, and so on
  - KbordaNextLastEq: use the (next) and (last) questions to select the top k candidates with the highest borda score under a question number constraint while maintaining the same number of questions for all voters
  - KbordaNextLastFCFS: same as KbordaNextLastEq but instead of maintaining the same number of questions for all voters, first use all questions you can for the first voter, then use all questions you can for the second voter, and so on
- SNTV: Select the top k candidates with the highest number of votes
  - SNTVConstrained: use the (next) question to select the top k candidates with the highest number of votes under a question number constraint, while using the question on a first-come-first-serve basis.
- Random: Select k candidates at random

### Question types
- Next: Ask the voter for the next best candidate in his preference list
- Last: Ask the voter for the next worst candidate in his preference list
- Split: Ask the voter to halve the set of candidates provided into two sets, the first set containing the candidates he prefers over the second set

### Distance metric
- The only metric currently implemented is the size of the symmetric difference between the approximation and the committee

## todo
- [ ] Implement more voting systems
- [ ] Implement more approximation methods 
- [ ] Implement more distance metrics
- [ ] Implement more question types 
