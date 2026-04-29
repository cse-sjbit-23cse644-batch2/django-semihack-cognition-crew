#!/usr/bin/env python
"""
Dashboard Setup & Integration Guide

Quick reference for integrating and using the new dashboard system.
"""

# =====================================================
# INSTALLATION & SETUP
# =====================================================

"""
Step 1: Verify Django Installation
--------------------------------------
Ensure your Django project is set up with:
- Python 3.8+
- Django 4.2+
- All required apps installed in INSTALLED_APPS

Step 2: Files Already Generated
--------------------------------------
✓ templates/dashboards/admin_dashboard.html
✓ templates/dashboards/guide_dashboard.html
✓ templates/dashboards/student_dashboard.html
✓ static/js/dashboard.js
✓ dashboards/views.py (UPDATED)
✓ dashboards/urls.py (UPDATED)

Step 3: Verify Base Template Configuration
--------------------------------------
Check that templates/base.html includes:
- Tailwind CSS CDN (✓ Already included)
- Phosphor Icons (✓ Already included)
- Chart.js Library (✓ Already included)
- CSRF meta tag

Step 4: Database Models
--------------------------------------
Ensure these models exist and are migrated:
- auth_app.models.User (with 'role' field)
- projects.models.Team
- projects.models.Submission
- projects.models.Phase
- projects.models.Feedback
- projects.models.Version
- projects.models.Domain

Step 5: Static Files Collection
--------------------------------------
Run:
    python manage.py collectstatic --noinput

Step 6: Test the Dashboard
--------------------------------------
Start development server:
    python manage.py runserver

Navigate to:
    http://localhost:8000/dashboard/

Depending on your user role, you'll see:
- Admin: Admin Dashboard
- Guide: Guide Dashboard
- Student: Student Dashboard
"""

# =====================================================
# VIEW EXAMPLES & USAGE
# =====================================================

# Example 1: Using the Admin Dashboard View
"""
from dashboards.views import admin_dashboard
from django.test import RequestFactory

# Create a test request
factory = RequestFactory()
request = factory.get('/dashboard/admin/')
request.user = admin_user  # Your admin user

# Call the view
response = admin_dashboard(request)
# Returns HttpResponse with admin_dashboard.html rendered
"""

# Example 2: Custom Context Data
"""
# In dashboards/views.py, you can add custom context:

@login_required
def admin_dashboard(request):
    # ... existing code ...
    
    # Add custom metrics
    context['custom_metric'] = calculate_custom_value()
    
    return render(request, 'dashboards/admin_dashboard.html', context)
"""

# Example 3: Using AJAX in Templates
"""
In your template:

<!-- Call JavaScript function -->
<button onclick="checkSimilarity(projectId1, projectId2)">
    Check Similarity
</button>

<!-- Show result -->
<script>
checkSimilarity(projectId1, projectId2)
    .then(result => {
        console.log('Similarity:', result.similarity_score);
        if (result.is_flagged) {
            showNotification('High similarity detected!', 'warning');
        }
    });
</script>
"""

# =====================================================
# TEMPLATE CUSTOMIZATION EXAMPLES
# =====================================================

# Example 1: Adding New KPI Card
"""
<!-- In admin_dashboard.html, add after existing KPI cards -->
<div class="stat-card bg-white rounded-lg shadow-sm border border-slate-200 p-6">
    <div class="flex items-start justify-between">
        <div>
            <p class="text-sm font-medium text-slate-600">Your Metric</p>
            <p class="text-3xl font-bold text-slate-900 mt-2">{{ your_value }}</p>
        </div>
        <div class="bg-custom-100 p-3 rounded-lg">
            <i class="ph ph-icon-name text-custom-600 text-2xl"></i>
        </div>
    </div>
</div>
"""

# Example 2: Adding New Chart
"""
<!-- In template, add canvas -->
<div class="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
    <h2 class="text-lg font-semibold mb-4">My Chart</h2>
    <div class="chart-container">
        <canvas id="myChart"></canvas>
    </div>
</div>

<!-- In dashboard.js, add function -->
function initMyChart() {
    const ctx = document.getElementById('myChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar'],
            datasets: [{
                label: 'Data',
                data: [10, 20, 15],
                borderColor: '#3b82f6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

<!-- Then call in DOMContentLoaded event -->
document.addEventListener('DOMContentLoaded', function() {
    // ... other inits ...
    initMyChart();
});
"""

