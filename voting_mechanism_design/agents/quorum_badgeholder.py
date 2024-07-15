from voting_mechanism_design.agents.definitions import BadgeHolder, BadgeHolderPopulation
from voting_mechanism_design.voting_designs.quorum import QuorumVote

class QuorumBadgeholder(BadgeHolder):
    def __init__(self, badgeholder_id, total_funds, min_vote, max_vote, laziness, expertise, coi_factor=0):
        self.badgeholder_id = badgeholder_id
        self.votes = []

        # accounting
        self.total_funds = total_funds
        self.min_vote = min_vote
        self.max_vote = max_vote
        self.funds_spent = 0

        # attributes which affect how the badgeholder votes
        self.laziness_factor = laziness
        self.expertise_factor = expertise
        self.coi_factor = coi_factor

        self.projects = None
        self.rng=None

    def reset_voter(self):
        self.votes = []
        self.funds_spent = 0

    def send_applications_to_voter(self, projects):
        self.projects = projects

    def set_random_generator(self, rng):
        self.rng = rng

    def cast_votes(self):
        """
        Vote on a subset of all the projects that were made available to the voter
        """
        assert self.projects is not None, "Projects have not been sent to the voter yet"

        # # TODO: determine the amount according to some distribution, and taking into account COI

        # if self.voter_id == project.owner_id:
        #     amount = None
        # if amount:
        #     self.balance_op -= amount
        # vote = QuorumVote(self, project, amount)
        # self.votes.append(vote)
        # project.add_vote(vote)
        pass

    def cast_vote(self, project, amount):
        if self.voter_id == project.owner_id:
            amount = None
        if amount:
            self.balance_op -= amount
        vote = Vote(self, project, amount)
        self.votes.append(vote)
        project.add_vote(vote)

    def get_votes(self):
        return [
            {'project_id': v.project.project_id, 'amount': v.amount} 
            for v in self.votes
        ]
    

class QuorumBadgeholderPopulation(BadgeHolderPopulation):
    def __init__(self):
        self.badgeholders = []
        self.num_badgeholders = 0

    def add_badgeholders(self, badgeholders):
        self.badgeholders.extend(badgeholders)
        self.num_badgeholders += len(badgeholders)

    def get_badgeholders(self):
        return self.badgeholders

    def get_badgeholder(self, badgeholder_id):
        for badgeholder in self.badgeholders:
            if badgeholder.badgeholder_id == badgeholder_id:
                return badgeholder
        return None

    def send_application_information(self, projects):
        for badgeholder in self.badgeholders:
            badgeholder.send_applications_to_voter(projects)

    def communicate(self):
        # implement different communication schemes here, including
        # negative and positive based on the things we want to test
        pass

    def cast_votes(self, view=None): #code from pairwise
        if view is None:
            view = []
        for badgeholder in self.badgeholders:
            badgeholder.cast_votes(view)# code breaks here

    def cast_vote(self,)
            
    def get_all_votes(self):
        all_votes = []
        for badgeholder in self.badgeholders:
            all_votes.extend(badgeholder.votes)
        return all_votes

    def set_random_generator(self,rng):
        for badgeholder in self.badgeholders:
            badgeholder.set_random_generator(rng)