from typing import List, TypedDict

from pydantic import BaseModel


class AgentState(TypedDict):
    task: str # Essay topic
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int

class Queries(BaseModel):
    queries: List[str]