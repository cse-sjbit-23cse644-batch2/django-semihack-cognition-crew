# 🎓 Student Project & Milestone Tracker

A comprehensive Django-based application for managing student projects, milestones, and evaluations. The system provides role-based dashboards for students, coordinators, guides, and administrators to track progress, submit work, manage feedback, and evaluate project quality.

## 📋 Application Overview

**Student Project & Milestone Tracker** is a full-featured web application designed to streamline project management in educational settings. It enables:

- **Role-Based Access Control**: Separate dashboards for students, coordinators, guides, and administrators
- **Project Management**: Create, track, and manage student projects with milestone submissions
- **Evaluation System**: Structured feedback and project evaluation workflows
- **Notification System**: Real-time notifications for submissions, reviews, and feedback
- **Plagiarism Detection**: Built-in similarity checking for submitted work
- **Certificate Generation**: Automated certificate creation for successful project completions
- **Document Management**: Support for file uploads, versioning, and media handling

## ✨ Key Features

### 🔐 Authentication & Authorization
- Secure user registration and login system
- Role-based access control (Student, Coordinator, Guide, Admin)
- User profile management
- Session management with automatic logout

### 📊 Dashboards
- **Student Dashboard**: View assigned teams, track milestone submissions, and track project progress
- **Coordinator Dashboard**: Manage teams, track submissions, view pending reviews, oversee all projects
- **Guide Dashboard**: Review student work, provide feedback, track assigned teams
- **Admin Dashboard**: System administration, user management, project oversight

### 📁 Project Management
- Create and manage student projects
- Milestone-based project structure
- File submission handling with versioning support
- Automatic media organization (certificates, submissions)

### 📝 Evaluation & Feedback
- Structured evaluation framework
- Feedback versioning system
- Certificate generation for completed projects
- Project-level evaluations and ratings

### 🔔 Notifications
- Real-time notification system
- Event-based alerts (submissions, reviews, feedback)
- User-specific notification tracking

### 🔍 Plagiarism Detection
- Similarity checking for submitted work
- Integration with file submission system
- Automatic detection reports
## 🏗️ Project Architecture

### Django Apps
- **auth_app**: Authentication, user management, and role assignment
- **projects**: Core project management, submissions, and evaluations
- **dashboards**: Role-based dashboard views and reports
- **notifications**: Event-driven notification system
- **similarity**: Plagiarism detection and similarity analysis
- **capstone_tracker**: Main Django project configuration

### Database Models
- Custom User model with role-based permissions
- Project and Milestone models for project tracking
- Feedback and Evaluation models for assessment
- Notification models for event tracking
- Submission and Certificate models for deliverables

## 📦 Setup Instructions

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone [your-repo-url]
cd django-semihack-cognition-crew/student_project_n_milestone_tracker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create superuser account (for admin access)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The application will be available at `http://localhost:8000`
## � User Roles & Features

### 🎓 Student
- View assigned team and project details
- Submit milestone work and project files
- Track submission status and feedback
- Access personal dashboard
- Download certificates upon project completion

### 👨‍💼 Coordinator
- Create and manage projects
- Assign students to teams
- Manage project milestones
- Review submissions and provide feedback
- Access coordinator dashboard
- Track all project submissions
- Monitor project progress and team assignments

### 📖 Guide (Faculty/Mentor)
- Review assigned student work
- Provide detailed feedback on submissions
- Track assigned teams
- View project evaluations
- Participate in evaluation process

### ⚙️ Administrator
- System user management
- Create and manage users
- Manage system settings
- Access administrative dashboard
- Oversee all projects and evaluations
- Generate reports and analytics

## 🚀 Deployment Guide (Render)

### Pre-Deploy Checklist
- [ ] `DEBUG = False` in `settings.py`
- [ ] `STATIC_ROOT` configured
- [ ] `ALLOWED_HOSTS` includes cloud domain
- [ ] `gunicorn` in `requirements.txt`
- [ ] Local `python manage.py collectstatic` ran successfully

1. **Sign Up & Connect**
   - Go to [render.com](https://render.com) → Sign up with GitHub
   - Authorize Render to access your repositories

2. **Create Web Service**
   - Click `New +` → `Web Service` → Connect this repository
   - Fill in the following details:
     - **Name**: `student-milestone-tracker`
     - **Region**: `Ohio` or `Frankfurt` (geographically appropriate)
     - **Branch**: `main`
     - **Build Command**: `pip install -r requirements.txt && python student_project_n_milestone_tracker/manage.py collectstatic --noinput`
     - **Start Command**: `gunicorn student_project_n_milestone_tracker.capstone_tracker.wsgi`

3. **Environment Variables (Critical)**
   Click `Advanced` → `Add Environment Variable`:
   
   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | Generate at [miniwebtool.com/django-secret-key-generator](https://miniwebtool.com/django-secret-key-generator/) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `*.onrender.com, localhost, 127.0.0.1` |
   | `DATABASES_PATH` | `student_project_n_milestone_tracker` |

4. **Deploy & Verify**
   - Click `Create Web Service` → Wait 3–5 minutes for build to complete
   - Once deployment is live, copy the `https://...onrender.com` URL
   - ✅ Test: Open URL in browser, verify CSS/JS loads, test login, check dashboard functionality
   - 📝 Update `Live URL` in documentation after successful deployment

### 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| `Application Error` on Render | Verify `gunicorn` is in `requirements.txt` and wsgi path is correct: `student_project_n_milestone_tracker.capstone_tracker.wsgi` |
| Broken CSS/JS on live site | Ensure `STATIC_ROOT` is configured and `collectstatic` command runs successfully in build step |
| `DisallowedHost` error | Check `ALLOWED_HOSTS` environment variable matches your Render domain (should include `*.onrender.com`) |
| Database migration errors | Run `python manage.py migrate` locally before pushing; free tier uses SQLite which is suitable for development |
| Login page not appearing | Ensure `auth_app` migrations have run: `python manage.py migrate auth_app` |
| Static files not loading (CSS/JS blank) | Run `python manage.py collectstatic --noinput` locally and verify `STATIC_ROOT` setting |
| Media files (uploads) missing | Check that `media/` directory exists and is properly configured in `settings.py` |

> 💡 **Note:** Every `git push` to `main` branch automatically triggers a rebuild on Render. No manual server restarts needed.

## 📚 Documentation

For detailed setup and usage guides, see:
- [Coordinator Login Setup](COORDINATOR_LOGIN_SETUP.md)
- [Coordinator Quick Start](COORDINATOR_QUICK_START.md)
- [Dashboard Documentation](DASHBOARD_DOCUMENTATION.md)
- [Dashboard Setup Guide](DASHBOARD_SETUP_GUIDE.py)

## 📁 Project Structure

```
student_project_n_milestone_tracker/
├── auth_app/                 # User authentication & roles
├── projects/                 # Project management & submissions
├── dashboards/               # Dashboard views & reports
├── notifications/            # Notification system
├── similarity/               # Plagiarism detection
├── capstone_tracker/         # Main Django configuration
├── templates/                # HTML templates
├── static/                   # CSS, JavaScript assets
├── media/                    # User uploads (certificates, submissions)
├── manage.py                 # Django management script
└── requirements.txt          # Python dependencies
```

## 🔧 Technology Stack

- **Backend**: Django 3.2+
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: HTML5, CSS3, JavaScript
- **File Handling**: Django file fields with media management
- **Notifications**: Django signals-based event system

## 📧 Support & Contact

For issues, documentation updates, or feature requests, please refer to the project documentation files in the root directory.

---

**Last Updated**: April 2026
**Status**: Production Ready
