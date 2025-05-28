from pydantic import BaseModel
from typing import Optional

class JobLocation(BaseModel):
    country: str
    city: str

class BaseJob(BaseModel):
    id: str
    job_title: str
    company: str
    location: JobLocation
    date_uploaded: str

class MatchedJob(BaseJob):
    score: float

class AppliedJob(BaseJob):
    application_id: str
    applied_date: str

class FullJob(BaseJob):
    description: str
    job_url: str


# JobSearch
class LocationFilter(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    location: Optional[LocationFilter] = None