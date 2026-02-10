from datetime import datetime
import enum
from extensions import db

# --- Enums ---

class EducationLevel(enum.Enum):
    HIGH_SCHOOL = "High School"
    ASSOCIATE = "Associate"
    BACHELOR = "Bachelor"
    MASTER = "Master"
    PHD = "PhD"
    SELF_TAUGHT = "Self-Taught"
    OTHER = "Other"

class SkillLevel(enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

class RoadmapStatus(enum.Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"

# --- Models ---

class UserProfileExtended(db.Model):
    __tablename__ = 'user_profile_extended'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    education_level = db.Column(db.Enum(EducationLevel), nullable=True)
    current_skill_level = db.Column(db.Enum(SkillLevel), nullable=True)
    preferred_job_role = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserProfileExtended User:{self.user_id}>'

class SkillGapAnalysis(db.Model):
    __tablename__ = 'skill_gap_analysis'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    analysis_json = db.Column(db.JSON, nullable=False)
    readiness_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GeneratedRoadmap(db.Model):
    __tablename__ = 'generated_roadmap'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    roadmap_json = db.Column(db.JSON, nullable=False)
    progress_percent = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum(RoadmapStatus), default=RoadmapStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobMatchAnalysis(db.Model):
    __tablename__ = 'job_match_analysis'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    job_description_hash = db.Column(db.String(64), nullable=True, index=True)
    match_score = db.Column(db.Integer, default=0)
    analysis_json = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

    modules = db.relationship('LearningModule', backref='path', cascade='all, delete-orphan', order_by='LearningModule.order_index')

class LearningModule(db.Model):
    __tablename__ = 'learning_modules'

    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    topics_data = db.Column(db.JSON, nullable=True)
    
    resources = db.relationship('LearningResource', backref='module', cascade='all, delete-orphan', order_by='LearningResource.order_index')

class LearningResource(db.Model):
    __tablename__ = 'learning_resources'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('learning_modules.id'), nullable=False)
    resource_type = db.Column(db.String(20), nullable=False)  # 'video' or 'pdf'
    title = db.Column(db.String(200), nullable=False)
    youtube_video_id = db.Column(db.String(50), nullable=True)  # For YouTube videos
    pdf_url = db.Column(db.String(500), nullable=True)  # URL or path to PDF
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserLearningProgress(db.Model):
    __tablename__ = 'user_learning_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('learning_modules.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_id', name='unique_user_module_progress'),
    )