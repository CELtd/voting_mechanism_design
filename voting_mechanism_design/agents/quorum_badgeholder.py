from voting_mechanism_design.agents.definitions import BadgeHolder, BadgeHolderPopulation
from voting_mechanism_design.voting_designs.quorum import QuorumVote
import numpy as np

def create_monotonic_array(max_val, min_val, length, total_sum):
    x = np.linspace(max_val, min_val, length)
    x /= x.sum()
    x *= total_sum
    
    # if any values exceed the first_value, we need to adjust the values
    mm1 = x[0]
    mm2 = x[-1]
    if mm1 > max_val:
        delta = mm1 - max_val
    else:
        delta = 0
    x = np.linspace(mm1-delta, mm2+delta, length)
    x /= x.sum()
    x *= total_sum

    return x

class QuorumBadgeholder(BadgeHolder):
    def __init__(
        self, 
        badgeholder_id, 
        total_funds=100, 
        min_vote=1, 
        max_vote=16, 
        laziness=1, 
        expertise=1, 
        coi_factor=0, 
        coi_project_ix_vec=[],  # a list of project IDs that the badgeholder has a conflict of interest with
    ):
        self.badgeholder_id = badgeholder_id
        self.votes = []

        # accounting
        self.initial_funds = total_funds
        self.total_funds = total_funds
        self.min_vote = min_vote
        self.max_vote = max_vote
        self.funds_spent = 0

        # attributes which affect how the badgeholder votes
        self.laziness_factor = laziness
        self.expertise_factor = expertise
        self.coi_factor = coi_factor
        self.coi_project_ix_vec = coi_project_ix_vec
        if self.coi_project_ix_vec is not None:
            assert len(self.coi_project_ix_vec) <= 1, "COI only possible for 1 project at a time, currently!"

        self.project_population = None
        self.rng=None

        # debugging
        self.sorted_project_indices = None
        self.personal_ratings_ix = None

    def reset_voter(self):
        self.votes = []
        self.funds_spent = 0
        self.total_funds = self.initial_funds

    def send_applications_to_voter(self, project_population):
        self.project_population = project_population

    def set_random_generator(self, rng):
        self.rng = rng

    def cast_vote(self, project, amount):
        if self.badgeholder_id == project.owner_id:
            amount = None
        if amount:
            self.total_funds -= amount
        vote_obj = QuorumVote(self, project, amount)
        self.votes.append(vote_obj)
        project.add_vote(vote_obj)

    def cast_votes(self):
        projects = self.project_population.get_projects()
        num_projects = self.project_population.num_projects
        ballot_size = int((1 - self.laziness_factor) * num_projects)

        personal_ratings_ix = self.expertise2alignment(projects)
        sorted_project_indices = np.argsort(-personal_ratings_ix)

        # TODO: model COI here
        # The approach we take is as follows:
        # The COI project will be sorted proportional to the COI factor.  If COI factor is 1, then
        # the COI project will be the first project in the list.  If COI factor is 0.5, then the project
        #  will be moved by half as many steps as it would if it were COI=1, and so on.
        if self.coi_factor > 0:
            coi_project_idx = self.coi_project_ix_vec[0]
            # compute how many steps needed if COI_factor is 1
            num_steps_coi_1 = np.where(sorted_project_indices == coi_project_idx)[0][0]
            num_steps_actual = int(num_steps_coi_1 * self.coi_factor)
            ix_actual = coi_project_idx - num_steps_actual
            assert ix_actual >= 0, "COI project index is negative!"
            
            print('before', sorted_project_indices)
            # move the COI project by num_steps_actual
            vv = sorted_project_indices[coi_project_idx]
            sorted_project_indices = np.delete(sorted_project_indices, coi_project_idx)
            sorted_project_indices = np.insert(sorted_project_indices, ix_actual, vv)
            print('after', sorted_project_indices)

        vote_amounts = np.ones(num_projects)*-999
        vote_amounts[0:ballot_size] = create_monotonic_array(self.max_vote, self.min_vote, ballot_size, self.total_funds)
        for ix, project_idx in enumerate(sorted_project_indices):
            project = self.project_population.get_project(project_idx)
            vote_amt = vote_amounts[ix]
            if vote_amt == -999:
                vote_amt = None
            self.cast_vote(project, vote_amt)
        
        self.sorted_project_indices = sorted_project_indices
        self.vote_amounts = vote_amounts

    def expertise2alignment(self, projects):
        true_project_impact_vec = [project.true_impact for project in projects]
        
        personal_ratings_ix = np.argsort(true_project_impact_vec)  # this is perfect rating
        p_shuffle_vec = np.zeros(len(personal_ratings_ix))
        for ii in range(len(personal_ratings_ix)):
            p_shuffle_vec[ii] = (1-self.expertise_factor)      # currently, not dependent on the "true impact" of a project, but can be in the future
        # find which indices we should shuffle
        ix_to_shuffle = []
        for ii in range(len(p_shuffle_vec)):
            rv = self.rng.uniform(0,1)
            if rv < p_shuffle_vec[ii]:
                ix_to_shuffle.append(ii)
        # shuffle the indices that need to be
        personal_ratings_ix[ix_to_shuffle] = self.rng.permutation(personal_ratings_ix[ix_to_shuffle])
        self.personal_ratings_ix = personal_ratings_ix
        return personal_ratings_ix

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

    def cast_votes(self):
        for badgeholder in self.badgeholders:
            badgeholder.cast_votes()

    def get_all_votes(self):
        all_votes = []
        for badgeholder in self.badgeholders:
            all_votes.extend(badgeholder.votes)
        return all_votes

    def set_random_generator(self,rng):
        for badgeholder in self.badgeholders:
            badgeholder.set_random_generator(rng)

    def reset_all(self):
        for badgeholder in self.badgeholders:
            badgeholder.reset_voter()