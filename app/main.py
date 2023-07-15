from typing import Annotated
from contextlib import asynccontextmanager
import csv
from fastapi import FastAPI, Query
from app.models import Image, Category, ViewsHistory, engine, DB_NAME
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os
from app.image_selector.selector import ImageSelector
from app.image_selector.calculators import CategoryMatchCalculator, LifeCountCalculator, LastViewsCalculator
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.requests import Request

MIN_CSV_PARAM_COUNT = 3 # url, view count and one category required
USE_HISTORY_COUNT = 10 # use last N history records to decrease repetition

@asynccontextmanager
async def lifespan(app: FastAPI):
    configurate_from_csv() # mode data from csv to db after start
    yield
    os.remove(DB_NAME) # drop DB everytime after shutdown

def get_history() -> list[int]:
    with Session(autoflush=False, bind=engine) as db:
        history_objs = db.query(ViewsHistory).order_by(desc(ViewsHistory.timestamp)).limit(USE_HISTORY_COUNT).all()
    return [h.image_id for h in history_objs]

    
app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def index(request: Request, category: Annotated[list[str] | None, Query()] = None):
    sel = ImageSelector()
    history = get_history()

    #configurate calculators we wish to use
    calcs = [LifeCountCalculator(), LastViewsCalculator(history)]

    if category != None:
        calcs.append(CategoryMatchCalculator(category))

    sel.prob_calculators.extend(calcs)

    image = sel.select_image_by_categories(category)

    if image == None:
        return HTMLResponse("Nothing to show :(", status_code=404)

    return templates.TemplateResponse("index.html", {"request": request, "image_url": image.url})
    

def configurate_from_csv() -> None:
    images = []

    common_categories = set()
    
    with open("content.csv", "r") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=";")

        for row in csv_data:
            if len(row) < MIN_CSV_PARAM_COUNT:
                raise Exception("Incorrect data in your csv")

            url = row[0]
            count = int(row[1])
            categories = row[2:]

            # getting unique categories using 'set'
            common_categories.update(categories)

            images.append({"url": url, "count": count, "categories": categories})

    categories_db = {k:Category(name=k) for k in common_categories}
    for image in images:
        related_categories_db = []
        for cat in image["categories"]:
            related_categories_db.append(categories_db[cat])
            #tie categories to images on DB level
        image["categories"] = related_categories_db

    with Session(autoflush=False, bind=engine) as db:
        for image in images:
            db.add(Image(url=image["url"], total_count=image["count"], categories=image["categories"]))
    
        db.commit()
        
    
    