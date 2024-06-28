import numpy as np

from voting_mechanism_design.agents.definitions import BadgeHolderPopulation
from voting_mechanism_design.projects.project import ProjectPopulation
from voting_mechanism_design.funds_distribution.funding_design import FundingDesign

class RoundSimulation:
    """
    Integrates the other components and runs a simulation
    """
    def __init__(
            self, 
            badgeholder_population:BadgeHolderPopulation, 
            projects:ProjectPopulation, 
            funding_design:FundingDesign, 
            random_seed=1234
        ):
        self.badgeholder_population = badgeholder_population
        self.projects = projects
        self.funding_design = funding_design
        self.rng = np.random.default_rng(random_seed)

    def run(self, cast_votes_kwargs=None):
        """
        Steps
        1 - Send application information to the badgeholders
        2 - Execute any communication that happens between badgeholders (for modeling different kinds of behavior)
        3 - Execute agents to vote
        4 - Tally up projects scores
        5 - Allocate funds  
        6 - Compute metrics
        """
        if cast_votes_kwargs is None:
            cast_votes_kwargs = {}
        
        # setup the simulation for reproducibility
        self.badgeholder_population.set_random_generator(self.rng)

        self.badgeholder_population.send_application_information(self.projects)
        self.badgeholder_population.communicate()
        self.badgeholder_population.cast_votes(**cast_votes_kwargs) # this step updates internal variables for each project
        self.funding_design.allocate_funds(self.projects)
        # TODO: compute metrics and store

    def get_results(self):
        pass

