from .vote import Vote

# TODO: define a class which describes what a vote looks like in  a pairwise ranking system
class PairwiseRankingVote(Vote):
    def __init__(self, voter, project1, project2, val1, val2):
        self.voter = voter
        self.project1 = project1
        self.project2 = project2
        self.val1 = val1
        self.val2 = val2