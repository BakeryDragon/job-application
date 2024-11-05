from pydantic import BaseModel, Field
from typing import List, Optional


class JobEventData(BaseModel):
    job_title: str = Field(default="Unknown Title")
    company_name: str = Field(default="Unknown Company")
    cover_letter: Optional[str] = Field(default="")
    tech_stack: Optional[List[str]] = Field(default=None)
    job_duty_summary: Optional[str] = Field(default="")
    date_posted: Optional[str] = Field(default="")
