import numpy as np


class Project:
    def __init__(self, project_id, rating, owner_id=None):
        self.project_id = project_id
        self.owner_id = owner_id    

        # a project's "true" impact
        self.rating = rating    

        # variables needed for voting simulations
        self.votes = []
        self.num_votes = 0
        self.score = None
        self.mean = 0
        self.token_amount = 0

    def reset_project(self):
        self.votes = []
        self.num_votes = 0
        self.score = None
        self.mean = 0
        self.token_amount = 0

    def add_vote(self, vote):
        self.votes.append(vote)
        votes = self.get_votes()
        self.num_votes = len(votes)

    def add_zeroes(self, num_zeroes):
        for _ in range(num_zeroes):
            self.add_vote(Vote(None, self, 0))

    def get_votes(self):
        return [vote.amount for vote in self.votes if vote.amount is not None]
    
    def show_results(self):
        return {
            'project_id': self.project_id,
            'owner_id': self.owner_id,
            'rating': self.rating,
            'num_votes': self.num_votes,
            'score': self.score,
            'token_amount': self.token_amount
        }
    
class Vote:
    def __init__(self, voter, project, amount):
        self.voter = voter
        self.project = project
        self.amount = amount

class Voter:
    def __init__(self, voter_id, op_available, laziness, expertise):
        self.voter_id = voter_id
        self.votes = []

        # how much total OP they are willing to put in their ballot
        self.total_op = op_available

        # running balance of OP not yet allocated
        self.balance_op = op_available

        # voter attributes
        self.laziness_factor = laziness
        self.expertise_factor = expertise

    def reset_voter(self):
        self.votes = []
        self.balance_op = self.total_op

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

class Round:
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

    def calculate_scores(self, scoring_method, quorum, min_amount=0):
        projectid2score = {}
        for project in self.projects:
            votes = project.get_votes()
            # print(project.project_id, votes)
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
            # scores.append(score)
            projectid2score[project.project_id] = score
        
        return projectid2score

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


