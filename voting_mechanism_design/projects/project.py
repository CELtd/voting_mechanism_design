from typing import List

from voting_mechanism_design.voting_designs.vote import Vote

class Project:
    def __init__(self, project_id, true_impact, owner_id=None):
        self.project_id = project_id
        self.owner_id = owner_id    

        self.true_impact = true_impact    

        # variables needed for voting simulations
        self.votes: List[Vote] = []
        self.num_votes = 0
        self.score = None
        self.token_amount = 0

    # TODO: do we need this?
    def reset_project(self):
        self.votes: List[Vote] = []
        self.num_votes = 0
        self.score = None
        self.token_amount = 0

    def add_vote(self, vote):
        self.votes.append(vote)
        self.num_votes = len(self.votes)

    # def get_votes(self):
    #     return [vote.amount for vote in self.votes if vote.amount is not None]
    
    def show_results(self):
        return {
            'project_id': self.project_id,
            'owner_id': self.owner_id,
            'rating': self.true_impact,
            'num_votes': self.num_votes,
            'score': self.score,
            'token_amount': self.token_amount
        }
    
class ProjectPopulation:
    def __init__(self):
        self.projects = []
        self.num_projects = 0

    def add_projects(self, projects):
        self.projects.extend(projects)
        self.num_projects += len(projects)

    def get_projects(self):
        return self.projects

    def get_project(self, project_id):
        for project in self.projects:
            if project.project_id == project_id:
                return project
        return None

    def reset_projects(self):
        for project in self.projects:
            project.reset_project()