from typing import List, Dict, Optional
from pydantic import BaseModel,Field


# schemas.py

from typing import List, Optional
from pydantic import BaseModel, Field

class Metadata(BaseModel):
    case_type: str = Field(description="The legal category of the case, e.g., 'defamation'.")
    jurisdiction: str = Field(description="The relevant legal jurisdiction, e.g., 'Supreme Court of India'.")
    year: int = Field(description="The year the judgment was made.")
    key_legal_principles: List[str] = Field(description="Core legal principles cited.")
    plaintiff_details: str = Field(description="Description of the plaintiff.")
    defendant_details: str = Field(description="Description of the defendant.")
    outcome: str = Field(description="A brief summary of the case outcome, e.g., 'dismissed', 'guilty'.")

class RagLawyerOutput(BaseModel):
    argument: str = Field(description="The detailed, fact-based legal argument.")
    citation: str = Field(description="A relevant case law, statute, or precedent.")
    metadata: Metadata

class ChaosLawyerOutput(BaseModel):
    argument: str = Field(description="The absurd, exaggerated, or chaotic counter-argument.")
    rhetoric: str = Field(description="The rhetorical style or flourish used.")




