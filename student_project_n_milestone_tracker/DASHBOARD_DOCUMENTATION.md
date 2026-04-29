# 🎓 MilestoneTrack Dashboard System

A production-quality, hackathon-winning dashboard system for the Intelligent Student Project & Milestone Tracker. Built with Django Templates, Tailwind CSS, and Chart.js.

---

## 📋 Overview

The dashboard system consists of **three role-based dashboards** designed for different user types in a capstone project management system:

1. **Admin Dashboard** - System-wide analytics and project oversight
2. **Guide Dashboard** - Team management and submission reviews  
3. **Student Dashboard** - Personal project tracking and feedback management

---

## 🎯 Key Features

### Universal Features (All Dashboards)
- ✨ Clean, modern, card-based layout
- 📱 Fully responsive (mobile, tablet, desktop)
- 🎨 Tailwind CSS styling with custom Phosphor icons
- ⚡ Smooth animations and transitions
- 🔔 Toast notification system
- 🎭 Interactive components with keyboard shortcuts
- 📊 Real-time chart visualization with Chart.js

### Admin Dashboard Features
- **KPI Cards**: Total projects, completion rate, delayed projects, active submissions
- **Charts**: 
  - Phase-wise completion bar chart
  - Domain distribution pie chart
  - Submission trends line chart
- **Alert Panel**: High-priority issues, deadline warnings, system notifications
- **Projects Table**: Searchable/filterable project listing with status indicators

### Guide Dashboard Features
- **Team Cards**: Assigned teams with progress bars and status
- **Stats Overview**: Approved, in-review, rejected, and pending submissions
- **Alert Banner**: Pending reviews that need attention
- **Team Management**: Quick actions to view teams and review submissions
- **Activity Feed**: Recent review actions and team updates

### Student Dashboard Features
- **Project Summary**: Title, domain, guide, completion percentage
- **Milestone Timeline**: Visual timeline of phases with completion status
  - Locked/unlocked states
  - Progress indicators for active phases
  - Visual differentiation (completed, active, locked)
- **Feedback Panel**: Latest guide feedback with resolution status
- **Team Members**: View team composition
- **Submission History**: Complete version history with timestamps

---

## 🗂️ File Structure

```
templates/
├── dashboards/
│   ├── admin_dashboard.html      # Admin system overview
│   ├── guide_dashboard.html      # Guide team management
│   └── student_dashboard.html    # Student project tracking

static/
├── js/
│   └── dashboard.js              # All interactive features & Charts
└── css/
    └── style.css                 # Custom styles (if needed)
```

---

## 🚀 How to Use

### Access the Dashboards

The main dashboard route (`/dashboard/`) automatically routes users to their role-specific dashboard:

```python
# Django URL pattern
path('', views.dashboard_overview, name='dashboard')

# Routes:
/dashboard/          # Auto-routes based on user.role
/dashboard/admin/    # Direct admin access
/dashboard/guide/    # Direct guide access
/dashboard/student/  # Direct student access
```

### User Roles

The system recognizes three user roles:

```python
ROLE_CHOICES = [
    ('ADMIN', 'Administrator'),      # Full system access
    ('GUIDE', 'Guide/Teacher'),      # Team & submission management
    ('STUDENT', 'Student'),          # Personal project tracking
]
```

---

## 🎨 Design System

### Color Coding

**Status Indicators:**
- 🟢 **Green** (`#10b981`) - Approved / Completed
- 🟡 **Yellow/Amber** (`#f59e0b`) - Pending / In Review
- 🔴 **Red** (`#ef4444`) - Blocked / Delayed / Critical
- 🔵 **Blue** (`#3b82f6`) - Active / In Progress
- ⚫ **Gray** (`#6b7280`) - Neutral / Disabled

**Component Colors:**
- Primary: Blue (`#3b82f6`)
- Success: Green (`#10b981`)
- Warning: Amber (`#f59e0b`)
- Error: Red (`#ef4444`)

### Typography

- **Headings**: Outfit font family (bold, tracking)
- **Body**: Inter font family (clean, readable)
- **Font Sizes**: 
  - Titles: 2xl-4xl (24px-36px)
  - Subheadings: lg-xl (18px-20px)
  - Body: sm-base (12px-16px)

### Spacing

- Card padding: 1.5rem (24px)
- Section margins: 2rem (32px)
- Component gap: 0.5rem-1rem (8px-16px)

---

## 📊 Chart.js Integration

The dashboard uses Chart.js for beautiful, responsive charts. Initialize charts on page load:

```javascript
// Auto-initializes on DOM load
document.addEventListener('DOMContentLoaded', function() {
    initPhaseChart();      // Bar chart - phase progress
    initDomainChart();     // Pie chart - domain distribution
    initTrendChart();      // Line chart - submission trends
});
```

### Chart Configuration

All charts are:
- Responsive and maintain aspect ratio
- Styled with custom colors
- Smooth animations
- Hover interactions
- Legend support

---

## 🔗 AJAX Functionality

### Making API Calls

```javascript
// Generic AJAX request
makeAjaxRequest('/api/endpoint/', 'POST', {
    data: 'value'
}).then(response => {
    console.log(response);
});
```

### Available Functions

```javascript
// Validate project title
validateProjectTitle('title', teamId)
    .then(isValid => { ... });

// Check similarity between projects
checkSimilarity(projectId1, projectId2)
    .then(result => { ... });

// Submit feedback response
submitFeedbackResponse(feedbackId, responseText)
    .then(response => { ... });

// Upload submission version
uploadSubmissionVersion(submissionId, fileInput, changeSummary)
    .then(response => { ... });

// Mark feedback as resolved
markFeedbackResolved(feedbackId)
    .then(response => { ... });
```

