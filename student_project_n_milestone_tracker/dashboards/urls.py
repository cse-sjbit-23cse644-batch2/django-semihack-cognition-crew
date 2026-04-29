from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard - routes to role-specific dashboard
    path('', views.dashboard_overview, name='dashboard'),
    
    # Role-specific dashboards
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('guide/', views.guide_dashboard, name='guide_dashboard'),
    path('coordinator/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('admin/export/', views.admin_export_page, name='admin_export'),
    
    # Legacy/Additional routes
    path('my-team/', views.my_team, name='my_team'),
    path('submissions/', views.team_submissions, name='submissions'),
    path('assigned-teams/', views.assigned_teams, name='assigned_teams'),
    path('export-teams/', views.export_teams_csv, name='export_teams_csv'),
    path('reviews/', views.pending_reviews, name='reviews'),
    path('timeline/<int:submission_id>/', views.submission_timeline, name='submission_timeline'),
]
