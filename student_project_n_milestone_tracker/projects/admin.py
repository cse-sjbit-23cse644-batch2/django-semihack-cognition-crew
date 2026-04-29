from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Domain, Project, TeamMember, Phase, Submission, Version, Feedback, Evaluation

User = get_user_model()


# Custom User Admin (extends auth_app User model)
class CustomUserAdmin(UserAdmin):
    """Enhanced User admin with role-based filtering and permissions."""

    list_display = ('username', 'email', 'get_full_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        ('Role & Profile', {
            'fields': ('role', 'bio', 'profile_picture')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {
            'fields': ('role',)
        }),
    )

    def get_queryset(self, request):
        """Filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Non-superusers can only see users in their role domain
            if request.user.role == 'GUIDE':
                qs = qs.filter(Q(role='STUDENT') | Q(pk=request.user.pk))
            elif request.user.role == 'STUDENT':
                qs = qs.filter(pk=request.user.pk)
        return qs


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Admin interface for academic domains."""

    list_display = ('name', 'description', 'project_count', 'student_count', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

    def project_count(self, obj):
        return obj.project_set.count()
    project_count.short_description = 'Projects'

    def student_count(self, obj):
        return User.objects.filter(role='STUDENT', domain=obj).count()
    student_count.short_description = 'Students'


class TeamMemberInline(admin.TabularInline):
    """Inline admin for team members."""

    model = TeamMember
    extra = 0
    readonly_fields = ('joined_at',)
    autocomplete_fields = ['user']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for projects."""

    list_display = ('title', 'domain', 'guide', 'status', 'team_size', 'created_at', 'updated_at')
    list_filter = ('status', 'domain', 'created_at', 'updated_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
    autocomplete_fields = ['guide']
    inlines = [TeamMemberInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'domain', 'guide')
        }),
        ('Status & Timeline', {
            'fields': ('status', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def team_size(self, obj):
        return obj.teammember_set.count()
    team_size.short_description = 'Team Size'

    def get_queryset(self, request):
        """Filter projects based on user role."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if request.user.role == 'GUIDE':
                qs = qs.filter(guide=request.user)
            elif request.user.role == 'STUDENT':
                # Students can see projects they're part of
                qs = qs.filter(team_members__user=request.user)
        return qs.distinct()


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin interface for team members."""

    list_display = ('user', 'project', 'role', 'joined_at')
    list_filter = ('role', 'joined_at', 'project__domain')
    search_fields = ('user__username', 'user__email', 'project__title')
    autocomplete_fields = ['user', 'project']
    ordering = ('-joined_at',)


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    """Admin interface for project phases."""

    list_display = ('name', 'order', 'deadline_offset_days', 'submission_count')
    list_filter = ()
    search_fields = ('name', 'description')
    ordering = ('order',)

    def submission_count(self, obj):
        return Submission.objects.filter(phase=obj).count()
    submission_count.short_description = 'Submissions'


class VersionInline(admin.TabularInline):
    """Inline admin for submission versions."""

    model = Version
    extra = 0
    readonly_fields = ('version_number', 'uploaded_at', 'uploaded_by')
    fields = ('version_number', 'file', 'change_summary', 'uploaded_at', 'uploaded_by')


class FeedbackInline(admin.TabularInline):
    """Inline admin for submission feedback."""

    model = Feedback
    extra = 0
    readonly_fields = ('given_by', 'created_at', 'resolved')
    fields = ('given_by', 'comment', 'resolved', 'created_at')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin interface for submissions."""

    list_display = ('project_title', 'phase_name', 'status', 'version_count', 'feedback_count', 'created_at')
    list_filter = ('status', 'phase', 'created_at', 'submitted_at')
    search_fields = ('project__title', 'phase__name')
    ordering = ('-created_at',)
    inlines = [VersionInline, FeedbackInline]

    fieldsets = (
        ('Submission Info', {
            'fields': ('project', 'phase')
        }),
        ('Status & Timeline', {
            'fields': ('status', 'created_at', 'submitted_at', 'approved_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'submitted_at', 'approved_at')

    def project_title(self, obj):
        return obj.project.title
    project_title.short_description = 'Project'
    project_title.admin_order_field = 'project__title'

    def phase_name(self, obj):
        return obj.phase.name
    phase_name.short_description = 'Phase'
    phase_name.admin_order_field = 'phase__name'

    def version_count(self, obj):
        return obj.version_set.count()
    version_count.short_description = 'Versions'

    def feedback_count(self, obj):
        return obj.feedback_set.count()
    feedback_count.short_description = 'Feedback'

    def get_queryset(self, request):
        """Filter submissions based on user role."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if request.user.role == 'GUIDE':
                qs = qs.filter(project__guide=request.user)
            elif request.user.role == 'STUDENT':
                # Students can see submissions for projects they're part of
                qs = qs.filter(project__team_members__user=request.user)
        return qs.distinct()


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    """Admin interface for submission versions."""

    list_display = ('submission_info', 'version_number', 'uploaded_by', 'uploaded_at', 'file_size')
    list_filter = ('uploaded_at',)
    search_fields = ('submission__project__title', 'uploaded_by__username')
    ordering = ('-uploaded_at',)
    readonly_fields = ('version_number', 'uploaded_at')

    def submission_info(self, obj):
        return f"{obj.submission.project.title} - {obj.submission.phase.name}"
    submission_info.short_description = 'Submission'

    def file_size(self, obj):
        if obj.file:
            size = obj.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return '-'
    file_size.short_description = 'File Size'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin interface for feedback."""

    list_display = ('submission_info', 'given_by', 'resolved', 'created_at')
    list_filter = ('resolved', 'created_at', 'given_by__role')
    search_fields = ('submission__project__title', 'given_by__username', 'comment')
    ordering = ('-created_at',)

    fieldsets = (
        ('Feedback Info', {
            'fields': ('submission', 'given_by', 'comment')
        }),
        ('Resolution', {
            'fields': ('resolved', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

    def submission_info(self, obj):
        return f"{obj.submission.project.title} - {obj.submission.phase.name}"
    submission_info.short_description = 'Submission'

    def get_queryset(self, request):
        """Filter feedback based on user role."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if request.user.role == 'GUIDE':
                qs = qs.filter(submission__project__guide=request.user)
            elif request.user.role == 'STUDENT':
                # Students can see feedback on their project submissions
                qs = qs.filter(submission__project__team_members__user=request.user)
        return qs.distinct()


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """Admin interface for project evaluations."""

    list_display = ('project', 'phase', 'evaluator', 'rating', 'created_at')
    list_filter = ('rating', 'phase', 'created_at')
    search_fields = ('project__title', 'evaluator__username', 'comments')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Evaluation Info', {
            'fields': ('project', 'phase', 'evaluator', 'rating', 'comments')
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Filter evaluations based on user role."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if request.user.role == 'GUIDE':
                qs = qs.filter(evaluator=request.user)
            elif request.user.role == 'COORDINATOR':
                qs = qs.filter(evaluator=request.user)
        return qs


# Register the custom user admin
# Note: User model is registered in auth_app.admin, not here
