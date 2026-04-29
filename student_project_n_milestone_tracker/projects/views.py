"""
MilestoneTrack - Project Views

Production-ready Django views for the academic project workflow system.
Implements role-based access control and workflow enforcement.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, Http404
from django.db.models import Q, Count, Prefetch
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from django.contrib.auth import get_user_model
from .models import (
    Domain, Project, TeamMember, Phase, Submission, Version, Feedback, Evaluation
)
from .forms import (
    ProjectForm, TeamMemberForm, SubmissionForm, VersionUploadForm,
    FeedbackForm, ProjectSearchForm, BulkStudentImportForm,
    StudentForm, GuideForm, CoordinatorForm, GuideAllotmentForm,
    EvaluationForm, CertificateUploadForm
)

User = get_user_model()


def ensure_default_phases():
    """Create the standard milestone phases when the database is empty."""
    defaults = [
        ('SYNOPSIS', 1, 'Submit the initial project synopsis.'),
        ('PHASE_1', 2, 'Submit the first implementation milestone.'),
        ('PHASE_2', 3, 'Submit the second implementation milestone.'),
        ('FINAL_REPORT', 4, 'Submit the final project report.'),
        ('PUBLICATION', 5, 'Submit publication and certificate details.'),
    ]
    for name, order, description in defaults:
        Phase.objects.get_or_create(
            name=name,
            defaults={
                'order': order,
                'description': description,
                'deadline_offset_days': order * 30,
            }
        )


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin to require specific user roles."""

    allowed_roles = []

    def test_func(self):
        return self.request.user.role in self.allowed_roles


