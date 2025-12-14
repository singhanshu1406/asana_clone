# Asana API Clone

A comprehensive FastAPI-based implementation of the Asana API, providing project management capabilities with full CRUD operations, relationships, and advanced features.

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic

# 2. Start the server
uvicorn main:app --reload

# 3. Access API documentation
# Open http://localhost:8000/docs in your browser

# 4. Seed test data (optional)
python seed_data.py
```

The API will be available at `http://localhost:8000/api/1.0`

## 🚀 Features

- **Complete API Implementation**: 138+ endpoints covering all Asana API functionality
- **RESTful Design**: Follows Asana API v1.0 specification
- **PostgreSQL Database**: Robust data persistence with SQLAlchemy ORM
- **Auto-Generated GIDs**: UUID-based globally unique identifiers
- **Comprehensive Testing**: Automated comparison with real Asana API
- **Full CRUD Operations**: Create, Read, Update, Delete for all resources
- **Relationship Management**: Handles complex relationships between resources
- **Error Handling**: Proper HTTP status codes and error messages
- **Request/Response Validation**: Pydantic schemas for type safety

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Development](#development)

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Step 1: Clone and Navigate

```bash
cd /Users/anshuanshu/Desktop/Asana
```

### Step 2: Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv
```

Or install from requirements file (if available):
```bash
pip install -r requirements.txt
```

### Step 3: Database Setup

1. Create PostgreSQL database:
```sql
CREATE DATABASE asana;
```

2. Update database connection in `database.py`:
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/asana"
```

3. Initialize database tables:
```bash
python -c "from database import init_db; init_db()"
```

4. Seed test data:
```bash
python seed_data.py
```

## ⚙️ Configuration

### Database Configuration

Edit `database.py` to set your database connection:
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/asana"
```

### API Key Configuration (for Testing)

For API comparison testing, set your Asana API key in `config.py`:
```python
ASANA_API_KEY = "your_asana_api_key_here"
```

Or use environment variable:
```bash
export ASANA_API_KEY="your_asana_api_key_here"
```

## 🗄️ Database Setup

### Initialize Database

The database will be automatically initialized when you start the application, or manually:

```bash
python -c "from database import init_db; init_db()"
```

### Seed Test Data

Populate the database with test data:

```bash
python seed_data.py
```

This creates:
- 2 Workspaces
- 5 Users
- 3 Teams
- 5 Projects
- 8 Tasks
- And many more test resources...

### Database Schema

The project includes models for:
- **Core Resources**: Workspaces, Users, Teams, Projects, Tasks
- **Organization**: Portfolios, Goals, Sections, Tags
- **Collaboration**: Stories, Comments, Reactions
- **Management**: Memberships, Webhooks, Status Updates
- **Advanced**: Custom Fields, Allocations, Budgets, Time Tracking
- **And 30+ more resource types**

## 🏃 Running the Application

### Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API Base URL**: `http://localhost:8000/api/1.0`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

### Run on Different Port

```bash
uvicorn main:app --reload --port 8001
```

## 📚 API Documentation

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Base URL

All endpoints are prefixed with `/api/1.0`

Example:
```
GET http://localhost:8000/api/1.0/projects
GET http://localhost:8000/api/1.0/projects/{project_gid}
POST http://localhost:8000/api/1.0/projects
PUT http://localhost:8000/api/1.0/projects/{project_gid}
DELETE http://localhost:8000/api/1.0/projects/{project_gid}
```

### Authentication

Currently, the API doesn't require authentication. In production, you should add authentication middleware.

### GID (Globally Unique Identifier)

All resources use UUID-based GIDs:
- **Format**: UUID v4 (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **Auto-generated**: GIDs are automatically generated on create
- **Required**: GIDs are required for GET, PUT, DELETE operations

## 🧪 Testing

### API Comparison Testing

Compare your API with the real Asana API:

#### Comprehensive Test (All Endpoints)
```bash
python3 comprehensive_api_test.py
```
- Tests all 138 endpoints
- Compares responses with Asana API
- Tests status codes
- Generates detailed reports

#### Status Code Testing
```bash
python3 test_all_status_codes.py
```
- Focuses on status code matching
- Tests error scenarios

#### Selective Testing
```bash
python3 test_api_comparison.py
```
- Tests curated list of important endpoints

### Test Reports

After running tests, review:
- `comprehensive_api_comparison_report.json` - Full test results
- `comprehensive_ai_fix_prompt.txt` - AI-ready fix instructions
- `status_code_test_report.json` - Status code test results

### Analyze Results

```bash
python3 auto_fix_helper.py
```

This analyzes differences and generates fix suggestions.

## 📁 Project Structure

```
Asana/
├── main.py                 # FastAPI application entry point
├── database.py             # Database connection and initialization
├── utils.py                # Utility functions (GID generation)
├── config.py               # Configuration (API keys, URLs)
│
├── models/                 # SQLAlchemy database models
│   ├── user.py
│   ├── workspace.py
│   ├── project.py
│   ├── task.py
│   └── ... (40+ models)
│
├── schemas/                 # Pydantic request/response schemas
│   ├── base.py
│   ├── user.py
│   ├── project.py
│   └── ... (40+ schemas)
│
├── endpoints/               # API endpoint implementations
│   ├── users.py
│   ├── projects.py
│   ├── tasks.py
│   └── ... (40+ endpoints)
│
├── seed_data.py            # Database seeding script
│
├── api_comparison.py       # Core comparison logic
├── comprehensive_api_test.py  # Comprehensive test suite
├── test_api_comparison.py  # Selective test suite
├── test_all_status_codes.py    # Status code testing
└── auto_fix_helper.py      # Test result analysis
```

## 🔌 API Endpoints

### Core Resources

#### Workspaces
- `GET /workspaces` - List workspaces
- `GET /workspaces/{workspace_gid}` - Get workspace
- `GET /workspaces/{workspace_gid}/users` - Get workspace users

#### Users
- `GET /users` - List users
- `GET /users/{user_gid}` - Get user
- `GET /users/me` - Get current user

#### Teams
- `GET /teams` - List teams
- `GET /teams/{team_gid}` - Get team
- `POST /organizations/{organization_gid}/teams` - Create team
- `PUT /teams/{team_gid}` - Update team
- `DELETE /teams/{team_gid}` - Delete team

#### Projects
- `GET /projects` - List projects
- `GET /projects/{project_gid}` - Get project
- `POST /projects` - Create project
- `PUT /projects/{project_gid}` - Update project
- `DELETE /projects/{project_gid}` - Delete project

#### Tasks
- `GET /tasks` - List tasks
- `GET /tasks/{task_gid}` - Get task
- `POST /tasks` - Create task
- `PUT /tasks/{task_gid}` - Update task
- `DELETE /tasks/{task_gid}` - Delete task

### Advanced Features

#### Portfolios
- `GET /portfolios` - List portfolios
- `GET /portfolios/{portfolio_gid}` - Get portfolio
- `POST /portfolios` - Create portfolio
- `PUT /portfolios/{portfolio_gid}` - Update portfolio
- `DELETE /portfolios/{portfolio_gid}` - Delete portfolio

#### Goals
- `GET /goals` - List goals
- `GET /goals/{goal_gid}` - Get goal
- `POST /goals` - Create goal
- `PUT /goals/{goal_gid}` - Update goal
- `DELETE /goals/{goal_gid}` - Delete goal

#### Custom Fields
- `GET /workspaces/{workspace_gid}/custom_fields` - List custom fields
- `GET /custom_fields/{custom_field_gid}` - Get custom field
- `POST /workspaces/{workspace_gid}/custom_fields` - Create custom field
- `PUT /custom_fields/{custom_field_gid}` - Update custom field
- `DELETE /custom_fields/{custom_field_gid}` - Delete custom field

### And 100+ More Endpoints

See the interactive API documentation at `/docs` for the complete list.

## 📝 Example Usage

### Create a Project

```bash
curl -X POST "http://localhost:8000/api/1.0/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "My New Project",
      "workspace": "31a12bd3-4f18-45f5-a43b-71f9737ad873"
    }
  }'
```

### Get a Project

```bash
curl "http://localhost:8000/api/1.0/projects/1df26615-9cba-4728-bc10-37bec696e77a"
```

### Create a Task

```bash
curl -X POST "http://localhost:8000/api/1.0/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "Complete API documentation",
      "workspace": "31a12bd3-4f18-45f5-a43b-71f9737ad873"
    }
  }'
```

### Update a Task

```bash
curl -X PUT "http://localhost:8000/api/1.0/tasks/2844d3c4-f9e9-4f18-80ef-8ff4b566c2fe" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "completed": true
    }
  }'
```

## 🔧 Development

### Adding New Endpoints

1. **Create Model** (if needed): `models/your_resource.py`
2. **Create Schema**: `schemas/your_resource.py`
3. **Create Endpoint**: `endpoints/your_resource.py`
4. **Register Router**: Add to `main.py`

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Use Pydantic for validation

### Database Migrations

Currently using SQLAlchemy's `create_all()`. For production, consider using Alembic for migrations.

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Connection Error

- Verify PostgreSQL is running
- Check database credentials in `database.py`
- Ensure database exists

### Import Errors

- Ensure all dependencies are installed
- Check Python path
- Verify virtual environment is activated (if using)

### API Key Issues

- Verify API key is set in `config.py` or environment
- Check key format (should be valid Asana API key)

## 📊 Statistics

- **Total Endpoints**: 138
- **Database Models**: 40+
- **Schemas**: 40+
- **Test Coverage**: Comprehensive comparison with Asana API

## 🔐 Security Notes

- **API Keys**: Never commit API keys to version control
- **Database Credentials**: Use environment variables in production
- **Authentication**: Add authentication middleware for production
- **Input Validation**: All inputs are validated via Pydantic
- **SQL Injection**: Protected by SQLAlchemy ORM

## 📄 License

This project is a clone/implementation of the Asana API for educational and development purposes.

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new endpoints
3. Update documentation
4. Ensure API compatibility with Asana API

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check test reports for API differences

## 🎯 Key Features Implemented

✅ Auto-generated UUID GIDs  
✅ Full CRUD operations  
✅ Relationship management  
✅ Error handling with proper status codes  
✅ Request/response validation  
✅ Comprehensive testing suite  
✅ API comparison with real Asana API  
✅ Database seeding for testing  
✅ Interactive API documentation  

---

**Built with**: FastAPI, SQLAlchemy, PostgreSQL, Pydantic

