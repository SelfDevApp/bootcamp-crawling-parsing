from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import motor.motor_asyncio


class Book(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    price_amount: Optional[int] = None
    price_currency: Optional[str] = None
    rating_value: Optional[float] = None
    rating_count: Optional[int] = None
    publication_year: int
    isbn: str
    pages_cnt: Optional[int] = None
    publisher: Optional[str] = None
    book_cover: Optional[str] = None
    source_url: str


app = FastAPI(
    title="Book ISBN Search Service",
    description="Study Case Example",
)

# Одно соединение на всё приложение
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
mongo_db = client["books"]
collection = mongo_db["books"]


@app.get("/search_by_isbn", response_model=Book, tags=["ISBN Searcher"])
async def get_book_by_isbn(isbn: str = Query(..., description="Book ISBN")):
    result = await collection.find_one({"isbn": isbn})
    if not result:
        raise HTTPException(status_code=404, detail="Can't find book with this ISBN")
    result.pop("_id", None)  # MongoDB stores _id, Pydantic doesn't expect it
    return Book(**result)
