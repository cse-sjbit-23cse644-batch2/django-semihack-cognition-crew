# Quick Start: Coordinator Account Setup

## 🚀 For Admins: Creating a Coordinator Account

### Option 1: Command Line (Quickest)

```bash
# Create a coordinator account with interactive password prompt
python manage.py create_coordinator --username john_doe --email john@example.com --first-name John --last-name Doe

# Create with password in one command
python manage.py create_coordinator --username john_doe --email john@example.com --password "secure_password" --first-name John --last-name Doe
```

### Option 2: Django Admin Panel

1. Go to `http://localhost:8000/admin/`
2. Login with admin credentials
3. Click "Users"
4. Click "+ Add User"
5. Enter username and password
6. Click "Save"
7. Change "Role" field to "COORDINATOR"
8. Fill in email, first name, last name
9. Click "Save" again

### Option 3: Python Shell

```bash
python manage.py shell
```

```python
from auth_app.models import User

coordinator = User.objects.create_user(
    username='john_doe',
    email='john@example.com',
    password='secure_password',
    role='COORDINATOR',
    first_name='John',
    last_name='Doe'
)
print(f"Coordinator created: {coordinator.username}")
```

---

## 👤 For Coordinators: Logging In

### Step 1: Go to Login Page
- URL: `http://localhost:8000/login/` (or your domain)

### Step 2: Enter Credentials
- **Username**: The username created by admin
- **Password**: The password you received

### Step 3: Click "Sign In"

### Step 4: You'll See Your Dashboard
- View assigned projects
- See projects ready for approval
- Manage publication status
- Upload certificates

---

## 📊 Coordinator Dashboard Features

Once logged in, you'll see:

### KPI Cards
- **Total Projects**: All projects assigned to you
- **Ready for Approval**: Projects with all phases approved by guide
- **Published**: Projects with published status
- **Completed**: All finalized projects

### Projects Ready for Approval
- List of projects ready for coordinator approval
- Shows completion %, guide info, team members
- Quick button to "Approve & Finalize"

### All Assigned Projects Table
- Complete project list
- Completion percentage
- Publication status
- Certificate status
- Links to view details

### Recent Activity
- Shows recent approvals and updates
- Timeline of coordinator actions

---

## ✅ Complete Workflow Example

### As a Guide:
1. Review student submissions
2. Approve all 5 phases

### As a Coordinator:
1. Login to dashboard
2. See project in "Ready for Approval" section
3. Click "Approve & Finalize" button
4. Fill form:
   - Select publication status (PENDING/APPROVED/PUBLISHED/REJECTED)
   - Optionally upload certificate PDF
5. Click "Finalize Project"
6. Project completed! Team notified automatically

---

## 🔍 Verifying Coordinator Setup

To verify a coordinator account exists and is properly configured:

```bash
python manage.py shell
```

```python
from auth_app.models import User

# Check coordinator
coordinator = User.objects.get(username='john_doe')
print(f"Username: {coordinator.username}")
print(f"Role: {coordinator.role}")
print(f"Email: {coordinator.email}")
print(f"Full Name: {coordinator.get_full_name()}")
```

---

## ❓ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Username already exists" | Choose a different username |
| "Coordinator can't login" | Verify username/password are correct |
| "Login page shows error" | Check that Django server is running |
| "Can't see projects in dashboard" | Admin needs to assign projects to coordinator |
| "Certificate upload fails" | Ensure file is PDF format |

---

## 📋 Reference: Role Comparison

| Feature | Student | Guide | Coordinator | Admin |
|---------|---------|-------|-------------|-------|
| Self-signup | ✅ | ✅ | ❌ | ❌ |
| View dashboard | ✅ | ✅ | ✅ | ✅ |
| Submit work | ✅ | ❌ | ❌ | ❌ |
| Review submissions | ❌ | ✅ | ❌ | ✅ |
| Approve phases | ❌ | ✅ | ❌ | ✅ |
| Finalize projects | ❌ | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ✅ |

---

## 🆘 Need Help?

For more details, see: `COORDINATOR_LOGIN_GUIDE.md`

For system troubleshooting, check: `DASHBOARD_SETUP_GUIDE.py`
