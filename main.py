from fastapi import FastAPI
from database import init_db
from endpoints import (
    events, goals, goal_relationships, jobs, portfolios, portfolio_memberships,
    projects, tasks, sections, stories, tags, teams, users, workspaces,
    project_briefs, project_statuses, project_memberships, team_memberships,
    workspace_memberships, webhooks, status_updates, time_periods,
    user_task_lists, goal_memberships, custom_field_memberships,
    resource_exports, graph_exports, access_requests, allocations, attachments, budgets,
    custom_fields, custom_types, rates, reactions, task_templates,
    time_tracking_entries, batch, organization_exports, custom_field_settings,
    rules, typeahead
)

app = FastAPI(
    title="Asana API",
    description="Asana-like project management API",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


# Include routers
app.include_router(events.router, prefix="/api/1.0", tags=["Events"])
app.include_router(goals.router, prefix="/api/1.0", tags=["Goals"])
app.include_router(goal_relationships.router, prefix="/api/1.0", tags=["Goal Relationships"])
app.include_router(jobs.router, prefix="/api/1.0", tags=["Jobs"])
app.include_router(portfolios.router, prefix="/api/1.0", tags=["Portfolios"])
app.include_router(portfolio_memberships.router, prefix="/api/1.0", tags=["Portfolio Memberships"])
app.include_router(projects.router, prefix="/api/1.0", tags=["Projects"])
app.include_router(tasks.router, prefix="/api/1.0", tags=["Tasks"])
app.include_router(sections.router, prefix="/api/1.0", tags=["Sections"])
app.include_router(stories.router, prefix="/api/1.0", tags=["Stories"])
app.include_router(tags.router, prefix="/api/1.0", tags=["Tags"])
app.include_router(teams.router, prefix="/api/1.0", tags=["Teams"])
app.include_router(users.router, prefix="/api/1.0", tags=["Users"])
app.include_router(workspaces.router, prefix="/api/1.0", tags=["Workspaces"])
app.include_router(project_briefs.router, prefix="/api/1.0", tags=["Project Briefs"])
app.include_router(project_statuses.router, prefix="/api/1.0", tags=["Project Statuses"])
app.include_router(project_memberships.router, prefix="/api/1.0", tags=["Project Memberships"])
app.include_router(team_memberships.router, prefix="/api/1.0", tags=["Team Memberships"])
app.include_router(workspace_memberships.router, prefix="/api/1.0", tags=["Workspace Memberships"])
app.include_router(webhooks.router, prefix="/api/1.0", tags=["Webhooks"])
app.include_router(status_updates.router, prefix="/api/1.0", tags=["Status Updates"])
app.include_router(time_periods.router, prefix="/api/1.0", tags=["Time Periods"])
app.include_router(user_task_lists.router, prefix="/api/1.0", tags=["User Task Lists"])
app.include_router(goal_memberships.router, prefix="/api/1.0", tags=["Goal Memberships"])
app.include_router(custom_field_memberships.router, prefix="/api/1.0", tags=["Custom Field Memberships"])
app.include_router(resource_exports.router, prefix="/api/1.0", tags=["Resource Exports"])
app.include_router(graph_exports.router, prefix="/api/1.0", tags=["Graph Exports"])
app.include_router(access_requests.router, prefix="/api/1.0", tags=["Access Requests"])
app.include_router(allocations.router, prefix="/api/1.0", tags=["Allocations"])
app.include_router(attachments.router, prefix="/api/1.0", tags=["Attachments"])
app.include_router(budgets.router, prefix="/api/1.0", tags=["Budgets"])
app.include_router(custom_fields.router, prefix="/api/1.0", tags=["Custom Fields"])
app.include_router(custom_types.router, prefix="/api/1.0", tags=["Custom Types"])
app.include_router(rates.router, prefix="/api/1.0", tags=["Rates"])
app.include_router(reactions.router, prefix="/api/1.0", tags=["Reactions"])
app.include_router(task_templates.router, prefix="/api/1.0", tags=["Task Templates"])
app.include_router(time_tracking_entries.router, prefix="/api/1.0", tags=["Time Tracking Entries"])
app.include_router(batch.router, prefix="/api/1.0", tags=["Batch API"])
app.include_router(organization_exports.router, prefix="/api/1.0", tags=["Organization Exports"])
app.include_router(custom_field_settings.router, prefix="/api/1.0", tags=["Custom Field Settings"])
app.include_router(rules.router, prefix="/api/1.0", tags=["Rules"])
app.include_router(typeahead.router, prefix="/api/1.0", tags=["Typeahead"])


@app.get("/")
def root():
    return {"message": "Asana API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}

