from app.image_selector.calculators import ProbabilityCalculator, LastViewsCalculator
from app.models import Image, Category, ViewsHistory, engine
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from random import random

class ImageSelector():
    """Class that helps to get suited image from DB"""
    def __init__(self):
        self.prob_calculators = []

    def __get_from_db(self, categories: list[str]) -> list[Image]:
        with Session(autoflush=False, bind=engine) as db:
            images = db.query(Image).filter(Image.categories.any(Category.name.in_(categories))) \
                .options(joinedload(Image.categories)).all()

        return images

    def __get_any_from_db(self) -> list[Image]:
        history_count = 10 # base history count

        #try to get history length from related calc if exists
        for calc in self.prob_calculators:
            if type(calc) == LastViewsCalculator:
                history_count = len(calc.history)

        with Session(autoflush=False, bind=engine) as db:
            images = db.query(Image).order_by(desc(Image.count_coef)).limit(history_count + 1).all()

        return images

    def __use_image(self, image: Image) -> None:
        #check every image before return to user

        with Session(autoflush=False, bind=engine) as db:
            updated_image = db.query(Image).get(image.id)
            updated_image.used_count += 1

            history = ViewsHistory()
            history.image = updated_image
            db.add(history)
            db.commit()
        

    def __select_by_random(self, probs: list[float]) -> int:
        val = random() * sum(probs)
        sum_prob = 0.0

        for i in range(len(probs)):
            sum_prob += probs[i]
            if val <= sum_prob:
                return i

    def __calc_probabilities(self, images: list[Image]) -> list[float]:
        probs = [1.0] * len(images)

        for calc in self.prob_calculators:
            for i in range(len(images)):
                probs[i] = probs[i] * calc.get_coefficient(images[i])
        
        return probs
        
    def select_image_by_categories(self, categories: list[str]) -> Image | None:
        """Returns suitable image based on categories. Returns random image if no categories."""
        if categories:
            images = self.__get_from_db(categories)
        else:
            #if no categories
            images = self.__get_any_from_db()

        if len(images) == 0:
            return None
        #calculate index of selected image          based on computed probabilities
        index = self.__select_by_random(self.__calc_probabilities(images))
        self.__use_image(images[index])

        return images[index]