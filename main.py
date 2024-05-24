from Experiment import Experiment
from ExperimentHelper import ExperimentHelper
from SNTV import SNTV
from SNTV_constrained import SNTV_constrained


def main():
    """
    Main function to run the experiment
    :return: None
    """
    # Fabricate an election with 10 candidates and 5 voters
    election = ExperimentHelper.fabricate_election(10, 5)
    # Run the experiment with the Single Non-Transferable Vote voting rule and the constrained Single Non-Transferable Vote voting rule
    experiment = Experiment(5, election, SNTV, SNTV_constrained, 5)
    distance = experiment.experiment()
    print(distance)


if __name__ == '__main__':
    main()
