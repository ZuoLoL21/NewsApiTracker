from pydantic import BaseModel
from typing import List, Optional


class Source(BaseModel):
    id:Optional[str]
    name:Optional[str]

class Article(BaseModel):
    source:Source
    author:Optional[str]
    title:Optional[str]
    description:Optional[str]
    url:Optional[str]
    urlToImage:Optional[str]
    publishedAt:Optional[str]
    content:Optional[str]

class Articles(BaseModel):
    status:str
    totalResults:int
    articles:List[Article]