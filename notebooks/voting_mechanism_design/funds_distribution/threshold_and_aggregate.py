from .funding_design import FundingDesign
from voting_mechanism_design.mapping import mapping
import numpy as np

class ThresholdAndAggregate(FundingDesign):
    def __init__(self, scoring_method, quorum, normalize, funding_model='linear', min_amount=0):
        self.scoring_method = scoring_method
        self.quorum = quorum
        self.min_amount = min_amount
        self.normalize = normalize
        if normalize:
            self.funding_model = funding_model
        else:
            self.funding_model = None

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

        total_amount = project.votes[0].voter.initial_funds #.votes[0] is a QuorumVote object, .voter is a voter and .intial_funds is the total funds entered to the simulator
        #normalize it such that sum of funding = total amount
        total_score = sum(projectid2score.values())
        #normalizes the scores to be % of total score, we will then multiply the project such % of total amount
        fundedProjects = {} #keeps track of how many projects receives funding
        unfundedProjects = [] #keeps track of how many projects does not funding
        for project in projects:
            if projectid2score[project.project_id] is not None:
                funding = (projectid2score[project.project_id] / total_score) * total_amount
                projectid2funding[project.project_id]=funding
                project.token_amount = funding
                fundedProjects[project.project_id] = funding
            else:
                #print(f"Project id: {project.project_id} has None score")
                projectid2funding[project.project_id]=0
                project.token_amount = 0
                unfundedProjects.append(project.project_id)
            #print(sum(projectid2funding.values()))
        if self.normalize:
            #in this case, the scores for projects is the % of funding voters want the projects to receive does not add up to 100%
            #assumes min, max funding per project is the min, max vote from users 
            max_amount = project.votes[0].voter.max_vote
            min_amount = project.votes[0].voter.min_vote
            length = len(fundedProjects.keys())
            mappingObj = mapping(max_val =  max_amount , min_val = min_amount, length = length, total_sum = total_amount)
            vote_amounts = np.ones(length)*-999

            #funding models
            if self.funding_model == 'linear':
                funding_array = mappingObj.linear()
            elif self.vote_model == 'logarithmic':
                funding_array = mappingObj.logarithmic() 

            sorted_fundedProjects = dict(sorted(fundedProjects.items(), key=lambda item: item[1], reverse=True)) #sorts fundedProjects with descending values (funding amounts)
            rankedFundedProjects = sorted_fundedProjects.keys()
            vote_amount_idx = 0
            for projectID in rankedFundedProjects:
                #add fundings determined by the funding model to funded projects
                projectid2funding[projectID] = funding_array[vote_amount_idx]
                vote_amount_idx+=1
            for projectID in unfundedProjects:
                projectid2funding[projectID] = 0 #I don't think need to update (just in case)
                
        
        return projectid2score, projectid2funding

     



