from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, F
from django.db.models.functions import TruncDay
from projects.models import Project, Submission, Version, Feedback, Phase, Evaluation, Domain
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta
import json

@login_required
def dashboard_overview(request):
    """Main overview dashboard - routes to role-specific dashboards"""
    user = request.user
    
    # Route to appropriate dashboard based on user role
    if user.role == 'ADMIN':
        return admin_dashboard(request)
    elif user.role == 'GUIDE':
        return guide_dashboard(request)
    elif user.role == 'COORDINATOR':
        return coordinator_dashboard(request)
    elif user.role == 'STUDENT':
        return student_dashboard(request)
    else:
        return redirect('login_page')


@login_required
def admin_dashboard(request):
    """Admin Dashboard - System-wide analytics and project management"""
    
    # KPIs
    total_projects = Project.objects.count()
    completed_projects = Project.objects.filter(status='COMPLETED').count()
    completion_rate = int((completed_projects / total_projects * 100) if total_projects > 0 else 0)
    delayed_projects = Project.objects.filter(
        status='ACTIVE',
        updated_at__lte=timezone.now() - timedelta(days=45)
    ).count()
    under_review = Submission.objects.filter(status='UNDER_REVIEW').count()
    new_projects_last_30_days = Project.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()

    # Project table data
    projects = list(
        Project.objects.select_related('guide', 'domain')
        .prefetch_related('team_members', 'submissions__phase')
        .order_by('-created_at')[:20]
    )

    for project in projects:
        project.team_count = project.team_members.count()
        project.guide_name = project.guide.get_full_name() if project.guide else 'Unassigned'
        project.current_phase = project.get_current_phase()
        project.status_class = 'approved' if project.status == 'COMPLETED' else 'pending' if project.status == 'ACTIVE' else 'blocked'

    # Chart data
    domain_counts = Project.objects.values('domain__name').annotate(count=Count('id')).order_by('-count')
    phase_counts = Submission.objects.values('phase__name').annotate(count=Count('id')).order_by('phase__name')
    trend_data = (
        Project.objects.filter(created_at__gte=timezone.now() - timedelta(days=56))
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    phase_labels = [item['phase__name'] for item in phase_counts]
    phase_values = [item['count'] for item in phase_counts]
    domain_labels = [item['domain__name'] for item in domain_counts]
    domain_values = [item['count'] for item in domain_counts]
    trend_labels = [item['day'].strftime('%b %d') for item in trend_data]
    trend_values = [item['count'] for item in trend_data]

    # Quick insights
    reviewed_submissions = Submission.objects.filter(status__in=['APPROVED', 'REJECTED'], submitted_at__isnull=False)
    review_count = reviewed_submissions.count()
    approved_submissions = Submission.objects.filter(status='APPROVED', submitted_at__isnull=False)
    approved_count = approved_submissions.count()
    avg_review_time = 0
    if approved_count > 0:
        durations = [
            (submission.approved_at - submission.submitted_at).total_seconds() / 86400
            for submission in approved_submissions
            if submission.approved_at and submission.submitted_at
        ]
        if durations:
            avg_review_time = round(sum(durations) / len(durations), 1)

    guides_efficiency = int((approved_count / review_count * 100) if review_count > 0 else 0)
    most_active_domain = domain_counts[0]['domain__name'] if domain_counts else 'N/A'
    most_active_domain_count = domain_counts[0]['count'] if domain_counts else 0

    alerts = []
    if delayed_projects > 0:
        alerts.append({
            'level': 'high',
            'title': f'{delayed_projects} delayed active projects',
            'message': 'These teams have not updated in over 45 days. Review their progress and guide assignments.'
        })
    if under_review > 0:
        alerts.append({
            'level': 'medium',
            'title': f'{under_review} submissions currently under review',
            'message': 'Keep the review queue moving to avoid delays in team progress.'
        })
    alerts.append({
        'level': 'low',
        'title': f'Most active domain: {most_active_domain}',
        'message': f'{most_active_domain_count} projects are currently in {most_active_domain}.'
    })

    context = {
        'role': request.user.role,
        'total_projects': total_projects,
        'completion_rate': completion_rate,
        'delayed_projects': delayed_projects,
        'under_review': under_review,
        'new_projects_last_30_days': new_projects_last_30_days,
        'projects': projects,
        'alerts': alerts,
        'avg_review_time': avg_review_time,
        'most_active_domain': most_active_domain,
        'most_active_domain_count': most_active_domain_count,
        'guides_efficiency': guides_efficiency,
        'chart_phase_labels': mark_safe(json.dumps(phase_labels)),
        'chart_phase_values': mark_safe(json.dumps(phase_values)),
        'chart_domain_labels': mark_safe(json.dumps(domain_labels)),
        'chart_domain_values': mark_safe(json.dumps(domain_values)),
        'chart_trend_labels': mark_safe(json.dumps(trend_labels)),
        'chart_trend_values': mark_safe(json.dumps(trend_values)),
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def admin_export_page(request):
    """Admin export page for super admins to export filtered project CSVs."""
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    User = get_user_model()
    guides = User.objects.filter(role='GUIDE').order_by('first_name', 'last_name')
    domains = Domain.objects.order_by('name')

    publication_choices = [
        ('', 'All'),
        ('Yes', 'Published'),
        ('No', 'Not Published'),
    ] + list(Project.PUBLICATION_CHOICES)

    context = {
        'role': request.user.role,
        'guides': guides,
        'domains': domains,
        'publication_choices': publication_choices,
    }
    return render(request, 'dashboards/admin_export.html', context)


@login_required
def guide_dashboard(request):
    """Guide Dashboard - Team management and submission reviews"""
    user = request.user
    
    # Get assigned projects for this guide
    assigned_teams = Project.objects.filter(guide=user).select_related('domain', 'guide').prefetch_related('team_members__user', 'submissions__phase')
    
    # Count submissions by status
    team_ids = assigned_teams.values_list('id', flat=True)
    pending_submissions = Submission.objects.filter(project_id__in=team_ids, status='SUBMITTED').count()
    
    # Calculate stats
    approved_count = Submission.objects.filter(project_id__in=team_ids, status='APPROVED').count()
    in_review_count = Submission.objects.filter(project_id__in=team_ids, status='UNDER_REVIEW').count()
    rejected_count = Submission.objects.filter(project_id__in=team_ids, status='REJECTED').count()

    # Prepare team objects for template
    teams_data = []
    chart_team_names = []
    chart_team_progress = []
    for team in assigned_teams:
        latest_submission = team.submissions.order_by('-updated_at').first()
        last_submission_days = None
        if latest_submission and latest_submission.updated_at:
            last_submission_days = (timezone.now() - latest_submission.updated_at).days

        current_phase = team.get_current_phase()
        phase_name = current_phase.get_name_display() if current_phase else 'N/A'
        phase_key = current_phase.name.lower().replace('_', '-') if current_phase else 'unknown'
        teams_data.append({
            'id': team.id,
            'name': team.title,
            'title': team.domain.name if team.domain else 'General',
            'description': team.domain.description if team.domain and team.domain.description else 'No description available.',
            'current_phase': phase_name,
            'phase_class': f'phase-{phase_key}',
            'progress': team.get_completion_percentage(),
            'members_count': team.team_members.count(),
            'last_submission_days': f'{last_submission_days}d ago' if last_submission_days is not None else 'No submissions yet',
            'status': team.get_status_display(),
        })
        chart_team_names.append(team.title)
        chart_team_progress.append(team.get_completion_percentage())

    recent_submissions = Submission.objects.filter(project__guide=user).select_related('project', 'phase').order_by('-updated_at')[:3]
    recent_activity = []
    for submission in recent_submissions:
        if submission.status == 'APPROVED':
            title = f'{submission.project.title} - {submission.phase.get_name_display()} Approved'
            message = f'Approved {submission.updated_at.strftime("%b %d")}. Submitted by the team.'
            level = 'success'
        elif submission.status == 'UNDER_REVIEW':
            title = f'{submission.project.title} - {submission.phase.get_name_display()} Under Review'
            message = f'Submitted {submission.submitted_at.strftime("%b %d") if submission.submitted_at else "recently"}. Awaiting your review.'
            level = 'warning'
        elif submission.status == 'REJECTED':
            title = f'{submission.project.title} - {submission.phase.get_name_display()} Rejected'
            message = f'Returned on {submission.updated_at.strftime("%b %d")}. Awaiting revision.'
            level = 'danger'
        else:
            title = f'{submission.project.title} - {submission.phase.get_name_display()} {submission.get_status_display()}'
            message = f'Last update on {submission.updated_at.strftime("%b %d") if submission.updated_at else "recently"}.'
            level = 'info'

        recent_activity.append({
            'title': title,
            'message': message,
            'level': level,
        })
    
    context = {
        'role': request.user.role,
        'assigned_teams_count': assigned_teams.count(),
        'assigned_teams': teams_data,
        'chart_team_names': json.dumps(chart_team_names),
        'chart_team_progress': json.dumps(chart_team_progress),
        'pending_submissions': pending_submissions,
        'approved_count': approved_count,
        'in_review_count': in_review_count,
        'rejected_count': rejected_count,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'dashboards/guide_dashboard.html', context)


@login_required
def student_dashboard(request):
    """Student Dashboard - Personal project tracking and feedback"""
    user = request.user
    from projects.models import TeamMember
    membership = TeamMember.objects.filter(user=user).select_related('project__domain', 'project__guide').first()
    team = membership.project if membership else None
    
    context = {
        'role': request.user.role,
        'user': user,
    }
    
    if team:
        # Project information
        context['project_title'] = team.title
        context['project_description'] = team.domain.description if team.domain and team.domain.description else 'No project description available yet.'
        context['project_domain'] = team.domain.name if team.domain else 'General'
        context['guide_name'] = team.guide.get_full_name() if team.guide else 'Not Assigned'
        context['project_status'] = team.get_status_display()
        
        # Calculate progress
        submissions = team.submissions.all()
        context['project_progress'] = team.get_completion_percentage()
        
        # Feedback information
        context['feedbacks'] = Feedback.objects.filter(submission__project=team).order_by('-created_at')[:5]
        
        # Add timeline phases
        timeline_phases = []
        for phase in Phase.objects.order_by('order'):
            submission = team.submissions.filter(phase=phase).first()
            if submission:
                status = submission.get_status_display()
                completed = submission.status == 'APPROVED'
                active = submission.status in ['SUBMITTED', 'UNDER_REVIEW', 'REJECTED']
            else:
                status = 'Not Started'
                completed = False
                active = team.can_access_phase(phase)

            timeline_phases.append({
                'name': phase.get_name_display(),
                'description': phase.description or 'Complete this phase before moving to the next milestone.',
                'status': status,
                'completed': completed,
                'active': active,
                'due_date': team.created_at + timedelta(days=phase.deadline_offset_days),
                'is_current': not completed and active,
            })

        # Calculate progress ring offset (283 is approx circumference of circle with r=45)
        context['project_progress_offset'] = 283 * (1 - (context['project_progress'] / 100))
        context['current_year'] = timezone.now().year
        
        context['timeline_phases'] = timeline_phases
        context['team'] = team
        team.members_all = [m.user for m in team.team_members.select_related('user')]
        team.name = team.title
    
    return render(request, 'dashboards/student_dashboard.html', context)


@login_required
def coordinator_dashboard(request):
    """Coordinator Dashboard - Final approval and publication management"""
    user = request.user

    assigned_projects = Project.objects.filter(
        coordinator=user
    ).select_related('domain', 'guide').prefetch_related('team_members__user', 'submissions__phase').distinct()

    # Stats
    total_projects = assigned_projects.count()
    completed_projects = assigned_projects.filter(status='COMPLETED').count()
    published_projects = assigned_projects.filter(publication_status='PUBLISHED').count()

    # Recent projects needing attention
    projects_needing_attention = []
    phase_total = Phase.objects.count()
    for project in assigned_projects:
        guide_approved_count = project.submissions.filter(status='APPROVED').count()
        project.approved_count = guide_approved_count
        project.phase_total = phase_total
        project.latest_submission = project.submissions.order_by('-updated_at').first()

        if project.status == 'ACTIVE' and phase_total and guide_approved_count == phase_total:
            projects_needing_attention.append({
                'project': project,
                'status': 'Ready for Final Approval',
                'action': 'Review and Approve'
            })
    pending_approvals = len(projects_needing_attention)

    # Recent activity
    recent_activity = []
    recent_evaluations = Evaluation.objects.filter(
        evaluator=user
    ).select_related('project', 'phase').order_by('-created_at')[:5]

    for eval in recent_evaluations:
        recent_activity.append({
            'title': f'Evaluated {eval.project.title}',
            'message': f'Rated {eval.phase.get_name_display()} with {eval.rating}/5',
            'level': 'info',
        })

    context = {
        'role': user.role,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'pending_approvals': pending_approvals,
        'published_projects': published_projects,
        'projects_needing_attention': projects_needing_attention,
        'recent_activity': recent_activity,
        'assigned_projects': assigned_projects,
    }

    return render(request, 'dashboards/coordinator_dashboard.html', context)

@login_required
def my_team(request):
    if request.user.role != 'STUDENT':
        return redirect('dashboard')
    
    from projects.models import TeamMember
    membership = TeamMember.objects.filter(user=request.user).first()
    team = membership.project if membership else None
    if team:
        team.name = team.title
        team.members_all = [m.user for m in team.team_members.select_related('user')]
    return render(request, 'dashboards/my_team.html', {'team': team})

@login_required
def team_submissions(request):
    if request.user.role != 'STUDENT':
        return redirect('dashboard')
    
    from projects.models import TeamMember
    membership = TeamMember.objects.filter(user=request.user).first()
    team = membership.project if membership else None
    if not team:
        return redirect('dashboard')
        
    submissions = team.submissions.all().order_by('phase__order')
    return render(request, 'dashboards/submissions.html', {'team': team, 'submissions': submissions})

@login_required
def assigned_teams(request):
    if request.user.role != 'GUIDE':
        return redirect('dashboard')
    
    teams = Project.objects.filter(guide=request.user).select_related('domain').prefetch_related('team_members__user')
    for team in teams:
        team.name = team.title
        team.description = team.domain.description if team.domain and team.domain.description else 'No description available.'
        team.members_count = team.team_members.count()
    return render(request, 'dashboards/assigned_teams.html', {'teams': teams})

@login_required
def pending_reviews(request):
    if request.user.role != 'GUIDE':
        return redirect('dashboard')
    
    # Submissions under review for teams assigned to this guide
    teams = Project.objects.filter(guide=request.user)
    submissions = Submission.objects.filter(project__in=teams, status__in=['SUBMITTED', 'UNDER_REVIEW'])
    
    return render(request, 'dashboards/pending_reviews.html', {'submissions': submissions})

@login_required
def submission_timeline(request, submission_id):
    """The clean, clear-cut timeline view of a submission's versions and feedback"""
    submission = Submission.objects.get(id=submission_id)
    
    # Permission check
    user = request.user
    project = submission.project
    
    if user.role == 'STUDENT':
        is_member = project.team_members.filter(user=user).exists()
        if not is_member:
            return redirect('dashboard')
    if user.role == 'GUIDE' and project.guide != user:
        return redirect('dashboard')
        
    submission.team = project
    submission.team.name = project.title
        
    versions = submission.versions.all().order_by('-version_number')
    
    return render(request, 'dashboards/timeline.html', {
        'submission': submission,
        'versions': versions
    })

@login_required
def export_teams_csv(request):
    """Export assigned teams to CSV for the guide"""
    if request.user.role != 'GUIDE':
        return redirect('dashboard')
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="assigned_teams_{request.user.username}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Project Title', 'Domain', 'Members', 'Current Phase', 'Completion %', 'Status'])
    
    projects = Project.objects.filter(guide=request.user).select_related('domain').prefetch_related('team_members__user')
    
    for project in projects:
        members = ", ".join([m.user.get_full_name() or m.user.username for m in project.team_members.all()])
        current_phase = project.get_current_phase()
        writer.writerow([
            project.title,
            project.domain.name if project.domain else 'N/A',
            members,
            current_phase.get_name_display() if current_phase else 'N/A',
            project.get_completion_percentage(),
            project.get_status_display()
        ])
    
    return response
