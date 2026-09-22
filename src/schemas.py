from pydantic import BaseModel, Field
from typing import List, Literal

class QuestionItem(BaseModel):
    concept: str = Field(..., description="The fundamental concept or principle being tested.")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field(..., description="Assessed difficulty level.")
    question: str = Field(..., description="Clear, concise revision or exam question.")
    key_points: List[str] = Field(..., description="Bullet points required for a complete answer.")

class BenchmarkTaskOutput(BaseModel):
    topic: str = Field(..., description="The subject or topic analyzed.")
    summary: str = Field(..., description="A 2-3 sentence overview of the provided material.")
    questions: List[QuestionItem] = Field(..., description="Generated question set.")