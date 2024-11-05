import numpy as np

from voting_mechanism_design.funds_distribution.funding_design import FundingDesign

class OpQuorum(FundingDesign):
    def __init__(self, max_funding):
        self.max_funding = max_funding

        self.projects = []
        self.voters = []
        self.num_voters = 0
        self.num_projects = 0

    def add_projects(self, projects):
        self.projects.extend(projects)
        self.num_projects += len(projects)

    def add_voters(self, voters):
        self.voters.extend(voters)
        self.num_voters += len(voters)

    def calculate_allocations(self, scoring_method, quorum, min_amount, normalize=True):        
        scores = []
        for project in self.projects:
            votes = project.get_votes()
            if len(votes) < quorum:
                score = 0
            else:
                if scoring_method == 'median':
                    score = np.median(votes)
                elif scoring_method == 'mean':
                    score = np.mean(votes)
                elif scoring_method == 'quadratic':
                    score = sum(np.sqrt(votes))
                elif scoring_method == 'outliers':
                    lo = np.quantile(votes, .25)
                    hi = np.quantile(votes, .75)
                    score = np.mean([v for v in votes if lo <= v <= hi])
                else:
                    score = sum(votes)            
                if score < min_amount:
                    score = 0            
            project.score = score
            scores.append(score)
        
        total_score = sum(scores)
        allocations = []
        for i, project in enumerate(self.projects):
            if normalize:
                if total_score == 0:
                    allocation = 0
                else:
                    allocation = np.round(scores[i] / total_score * self.max_funding, 2)
            else:
                allocation = scores[i]
            project.token_amount = allocation
            allocations.append(allocation)
        return allocations