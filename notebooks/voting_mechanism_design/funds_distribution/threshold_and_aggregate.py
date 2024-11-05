from .funding_design import FundingDesign
import numpy as np

class ThresholdAndAggregate(FundingDesign):
    def __init__(self, scoring_method, quorum, normalize, min_amount=0):
        self.scoring_method = scoring_method
        self.quorum = quorum
        self.min_amount = min_amount
        self.normalize = normalize

    def allocate_funds(self, projects):
        projectid2score = {}
        projectid2funding = {}
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

        max_amount = project.votes[0].voter.initial_funds #.votes[0] is a QuorumVote object, .voter is a voter and .intial_funds is the total funds entered to the simulator
        #print(f"Max amount is {max_amount}")
        #print(f"self.normalize is {self.normalize}")
        if self.normalize:
            #in this case, the scores for projects is the % of funding voters want the projects to receive does not add up to 100%
            total_score = sum(projectid2score.values())
            #normalizes the scores to be % of total score, we will then multiply the project such % of total amount
            #print(projectid2score.values())
            for project in projects:
                if projectid2score[project.project_id] is not None:
                    #print(f"Max amount is {max_amount}")
                    #print(f"Total score is {total_score}")
                    #print(f"Project score is {projectid2score[project.project_id]}")
                    #print(f"Percentage is {(projectid2score[project.project_id] / total_score)}")
                    #print("-----------------------")
                    funding = (projectid2score[project.project_id] / total_score) * max_amount
                    projectid2funding[project.project_id]=funding
                    project.token_amount = funding
                else:
                    print(f"Project id: {project.project_id} has None score")
                    projectid2funding[project.project_id]=0
                    project.token_amount = 0
            #print(sum(projectid2funding.values()))
        
        return projectid2score, projectid2funding

     



