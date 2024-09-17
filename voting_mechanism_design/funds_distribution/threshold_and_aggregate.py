from .funding_design import FundingDesign
import numpy as np

class ThresholdAndAggregate(FundingDesign):
    def __init__(self, scoring_method, quorum, min_amount=0):
        self.scoring_method = scoring_method
        self.quorum = quorum
        self.min_amount = min_amount

    def allocate_funds(self, projects):
        projectid2score = {}
        for project in projects:
            # votes = project.get_votes()
            votes_objs = project.votes
            votes = [v.amount for v in votes_objs if v.amount is not None]
            # print(project.project_id, votes)
            if len(votes) < self.quorum:
                score = 0
            else:
                if self.scoring_method == 'median':
                    score = np.median(votes)
                elif self.scoring_method == 'mean':
                    score = np.mean(votes)
                elif self.scoring_method == 'quadratic':
                    score = sum(np.sqrt(votes))
                elif self.scoring_method == 'outliers':
                    lo = np.quantile(votes, .25)
                    hi = np.quantile(votes, .75)
                    score = np.mean([v for v in votes if lo <= v <= hi])
                else:
                    score = sum(votes)            
                if score < self.min_amount:
                    score = 0            
            project.score = score
            projectid2score[project.project_id] = score
        
        return projectid2score