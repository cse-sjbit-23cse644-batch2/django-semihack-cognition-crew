# Coordinator Login & Setup - Complete Guide

## 📍 Updated Components

### 1. **Enhanced Login Page** 
`templates/auth/login.html`

The login page has been completely redesigned with:

✨ **Features:**
- Clear role-specific information cards
- Instructions for each user type (Coordinator, Student, Guide)
- What each role can do in the system
- Account creation instructions
- Admin contact info for coordinator setup

🎨 **Design:**
- Responsive layout (works on mobile/desktop)
- Color-coded role cards (Purple for Coordinator, Green for Student, Orange for Guide)
- Clear call-to-action buttons
- Professional gradient background

---

## 🔐 How to Login as Coordinator

### Prerequisites
- Admin must create your coordinator account
- You must have username and password

### Login Steps

1. **Navigate to Login Page**
   - Go to: `http://localhost:8000/login/`

2. **See the Login Page**
   - Main login form on the left
   - Role information on the right
   - Coordinator card shows what you can do

3. **Enter Your Credentials**
   - Username: `[Your username]`
   - Password: `[Your password]`

4. **Click "Sign In"**

5. **You'll See Coordinator Dashboard**
   - KPI cards showing project stats
   - "Projects Ready for Approval" section
   - All assigned projects table
   - Recent activity feed

---

## 👨‍💼 For Admins: Creating Coordinator Accounts

### Three Methods Available

#### **Method 1: Command Line (Recommended) ⚡**

Fastest way to create coordinator accounts:

```bash
# With interactive password prompt
python manage.py create_coordinator \
  --username john_coord \
  --email john@example.com \
  --first-name John \
  --last-name Doe

# With password in command
python manage.py create_coordinator \
  --username jane_coord \
  --email jane@example.com \
  --password "SecurePass123!" \
  --first-name Jane \
  --last-name Smith
```

**Output:**
```
✓ Coordinator "john_coord" created successfully!
  Email: john@example.com
  Name: John Doe
  Role: COORDINATOR
```

#### **Method 2: Django Admin Panel**

Web-based interface:

1. Go to: `http://localhost:8000/admin/`
2. Login with admin account
3. Click "Users" section
4. Click "+ Add User"
5. Fill form:
   - Username: `john_coord`
   - Password: `[secure password]`
   - Confirm: `[repeat password]`
6. Click "Save"
7. In the detail page, find "Role" dropdown
8. Select "Coordinator"
9. Fill optional fields:
   - Email: `john@example.com`
   - First Name: `John`
   - Last Name: `Doe`
10. Click "Save"

#### **Method 3: Python Shell**

Manual creation:

```bash
python manage.py shell
```

```python
from auth_app.models import User

# Create coordinator
coordinator = User.objects.create_user(
    username='john_coord',
    email='john@example.com',
    password='SecurePass123!',
    role='COORDINATOR',
    first_name='John',
    last_name='Doe'
)

print(f"Created: {coordinator.get_full_name()}")
```

---

## ✅ Coordinator Dashboard Overview

### After Login, Coordinators See:

#### **1. KPI Cards (Top)**
- **Total Projects**: All assigned projects
- **Ready for Approval**: Need coordinator action (⚠️ Warning badge)
- **Published**: Projects with published status ✓
- **Completed**: Finalized projects

#### **2. Projects Ready for Approval**
- Yellow alert section with count badge
- Shows:
  - Project title
  - Domain
  - Guide name
  - Team members
  - Completion status
- One-click "Approve & Finalize" button

#### **3. All Assigned Projects Table**
- Complete list of coordinator's projects
- Shows:
  - Project title
  - Domain
  - Completion % (progress bar)
  - Publication status (badge)
  - Certificate status (view link or "—")
  - Quick "View" button

#### **4. Sidebar**
- Recent activity feed
- Approval statistics
- Workflow diagram

---

## 🔄 Complete Workflow

### Phase 1: Guide Reviews (Guide Role)
```
Student submits phase
  ↓
Guide reviews submission
  ↓
Guide provides feedback (if needed)
  ↓
Student revises (if rejected)
  ↓
Guide approves ✓
  ↓
(Repeat for all 5 phases)
```

### Phase 2: Coordinator Finalizes (Coordinator Role)
```
All phases approved by guide
  ↓
Project appears in coordinator dashboard
  ↓
Coordinator clicks "Approve & Finalize"
  ↓
Coordinator fills form:
  - Publication Status (required)
  - Certificate PDF (optional)
  ↓
Coordinator clicks "Finalize Project"
  ↓
System updates:
  - Project status → COMPLETED
  - Sends notification to team
  ↓
Workflow complete! ✓
```

---

## 📋 Quick Reference

### Login URL
- **Local**: `http://localhost:8000/login/`
- **Production**: `https://yourdomain.com/login/`

### Dashboard URL
- Automatic redirect after login
- Or: `http://localhost:8000/dashboard/`

### Admin Panel
- **Local**: `http://localhost:8000/admin/`
- Only accessible to admin users

### Management Command
```bash
python manage.py create_coordinator --help
```

---

## 🛠️ Troubleshooting

### Coordinator Can't Login
**Problem**: "Invalid username or password"
- **Fix**: Verify username/password are correct
- **Fix**: Admin checks Django admin that account exists

### Can't See "Coordinator" Option on Login
**Problem**: Login page doesn't show coordinator info
- **Fix**: Browser cache issue - refresh page (Ctrl+F5)
- **Fix**: Verify you're on updated version

### Projects Don't Appear in Dashboard
**Problem**: "No projects assigned to you"
- **Fix**: Admin needs to assign projects to coordinator
- **Fix**: Check if role is correctly set to COORDINATOR

### Certificate Upload Fails
**Problem**: "Invalid file format"
- **Fix**: Ensure file is PDF (not image or DOC)
- **Fix**: Try converting to PDF if different format

### "All phases must be approved by guide" Error
**Problem**: Can't approve project
- **Fix**: Verify all 5 phases are approved by guide first
- **Fix**: Ask guide to review and approve remaining phases

---

## 📞 Support Resources

1. **Quick Start Guide**: `COORDINATOR_QUICK_START.md`
2. **Detailed Guide**: `COORDINATOR_LOGIN_GUIDE.md`
3. **System Setup**: `DASHBOARD_SETUP_GUIDE.py`
4. **Main Docs**: `DASHBOARD_DOCUMENTATION.md`

---

## 🎯 Key Takeaways

✅ **Coordinators login** like any other user (same login page)
✅ **Admins create accounts** using command line, admin panel, or shell
✅ **Enhanced login page** shows role-specific information
✅ **Dashboard management** command makes setup easier
✅ **Full workflow support** from guide approval to coordinator finalization

---

**Last Updated**: April 28, 2026
**Version**: 1.0
