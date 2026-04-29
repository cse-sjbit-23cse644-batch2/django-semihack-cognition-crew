from django.urls import path
from . import views
from . import api

app_name = 'projects'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Project Management
    path('', views.ProjectListView.as_view(), name='project-list'),
    path('create/', views.ProjectCreateView.as_view(), name='project-create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project-edit'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),

    # Team Management
    path('<int:project_id>/add-member/', views.add_team_member, name='add-team-member'),
    path('<int:project_id>/remove-member/<int:member_id>/', views.remove_team_member, name='remove-team-member'),

    # Submission Management
    path('<int:project_id>/create-submission/', views.create_submission, name='create-submission'),
    path('submissions/<int:submission_id>/', views.submission_detail, name='submission-detail'),
    path('submissions/<int:submission_id>/upload/', views.upload_version, name='upload-version'),
    path('submissions/<int:submission_id>/submit/', views.submit_for_review, name='submit-for-review'),
    path('submissions/<int:submission_id>/approve/', views.approve_submission, name='approve-submission'),

    # Feedback Management
    path('submissions/<int:submission_id>/feedback/', views.add_feedback, name='add-feedback'),
    path('feedback/<int:feedback_id>/resolve/', views.resolve_feedback, name='resolve-feedback'),

    # API endpoints
    path('api/check-title/', api.check_project_title, name='api-check-title'),
    path('api/project/<int:project_id>/status/', api.get_project_status, name='api-project-status'),
    path('api/guides/', api.get_guides_list, name='api-guides'),
    path('api/coordinators/', api.get_coordinators_list, name='api-coordinators'),
    path('api/students/', api.get_students_list, name='api-students'),
    path('api/search/', api.search_projects, name='api-search'),
    path('api/submissions/<int:submission_id>/<str:action>/', api.submission_action, name='api-submission-action'),

    # AJAX endpoints
    path('<int:project_id>/phases/', views.get_project_phases, name='get-project-phases'),
    path('submissions/<int:submission_id>/status/', views.get_submission_status, name='get-submission-status'),

    # User Management (Admin)
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/create/', views.StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student-edit'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),

    path('guides/', views.GuideListView.as_view(), name='guide-list'),
    path('guides/create/', views.GuideCreateView.as_view(), name='guide-create'),
    path('guides/<int:pk>/edit/', views.GuideUpdateView.as_view(), name='guide-edit'),
    path('guides/<int:pk>/delete/', views.GuideDeleteView.as_view(), name='guide-delete'),

    path('coordinators/', views.CoordinatorListView.as_view(), name='coordinator-list'),
    path('coordinators/create/', views.CoordinatorCreateView.as_view(), name='coordinator-create'),
    path('coordinators/<int:pk>/edit/', views.CoordinatorUpdateView.as_view(), name='coordinator-edit'),
    path('coordinators/<int:pk>/delete/', views.CoordinatorDeleteView.as_view(), name='coordinator-delete'),

    # Guide Allotment
    path('allot-guide/', views.allot_guide, name='allot-guide'),

    # Evaluation
    path('submissions/<int:submission_id>/evaluate/', views.evaluate_submission, name='evaluate-submission'),

    # Coordinator Approval
    path('<int:project_id>/coordinator-approve/', views.coordinator_approve, name='coordinator-approve'),

    # CSV Export
    path('export/', views.export_projects_csv, name='export-csv'),
]

