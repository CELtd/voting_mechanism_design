from vote import Vote

class QuorumVote(Vote):
    def __init__(self, voter, project, amount):
        self.voter = voter
        self.project = project
        self.amount = amount
