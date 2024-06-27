from abc import ABC, abstractmethod

class Vote(ABC):
    # there could be additional items, like the amount, for example
    # but we leave this general so it can accomodate different kinds of voting
    # designs
    def __init__(self, voter, project):
        self.voter = voter
        self.project = project