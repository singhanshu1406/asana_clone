# Proposed Database Tables

Based on the schema names and API parameters provided, here are 5 representative tables:

## 1. **users** table

For: `UserResponse`, `UserCompact`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    gid VARCHAR(255) UNIQUE NOT NULL,  -- Globally unique identifier
    resource_type VARCHAR(50) DEFAULT 'user',
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    photo VARCHAR(500),  -- Photo URL
    workspaces TEXT[],  -- Array of workspace GIDs
    is_workspace_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**

- `gid`: Used in path parameters like `user_gid`
- `email`: Used in query parameters for user identification
- `name`: For UserResponse display

---

## 2. **workspaces** table

For: `WorkspaceResponse`, `WorkspaceCompact`

```sql
CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    gid VARCHAR(255) UNIQUE NOT NULL,
    resource_type VARCHAR(50) DEFAULT 'workspace',
    name VARCHAR(255) NOT NULL,
    is_organization BOOLEAN DEFAULT FALSE,
    email_domains TEXT[],  -- Array of email domains
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**

- `gid`: Used in path parameters like `workspace_gid` and query params like `workspace_query_param`
- `is_organization`: Distinguishes workspace vs organization

---

## 3. **projects** table

For: `ProjectResponse`, `ProjectCompact`

```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    gid VARCHAR(255) UNIQUE NOT NULL,
    resource_type VARCHAR(50) DEFAULT 'project',
    name VARCHAR(255) NOT NULL,
    notes TEXT,
    archived BOOLEAN DEFAULT FALSE,
    color VARCHAR(50),
    default_view VARCHAR(50),  -- list, board, calendar, etc.
    due_date DATE,
    start_on DATE,
    current_status_update_id INTEGER,  -- FK to project_statuses
    workspace_id INTEGER REFERENCES workspaces(id),
    team_id INTEGER,  -- FK to teams (optional)
    owner_id INTEGER REFERENCES users(id),
    public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**

- `gid`: Used in `project_path_gid`, `project_query_param`
- `archived`: Used in `archived_query_param`
- `workspace_id`: Links to workspace
- `team_id`: Used with `team_query_param`

---

## 4. **tasks** table

For: `TaskResponse`, `TaskCompact`

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    gid VARCHAR(255) UNIQUE NOT NULL,
    resource_type VARCHAR(50) DEFAULT 'task',
    name VARCHAR(255) NOT NULL,
    notes TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    due_on DATE,
    due_at TIMESTAMP,
    start_on DATE,
    assignee_id INTEGER REFERENCES users(id),
    assignee_status VARCHAR(50),  -- upcoming, later, new, inbox
    workspace_id INTEGER REFERENCES workspaces(id),
    parent_id INTEGER REFERENCES tasks(id),  -- For subtasks
    num_subtasks INTEGER DEFAULT 0,
    num_likes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**

- `gid`: Used in `task_path_gid`
- `completed_at`: Used with `completed_since` query param
- `workspace_id`: Links to workspace
- `assignee_id`: Links to user

---

## 5. **goals** table

For: `GoalResponse`, `GoalCompact`

```sql
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    gid VARCHAR(255) UNIQUE NOT NULL,
    resource_type VARCHAR(50) DEFAULT 'goal',
    name VARCHAR(255) NOT NULL,
    html_notes TEXT,
    notes TEXT,
    due_on DATE,
    start_on DATE,
    status VARCHAR(50),  -- green, yellow, red, missed, achieved, partial, dropped
    is_workspace_level BOOLEAN DEFAULT FALSE,
    liked BOOLEAN DEFAULT FALSE,
    num_likes INTEGER DEFAULT 0,
    workspace_id INTEGER REFERENCES workspaces(id),
    team_id INTEGER,  -- FK to teams (optional)
    owner_id INTEGER REFERENCES users(id),
    time_period_id INTEGER,  -- FK to time_periods
    metric_id INTEGER,  -- For goal metrics
    parent_goal_id INTEGER REFERENCES goals(id),  -- For goal hierarchies
    current_status_update_id INTEGER,  -- FK to status_updates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**

- `gid`: Used in `goal_path_gid`
- `workspace_id`: Links to workspace
- `team_id`: Links to team
- `status`: Goal status tracking

---

## Additional Supporting Tables (for relationships):

- **project_memberships**: Links users/teams to projects
- **goal_memberships**: Links users/teams to goals
- **workspace_memberships**: Links users to workspaces
- **project_statuses**: Status updates for projects
- **status_updates**: Status updates for goals
- **teams**: Team information
- **time_periods**: Time periods for goals

---

**Notes:**

- All tables use `gid` (Globally Unique Identifier) as the external identifier
- All tables have `resource_type` to match Asana's API format
- Timestamps (`created_at`, `updated_at`) for audit purposes
- Foreign keys maintain referential integrity
- Arrays (TEXT[]) used where Asana supports multiple values