# Example 3: Dynamic Data with Django Loop
"""
<!-- Render actual database data instead of sample data -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {% for team in assigned_teams %}
    <div class="team-card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold">{{ team.name }}</h3>
        <p class="text-sm text-slate-600">{{ team.title }}</p>
        
        <!-- Progress bar with real data -->
        <div class="mt-4">
            <div class="progress-bar">
                <div class="progress-fill" 
                     data-progress="{{ team.completion_percentage }}">
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
"""

# =====================================================
# JAVASCRIPT INTEGRATION EXAMPLES
# =====================================================

# Example 1: AJAX Form Submission
"""
<!-- HTML Form -->
<form id="reviewForm">
    <textarea name="feedback" placeholder="Enter feedback"></textarea>
    <button type="button" onclick="submitReview()">Submit</button>
</form>

<!-- JavaScript -->
<script>
function submitReview() {
    const feedback = document.querySelector('textarea[name="feedback"]').value;
    
    submitFeedbackResponse(feedbackId, feedback)
        .then(response => {
            showNotification('Feedback submitted!', 'success');
            // Refresh page or update DOM
            location.reload();
        })
        .catch(error => {
            showNotification('Error: ' + error.message, 'error');
        });
}
</script>
"""

# Example 2: Real-time Search
"""
<!-- HTML -->
<input 
    type="text" 
    placeholder="Search teams..." 
    id="searchInput"
    onkeyup="searchTeams()"
>

<!-- JavaScript -->
<script>
function searchTeams() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const teamCards = document.querySelectorAll('.team-card');
    
    teamCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// Or use debounce for better performance:
document.getElementById('searchInput').addEventListener('input', 
    debounce(searchTeams, 300)
);
</script>
"""

# Example 3: Status Badge Coloring
"""
<!-- HTML -->
<span class="status-badge" data-status="{{ submission.status }}">
    {{ submission.get_status_display }}
</span>

<!-- JavaScript auto-styles based on status -->
<!-- This is handled by initStatusBadges() in dashboard.js -->
"""

# =====================================================
# STYLING CUSTOMIZATION
# =====================================================

# Example 1: Custom Color Theme
"""
To change the primary color theme:

1. Update Tailwind config in base.html
2. Change primary color from blue to your preference:

tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    500: '#your-color', // Change this
                    600: '#your-color-600',
                    // ...
                }
            }
        }
    }
}

3. Update status colors in CSS:

.status-approved { background-color: #your-color-light; }
.status-pending { background-color: #your-color-lighter; }
"""

# Example 2: Custom Card Style
"""
<!-- Add custom class to card -->
<div class="stat-card custom-gradient bg-white rounded-lg shadow-sm p-6">
    <!-- content -->
</div>

<!-- Add to static/css/style.css -->
.custom-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.custom-gradient h3 {
    color: white;
}
"""

# =====================================================
# API ENDPOINT EXAMPLES
# =====================================================

"""
The dashboard expects these API endpoints to exist:

POST /api/validate-title/
    Request: { title, team_id }
    Response: { valid: true/false }

POST /api/check-similarity/
    Request: { project1_id, project2_id }
    Response: { similarity_score: 0-100, is_flagged: true/false }

POST /api/feedback/respond/
    Request: { feedback_id, response }
    Response: { success: true/false, message: '...' }

POST /api/feedback/resolve/
    Request: { feedback_id, resolved: true }
    Response: { success: true/false }

POST /api/submissions/upload/
    Request: FormData { submission_id, file, change_summary }
    Response: { success: true/false, version_id: ... }

Create these endpoints in your API app:
"""

# =====================================================
# DJANGO TEMPLATE TAG EXAMPLES
# =====================================================

# Example 1: Using Custom Template Tags
"""
<!-- In template -->
{% load dashboard_tags %}

<!-- If you create custom filters -->
{{ project.completion_percentage|percentage_color }}

<!-- Create in templatetags/dashboard_tags.py -->
from django import template

register = template.Library()

@register.filter
def percentage_color(value):
    if value >= 80:
        return 'green'
    elif value >= 50:
        return 'amber'
    else:
        return 'red'
"""

