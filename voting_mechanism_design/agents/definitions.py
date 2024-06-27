from abc import ABC, abstractmethod

class BadgeHolder(ABC):
    @abstractmethod
    def cast_vote(self):
        pass

class BadgeholderPopulation(ABC):
    @abstractmethod
    def __init__(self, badgeholders):
        self.badgeholders = badgeholders

    @abstractmethod
    def send_application_information(self):
        pass

    @abstractmethod
    def communicate(self):
        pass

    @abstractmethod
    def cast_votes(self):
        pass