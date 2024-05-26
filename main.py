from Experiment import Experiment
from ExperimentHelper import ExperimentHelper
from SNTV import SNTV
from SNTV_constrained import SNTV_constrained
from KBorda import KBorda
from KbordaConstrained import KbordaConstrained


def main():
    """
    Main function to run the experiment
    :return: None
    """


    # Fabricate an election with 10 candidates and 5 voters
    election = ExperimentHelper.fabricate_election(10, 5)
    # Run the experiment with the Single Non-Transferable Vote voting rule and the constrained Single Non-Transferable Vote voting rule
    print("""Experiment with random election, 10 candidates, 5 voters, 5 questions and 5 winners using SNTV and SNTV constrained:
_________________________________________________________________________________________________________________________________________________________""")
    print(Experiment(5, election, SNTV, SNTV_constrained, 5))
    print("""_________________________________________________________________________________________________________________________________________________________""")
    # Run the experiment with the K-Borda voting rule and the constrained K-Borda voting rule
    print("""Experiment with random election, 10 candidates, 5 voters, 5 questions and 5 winners using K-Borda and K-Borda constrained:
_________________________________________________________________________________________________________________________________________________________""")
    print(Experiment(5, election, KBorda, KbordaConstrained, 5))
    print("""_________________________________________________________________________________________________________________________________________________________""")


if __name__ == '__main__':
    main()
