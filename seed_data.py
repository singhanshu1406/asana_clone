"""
Seed script to populate database with test data for API testing
"""
import uuid
from datetime import datetime, date, timedelta
from database import SessionLocal, init_db
from models.user import User
from models.workspace import Workspace
from models.team import Team
from models.project import Project
from models.task import Task
from models.section import Section
from models.tag import Tag
from models.goal import Goal
from models.portfolio import Portfolio
from models.custom_field import CustomField
from models.enum_option import EnumOption
from models.custom_type import CustomType
from models.custom_type_status_option import CustomTypeStatusOption
from models.rate import Rate
from models.task_template import TaskTemplate
from models.time_tracking_entry import TimeTrackingEntry
from models.budget import Budget
from models.allocation import Allocation
from models.access_request import AccessRequest
from models.attachment import Attachment
from models.project_status import ProjectStatus
from models.project_brief import ProjectBrief
from models.status_update import StatusUpdate
from models.story import Story
from models.reaction import Reaction
from models.workspace_membership import WorkspaceMembership
from models.team_membership import TeamMembership
from models.project_membership import ProjectMembership
from models.portfolio_membership import PortfolioMembership
from models.custom_field_setting import CustomFieldSetting
from models.job import Job


def generate_gid():
    """Generate a unique GID"""
    return str(uuid.uuid4())


def clear_database(db):
    """Clear all data from database tables"""
    print("Clearing existing data...")
    try:
        # Delete in reverse order of dependencies
        db.query(Job).delete()
        db.query(TimeTrackingEntry).delete()
        db.query(Reaction).delete()
        db.query(Story).delete()
        db.query(ProjectBrief).delete()
        db.query(ProjectStatus).delete()
        db.query(Attachment).delete()
        db.query(AccessRequest).delete()
        db.query(Allocation).delete()
        db.query(Budget).delete()
        db.query(TaskTemplate).delete()
        db.query(Rate).delete()
        db.query(CustomTypeStatusOption).delete()
        db.query(CustomType).delete()
        db.query(EnumOption).delete()
        db.query(CustomFieldSetting).delete()
        db.query(CustomField).delete()
        db.query(ProjectMembership).delete()
        db.query(PortfolioMembership).delete()
        db.query(TeamMembership).delete()
        db.query(WorkspaceMembership).delete()
        db.query(Task).delete()
        db.query(Section).delete()
        db.query(Tag).delete()
        db.query(Goal).delete()
        db.query(Portfolio).delete()
        db.query(Project).delete()
        db.query(Team).delete()
        db.query(User).delete()
        db.query(Workspace).delete()
        db.commit()
        print("Database cleared successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error clearing database: {str(e)}")
        raise


