"""
JSON API endpoints for AJAX calls
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from projects.models import Project, Submission, TeamMember, Phase
from auth_app.models import User


@require_http_methods(["GET"])
@login_required
def check_project_title(request):
    """AJAX endpoint to check if project title is unique (case-insensitive)"""
    title = request.GET.get('title', '').strip()
    project_id = request.GET.get('project_id')  # For edit views

    if not title:
        return JsonResponse({
            'available': False,
            'message': 'Project title cannot be empty'
        })

    # Check for case-insensitive duplicate
    queryset = Project.objects.filter(title__iexact=title)
    
    if project_id:
        # Exclude current project when editing
        queryset = queryset.exclude(pk=project_id)

    exists = queryset.exists()

    return JsonResponse({
        'available': not exists,
        'message': 'Title already in use' if exists else 'Title is available'
    })


@require_http_methods(["GET"])
@login_required
def get_project_status(request, project_id):
    """Get current project status and progress"""
    project = get_object_or_404(Project, pk=project_id)

    # Check access
    user = request.user
    can_access = (
        user.is_admin() or
        (user.is_guide() and project.guide == user) or
        (user.is_coordinator() and project.coordinator == user) or
        (user.is_student() and project.team_members.filter(user=user).exists())
    )

    if not can_access:
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Get submission statuses
    submissions = project.submissions.all()
    submission_data = []
    
    for submission in submissions:
        submission_data.append({
            'phase': submission.phase.name,
            'status': submission.status,
            'versions': submission.versions.count(),
            'feedback_count': submission.feedback.count(),
        })

    return JsonResponse({
        'project': {
            'id': project.pk,
            'title': project.title,
            'status': project.status,
            'completion': project.get_completion_percentage(),
        },
        'submissions': submission_data,
        'team_size': project.team_members.count(),
    })


@require_http_methods(["GET"])
@login_required
def get_guides_list(request):
    """Get list of available guides for dropdown"""
    guides = User.objects.filter(role='GUIDE').values('id', 'first_name', 'last_name', 'email')
    return JsonResponse({
        'guides': list(guides)
    })


@require_http_methods(["GET"])
@login_required
def get_coordinators_list(request):
    """Get list of available coordinators for dropdown"""
    coordinators = User.objects.filter(role='COORDINATOR').values('id', 'first_name', 'last_name', 'email')
    return JsonResponse({
        'coordinators': list(coordinators)
    })


@require_http_methods(["GET"])
@login_required
def get_students_list(request):
    """Get list of available students"""
    students = User.objects.filter(role='STUDENT').values('id', 'first_name', 'last_name', 'email')
    return JsonResponse({
        'students': list(students)
    })


@require_http_methods(["GET"])
@login_required
def search_projects(request):
    """Search projects with filters"""
    query = request.GET.get('q', '').strip()
    domain = request.GET.get('domain')
    guide = request.GET.get('guide')
    status = request.GET.get('status')
    
    user = request.user
    projects = Project.objects.select_related('domain', 'guide')

    # Role-based filtering
    if user.is_guide():
        projects = projects.filter(guide=user)
    elif user.is_coordinator():
        projects = projects.filter(coordinator=user)
    elif user.is_student():
        projects = projects.filter(team_members__user=user)

    # Apply search and filters
    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(domain__name__icontains=query)
        )
    
    if domain:
        projects = projects.filter(domain_id=domain)
    
    if guide:
        projects = projects.filter(guide_id=guide)
    
    if status:
        projects = projects.filter(status=status)

    results = projects.values('id', 'title', 'domain__name', 'guide__first_name', 'guide__last_name', 'status')[:10]

    return JsonResponse({
        'results': list(results),
        'count': projects.count()
    })


@require_http_methods(["POST"])
@login_required
def submission_action(request, submission_id, action):
    """Handle submission actions (approve, reject, submit)"""
    submission = get_object_or_404(Submission, pk=submission_id)
    user = request.user

    # Check permissions
    if action == 'approve':
        if not (user.is_guide() or user.is_admin()):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        if user.is_guide() and submission.project.guide != user:
            return JsonResponse({'error': 'Not the assigned guide'}, status=403)
        
        submission.approve(user)
        return JsonResponse({
            'success': True,
            'status': submission.status,
            'message': f'Submission approved!'
        })

    elif action == 'reject':
        if not (user.is_guide() or user.is_admin()):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        if user.is_guide() and submission.project.guide != user:
            return JsonResponse({'error': 'Not the assigned guide'}, status=403)
        
        submission.reject(user)
        return JsonResponse({
            'success': True,
            'status': submission.status,
            'message': f'Submission rejected'
        })

    elif action == 'submit':
        if not (user.is_admin() or (user.is_student() and submission.project.team_members.filter(user=user).exists())):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        if submission.status == 'DRAFT':
            submission.submit(user)
            return JsonResponse({
                'success': True,
                'status': submission.status,
                'message': 'Submission submitted for review'
            })
        return JsonResponse({
            'error': 'Cannot submit at this time'
        }, status=400)

    return JsonResponse({'error': 'Invalid action'}, status=400)
