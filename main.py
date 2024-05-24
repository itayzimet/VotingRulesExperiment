from Experiment import Experiment
from ExperimentHelper import ExperimentHelper
from SNTV import SNTV
from SNTV_constrained import SNTV_constrained
from VotingRule import VotingRule

def main():
    election = ExperimentHelper.fabricateElection(10, 5)
    experiment = Experiment(5, election, SNTV, SNTV_constrained, 5)
    distance = experiment.experiment()
    print(distance)

if __name__ == '__main__':
    main()