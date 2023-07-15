from abc import ABC, abstractmethod
from app.models import Image

class ProbabilityCalculator(ABC):
    """Common abstact class for all probability calculators. 
    It's possible add custom one if you want"""

    #Get coefficient from 0.0 to 1.0 that means probability of view
    @abstractmethod
    def get_coefficient(self, img: Image) -> float:
        pass


class LifeCountCalculator(ProbabilityCalculator):
    """Calculator that changes probability
    based on count of ramaining views"""
    def get_coefficient(self, img: Image) -> float:
        return (img.total_count - img.used_count) / img.total_count


class CategoryMatchCalculator(ProbabilityCalculator):
    """Calculator that changes probability based on number 
    of requested categories that match image categories"""
    def __init__(self, requested_cat: list[str]):
        self.requested_cat = requested_cat

    def get_coefficient(self, img: Image) -> float:
        match_cat = 0
        cur_categories = [c.name for c in img.categories]

        for cat in self.requested_cat:
            if cat in cur_categories:
                match_cat  += 1
        
        return match_cat / len(self.requested_cat)
    
class LastViewsCalculator(ProbabilityCalculator):
    """Calculator that changes probability based history of views
    and decreases repetition"""
    def __init__(self, history: list[int]):
        self.history = history

    def get_coefficient(self, img: Image) -> float:
        last_view_seq = []

        for i in range(len(self.history)):
            if self.history[i] == img.id:
                last_view_seq.append((len(self.history) - i) ** 3)

        if len(last_view_seq) == 0:
            return 1.0

        mul = 1.0
        for num in last_view_seq:
            mul *= num

        return 1.0/(1.0 + mul)

        