# Example 2: Using Built-in Filters
"""
<!-- Format dates -->
{{ project.created_at|date:"M d, Y" }}

<!-- Default values -->
{{ user.full_name|default:"Anonymous" }}

<!-- Truncate text -->
{{ project.description|truncatewords:20 }}
"""

# =====================================================
# PERFORMANCE TIPS
# =====================================================

"""
1. Database Query Optimization:
   - Use select_related() for ForeignKey
   - Use prefetch_related() for ManyToMany
   
   Example:
   projects = Team.objects.select_related('guide', 'domain')\
                          .prefetch_related('members')\
                          .all()

2. Template Caching:
   {% load cache %}
   {% cache 500 dashboard_cache %}
       <!-- Expensive content here -->
   {% endcache %}

3. Lazy Load Charts:
   - Charts only initialize when in viewport
   - Use IntersectionObserver for optimal performance

4. CSS Classes vs Inline Styles:
   - Use Tailwind classes instead of inline styles
   - Browser can cache class-based styling better

5. Minify Static Assets:
   - Run collectstatic in production
   - Use CDN for third-party libraries
"""

# =====================================================
# TROUBLESHOOTING
# =====================================================

"""
Issue: Charts not showing
Solution:
  - Check Chart.js is loaded before dashboard.js
  - Verify canvas elements exist in HTML
  - Check browser console for errors
  - Ensure Chart is globally available

Issue: AJAX calls failing
Solution:
  - Verify CSRF token is in response headers
  - Check endpoint URLs are correct
  - Look for CORS issues
  - Check API endpoints exist

Issue: Styling looks broken
Solution:
  - Clear browser cache (Ctrl+Shift+Del)
  - Verify Tailwind CDN is loaded
  - Check for CSS conflicts
  - Use browser DevTools to inspect elements

Issue: Mobile layout looks wrong
Solution:
  - Check viewport meta tag in base.html
  - Test in responsive design mode (F12)
  - Verify grid breakpoints (md:, lg:)
  - Check for fixed widths instead of responsive

Issue: Slow performance
Solution:
  - Reduce number of queries (N+1 problem)
  - Implement database indexing
  - Cache frequently accessed data
  - Lazy load charts and images
  - Use CDN for static files
"""

# =====================================================
# PRODUCTION CHECKLIST
# =====================================================

"""
Before deploying to production:

□ Security
  □ Set DEBUG = False
  □ Update SECRET_KEY
  □ Set ALLOWED_HOSTS correctly
  □ Enable CSRF protection
  □ Use HTTPS only

□ Performance
  □ Run collectstatic
  □ Enable caching headers
  □ Minify CSS/JS
  □ Optimize database queries
  □ Use CDN for static files

□ Testing
  □ Test all three dashboards
  □ Check responsive design on mobile
  □ Test AJAX endpoints
  □ Verify charts render correctly
  □ Test with different user roles

□ Monitoring
  □ Set up error logging
  □ Monitor database performance
  □ Track user engagement
  □ Monitor page load times

□ Documentation
  □ Update API documentation
  □ Document custom endpoints
  □ Create user guides
  □ Document deployment process
"""

# =====================================================
# QUICK START CHECKLIST
# =====================================================

"""
✓ 1. Files Created:
     - admin_dashboard.html
     - guide_dashboard.html
     - student_dashboard.html
     - static/js/dashboard.js
     - Updated views.py
     - Updated urls.py

✓ 2. Go to /dashboard/ in your browser
     (Will auto-route based on user role)

✓ 3. Test with different user roles:
     - Admin user → Admin Dashboard
     - Guide user → Guide Dashboard
     - Student user → Student Dashboard

✓ 4. Customize with your actual data:
     - Update views.py to query your models
     - Replace sample data with real data
     - Add your own metrics and charts

✓ 5. Configure API endpoints:
     - Create endpoints for AJAX calls
     - Test AJAX functionality
     - Add error handling

✓ 6. Deploy to production:
     - Run migrations
     - Collect static files
     - Configure web server
     - Set up SSL certificate
"""

if __name__ == "__main__":
    print(__doc__)
