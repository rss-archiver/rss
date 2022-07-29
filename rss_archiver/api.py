"""Main module for rss-archiver"""
__version__ = 1
import re

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
tags_metadata = [
    {
        "name": "Feeds",
        "description": "Operations with feeds.",
    },
]
app = FastAPI(title="RSS-Archiver", openapi_tags=tags_metadata)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/feeds/", response_model=schemas.Feed, tags=["Feeds"])
def create_feed(feed: schemas.FeedCreate, db: Session = Depends(get_db)):
    try:
        db_feed = crud.create_feed(db=db, feed=feed)
    except IntegrityError:
        raise HTTPException(status_code=422, detail="Integrity Error")
    for scraper in crud.get_scrapers(db):
        if re.match(scraper.regex, feed.url):
            db_feed.scrapers.append(scraper)
    if not db_feed.scrapers:
        raise HTTPException(
            status_code=422,
            detail="The URL of the feed doesn't match any of the scraper regex's",
        )
    db.commit()
    return db_feed


@app.get("/feeds/", response_model=list[schemas.Feed], tags=["Feeds"])
def read_feeds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feeds = crud.get_feeds(db, skip=skip, limit=limit)
    return feeds


@app.get("/feeds/{feed_id}", response_model=schemas.Feed, tags=["Feeds"])
def read_feed(feed_id: int, db: Session = Depends(get_db)):
    db_feed = crud.get_feed(db, feed_id=feed_id)
    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return db_feed


@app.delete("/feeds/{feed_id}", response_model=schemas.Feed, tags=["Feeds"])
def delete_feed(feed_id: int, db: Session = Depends(get_db)):
    db_feed = crud.delete_feed(db, feed_id=feed_id)
    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return db_feed