def seed_database():
    """Populate database with test data"""
    db = SessionLocal()
    
    try:
        print("Starting database seeding...")
        
        # Clear existing data
        clear_database(db)
        
        # Create Workspaces
        print("Creating workspaces...")
        workspace1 = Workspace(
            gid=generate_gid(),
            name="Acme Corporation",
            is_organization=True,
            email_domains=["acme.com"]
        )
        workspace2 = Workspace(
            gid=generate_gid(),
            name="Tech Startup Inc",
            is_organization=False,
            email_domains=["techstartup.com"]
        )
        db.add(workspace1)
        db.add(workspace2)
        db.commit()
        db.refresh(workspace1)
        db.refresh(workspace2)
        print(f"Created workspaces: {workspace1.name}, {workspace2.name}")
        
        # Create Users
        print("Creating users...")
        users = []
        user_data = [
            {"name": "John Doe", "email": "john.doe@acme.com"},
            {"name": "Jane Smith", "email": "jane.smith@acme.com"},
            {"name": "Bob Johnson", "email": "bob.johnson@acme.com"},
            {"name": "Alice Williams", "email": "alice.williams@techstartup.com"},
            {"name": "Charlie Brown", "email": "charlie.brown@techstartup.com"},
        ]
        
        for u_data in user_data:
            user = User(
                gid=generate_gid(),
                name=u_data["name"],
                email=u_data["email"],
                photo=f"https://api.adorable.io/avatars/100/{u_data['email']}.png",
                workspaces=[workspace1.gid if "acme" in u_data["email"] else workspace2.gid],
                is_workspace_admin=(u_data["name"] == "John Doe")
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        for user in users:
            db.refresh(user)
        print(f"Created {len(users)} users")
        
        # Create Teams
        print("Creating teams...")
        team1 = Team(
            gid=generate_gid(),
            name="Engineering Team",
            workspace_id=workspace1.id
        )
        team2 = Team(
            gid=generate_gid(),
            name="Product Team",
            workspace_id=workspace1.id
        )
        team3 = Team(
            gid=generate_gid(),
            name="Design Team",
            workspace_id=workspace2.id
        )
        db.add(team1)
        db.add(team2)
        db.add(team3)
        db.commit()
        db.refresh(team1)
        db.refresh(team2)
        db.refresh(team3)
        print(f"Created teams: {team1.name}, {team2.name}, {team3.name}")
        
        # Create Projects
        print("Creating projects...")
        projects = []
        project_data = [
            {"name": "Website Redesign", "color": "blue", "team": team1},
            {"name": "Mobile App Development", "color": "green", "team": team1},
            {"name": "Marketing Campaign", "color": "purple", "team": team2},
            {"name": "Product Launch", "color": "orange", "team": team2},
            {"name": "UI/UX Improvements", "color": "pink", "team": team3},
        ]
        
        for p_data in project_data:
            project = Project(
                gid=generate_gid(),
                name=p_data["name"],
                notes=f"Project description for {p_data['name']}",
                color=p_data["color"],
                default_view="board",
                workspace_id=workspace1.id if p_data["team"] in [team1, team2] else workspace2.id,
                team_id=p_data["team"].id,
                owner_id=users[0].id,
                public=False,
                start_on=date.today(),
                due_date=date.today() + timedelta(days=30)
            )
            db.add(project)
            projects.append(project)
        
        db.commit()
        for project in projects:
            db.refresh(project)
        print(f"Created {len(projects)} projects")
        
        # Create Sections
        print("Creating sections...")
        sections = []
        section_names = ["To Do", "In Progress", "Done"]
        for project in projects[:3]:  # Add sections to first 3 projects
            for section_name in section_names:
                section = Section(
                    gid=generate_gid(),
                    name=section_name,
                    project_id=project.id
                )
                db.add(section)
                sections.append(section)
        db.commit()
        for section in sections:
            db.refresh(section)
        print(f"Created {len(sections)} sections")
        
        # Create Tasks
        print("Creating tasks...")
        tasks = []
        task_data = [
            {"name": "Design homepage mockup", "project": projects[0], "assignee": users[0], "section": sections[0] if sections else None},
            {"name": "Implement user authentication", "project": projects[1], "assignee": users[1], "section": sections[3] if len(sections) > 3 else None},
            {"name": "Create marketing materials", "project": projects[2], "assignee": users[2], "section": sections[6] if len(sections) > 6 else None},
            {"name": "Write product documentation", "project": projects[3], "assignee": users[0], "section": None},
            {"name": "Design user interface", "project": projects[4], "assignee": users[3], "section": None},
            {"name": "Set up CI/CD pipeline", "project": projects[1], "assignee": users[1], "section": None},
            {"name": "Conduct user research", "project": projects[0], "assignee": users[2], "section": None},
            {"name": "Plan sprint", "project": projects[2], "assignee": users[0], "section": None},
        ]
        
        for t_data in task_data:
            task = Task(
                gid=generate_gid(),
                name=t_data["name"],
                notes=f"Task notes for {t_data['name']}",
                completed=(t_data["name"] in ["Design homepage mockup", "Plan sprint"]),
                assignee_id=t_data["assignee"].id,
                workspace_id=t_data["project"].workspace_id,
                due_on=date.today() + timedelta(days=7),
                assignee_status="upcoming"
            )
            db.add(task)
            tasks.append(task)
        
        db.commit()
        for task in tasks:
            db.refresh(task)
        print(f"Created {len(tasks)} tasks")
        
        # Create Tags
        print("Creating tags...")
        tags = []
        tag_names = ["urgent", "frontend", "backend", "design", "marketing", "bug", "feature"]
        for tag_name in tag_names:
            tag = Tag(
                gid=generate_gid(),
                name=tag_name,
                workspace_id=workspace1.id
            )
            db.add(tag)
            tags.append(tag)
        db.commit()
        for tag in tags:
            db.refresh(tag)
        print(f"Created {len(tags)} tags")
        
        # Create Goals
        print("Creating goals...")
        goals = []
        goal_data = [
            {"name": "Increase user engagement by 50%", "workspace": workspace1},
            {"name": "Launch new product by Q2", "workspace": workspace1},
            {"name": "Improve customer satisfaction", "workspace": workspace2},
        ]
        
        for g_data in goal_data:
            goal = Goal(
                gid=generate_gid(),
                name=g_data["name"],
                workspace_id=g_data["workspace"].id,
                owner_id=users[0].id,
                due_on=date.today() + timedelta(days=90)
            )
            db.add(goal)
            goals.append(goal)
        db.commit()
        for goal in goals:
            db.refresh(goal)
        print(f"Created {len(goals)} goals")
        
        # Create Portfolios
        print("Creating portfolios...")
        portfolio1 = Portfolio(
            gid=generate_gid(),
            name="Q1 2024 Portfolio",
            workspace_id=workspace1.id,
            owner_id=users[0].id,
            color="blue"
        )
        portfolio2 = Portfolio(
            gid=generate_gid(),
            name="Strategic Initiatives",
            workspace_id=workspace1.id,
            owner_id=users[0].id,
            color="green"
        )
        db.add(portfolio1)
        db.add(portfolio2)
        db.commit()
        db.refresh(portfolio1)
        db.refresh(portfolio2)
        print(f"Created portfolios: {portfolio1.name}, {portfolio2.name}")
        
        # Create Portfolio Memberships
        print("Creating portfolio memberships...")
        portfolio_memberships = []
        # Add users to portfolios
        for portfolio in [portfolio1, portfolio2]:
            for user in users[:3]:  # Add first 3 users to each portfolio
                membership = PortfolioMembership(
                    gid=generate_gid(),
                    portfolio_id=portfolio.id,
                    user_id=user.id,
                    write_access="full" if user.id == users[0].id else "editor"
                )
                db.add(membership)
                portfolio_memberships.append(membership)
        
        # Add teams to portfolios
        for portfolio in [portfolio1]:
            for team in [team1, team2]:  # Add teams to first portfolio
                membership = PortfolioMembership(
                    gid=generate_gid(),
                    portfolio_id=portfolio.id,
                    team_id=team.id,
                    write_access="editor"
                )
                db.add(membership)
                portfolio_memberships.append(membership)
        
        db.commit()
        for membership in portfolio_memberships:
            db.refresh(membership)
        print(f"Created {len(portfolio_memberships)} portfolio memberships")
        
        # Create Custom Fields
        print("Creating custom fields...")
        custom_fields = []
        cf_data = [
            {"name": "Priority", "type": "enum", "workspace": workspace1},
            {"name": "Status", "type": "enum", "workspace": workspace1},
            {"name": "Budget", "type": "number", "workspace": workspace1},
            {"name": "Due Date", "type": "date", "workspace": workspace1},
        ]
        
        for cf in cf_data:
            custom_field = CustomField(
                gid=generate_gid(),
                name=cf["name"],
                type=cf["type"],
                enabled=True,
                workspace_id=cf["workspace"].id,
                created_by_id=users[0].id
            )
            db.add(custom_field)
            custom_fields.append(custom_field)
        
        db.commit()
        for cf in custom_fields:
            db.refresh(cf)
        print(f"Created {len(custom_fields)} custom fields")
        
        # Create Enum Options
        print("Creating enum options...")
        enum_options = []
        priority_options = ["Low", "Medium", "High", "Critical"]
        status_options = ["Not Started", "In Progress", "Blocked", "Completed"]
        
        priority_cf = custom_fields[0]  # Priority custom field
        for opt_name in priority_options:
            enum_opt = EnumOption(
                gid=generate_gid(),
                name=opt_name,
                enabled=True,
                color="blue",
                custom_field_id=priority_cf.id
            )
            db.add(enum_opt)
            enum_options.append(enum_opt)
        
        status_cf = custom_fields[1]  # Status custom field
        for opt_name in status_options:
            enum_opt = EnumOption(
                gid=generate_gid(),
                name=opt_name,
                enabled=True,
                color="green",
                custom_field_id=status_cf.id
            )
            db.add(enum_opt)
            enum_options.append(enum_opt)
        
        db.commit()
        for eo in enum_options:
            db.refresh(eo)
        print(f"Created {len(enum_options)} enum options")
        
        # Create Custom Types
        print("Creating custom types...")
        custom_type1 = CustomType(
            gid=generate_gid(),
            name="Epic",
            description="Large work item",
            enabled=True,
            workspace_id=workspace1.id,
            created_by_id=users[0].id
        )
        custom_type2 = CustomType(
            gid=generate_gid(),
            name="Story",
            description="User story",
            enabled=True,
            workspace_id=workspace1.id,
            created_by_id=users[0].id
        )
        db.add(custom_type1)
        db.add(custom_type2)
        db.commit()
        db.refresh(custom_type1)
        db.refresh(custom_type2)
        print(f"Created custom types: {custom_type1.name}, {custom_type2.name}")
        
        # Create Custom Type Status Options
        print("Creating custom type status options...")
        status_opt1 = CustomTypeStatusOption(
            gid=generate_gid(),
            name="Backlog",
            enabled=True,
            color="gray",
            custom_type_id=custom_type1.id
        )
        status_opt2 = CustomTypeStatusOption(
            gid=generate_gid(),
            name="In Progress",
            enabled=True,
            color="blue",
            custom_type_id=custom_type1.id
        )
        status_opt3 = CustomTypeStatusOption(
            gid=generate_gid(),
            name="Done",
            enabled=True,
            color="green",
            custom_type_id=custom_type1.id
        )
        db.add(status_opt1)
        db.add(status_opt2)
        db.add(status_opt3)
        db.commit()
        print("Created custom type status options")
        
        # Create Rates
        print("Creating rates...")
        rates = []
        for user in users[:3]:  # Create rates for first 3 users
            rate = Rate(
                gid=generate_gid(),
                rate=100.00 + (user.id * 10),  # Different rates for each user
                currency_code="USD",
                parent_id=projects[0].id,
                resource_id=user.id,
                resource_type_field="user",
                created_by_id=users[0].id
            )
            db.add(rate)
            rates.append(rate)
        db.commit()
        for rate in rates:
            db.refresh(rate)
        print(f"Created {len(rates)} rates")
        
        # Create Task Templates
        print("Creating task templates...")
        template1 = TaskTemplate(
            gid=generate_gid(),
            name="Bug Fix Template",
            template={
                "name": "Fix bug: {bug_description}",
                "notes": "Steps to reproduce:\n1. \n2. \n3.",
                "tags": ["bug"]
            },
            project_id=projects[0].id,
            created_by_id=users[0].id
        )
        template2 = TaskTemplate(
            gid=generate_gid(),
            name="Feature Request Template",
            template={
                "name": "Implement: {feature_name}",
                "notes": "Description:\n\nAcceptance Criteria:\n1. \n2. \n3.",
                "tags": ["feature"]
            },
            project_id=projects[1].id,
            created_by_id=users[0].id
        )
        db.add(template1)
        db.add(template2)
        db.commit()
        db.refresh(template1)
        db.refresh(template2)
        print(f"Created task templates: {template1.name}, {template2.name}")
        
        # Create Time Tracking Entries
        print("Creating time tracking entries...")
        time_entries = []
        for task in tasks[:5]:  # Add time entries to first 5 tasks
            # Find the project for this task (simplified - in reality you'd have task-project relationship)
            project_for_task = projects[task.id % len(projects)]
            entry = TimeTrackingEntry(
                gid=generate_gid(),
                duration_minutes=120 + (task.id * 15),  # Different durations
                entered_on=date.today() - timedelta(days=task.id % 7),
                task_id=task.id,
                attributable_to_id=project_for_task.id,
                workspace_id=task.workspace_id,
                user_id=users[0].id,
                created_by_id=users[0].id
            )
            db.add(entry)
            time_entries.append(entry)
        db.commit()
        for entry in time_entries:
            db.refresh(entry)
        print(f"Created {len(time_entries)} time tracking entries")
        
        # Create Budgets
        print("Creating budgets...")
        budget1 = Budget(
            gid=generate_gid(),
            budget_type="cost",
            estimate_enabled=True,
            estimate_value=50000.00,
            estimate_units="USD",
            total_enabled=True,
            total_value=50000.00,
            total_units="USD",
            parent_id=projects[0].id
        )
        budget2 = Budget(
            gid=generate_gid(),
            budget_type="cost",
            estimate_enabled=True,
            estimate_value=75000.00,
            estimate_units="USD",
            total_enabled=True,
            total_value=75000.00,
            total_units="USD",
            parent_id=projects[1].id
        )
        db.add(budget1)
        db.add(budget2)
        db.commit()
        db.refresh(budget1)
        db.refresh(budget2)
        print(f"Created budgets for projects")
        
        # Create Allocations
        print("Creating allocations...")
        allocations = []
        for i, user in enumerate(users[:3]):
            allocation = Allocation(
                gid=generate_gid(),
                resource_subtype="budget",
                parent_id=projects[0].id,
                assignee_id=user.id,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                effort_type="hours",
                effort_value=40.00,
                created_by_id=users[0].id
            )
            db.add(allocation)
            allocations.append(allocation)
        db.commit()
        for allocation in allocations:
            db.refresh(allocation)
        print(f"Created {len(allocations)} allocations")
        
        # Create Access Requests
        print("Creating access requests...")
        access_request1 = AccessRequest(
            gid=generate_gid(),
            target_id=projects[0].id,
            target_type="project",
            requester_id=users[3].id,
            approval_status="pending",
            message="I need access to this project to complete my work."
        )
        access_request2 = AccessRequest(
            gid=generate_gid(),
            target_id=projects[1].id,
            target_type="project",
            requester_id=users[4].id,
            approval_status="approved",
            message="Requesting access for review purposes."
        )
        db.add(access_request1)
        db.add(access_request2)
        db.commit()
        db.refresh(access_request1)
        db.refresh(access_request2)
        print("Created access requests")
        
        # Create Attachments
        print("Creating attachments...")
        attachments = []
        attachment_data = [
            {"name": "design_mockup.pdf", "task": tasks[0]},
            {"name": "requirements.docx", "task": tasks[1]},
            {"name": "screenshot.png", "task": tasks[2]},
        ]
        
        for att_data in attachment_data:
            attachment = Attachment(
                gid=generate_gid(),
                name=att_data["name"],
                resource_subtype="file",
                download_url=f"https://example.com/files/{att_data['name']}",
                host="example.com",
                parent_id=att_data["task"].id,
                parent_type="task",
                created_by_id=users[0].id
            )
            db.add(attachment)
            attachments.append(attachment)
        db.commit()
        for attachment in attachments:
            db.refresh(attachment)
        print(f"Created {len(attachments)} attachments")
        
        # Create Project Statuses
        print("Creating project statuses...")
        project_status1 = ProjectStatus(
            gid=generate_gid(),
            title="On Track",
            text="Project is progressing well",
            color="green",
            project_id=projects[0].id,
            author_id=users[0].id
        )
        project_status2 = ProjectStatus(
            gid=generate_gid(),
            title="At Risk",
            text="Some delays encountered",
            color="yellow",
            project_id=projects[1].id,
            author_id=users[1].id
        )
        db.add(project_status1)
        db.add(project_status2)
        db.commit()
        db.refresh(project_status1)
        db.refresh(project_status2)
        print("Created project statuses")
        
        # Create Project Briefs
        print("Creating project briefs...")
        brief1 = ProjectBrief(
            gid=generate_gid(),
            text="This project aims to redesign the company website with modern UI/UX principles.",
            project_id=projects[0].id
        )
        brief2 = ProjectBrief(
            gid=generate_gid(),
            text="Develop a mobile application for iOS and Android platforms.",
            project_id=projects[1].id
        )
        db.add(brief1)
        db.add(brief2)
        db.commit()
        db.refresh(brief1)
        db.refresh(brief2)
        print("Created project briefs")
        
        # Create Stories
        print("Creating stories...")
        stories = []
        for task in tasks[:3]:
            story = Story(
                gid=generate_gid(),
                text=f"Updated {task.name}",
                type="comment",
                task_id=task.id,
                created_by_id=users[0].id
            )
            db.add(story)
            stories.append(story)
        db.commit()
        for story in stories:
            db.refresh(story)
        print(f"Created {len(stories)} stories")
        
        # Create Reactions
        print("Creating reactions...")
        if stories:
            reaction1 = Reaction(
                gid=generate_gid(),
                emoji_base="thumbsup",
                emoji_skin_tone=None,
                target_id=stories[0].id,
                target_type="story",
                user_id=users[1].id
            )
            reaction2 = Reaction(
                gid=generate_gid(),
                emoji_base="heart",
                emoji_skin_tone=None,
                target_id=stories[0].id,
                target_type="story",
                user_id=users[2].id
            )
            db.add(reaction1)
            db.add(reaction2)
            db.commit()
            print("Created reactions")
        
        # Create Workspace Memberships
        print("Creating workspace memberships...")
        for user in users:
            membership = WorkspaceMembership(
                gid=generate_gid(),
                workspace_id=workspace1.id if user.id % 2 == 0 else workspace2.id,
                user_id=user.id,
                is_active=True
            )
            db.add(membership)
        db.commit()
        print("Created workspace memberships")
        
        # Create Team Memberships
        print("Creating team memberships...")
        team_memberships = []
        for i, user in enumerate(users[:3]):
            membership = TeamMembership(
                gid=generate_gid(),
                team_id=team1.id if i % 2 == 0 else team2.id,
                user_id=user.id,
                is_admin=(user.id == users[0].id)
            )
            db.add(membership)
            team_memberships.append(membership)
        db.commit()
        print("Created team memberships")
        
        # Create Project Memberships
        print("Creating project memberships...")
        for project in projects[:3]:
            for user in users[:3]:
                membership = ProjectMembership(
                    gid=generate_gid(),
                    project_id=project.id,
                    user_id=user.id,
                    write_access=True
                )
                db.add(membership)
        db.commit()
        print("Created project memberships")
        
        # Create Custom Field Settings
        print("Creating custom field settings...")
        for project in projects[:2]:
            for custom_field in custom_fields[:2]:
                setting = CustomFieldSetting(
                    gid=generate_gid(),
                    is_important=(custom_field.id % 2 == 0),
                    project_id=project.id,
                    custom_field_id=custom_field.id
                )
                db.add(setting)
        db.commit()
        print("Created custom field settings")
        
        # Create Jobs
        print("Creating jobs...")
        jobs = []
        job_statuses = ["pending", "in_progress", "succeeded", "failed"]
        job_subtypes = ["project", "task", "attachment", "project_template"]
        
        for i in range(5):
            job = Job(
                gid=generate_gid(),
                resource_type="job",
                resource_subtype=job_subtypes[i % len(job_subtypes)],
                status=job_statuses[i % len(job_statuses)],
                new_project={"name": f"Project from job {i+1}"} if i % 4 == 0 else None,
                new_task={"name": f"Task from job {i+1}"} if i % 4 == 1 else None,
                new_attachment={"name": f"Attachment from job {i+1}"} if i % 4 == 2 else None,
                new_project_template={"name": f"Template from job {i+1}"} if i % 4 == 3 else None
            )
            db.add(job)
            jobs.append(job)
        db.commit()
        print(f"Created {len(jobs)} jobs")
        
        print("\n✅ Database seeding completed successfully!")
        print(f"\nSummary:")
        print(f"  - Workspaces: 2")
        print(f"  - Users: {len(users)}")
        print(f"  - Teams: 3")
        print(f"  - Projects: {len(projects)}")
        print(f"  - Tasks: {len(tasks)}")
        print(f"  - Tags: {len(tags)}")
        print(f"  - Goals: {len(goals)}")
        print(f"  - Portfolios: 2")
        print(f"  - Custom Fields: {len(custom_fields)}")
        print(f"  - Enum Options: {len(enum_options)}")
        print(f"  - Rates: {len(rates)}")
        print(f"  - Time Tracking Entries: {len(time_entries)}")
        print(f"  - Jobs: {len(jobs)}")
        print(f"  - And more...")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database tables first
    print("Initializing database tables...")
    init_db()
    print()
    
    # Seed the database
    seed_database()

