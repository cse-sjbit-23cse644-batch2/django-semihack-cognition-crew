# Coordinator Login & Account Management Guide

## 📋 How to Login as a Coordinator

### Step 1: Access the Login Page
1. Go to the MilestoneTracker login page
2. You'll see login instructions for different roles

### Step 2: Enter Your Credentials
- **Username**: Your assigned username (e.g., `ganesh`)
- **Password**: Your password

### Step 3: Click Sign In
- You'll be redirected to the Coordinator Dashboard

---

## 🔐 Creating Coordinator Accounts

Coordinator accounts cannot be self-registered. Only **Admins** can create coordinator accounts.

### Method 1: Using Django Admin Panel (Recommended)

1. **Go to Admin Panel**
   - URL: `http://localhost:8000/admin/`
   - Login with admin credentials

2. **Navigate to Users**
   - Click on "Users" under AUTH_APP section

3. **Click "Add User"**
   - Click the "+ Add User" button in the top-right

4. **Fill in Basic Information**
   ```
   Username: [Enter username - e.g., 'coordinator_name']
   Password: [System will generate or you enter one]
   Confirm Password: [Re-enter password]
   ```

5. **Save**
   - Click "Save" to create the user

6. **Edit Role**
   - On the user detail page, scroll down to find the "Role" field
   - Change from "Student" to "Coordinator"
   - Add optional information:
     - First Name
     - Last Name
     - Email
     - Bio
     - Profile Picture

7. **Save Changes**
   - Click "Save" button at the bottom

---

### Method 2: Using Django Management Command

Run this command in the terminal:

```bash
python manage.py shell
```

Then in the Python shell:

```python
from auth_app.models import User

# Create coordinator account
user = User.objects.create_user(
    username='coordinator_username',
    email='coordinator@example.com',
    password='secure_password',
    role='COORDINATOR',
    first_name='Coordinator',
    last_name='Name'
)

print(f"Coordinator {user.username} created successfully!")
```

---

## ✅ What Can Coordinators Do?

Once logged in, coordinators can:

### Dashboard
- View all assigned projects
- See projects ready for approval
- Monitor publication status
- Track completion rates

### Project Approval
- Review guide-approved submissions
- See phase completion status
- Access team information
- View previous submissions

### Publication Management
- Set publication status (PENDING/APPROVED/PUBLISHED/REJECTED)
- Upload project certificates (PDF)
- Add approval notes
- Finalize projects

### Notifications
- Automatic notifications sent to teams after approval
- Activity feed showing recent approvals

---

## 🔗 Coordinator Workflow

```
1. Guide approves all 5 phases
   ↓
2. Project appears in "Projects Ready for Approval"
   ↓
3. Coordinator clicks "Approve & Finalize"
   ↓
4. Coordinator sets publication status
   ↓
5. Coordinator uploads certificate (optional)
   ↓
6. Coordinator clicks "Finalize Project"
   ↓
7. Project status → COMPLETED
   ↓
8. Team receives notification
```

---

## 🛠️ Troubleshooting

### Coordinator Can't Login
- **Check**: Verify username and password are correct
- **Solution**: Ask admin to reset password in Django admin

### Account Not Found
- **Check**: Confirm the account was created in Django admin
- **Solution**: Admin needs to create the coordinator account

### Can't Access Coordinator Dashboard
- **Check**: Verify user role is set to "COORDINATOR"
- **Solution**: Edit user in Django admin and change role

### Certificate Upload Fails
- **Check**: Ensure file is in PDF format
- **Check**: File size is reasonable (< 10MB recommended)
- **Solution**: Try converting to PDF if in different format

---

## 📞 Support

For issues or questions:
1. Contact your system administrator
2. Check the MilestoneTracker documentation
3. Review error messages in the browser console

---

## 📝 Quick Reference

| Task | Where | Notes |
|------|-------|-------|
| Login | `/login/` | Use coordinator credentials |
| Dashboard | `/dashboard/` | Automatic redirect after login |
| Approve Project | Project detail page | Click "Review & Approve" button |
| Upload Certificate | Approval form | PDF only, optional |
| View Projects | Dashboard table | Click "View" for details |
| Check Activity | Dashboard sidebar | Recent approvals shown |

---

**Last Updated**: April 28, 2026
