# voting experiment

This is a voting experiment to test different voting systems.

## Installation and usage

clone the repository and change main.py to your liking. Then run the following commands to create a virtual environment
and install the required packages.

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

- Number of voters: 100
- Number of candidates: 100
- Target committee size: 50
- Question budgets: 1 - 150000 (jumps of 1000)
- Number of runs: 20
- Voting system: Kborda
- Question type: Next, Last, Next and Last, Split - all using the refinement query syntax
- Distance metric: size of the symmetric difference between the approximation and the committee

### Data fabrication
 #### IC experiments
- Generate candidates labeled 0-number of candidates - 1
- Generate voters with random preferences by shuffling the candidates list for each voter
 #### mapOf experiments
- Generate different election cultures using the mapof library


### Experiment procedure

#### IC experiments

1. For each run:
    1. Generate candidates and voters
    2. For each voting system
        1. generate a committee of size target committee size using the voting system
        2. For each approximation of the voting system
            1. For each number of questions
                1. generate an approximation of the committee using the approximation of the voting system
                2. calculate the distance between the approximation and the committee
                3. store the distance in a list
2. calculate the average distances from the different runs for each voting system and approximation for all number of
   questions
3. plot the average distances for each voting system and approximation for all number of questions
4. save the plot
5. repeat for all voting systems and approximations

#### mapOf experiments
1. for each culture:
    1. generate a committee of size target committee size using the voting system
    2. For each approximation of the voting system
        1. For each number of questions
            1. generate an approximation of the committee using the approximation of the voting system
            2. calculate the distance between the approximation and the committee
            3. store the distance in a list
2. calculate the sum of normalized distances from the different runs for each voting system and approximation for all number of
   questions - this will be our approximation for how quickly the Query based Rule converges.
3. plot a map of the metrics calculated for each Query based rule
4. save the plots


### Voting systems

- Kborda: Select the top k candidates with the highest borda score
    - KbordaSplitEq: approximate the voters preferences by asking the voter to split the candidates into two sets,
      the first set containing the candidates he prefers over the second set. Then select the top k candidates with the
      highest borda score. Budget is distributed evenly between the voters.
    - KbordaSplitFCFS: same as KbordaSplitEq but budget is distributed on a first come first serve basis.
    - KbordaNextEq: approximate the voters preferences by asking the voter for the next best candidate in his preference
      list. Then select the top k candidates with the highest borda score. Budget is distributed evenly between the
      voters.
    - KbordaNextFCFS: same as KbordaNextEq but budget is distributed  on a first come first serve basis.
    - KbordaLastEq: same as KbordaNextEq but the voter is asked for the next worst candidate in his preference list.
    - KbordaLastFCFS: same as KbordaLastEq but budget is distributed  on a first come first serve basis.
    - KbordaNextLastEq: same as KbordaNextEq but the voter is asked for the next best and worst candidate in his
      preference list.
    - KbordaNextLastFCFS: same as KbordaNextLastEq but the budget is distributedon a first come first serve basis.
- Random: Select k candidates at random

### Question types

- Next: Ask the voter for the next best candidate in his preference list.
- Last: Ask the voter for the next worst candidate in his preference list.
- Split: Ask the voter to halve the set of candidates provided into two sets, the first set containing the candidates he
  prefers over the second set.
- Next and Last: Ask the voter for the next best candidate and the next worst candidate in his preference list.
- All question types use the refinement query syntax described in the latex document

### Distance metric

- The metric implemented is the size of the symmetric difference between the approximation and the
  committee