class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin to require admin role."""
    allowed_roles = ['ADMIN']


class GuideRequiredMixin(RoleRequiredMixin):
    """Mixin to require guide role."""
    allowed_roles = ['GUIDE']


class CoordinatorRequiredMixin(RoleRequiredMixin):
    """Mixin to require coordinator role."""
    allowed_roles = ['COORDINATOR']


# Dashboard Views
@login_required
def dashboard(request):
    """
    Main dashboard view showing relevant information based on user role.
    """
    user = request.user
    context = {'user': user}

    if user.is_admin():
        # Admin dashboard
        context.update({
            'total_projects': Project.objects.count(),
            'active_projects': Project.objects.filter(status='ACTIVE').count(),
            'total_users': user.__class__.objects.count(),
            'recent_projects': Project.objects.select_related('domain', 'guide').order_by('-created_at')[:5],
        })

    elif user.is_guide():
        # Guide dashboard
        projects = Project.objects.filter(guide=user).select_related('domain')
        context.update({
            'my_projects': projects.filter(status='ACTIVE'),
            'completed_projects': projects.filter(status='COMPLETED'),
            'pending_reviews': Submission.objects.filter(
                project__guide=user,
                status='SUBMITTED'
            ).select_related('project', 'phase').count(),
        })

    elif user.is_coordinator():
        # Coordinator dashboard
        projects = Project.objects.filter(coordinator=user).select_related('domain')
        context.update({
            'my_projects': projects.filter(status='ACTIVE'),
            'completed_projects': projects.filter(status='COMPLETED'),
            'pending_reviews': Submission.objects.filter(
                project__coordinator=user,
                status='APPROVED'  # Guide approved, waiting for coordinator
            ).select_related('project', 'phase').count(),
        })

    return render(request, 'dashboards/overview.html', context)


# Project Management Views
class ProjectListView(LoginRequiredMixin, ListView):
    """List view for projects with role-based filtering."""

    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 20

    def get_queryset(self):
        """Filter projects based on user role."""
        user = self.request.user
        queryset = Project.objects.select_related('domain', 'guide')

        if user.is_admin():
            # Admins see all projects
            pass
        elif user.is_guide():
            # Guides see their assigned projects
            queryset = queryset.filter(guide=user)
        elif user.is_coordinator():
            # Coordinators see their assigned projects
            queryset = queryset.filter(coordinator=user)
        elif user.is_student():
            # Students see their team projects
            queryset = queryset.filter(team_members__user=user)

        # Apply filters
        status = self.request.GET.get('status')
        domain = self.request.GET.get('domain')
        search = self.request.GET.get('search')

        if status:
            queryset = queryset.filter(status=status)
        if domain:
            queryset = queryset.filter(domain_id=domain)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(domain__name__icontains=search)
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        """Add filter options to context."""
        context = super().get_context_data(**kwargs)
        context['domains'] = Domain.objects.all()
        context['status_choices'] = Project.STATUS_CHOICES
        context['publication_choices'] = Project.PUBLICATION_CHOICES
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a project with all related information."""

    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        """Filter projects user can access."""
        user = self.request.user
        queryset = Project.objects.select_related('domain', 'guide').prefetch_related(
            'team_members__user',
            'submissions__phase',
            'submissions__versions',
            'submissions__feedback'
        )

        if user.is_admin():
            pass
        elif user.is_guide():
            queryset = queryset.filter(guide=user)
        elif user.is_coordinator():
            queryset = queryset.filter(coordinator=user)
        elif user.is_student():
            queryset = queryset.filter(team_members__user=user)

        return queryset

    def get_context_data(self, **kwargs):
        """Add project-related data to context."""
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user

        context.update({
            'team_members': project.team_members.select_related('user'),
            'submissions': project.submissions.select_related('phase').prefetch_related('versions', 'feedback'),
            'phases': Phase.objects.all(),
            'can_edit': user.is_admin() or (user.is_guide() and project.guide == user) or (user.is_coordinator() and project.coordinator == user),
            'can_add_members': user.is_admin() or user.is_guide(),
            'is_team_member': user.is_student() and project.team_members.filter(user=user).exists(),
        })

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create new project view."""

    model = Project
    form_class = ProjectForm
    template_name = 'projects/create.html'
    success_url = reverse_lazy('projects:project-list')

    def get_form_kwargs(self):
        """Pass user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Handle project creation and automatic team member assignment."""
        response = super().form_valid(form)
        
        # If a student created the project, add them as the team leader
        if self.request.user.role == 'STUDENT':
            TeamMember.objects.create(
                user=self.request.user,
                project=self.object,
                role='LEADER'
            )
        
        messages.success(self.request, f'Project "{form.instance.title}" created successfully!')
        return response


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update project view."""

    model = Project
    form_class = ProjectForm
    template_name = 'projects/edit.html'

    def test_func(self):
        """Check if user can edit this project."""
        user = self.request.user
        project = self.get_object()
        # Lock edits if project is completed
        if project.status == 'COMPLETED':
            return False
        return (
            user.is_admin() or
            (user.is_guide() and project.guide == user) or
            (user.is_coordinator() and project.coordinator == user)
        )

    def get_form_kwargs(self):
        """Pass user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        """Return to project detail."""
        return reverse('projects:project-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Show success message."""
        messages.success(self.request, f'Project "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete project view."""

    model = Project
    template_name = 'projects/confirm_delete.html'
    success_url = reverse_lazy('projects:project-list')

    def test_func(self):
        user = self.request.user
        project = self.get_object()
        # Lock delete if project is completed
        if project.status == 'COMPLETED':
            return False
        return user.is_admin() or (user.is_guide() and project.guide == user)

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        messages.success(request, f'Project "{project.title}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Team Management Views
@login_required
@require_POST
def add_team_member(request, project_id):
    """Add a team member to a project via AJAX."""
    project = get_object_or_404(Project, pk=project_id)

    # Check permissions
    user = request.user
    if not (
        user.is_admin() or
        (user.is_guide() and project.guide == user) or
        (user.is_coordinator() and project.coordinator == user)
    ):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    form = TeamMemberForm(request.POST, project=project)
    if form.is_valid():
        member = form.save()
        return JsonResponse({
            'success': True,
            'member': {
                'id': member.pk,
                'name': member.user.get_full_name(),
                'role': member.get_role_display(),
                'joined_at': member.joined_at.strftime('%Y-%m-%d'),
            }
        })

    return JsonResponse({'error': form.errors}, status=400)


@login_required
@require_POST
def remove_team_member(request, project_id, member_id):
    """Remove a team member from a project."""
    project = get_object_or_404(Project, pk=project_id)
    member = get_object_or_404(TeamMember, pk=member_id, project=project)

    # Check permissions
    user = request.user
    if not (
        user.is_admin() or
        (user.is_guide() and project.guide == user) or
        (user.is_coordinator() and project.coordinator == user)
    ):
        messages.error(request, 'Permission denied.')
        return redirect('projects:project-detail', pk=project_id)

    member.delete()
    messages.success(request, f'Removed {member.user.get_full_name()} from the team.')
    return redirect('projects:project-detail', pk=project_id)


# Submission Management Views
@login_required
def create_submission(request, project_id):
    """Create a new submission for a project phase."""
    ensure_default_phases()
    project = get_object_or_404(Project, pk=project_id)

    # Check if user can access this project
    user = request.user
    can_access = (
        user.is_admin() or
        (user.is_guide() and project.guide == user) or
        (user.is_student() and project.team_members.filter(user=user).exists())
    )

    if not can_access:
        raise Http404("Project not found")

    if request.method == 'POST':
        form = SubmissionForm(request.POST, project=project, user=user)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.project = project
            submission.save()

            messages.success(request, f'Submission created for {submission.phase.get_name_display()}.')
            return redirect('projects:submission-detail', submission_id=submission.pk)
    else:
        form = SubmissionForm(project=project, user=user)

    return render(request, 'projects/create_submission.html', {
        'form': form,
        'project': project,
    })


@login_required
def submission_detail(request, submission_id):
    """View submission details with versions and feedback."""
    submission = get_object_or_404(
        Submission.objects.select_related('project', 'phase').prefetch_related(
            'versions__uploaded_by',
            'feedback__given_by'
        ),
        pk=submission_id
    )

    # Check access permissions
    user = request.user
    can_access = (
        user.is_admin() or
        (user.is_guide() and submission.project.guide == user) or
        (user.is_coordinator() and submission.project.coordinator == user) or
        (user.is_student() and submission.project.team_members.filter(user=user).exists())
    )

    if not can_access:
        raise Http404("Submission not found")

    context = {
        'submission': submission,
        'versions': submission.versions.all(),
        'feedback': submission.feedback.all(),
        'can_upload_version': submission.can_submit_new_version(),
        'can_provide_feedback': user.is_guide() or user.is_admin(),
        'can_commit_submission': (
            submission.status == 'DRAFT' and
            submission.versions.exists() and
            (user.is_admin() or (user.is_student() and submission.project.team_members.filter(user=user).exists()))
        ),
        'can_approve_submission': (
            submission.status in ['SUBMITTED', 'UNDER_REVIEW'] and
            (user.is_admin() or (user.is_guide() and submission.project.guide == user))
        ),
        'can_resolve_feedback': any(f.can_resolve(user) for f in submission.feedback.filter(resolved=False)),
        'can_evaluate': (
            (user.is_guide() and submission.project.guide == user) or
            (user.is_coordinator() and submission.project.coordinator == user and submission.status == 'APPROVED') or
            user.is_admin()
        ),
    }

    return render(request, 'projects/submission_detail.html', context)


@login_required
def upload_version(request, submission_id):
    """Upload a new version to a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)

    # Check permissions
    user = request.user
    can_upload = (
        user.is_admin() or
        (user.is_guide() and submission.project.guide == user) or
        (user.is_student() and submission.project.team_members.filter(user=user).exists())
    )

    if not can_upload or not submission.can_submit_new_version():
        messages.error(request, 'Cannot upload version at this time.')
        return redirect('projects:submission-detail', submission_id=submission_id)

    if request.method == 'POST':
        form = VersionUploadForm(request.POST, request.FILES, submission=submission, user=user)
        if form.is_valid():
            version = Version.objects.create(
                submission=submission,
                uploaded_by=user,
                file=form.cleaned_data['file'],
                change_summary=form.cleaned_data.get('change_summary', '')
            )

            messages.success(request, f'File uploaded as version {version.version_number}. Click "Commit for Review" when the submission is ready.')
            return redirect('projects:submission-detail', submission_id=submission_id)
    else:
        form = VersionUploadForm(submission=submission, user=user)

    return render(request, 'projects/upload_version.html', {
        'form': form,
        'submission': submission,
    })


@login_required
@require_POST
def submit_for_review(request, submission_id):
    """Submit a submission for review."""
    submission = get_object_or_404(Submission, pk=submission_id)

    # Check permissions
    user = request.user
    can_submit = (
        user.is_admin() or
        (user.is_guide() and submission.project.guide == user) or
        (user.is_student() and submission.project.team_members.filter(user=user).exists())
    )

    if not can_submit:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        messages.error(request, 'Permission denied.')
        return redirect('projects:submission-detail', submission_id=submission_id)

    if submission.status == 'DRAFT':
        submission.submit(user)
        messages.success(request, 'Submission committed and sent to the guide for review.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'status': submission.status})
        return redirect('projects:submission-detail', submission_id=submission_id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Cannot submit at this time'}, status=400)
    messages.error(request, 'Cannot commit this submission at this time.')
    return redirect('projects:submission-detail', submission_id=submission_id)


@login_required
@require_POST
def approve_submission(request, submission_id):
    """Approve a submission (guide/admin only)."""
    submission = get_object_or_404(Submission, pk=submission_id)

    user = request.user
    if not (user.is_guide() or user.is_admin()):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        messages.error(request, 'Permission denied.')
        return redirect('projects:submission-detail', submission_id=submission_id)

    if user.is_guide() and submission.project.guide != user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Not the assigned guide'}, status=403)
        messages.error(request, 'Only the assigned guide can approve this submission.')
        return redirect('projects:submission-detail', submission_id=submission_id)

    submission.approve(user)
    messages.success(request, f'Submission for {submission.phase.get_name_display()} approved!')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': submission.status})
    return redirect('projects:submission-detail', submission_id=submission_id)


# Feedback Management Views
@login_required
def add_feedback(request, submission_id):
    """Add feedback to a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)

    user = request.user
    if not (user.is_guide() or user.is_admin()):
        raise Http404("Page not found")

    if user.is_guide() and submission.project.guide != user:
        raise Http404("Page not found")

    if request.method == 'POST':
        form = FeedbackForm(request.POST, submission=submission, user=user)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.submission = submission
            feedback.given_by = user
            feedback.save()

            messages.success(request, 'Feedback added successfully!')
            return redirect('projects:submission-detail', submission_id=submission_id)
    else:
        form = FeedbackForm(submission=submission, user=user)

    return render(request, 'projects/add_feedback.html', {
        'form': form,
        'submission': submission,
    })


@login_required
@require_POST
def resolve_feedback(request, feedback_id):
    """Resolve a feedback item."""
    feedback = get_object_or_404(Feedback, pk=feedback_id)

    user = request.user
    if feedback.can_resolve(user):
        feedback.resolve(user)
        messages.success(request, 'Feedback resolved successfully!')
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Cannot resolve this feedback'}, status=403)


# AJAX Views for dynamic content
@login_required
def get_project_phases(request, project_id):
    """Get accessible phases for a project."""
    project = get_object_or_404(Project, pk=project_id)

    # Check access
    user = request.user
    can_access = (
        user.is_admin() or
        (user.is_guide() and project.guide == user) or
        (user.is_student() and project.team_members.filter(user=user).exists())
    )

    if not can_access:
        return JsonResponse({'error': 'Access denied'}, status=403)

    phases = []
    for phase in Phase.objects.all():
        phases.append({
            'id': phase.pk,
            'name': phase.get_name_display(),
            'accessible': project.can_access_phase(phase),
            'current': phase == project.get_current_phase(),
        })

    return JsonResponse({'phases': phases})


@login_required
def get_submission_status(request, submission_id):
    """Get current submission status."""
    submission = get_object_or_404(Submission, pk=submission_id)

    # Check access
    user = request.user
    can_access = (
        user.is_admin() or
        (user.is_guide() and submission.project.guide == user) or
        (user.is_student() and submission.project.team_members.filter(user=user).exists())
    )

    if not can_access:
        return JsonResponse({'error': 'Access denied'}, status=403)

    return JsonResponse({
        'status': submission.status,
        'can_submit': submission.can_submit_new_version(),
        'version_count': submission.get_version_count(),
        'unresolved_feedback': submission.feedback.filter(resolved=False).count(),
    })


# User Management Views (Admin Only)
class StudentListView(AdminRequiredMixin, ListView):
    """List all students."""

    model = User
    template_name = 'projects/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(role='STUDENT').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Student'
        context['user_type_plural'] = 'Students'
        return context


class StudentCreateView(AdminRequiredMixin, CreateView):
    """Create new student."""

    model = User
    form_class = StudentForm
    template_name = 'projects/user_form.html'
    success_url = reverse_lazy('student-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Student'
        return context


class StudentUpdateView(AdminRequiredMixin, UpdateView):
    """Update student."""

    model = User
    form_class = StudentForm
    template_name = 'projects/user_form.html'
    success_url = reverse_lazy('student-list')

    def get_queryset(self):
        return User.objects.filter(role='STUDENT')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Student'
        return context


class StudentDeleteView(AdminRequiredMixin, DeleteView):
    """Delete student."""

    model = User
    template_name = 'projects/confirm_delete.html'
    success_url = reverse_lazy('student-list')

    def get_queryset(self):
        return User.objects.filter(role='STUDENT')


class GuideListView(AdminRequiredMixin, ListView):
    """List all guides."""

    model = User
    template_name = 'projects/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(role='GUIDE').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Guide'
        context['user_type_plural'] = 'Guides'
        return context


class GuideCreateView(AdminRequiredMixin, CreateView):
    """Create new guide."""

    model = User
    form_class = GuideForm
    template_name = 'projects/user_form.html'
    success_url = reverse_lazy('guide-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Guide'
        return context


class GuideUpdateView(AdminRequiredMixin, UpdateView):
    """Update guide."""

    model = User
    form_class = GuideForm
    template_name = 'projects/user_form.html'
    success_url = reverse_lazy('guide-list')

    def get_queryset(self):
        return User.objects.filter(role='GUIDE')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Guide'
        return context


class GuideDeleteView(AdminRequiredMixin, DeleteView):
    """Delete guide."""

    model = User
    template_name = 'projects/confirm_delete.html'
    success_url = reverse_lazy('guide-list')

    def get_queryset(self):
        return User.objects.filter(role='GUIDE')


class CoordinatorListView(AdminRequiredMixin, ListView):
    """List all coordinators."""

    model = User
    template_name = 'projects/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(role='COORDINATOR').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Coordinator'
        context['user_type_plural'] = 'Coordinators'
        return context


class CoordinatorCreateView(AdminRequiredMixin, CreateView):
    """Create new coordinator."""

    model = User
    form_class = CoordinatorForm
    template_name = 'projects/user_form.html'
    success_url = reverse_lazy('coordinator-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Coordinator'
        return context


class CoordinatorUpdateView(AdminRequiredMixin, UpdateView):
    """Update coordinator."""

    model = User
    form_class = CoordinatorForm
    template_name = 'projects/user_form.html'
    success_url = reverse_lazy('coordinator-list')

    def get_queryset(self):
        return User.objects.filter(role='COORDINATOR')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'Coordinator'
        return context


class CoordinatorDeleteView(AdminRequiredMixin, DeleteView):
    """Delete coordinator."""

    model = User
    template_name = 'projects/confirm_delete.html'
    success_url = reverse_lazy('coordinator-list')

    def get_queryset(self):
        return User.objects.filter(role='COORDINATOR')


# Guide Allotment View
@login_required
def allot_guide(request):
    """Admin view to assign projects to guides and student teams."""

    if not request.user.is_admin():
        raise Http404("Page not found")

    if request.method == 'POST':
        form = GuideAllotmentForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            guide = form.cleaned_data['guide']
            coordinator = form.cleaned_data.get('coordinator')
            students = list(form.cleaned_data['students'])

            with transaction.atomic():
                project.guide = guide
                project.coordinator = coordinator
                project.save(update_fields=['guide', 'coordinator', 'updated_at'])

                selected_ids = [student.id for student in students]
                TeamMember.objects.filter(project=project).exclude(user_id__in=selected_ids).delete()

                for index, student in enumerate(students):
                    member, created = TeamMember.objects.get_or_create(
                        project=project,
                        user=student,
                        defaults={'role': 'LEADER' if index == 0 else 'MEMBER'}
                    )
                    desired_role = 'LEADER' if index == 0 else 'MEMBER'
                    if member.role != desired_role:
                        member.role = desired_role
                        member.save(update_fields=['role'])

            messages.success(
                request,
                f'Project "{project.title}" assigned to guide {guide.get_full_name() or guide.username}, coordinator {coordinator.get_full_name() if coordinator else "Unassigned"}, and {len(students)} student(s).'
            )
            return redirect('allot-guide')
    else:
        initial = {}
        if request.GET.get('project'):
            initial['project'] = request.GET.get('project')
        form = GuideAllotmentForm(initial=initial)

    projects = Project.objects.select_related('domain', 'guide').prefetch_related('team_members__user').order_by('-updated_at')
    unassigned_projects = projects.filter(
        Q(guide__isnull=True) |
        Q(coordinator__isnull=True) |
        Q(team_members__isnull=True)
    ).distinct()

    return render(request, 'projects/allot_guide.html', {
        'form': form,
        'projects': projects,
        'unassigned_projects': unassigned_projects,
    })


# Evaluation Views
@login_required
def evaluate_submission(request, submission_id):
    """Evaluate a submission (guide/coordinator only)."""

    submission = get_object_or_404(Submission, pk=submission_id)
    user = request.user

    # Check permissions
    can_evaluate = False
    if user.is_guide() and submission.project.guide == user:
        can_evaluate = True
    elif user.is_coordinator() and submission.project.coordinator == user and submission.status == 'APPROVED':
        can_evaluate = True
    elif user.is_admin():
        can_evaluate = True

    if not can_evaluate:
        raise Http404("Page not found")

    if request.method == 'POST':
        form = EvaluationForm(request.POST, project=submission.project, phase=submission.phase, evaluator=user)
        if form.is_valid():
            evaluation = form.save()
            messages.success(request, 'Evaluation submitted successfully!')
            return redirect('projects:submission-detail', submission_id=submission_id)
    else:
        form = EvaluationForm(project=submission.project, phase=submission.phase, evaluator=user)

    return render(request, 'projects/evaluate.html', {
        'form': form,
        'submission': submission,
    })


# Coordinator Approval View
@login_required
def coordinator_approve(request, project_id):
    """Coordinator final approval and publication."""

    ensure_default_phases()
    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    if not (user.is_coordinator() and project.coordinator == user):
        raise Http404("Page not found")

    phases = Phase.objects.order_by('order')
    all_submissions = project.submissions.select_related('phase').prefetch_related('versions').order_by('phase__order')
    submissions_by_phase = {submission.phase_id: submission for submission in all_submissions}
    phase_rows = []
    for phase in phases:
        submission = submissions_by_phase.get(phase.id)
        phase_rows.append({
            'phase': phase,
            'submission': submission,
            'approved': submission is not None and submission.status == 'APPROVED',
        })

    approved_count = sum(1 for row in phase_rows if row['approved'])
    total_phases = phases.count()
    ready_to_finalize = bool(total_phases) and approved_count == total_phases

    if request.method == 'POST':
        publication_status = request.POST.get('publication_status')
        certificate = request.FILES.get('certificate')
        if not ready_to_finalize:
            messages.error(request, 'Final approval is locked until every phase is approved by the guide.')
            return redirect('projects:coordinator-approve', project_id=project_id)

        if not publication_status:
            messages.error(request, 'Please select a publication status.')
            return redirect('projects:coordinator-approve', project_id=project_id)

        if certificate and not certificate.name.lower().endswith('.pdf'):
            messages.error(request, 'Certificate must be a PDF file.')
            return redirect('projects:coordinator-approve', project_id=project_id)

        if publication_status in dict(Project.PUBLICATION_CHOICES):
            project.publication_status = publication_status
            if certificate:
                project.certificate = certificate
            project.status = 'COMPLETED'
            project.save()

            messages.success(request, f'✓ Project "{project.title}" has been finalized with status: {publication_status}')
            
            # Create notification for team. Notification failure should not block finalization.
            try:
                from notifications.models import Notification
                for team_member in project.team_members.select_related('user'):
                    Notification.objects.create(
                        user=team_member.user,
                        type='PHASE_COMPLETE',
                        title='Project Finalized',
                        message=f'Your project "{project.title}" has been finalized with publication status: {publication_status}.',
                        link=reverse('projects:project-detail', kwargs={'pk': project.pk})
                    )
            except Exception:
                pass
            
            return redirect('projects:project-detail', pk=project_id)
        else:
            messages.error(request, 'Invalid publication status selected.')

    context = {
        'project': project,
        'submissions': all_submissions,
        'phase_rows': phase_rows,
        'approved_count': approved_count,
        'total_phases': total_phases,
        'ready_to_finalize': ready_to_finalize,
        'team_members': project.team_members.select_related('user'),
        'phases': phases,
    }

    return render(request, 'projects/coordinator_approve.html', context)


# CSV Export View
@login_required
def export_projects_csv(request):
    """Export projects to CSV with filters."""

    import csv
    from django.http import HttpResponse

    # Get filters
    guide_id = request.GET.get('guide')
    domain_id = request.GET.get('domain')
    publication_status = request.GET.get('publication_status')

    # Build queryset
    projects = Project.objects.select_related('domain', 'guide', 'coordinator').prefetch_related('team_members__user', 'evaluations')

    if guide_id:
        projects = projects.filter(guide_id=guide_id)
    if domain_id:
        projects = projects.filter(domain_id=domain_id)
    if publication_status:
        projects = projects.filter(publication_status=publication_status)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="projects_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Project Title', 'Students', 'Domain', 'Guide', 'Coordinator',
        'Status', 'Publication Status', 'Average Rating', 'Created At'
    ])

    for project in projects:
        students = ', '.join([tm.user.get_full_name() for tm in project.team_members.all()])
        guide_name = project.guide.get_full_name() if project.guide else ''
        coordinator_name = project.coordinator.get_full_name() if project.coordinator else ''

        # Calculate average rating
        evaluations = project.evaluations.all()
        avg_rating = sum([e.rating for e in evaluations]) / len(evaluations) if evaluations else 0

        writer.writerow([
            project.title,
            students,
            project.domain.name,
            guide_name,
            coordinator_name,
            project.status,
            project.publication_status,
            f"{avg_rating:.1f}" if avg_rating > 0 else '',
            project.created_at.strftime('%Y-%m-%d'),
        ])

    return response
