from voting_mechanism_design.agents.definitions import BadgeHolder, BadgeHolderPopulation
from voting_mechanism_design.voting_designs.quorum import QuorumVote
import numpy as np

class QuorumBadgeholder(BadgeHolder):
    def __init__(self, badgeholder_id, total_funds=100, min_vote=1, max_vote=16, laziness=1, expertise=1, coi_factor=0, expertise_model="k2"):
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
        self.expertise_model = expertise_model


        self.projects = None
        self.rng=None

    def reset_voter(self):
        self.votes = []
        self.funds_spent = 0
        self.total_funds = self.initial_funds

    def send_applications_to_voter(self, projects):
        self.projects = projects

    def set_random_generator(self, rng):
        self.rng = rng

    def cast_vote(self, project, amount):
        #print(self.total_funds,amount) as intended
        if self.badgeholder_id == project.owner_id:
            amount = None
        if amount:
            self.total_funds -= amount
        vote_obj = QuorumVote(self, project, amount)
        self.votes.append(vote_obj)
        project.add_vote(vote_obj)

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

    def expertise2alignment_k2(self, projects, e):
        random_seed_start=123
        rng = np.random.default_rng(random_seed_start)
        true_project_impact_vec = [project.true_impact for project in projects]
        true_project_impact_vec_sorted_ix = np.argsort(true_project_impact_vec)  # only for comparison purposes
        
        personal_ratings_ix = np.argsort(true_project_impact_vec)  # this is perfect rating
        p_shuffle_vec = np.zeros(len(personal_ratings_ix))
        for ii in range(len(personal_ratings_ix)):
            p_shuffle_vec[ii] = (1- e)      # currently, not dependent on the "true impact" of a project, but can be in the future
        # find which indices we should shuffle
        ix_to_shuffle = []
        for ii in range(len(p_shuffle_vec)):
            rv = rng.uniform(0,1)
            if rv < p_shuffle_vec[ii]:
                ix_to_shuffle.append(ii)
        # shuffle the indices that need to be
        personal_ratings_ix[ix_to_shuffle] = rng.permutation(personal_ratings_ix[ix_to_shuffle])
        return personal_ratings_ix


    def expertise2alignment_carl(self, projects, e):
        random_seed_start=123
        rng = np.random.default_rng(random_seed_start)
        project_impact_vec = [project.true_impact for project in projects]
        #subjectivity_score = rng.uniform(e, 2-e, len(projects) )#this one uses rng
        subjectivity_score = np.random.uniform(e, 2-e, len(projects))
        #personal_ratings = np.array([project.true_impact for project in projects]) 
        personal_ratings = np.asarray(project_impact_vec*subjectivity_score)

        return personal_ratings
            
    def cast_votes(self, projects):
        for badgeholder in self.badgeholders:
            num_projects = len(projects)
            ballot_size = int((1 - badgeholder.laziness_factor) * num_projects)
            if badgeholder.expertise_model == "carl":
                personal_ratings= self.expertise2alignment_carl(projects, badgeholder.expertise_factor)
            else:
                personal_ratings= self.expertise2alignment_k2(projects, badgeholder.expertise_factor)
            sorted_project_indices = np.argsort(-personal_ratings)
            for idx, project_idx in enumerate(sorted_project_indices):
                project = projects[project_idx]
                if idx >= ballot_size:
                    amount = None
                else:
                    if badgeholder.laziness_factor==0:
                        max_vote_per_project = (badgeholder.total_funds) / np.sqrt(ballot_size - idx)
                    else:
                        max_vote_per_project = (badgeholder.total_funds * badgeholder.laziness_factor) / np.sqrt(ballot_size - idx)                
                    
                    if max_vote_per_project < badgeholder.min_vote:
                        amount = None
                    else:
                        lb = int(badgeholder.min_vote)
                        ub = int(min(badgeholder.max_vote, max_vote_per_project))
                        #amount = np.random.uniform(lb, ub) if lb < (ub) else lb
                        amount=(lb+ub)/2

                badgeholder.cast_vote(project, amount)

    
    def cast_votes_old(self, projects):
        for badgeholder in self.badgeholders:
            num_projects = len(projects)
            ballot_size = int((1 - badgeholder.laziness_factor) * num_projects)
            subjectivity_scores = np.random.uniform(badgeholder.expertise_factor, 2 - badgeholder.expertise_factor, num_projects)
            #personal_ratings = np.array([project.true_impact for project in projects]) * subjectivity_scores
            personal_ratings = np.array([project.true_impact for project in projects])
            
            
            
            #So i want to replace this stuff with a function that depends on the expertise and expertise_model
            sorted_project_indices = np.argsort(-personal_ratings)#[:ballot_size]
            for idx, project_idx in enumerate(sorted_project_indices):
                project = projects[project_idx]
                if idx >= ballot_size:
                    amount = None
                else:
                    #add if for case when laziness is 0: 
                    if badgeholder.laziness_factor==0:
                        max_vote_per_project = (badgeholder.total_funds) / np.sqrt(ballot_size - idx)
                    else:
                        max_vote_per_project = (badgeholder.total_funds * badgeholder.laziness_factor) / np.sqrt(ballot_size - idx)                
                    
                    if max_vote_per_project < badgeholder.min_vote:
                        amount = None
                    else:
                        lb = int(badgeholder.min_vote)
                        ub = int(min(badgeholder.max_vote, max_vote_per_project))
                        #amount = np.random.uniform(lb, ub) if lb < (ub) else lb
                        amount=(lb+ub)/2

                badgeholder.cast_vote(project, amount)
            
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