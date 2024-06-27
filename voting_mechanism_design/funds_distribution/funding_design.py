from abc import ABC, abstractmethod

class FundingDesign(ABC):
    @abstractmethod
    def allocate_funds(self, projects):
        pass