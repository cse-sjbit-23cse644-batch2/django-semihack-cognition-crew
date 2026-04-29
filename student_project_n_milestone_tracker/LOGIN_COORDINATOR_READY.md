# 🔐 COORDINATOR LOGIN - READY TO USE

## ✅ Current Status

### Existing Coordinator Account (Ready to Login)
```
Username: ganesh
Name: Ganesh G TML
Role: COORDINATOR
```

**This account can login right now!**

---

## 📖 How to Login as Coordinator

### Step 1: Open Login Page
```
URL: http://localhost:8000/login/
```

### Step 2: You'll See Enhanced Login Page
The new login page shows:
- **Main login form** (left side) 
- **Role information cards** (right side)
- **Coordinator card** explains what coordinators can do

### Step 3: Enter Coordinator Credentials
```
Username: ganesh
Password: [coordinator's password]
```

### Step 4: Click "Sign In"

### Step 5: View Coordinator Dashboard ✓
After login, you'll see:
- Total Projects assigned to you
- Projects ready for approval
- Published projects count
- Completed projects count
- List of all assigned projects
- Recent activity

---

## 🛠️ How to Create New Coordinator Accounts

### Quick Method (Recommended)

**Command 1: With interactive password**
```bash
python manage.py create_coordinator \
  --username coordinator_name \
  --email coordinator@example.com \
  --first-name FirstName \
  --last-name LastName
```
(System will prompt for password)

**Command 2: With password included**
```bash
python manage.py create_coordinator \
  --username coordinator_name \
  --email coordinator@example.com \
  --password "SecurePassword123!" \
  --first-name FirstName \
  --last-name LastName
```

### Full Example

```bash
# Create coordinator account for John Coordinator
python manage.py create_coordinator \
  --username john_coordinator \
  --email john.coord@example.com \
  --password "Welcome@123" \
  --first-name John \
  --last-name Coordinator

# Output:
# ✓ Coordinator "john_coordinator" created successfully!
#   Email: john.coord@example.com
#   Name: John Coordinator
#   Role: COORDINATOR
```

---

## 📋 What Can Coordinators Do?

In the coordinator dashboard, they can:

✅ **Review Approvals**
- View all projects assigned to them
- See phase completion status
- Check team member names

✅ **Finalize Projects**
- Set publication status:
  - PENDING (Under consideration)
  - APPROVED (Ready for publication)
  - PUBLISHED (Already published)
  - REJECTED (Not approved)

✅ **Upload Certificates**
- Upload project completion certificates (PDF)
- View previously uploaded certificates

✅ **Notifications**
- See what's ready for action
- Track recent approvals
- Monitor workflow progress

---

## 🎯 Workflow Example

### Step-by-Step Process

**1. Guide approves all 5 phases** (done by guide/teacher)
   - Phase 1: APPROVED ✓
   - Phase 2: APPROVED ✓
   - Phase 3: APPROVED ✓
   - Phase 4: APPROVED ✓
   - Phase 5: APPROVED ✓

**2. Coordinator sees project in dashboard**
   - "Projects Ready for Approval" section shows it
   - Yellow warning badge shows count

**3. Coordinator clicks "Approve & Finalize"**
   - Opens approval form
   - Shows all phase completion statuses
   - Shows team members

**4. Coordinator fills form**
   - Select Publication Status (required)
   - Upload Certificate (optional)
   - Add Notes (optional)

**5. Coordinator clicks "Finalize Project"**
   - Project status → COMPLETED
   - Team automatically notified
   - Appears in "Published" list

**✅ Done!** Project workflow complete.

---

## 🧪 Test Coordinator Login

### Right Now:
1. Login as: `ganesh`
2. Go to dashboard: `http://localhost:8000/dashboard/`
3. You should see **Coordinator Dashboard**

### What You'll See:
- KPI Cards (Total, Pending, Published, Completed)
- Any projects assigned to this coordinator
- Workflow instructions

---

## 🔗 Related Guides

| Document | Purpose |
|----------|---------|
| `COORDINATOR_LOGIN_SETUP.md` | Complete setup guide |
| `COORDINATOR_QUICK_START.md` | Quick reference |
| `COORDINATOR_LOGIN_GUIDE.md` | Detailed instructions |
| `DASHBOARD_DOCUMENTATION.md` | Full system docs |

---

## ❓ FAQ

**Q: Can anyone create a coordinator account?**
A: No, only admins can create coordinator accounts. Users can self-register as Students or Guides.

**Q: What if I forget the password?**
A: Admin can reset it in Django admin panel or create a new account.

**Q: Can I change my role after login?**
A: No, only admins can change user roles.

**Q: What if projects don't show in coordinator dashboard?**
A: Admin needs to assign projects to the coordinator.

**Q: How do I upload a certificate?**
A: Click "Approve & Finalize", fill the form, use the file upload field for PDF.

---

## 🚀 Quick Start Commands

```bash
# Test the command
python manage.py help create_coordinator

# Create a new coordinator
python manage.py create_coordinator \
  --username test_coord \
  --email test@example.com \
  --password "Test@123" \
  --first-name Test \
  --last-name Coordinator

# List all users
python manage.py shell -c "
from auth_app.models import User
for u in User.objects.filter(role='COORDINATOR'):
    print(f'{u.username}: {u.get_full_name()}')
"
```

---

## 📝 Summary

✅ **Login page updated** - shows role-specific instructions
✅ **Coordinator account exists** - ganesh can login now
✅ **Management command added** - easy account creation
✅ **Documentation complete** - guides for admins and coordinators
✅ **Dashboard ready** - coordinators see what they need to do

**Everything is ready to use!**

---

**Last Updated**: April 28, 2026
**Status**: ✅ Production Ready
