from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RecruiterJob:
    """
    Represents a job posting created by a recruiter.
    This is a data-only class and does not interact with the database directly.
    """
    title: str
    company: str
    location: str
    job_type: str  # e.g., 'Full-time', 'Part-time', 'Contract'
    description: str
    recruiter_id: int
    created_at: str
    
    # Optional fields
    salary_range: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    deadline: Optional[str] = None
    
    # Fields managed by the database
    id: Optional[int] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Converts the RecruiterJob object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "job_type": self.job_type,
            "salary_range": self.salary_range,
            "description": self.description,
            "skills": self.skills,
            "deadline": self.deadline,
            "recruiter_id": self.recruiter_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }