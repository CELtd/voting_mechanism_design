from voting_mechanism_design.agents.definitions import BadgeHolder, BadgeHolderPopulation
from voting_mechanism_design.voting_designs.ranking import PairwiseRankingVote

class PairwiseBadgeholder:
    def __init__(self, badgeholder_id):
        self.badgeholder_id = badgeholder_id
        self.votes = []

        self.project_population = None
        self.rng = None

    def reset_voter(self):
        self.votes = []

    def send_applications_to_voter(self, project_population):
        self.project_population = project_population

    def set_random_generator(self, rng):
        self.rng = rng

    def cast_votes(self, view):
        """
        view - a list of tuples, where the values are the projects to vote on
               pairwise to the agent to vote on
        """
        assert self.project_population is not None, "Projects have not been sent to the voter yet"
        assert self.rng is not None, "Random generator has not been set"

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
            # TODO: is it better to add the vote object??
            project1.add_vote(project1_vote)
            project2.add_vote(project2_vote)


class PairwiseBadgeholderPopulation(BadgeHolderPopulation):
    def __init__(self):
        self.badgeholders = []
        self.num_badgeholders = 0

    def add_badgeholders(self, badgeholders):
        self.badgeholders.extend(badgeholders)
        self.num_badgeholders += len(badgeholders)

    def send_application_information(self, projects):
        for badgeholder in self.badgeholders:
            badgeholder.send_applications_to_voter(projects)

    def communicate(self):
        pass

    def cast_votes(self, view=None):
        if view is None:
            view = []
        for badgeholder in self.badgeholders:
            badgeholder.cast_votes(view)

    def set_random_generator(self, rng):
        for badgeholder in self.badgeholders:
            badgeholder.set_random_generator(rng)