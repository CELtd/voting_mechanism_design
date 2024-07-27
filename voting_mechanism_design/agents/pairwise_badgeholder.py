import numpy as np
import copy

from voting_mechanism_design.agents.definitions import BadgeHolder, BadgeHolderPopulation
from voting_mechanism_design.voting_designs.ranking import PairwiseRankingVote

class PairwiseBadgeholder:
    def __init__(
            self, 
            badgeholder_id, 
            voting_style='random', 
            voting_style_kwargs=None,
            expertise=1.0,  # a floating point value indicating how closely to the true impact for a project the badgeholder will vote
                            # if it is not a "random" badgeholder
            laziness=0.0,   # a value between 0 and 1 representing how many projects the badgeholder will skip voting on
            coi_project_ix_vec=[],  # a list of project IDs that the badgeholder has a conflict of interest with
            coi_factor=0.0  # a floating point value between 0 and 1 that indicates how much COI this badgeholder is engaging in
        ):
        self.badgeholder_id = badgeholder_id
        self.votes = []

        self.project_population = None
        self.rng = None
        self.voting_style = voting_style
        self.voting_style_kwargs = voting_style_kwargs

        self.expertise = expertise
        self.laziness = laziness

        # conflict of interest information
        # The way this is implemented in this package is:
        #  if coi_factor is 0, then the badgeholder will not vote ON projects they have a COI with.
        #  if coi_factor > 0, then the badgeholder will vote FOR projects they have a COI with coi_factor% of the time, and vote
        #     the remaining according to their expertise.
        self.coi_project_ix_vec = coi_project_ix_vec
        self.coi_factor = coi_factor

    def reset_voter(self):
        self.votes = []

    def send_applications_to_voter(self, project_population):
        self.project_population = project_population

    def set_random_generator(self, rng):
        self.rng = rng

    def cast_votes(self, view):
        if self.voting_style == 'random':
            self.cast_random_votes(view)
        elif self.voting_style == 'skewed_towards_impact':
            self.cast_skewed_towards_impact_votes(view)
        elif self.voting_style == 'perfect':
            self.cast_perfect_votes(view)
        else:
            raise ValueError(f"{self.voting_style} not yet implemented!")
        
    def _prevote_checks(self):
        """
        view - a list of tuples, where the values are the projects to vote on
               pairwise to the agent to vote on
        """
        assert self.project_population is not None, "Projects have not been sent to the voter yet"
        assert self.rng is not None, "Random generator has not been set"

    # TODO: generalize the voting code for the different voting styles, currently the only one 
    # fully supported is the skewed one

    def cast_perfect_votes(self, view):
        """
        view - a list of tuples, where the values are the projects to vote on
               pairwise to the agent to vote on
        """
        self._prevote_checks()

        for pair in view:
            project1, project2 = pair
            assert self.project_population.get_project(project1.project_id) is not None, "Project 1 is not in the list of projects"
            assert self.project_population.get_project(project2.project_id) is not None, "Project 2 is not in the list of projects"

            # ideal voting
            if project1.true_impact > project2.true_impact:
                project1_vote, project2_vote = 1, 0
            else:
                project1_vote, project2_vote = 0, 1

            vote_obj = PairwiseRankingVote(
                self,  # pass the voter information to the project, although in the real round this won't be done to keep votes anonymous
                project1,
                project2,
                project1_vote,
                project2_vote
            )
            self.votes.append(vote_obj)
            # assign the vote received to each project
            project1.add_vote(vote_obj)  # vote_obj will have a self-reference to project1
            project2.add_vote(vote_obj)  # vote_obj will have a self-reference to project2

    def cast_skewed_towards_impact_votes(self, view, use_impact_delta=True):
        """
        view - a list of tuples, where the values are the projects to vote on
               pairwise to the agent to vote on
        """
        self._prevote_checks()
        
        # determine which indices to vote on, based on laziness
        num_votes = len(view)
        num_votes_to_cast = int(num_votes * (1 - self.laziness))
        if num_votes_to_cast == 0:
            return
        elif self.laziness == 0:
            view_to_process = view
        else:
            # ensure that the badgeholder will vote on all views w/ the COI projects, if they are
            # engaging in COI
            view_remaining = []
            view_to_process = []
            if self.coi_factor > 0:
                for coi_project_ix in self.coi_project_ix_vec:
                    for pair in view:
                        project1, project2 = pair
                        if coi_project_ix == project1.project_id or coi_project_ix == project2.project_id:
                            view_to_process.append(pair)
                            num_votes_to_cast -= 1
                        else:
                            view_remaining.append(pair)
                if num_votes_to_cast < len(view_remaining):
                    view_remaining = self.rng.choice(view_remaining, num_votes_to_cast, replace=False)
                view_to_process.extend(view_remaining)
            else:
                view_to_process = self.rng.choice(view, num_votes_to_cast, replace=False)
            
        for pair in view_to_process:
            project1, project2 = pair
            assert self.project_population.get_project(project1.project_id) is not None, "Project 1 is not in the list of projects"
            assert self.project_population.get_project(project2.project_id) is not None, "Project 2 is not in the list of projects"

            voted_on_pair = False
            if self.coi_factor > 0:
                # draw a random number to determine if the badgeholder will vote for a COI project, based on the coi factor
                probability_coi_vote = self.coi_factor*0.5 + 0.5
                if self.rng.random() < probability_coi_vote:
                    vote_coi = True
                else:
                    vote_coi = False

                if project1.project_id in self.coi_project_ix_vec:
                    if vote_coi:
                        project1_vote, project2_vote = 1, 0
                    else:
                        project1_vote, project2_vote = 0, 1
                    voted_on_pair = True
                elif project2.project_id in self.coi_project_ix_vec:
                    # print(f'ID{self.badgeholder_id} --> COI voting for {project2.project_id} // 2')
                    if vote_coi:
                        project1_vote, project2_vote = 0, 1
                    else:
                        project1_vote, project2_vote = 1, 0
                    voted_on_pair = True
                
            if not voted_on_pair:
                # decide which project to vote for, based on expertise
                # determine the probability that the voter will vote for the correct project
                # TODO: this mapping should be generalized!
                if self.expertise == 0:
                    probability_correct_vote = 0.5
                elif self.expertise == 1:
                    probability_correct_vote = 1.0
                else:
                    if use_impact_delta:
                        impact_delta = np.abs(project1.true_impact - project2.true_impact)

                        # experiment w/ different fn's, but make this cleaner once experimentation is complete
                        # probability_correct_vote = 0.5 + impact_delta * 0.5 / (1-self.expertise)
                        probability_correct_vote = self.expertise * impact_delta + 0.5
                    else:
                        probability_correct_vote = self.expertise  # this is mapped to the updated Q+T expertise mapping function
                probability_correct_vote = np.clip(probability_correct_vote, 0, 1)
                
                # determine from a random draw whether the vote will be correct or incorrect
                make_correct_vote = False
                if self.rng.random() < probability_correct_vote:
                    make_correct_vote = True

                # map this to the vote
                if make_correct_vote:
                    if project1.true_impact > project2.true_impact:
                        project1_vote, project2_vote = 1, 0
                    else:
                        project1_vote, project2_vote = 0, 1
                else:
                    if project1.true_impact > project2.true_impact:
                        project1_vote, project2_vote = 0, 1
                    else:
                        project1_vote, project2_vote = 1, 0

            vote_obj = PairwiseRankingVote(
                self,  # pass the voter information to the project, although in the real round this won't be done to keep votes anonymous
                project1,
                project2,
                project1_vote,
                project2_vote
            )
            self.votes.append(vote_obj)
            # assign the vote received to each project
            project1.add_vote(vote_obj)  # vote_obj will have a self-reference to project1
            project2.add_vote(vote_obj)  # vote_obj will have a self-reference to project2

    def cast_random_votes(self, view):
        """
        view - a list of tuples, where the values are the projects to vote on
               pairwise to the agent to vote on
        """
        self._prevote_checks()

        for pair in view:
            project1, project2 = pair
            assert self.project_population.get_project(project1.project_id) is not None, "Project 1 is not in the list of projects"
            assert self.project_population.get_project(project2.project_id) is not None, "Project 2 is not in the list of projects"
            
            # for now, randomly decide which one to rank higher
            if self.rng.random() < 0.5:
                project1_vote, project2_vote = 1, 0
            else:
                project1_vote, project2_vote = 0, 1
            vote_obj = PairwiseRankingVote(
                self,  # pass the voter information to the project, although in the real round this won't be done to keep votes anonymous
                project1, 
                project2,
                project1_vote,
                project2_vote
            )
            self.votes.append(vote_obj)
            # assign the vote received to each project
            project1.add_vote(vote_obj)  # vote_obj will have a self-reference to project1
            project2.add_vote(vote_obj)  # vote_obj will have a self-reference to project2


class PairwiseBadgeholderPopulation(BadgeHolderPopulation):
    def __init__(self):
        self.badgeholders = []
        self.num_badgeholders = 0
        self.rng = None

    def add_badgeholders(self, badgeholders):
        self.badgeholders.extend(badgeholders)
        self.num_badgeholders += len(badgeholders)

    def send_application_information(self, projects):
        for badgeholder in self.badgeholders:
            badgeholder.send_applications_to_voter(projects)

    def communicate(self):
        pass

    def cast_votes(self, view=None, randomize_order=False):
        # TODO: this is clunky - fix it
        if view is None:
            for badgeholder in self.badgeholders:
                badgeholder.cast_votes()
        else:
            for badgeholder in self.badgeholders:
                if randomize_order:
                    view = self.rng.permutation(view)
                badgeholder.cast_votes(view)

    def get_all_votes(self):
        all_votes = []
        for badgeholder in self.badgeholders:
            all_votes.extend(badgeholder.votes)
        return all_votes

    def set_random_generator(self, rng):
        self.rng = rng
        for badgeholder in self.badgeholders:
            badgeholder.set_random_generator(rng)