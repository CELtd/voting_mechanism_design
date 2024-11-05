from abc import ABC, abstractmethod

class BadgeHolder(ABC):
    pass

class BadgeHolderPopulation(ABC):
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

    @abstractmethod
    def set_random_generator(self):
        pass