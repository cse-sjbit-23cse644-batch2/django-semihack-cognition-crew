"""
URL configuration for capstone_tracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.shortcuts import redirect
from django.conf.urls.static import static

from projects import views as project_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth & OAuth2
    path('auth/', include('auth_app.urls')),
    # path('accounts/', include('allauth.urls')),
    
    # API endpoints (legacy/current)
    path('api/projects/', include('projects.urls')),
    path('api/similarity/', include('similarity.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # Frontend Pages
    path('dashboard/', include('dashboards.urls')),

    # Admin user management and workflow routes
    path('students/', project_views.StudentListView.as_view(), name='student-list'),
    path('students/create/', project_views.StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/edit/', project_views.StudentUpdateView.as_view(), name='student-edit'),
    path('students/<int:pk>/delete/', project_views.StudentDeleteView.as_view(), name='student-delete'),
    path('guides/', project_views.GuideListView.as_view(), name='guide-list'),
    path('guides/create/', project_views.GuideCreateView.as_view(), name='guide-create'),
    path('guides/<int:pk>/edit/', project_views.GuideUpdateView.as_view(), name='guide-edit'),
    path('guides/<int:pk>/delete/', project_views.GuideDeleteView.as_view(), name='guide-delete'),
    path('coordinators/', project_views.CoordinatorListView.as_view(), name='coordinator-list'),
    path('coordinators/create/', project_views.CoordinatorCreateView.as_view(), name='coordinator-create'),
    path('coordinators/<int:pk>/edit/', project_views.CoordinatorUpdateView.as_view(), name='coordinator-edit'),
    path('coordinators/<int:pk>/delete/', project_views.CoordinatorDeleteView.as_view(), name='coordinator-delete'),
    path('allot-guide/', project_views.allot_guide, name='allot-guide'),
    path('export/', project_views.export_projects_csv, name='export-csv'),
    
    # Root redirect
    path('', lambda request: redirect('dashboard'), name='root'),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