---

## 🎯 Keyboard Shortcuts

Power users can leverage these keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + S` | Save (prevents browser save) |
| `Cmd/Ctrl + K` | Open command palette (future) |
| `Esc` | Close any open modals |

---

## 🔧 Customization

### Adding New Charts

```javascript
function initCustomChart() {
    const ctx = document.getElementById('customChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar', // or 'line', 'pie', etc.
        data: {
            labels: ['Jan', 'Feb', 'Mar'],
            datasets: [{
                label: 'Data',
                data: [10, 20, 15],
                backgroundColor: '#3b82f6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
```

### Modifying Status Colors

Edit the status badge styles in respective template:

```html
<span class="status-badge status-approved">
    <i class="ph ph-check"></i> Approved
</span>
```

CSS classes in templates control colors:
```css
.status-approved { background-color: #dcfce7; color: #166534; }
.status-pending { background-color: #fef3c7; color: #92400e; }
.status-blocked { background-color: #fee2e2; color: #991b1b; }
```

---

## 📱 Responsive Breakpoints

The dashboards use Tailwind CSS breakpoints:

| Breakpoint | Width | Devices |
|------------|-------|---------|
| `sm` | 640px | Small phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Desktops |
| `xl` | 1280px | Large screens |
| `2xl` | 1536px | Extra large |

Grid layouts automatically adjust:
```html
<!-- 1 column on mobile, 2 on tablet, 4 on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
```

---

## 🎭 Interactive Components

### Modals

```html
<!-- Trigger button -->
<button data-modal-trigger="myModal">Open Modal</button>

<!-- Modal -->
<div id="myModal" data-modal class="hidden">
    <button data-modal-close>Close</button>
</div>
```

### Dropdowns

```html
<!-- Trigger -->
<button data-dropdown-trigger>Menu</button>

<!-- Menu -->
<div class="dropdown-menu hidden">
    <a href="#">Option 1</a>
    <a href="#">Option 2</a>
</div>
```

### Progress Bars

```html
<div class="w-full bg-blue-100 rounded-full h-2">
    <div class="bg-blue-600 h-2 rounded-full" 
         style="width: 75%"></div>
</div>
```

---

## 🔐 Security

### CSRF Protection

All AJAX requests automatically include CSRF token:

```javascript
headers: {
    'X-CSRFToken': getCookie('csrftoken')
}
```

### Permission Checks

Views enforce role-based access control:

```python
@login_required
def guide_dashboard(request):
    if request.user.role != 'GUIDE':
        return redirect('dashboard')
    # ...
```

---

## 🧪 Testing the Dashboards

### With Sample Data

Each dashboard includes sample/dummy data in fallback blocks:

```html
{% for project in projects|default:sample_projects %}
    <!-- Renders sample data if no projects exist -->
{% empty %}
    <!-- Sample project cards here -->
{% endfor %}
```

### Database Requirements

Ensure your database has:

```python
# Required models
- User (with role field)
- Team (projects)
- Submission (with status)
- Phase (timeline stages)
- Feedback (guide comments)
- Version (submission history)
```

---

## 📈 Performance Optimizations

- **Query Optimization**: Use `select_related()` and `prefetch_related()`
- **Lazy Loading**: Charts load only when in view
- **Debouncing**: Search input uses debounce (300ms delay)
- **Caching**: Static assets are cached by browser
- **Minification**: All CSS/JS is production-ready

---

## 🚨 Common Issues & Solutions

### Charts Not Rendering
- Ensure Chart.js library is loaded before `dashboard.js`
- Check that canvas elements have IDs matching function calls
- Verify `data-progress` values are valid percentages

### AJAX Calls Failing
- Check CSRF token is properly extracted
- Verify endpoint URLs in your `urls.py`
- Check console for error messages

### Styling Issues
- Ensure Tailwind CSS CDN is in base.html
- Check browser console for CSS warnings
- Clear browser cache if styles don't update

### Responsive Layout Broken
- Verify viewport meta tag in base.html
- Check Tailwind breakpoints are correct
- Test in responsive design mode (F12)

---

## 🎓 Development Guidelines

### Adding New Metrics

1. Calculate in the view
2. Pass to context
3. Display in template with fallback

```python
# In view
context['metric_name'] = calculated_value

# In template
{{ metric_name|default:0 }}
```

### Extending with New Charts

1. Create canvas element
2. Write init function
3. Call in DOMContentLoaded event

### Custom Styling

Add to `static/css/style.css` or inline in template:

```css
.custom-component {
    /* Your styles */
}
```

---

## 📚 Resources

- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Chart.js Documentation](https://www.chartjs.org)
- [Phosphor Icons](https://phosphoricons.com)
- [Django Templates](https://docs.djangoproject.com/en/stable/topics/templates/)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

## 🎯 Future Enhancements

- [ ] Real-time updates with WebSockets
- [ ] Export dashboards to PDF
- [ ] Custom dashboard widgets
- [ ] Advanced filtering and search
- [ ] Data analytics and predictions
- [ ] Mobile app integration
- [ ] Dark mode support
- [ ] Accessibility improvements (WCAG 2.1)

---

## 📄 License

This dashboard system is part of the MilestoneTrack project. Built with ❤️ for capstone project management.

---

## 👨‍💻 Technical Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 4.2+ |
| Frontend | Django Templates |
| Styling | Tailwind CSS v3 |
| Charts | Chart.js v3 |
| Icons | Phosphor Icons v1 |
| JavaScript | Vanilla JS (ES6+) |
| HTTP | AJAX/Fetch API |
| Database | PostgreSQL/SQLite |

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✨