class Simulation:
    def __init__(self):
        self.round = None
    
    def initialize_round(self, max_funding, min_project_vote=1, max_project_vote=16):
        self.round = Round(max_funding)

        self.min_project_vote = min_project_vote
        self.max_project_vote = max_project_vote

    def reset_round(self):
        # reset the voting simulation
        if self.round.num_projects:
            for project in self.round.projects:
                project.reset_project()
        if self.round.num_voters:
            for voter in self.round.voters:
                voter.reset_voter()

    def randomize_voters(self, num_voters, willingness_to_spend, laziness_factor, expertise_factor):
        # randomly generate voters with different attributes
        self.round.add_voters([
            Voter(
                voter_id = i, 
                
                # how much of the max funding they are willing to vote on (up to 100% of total)
                #op_available = self.round.max_funding * np.random.uniform(willingness_to_spend, 1), 
                op_available = self.round.max_funding * willingness_to_spend, 
                                        
                # how many of the total projects they are willing to consider in their ballot
                #laziness = np.random.uniform(laziness_factor, 1), 
                laziness = laziness_factor, 
                
                # how close their assessments track to project's "true" impact ratings
                #expertise = np.random.uniform(0, expertise_factor)
                expertise =  expertise_factor
            ) 
            for i in range(num_voters)
        ])

    def randomize_projects(self, num_projects, coi_factor=0):
        # randomly generate projects with impact ratings        
        self.round.add_projects([
            Project(
                project_id = i,

                # a project's "true" impact on a bell curve distribution
                #rating = abs(np.random.normal(loc=3)),
                rating = 1,

                # TODO: link projects to voters who may have conflicts of interest (COI)
                owner_id = np.random.randint(0, self.round.num_voters) if np.random.random() < coi_factor else None
            )
            for i in range(num_projects)
        ])

    def get_project_data(self):
        return [p.show_results() for p in self.round.projects]

    def simulate_voting(self):
        num_projects = self.round.num_projects
        for voter in self.round.voters:
            ballot_size = int((1 - voter.laziness_factor) * num_projects)

            # Create an array for subjectivity scores and personal ratings
            subjectivity_scores = np.random.uniform(voter.expertise_factor, 2 - voter.expertise_factor, num_projects)
            personal_ratings = np.array([project.rating for project in self.round.projects]) * subjectivity_scores
            personal_ratings = np.array([project.rating for project in self.round.projects])

            
            sorted_project_indices = np.argsort(-personal_ratings)
            for idx, project_idx in enumerate(sorted_project_indices):
                project = self.round.projects[project_idx]
                if idx >= ballot_size:
                    amount = None
                else:
                    if voter.laziness_factor==0:
                        max_vote_per_project = (voter.balance_op) / np.sqrt(ballot_size - idx)
                    else:
                        max_vote_per_project = (voter.balance_op * voter.laziness_factor) / np.sqrt(ballot_size - idx)
                    # if max_vote_per_project < 1:
                    if max_vote_per_project < self.min_project_vote:
                        amount = None
                    else:
                        # amount = np.random.uniform(0, max_vote_per_project)
                        lb = int(self.min_project_vote)
                        ub = int(min(self.max_project_vote, max_vote_per_project))
                        if lb >= ub:
                            amount = lb
                        else:
                            amount = np.random.randint(lb, ub)
                            amount = (lb+ub)/2
                voter.cast_vote(project, amount)

    
    def allocate_votes(self, scoring_method='median', quorum=1, min_amount=1, normalize=True):
        allocations = self.round.calculate_allocations(scoring_method, quorum, min_amount, normalize)
        payouts = [a for a in allocations if a > 0]
        return {
            'scoring_method': scoring_method,
            'vote_quorum': quorum,
            'min_amount': min_amount,
            'num_projects_above_quorum': len(payouts),
            'avg_payout': np.mean(payouts),
            'median_payout': np.median(payouts),
            'max_payout': np.max(payouts)
        }


    def simulate_voting_and_scoring(self, n=1, scoring_method='median', quorum=17, min_amount=1500, normalize=True):
        results = []
        for i in range(n):            
            self.simulate_voting()            
            allocations = self.round.calculate_allocations(scoring_method, quorum, min_amount, normalize)
            payouts = [a for a in allocations if a > 0]
            data = self.get_project_data()
            results.append({
                'num_projects_above_quorum': len(payouts),
                'avg_payout': np.mean(payouts),
                'median_payout': np.median(payouts),
                'max_payout': np.max(payouts) if len(payouts) > 0 else 0,
                'data': data
            })
            self.reset_round()
        
        return {
            'scoring_method': scoring_method,
            'vote_quorum': quorum,
            'min_amount': min_amount,
            'normalize': normalize,
            'num_projects_above_quorum': np.mean([r['num_projects_above_quorum'] for r in results]),
            'avg_payout': np.mean([r['avg_payout'] for r in results]),
            'median_payout': np.mean([r['median_payout'] for r in results]),
            'max_payout': np.mean([r['max_payout'] for r in results]),
            'data': [
                {
                    'project_id': d['project_id'],
                    'owner_id': d['owner_id'],
                    'rating': d['rating'],
                    'num_votes': np.mean([r['data'][i]['num_votes'] for r in results]),
                    'token_amount': np.mean([r['data'][i]['token_amount'] for r in results])
                }
                for i, d in enumerate(results[0]['data'])
            ]
        }
    

def test():

    simulation = Simulation()
    simulation.initialize_round(30_000_000)
    simulation.randomize_voters(150, willingness_to_spend=1, laziness_factor=0.6, expertise_factor=0.7)
    simulation.randomize_projects(600, coi_factor=0)
    simulation.simulate_voting()    
    results = simulation.allocate_votes('median', quorum=17, min_amount=1500)
    print(results)
    data = simulation.get_project_data()
    

# test()    