from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://anshuanshu:anshu1406@localhost:5432/asana"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    # Import all models to ensure they're registered with Base
    from models.user import User
    from models.workspace import Workspace
    from models.team import Team
    from models.project import Project
    from models.task import Task
    from models.goal import Goal
    from models.portfolio import Portfolio
    from models.tag import Tag
    from models.section import Section
    from models.story import Story
    from models.status_update import StatusUpdate
    from models.project_status import ProjectStatus
    from models.project_brief import ProjectBrief
    from models.project_template import ProjectTemplate
    from models.custom_field import CustomField
    from models.custom_field_setting import CustomFieldSetting
    from models.custom_type import CustomType
    from models.custom_type_status_option import CustomTypeStatusOption
    from models.enum_option import EnumOption
    from models.attachment import Attachment
    from models.audit_log_event import AuditLogEvent
    from models.event import Event
    from models.job import Job
    from models.webhook import Webhook
    from models.time_period import TimePeriod
    from models.user_task_list import UserTaskList
    from models.workspace_membership import WorkspaceMembership
    from models.team_membership import TeamMembership
    from models.project_membership import ProjectMembership
    from models.portfolio_membership import PortfolioMembership
    from models.goal_membership import GoalMembership
    from models.custom_field_membership import CustomFieldMembership
    from models.goal_relationship import GoalRelationship
    from models.graph_export import GraphExport
    from models.organization_export import OrganizationExport
    from models.resource_export import ResourceExport
    from models.rule_trigger import RuleTrigger
    from models.batch import Batch
    from models.allocation import Allocation
    from models.budget import Budget
    from models.access_request import AccessRequest
    from models.rate import Rate
    from models.reaction import Reaction
    from models.task_template import TaskTemplate
    from models.time_tracking_entry import TimeTrackingEntry
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("All database tables created successfully!")

