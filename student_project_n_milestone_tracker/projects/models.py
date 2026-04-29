"""
MilestoneTrack - Core Project Models

Production-ready models for the academic project workflow system.
Implements sequential phases, version control, and feedback enforcement.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.db.models import Q, F
import os

User = get_user_model()


class Domain(models.Model):
    """
    Subject domain/category for projects (e.g., AI, Healthcare, FinTech).

    Domains help categorize projects and assign appropriate guides.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Domain name (e.g., 'Artificial Intelligence', 'Data Science')"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the domain"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='domains_created',
        help_text="User who created this domain"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Ensure domain name is properly formatted."""
        if self.name:
            self.name = self.name.strip().title()


class Project(models.Model):
    """
    Core project model representing a student capstone project.

    Implements unique title validation (case-insensitive) and workflow tracking.
    """
    title = models.CharField(
        max_length=500,
        unique=True,
        help_text="Project title (must be unique across all projects)"
    )
    domain = models.ForeignKey(
        Domain,
        on_delete=models.CASCADE,
        related_name='projects',
        help_text="Project domain/category"
    )
    guide = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'GUIDE'},
        related_name='projects_guided',
        help_text="Assigned guide/teacher for this project"
    )
    coordinator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'COORDINATOR'},
        related_name='projects_coordinated',
        help_text="Assigned coordinator for this project"
    )

    students = models.ManyToManyField(
        User,
        through='TeamMember',
        related_name='projects',
        help_text="Student team members"
    )

    # Workflow status
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ARCHIVED', 'Archived'),
        ('SUSPENDED', 'Suspended'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        help_text="Current project status"
    )

    # Publication status
    PUBLICATION_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('PUBLISHED', 'Published'),
        ('REJECTED', 'Rejected'),
    ]
    publication_status = models.CharField(
        max_length=20,
        choices=PUBLICATION_CHOICES,
        default='PENDING',
        help_text="Publication status after coordinator approval"
    )
    certificate = models.FileField(
        upload_to='certificates/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Uploaded certificate PDF"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['guide', 'status']),
            models.Index(fields=['coordinator', 'status']),
            models.Index(fields=['domain']),
            models.Index(fields=['title']),  # For case-insensitive uniqueness
        ]

    def __str__(self):
        return f"{self.title} ({self.domain.name})"

    def clean(self):
        """Custom validation for Project model."""
        super().clean()

        if self.title:
            # Check for case-insensitive duplicates
            existing = Project.objects.filter(
                title__iexact=self.title.strip()
            ).exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError(
                    f"A project with the title '{self.title}' already exists."
                )

            # Normalize title
            self.title = self.title.strip()

    def get_team_members(self):
        """Get all team members for this project."""
        return self.team_members.select_related('user')

    def get_current_phase(self):
        """Get the current active phase for this project."""
        # Find the latest approved submission
        latest_approved = self.submissions.filter(
            status='APPROVED'
        ).select_related('phase').order_by('-phase__order').first()

        if latest_approved:
            # Check if next phase is accessible
            next_phase_order = latest_approved.phase.order + 1
            next_phase = Phase.objects.filter(order=next_phase_order).first()

            if next_phase and self.can_access_phase(next_phase):
                return next_phase

            return latest_approved.phase

        # No approved submissions, return first phase
        return Phase.objects.filter(order=1).first()

    def can_access_phase(self, phase):
        """
        Check if project can access a specific phase.

        Implements FALS (Feedback Action Lock System):
        - Project must not be COMPLETED
        - Previous phase must be approved
        - All feedback on previous submissions must be resolved
        """
        if self.status == 'COMPLETED':
            return False

        if phase.order == 1:
            return True  # First phase always accessible

        previous_phase = Phase.objects.filter(order=phase.order - 1).first()
        if not previous_phase:
            return False

        # Check if previous phase is approved
        previous_submission = self.submissions.filter(
            phase=previous_phase,
            status='APPROVED'
        ).first()

        if not previous_submission:
            return False

        # Check FALS: All feedback must be resolved
        unresolved_feedback = Feedback.objects.filter(
            submission__project=self,
            submission__phase=previous_phase,
            resolved=False
        ).exists()

        return not unresolved_feedback

    def get_completion_percentage(self):
        """Calculate project completion percentage."""
        total_phases = Phase.objects.count()
        if total_phases == 0:
            return 0

        approved_phases = self.submissions.filter(status='APPROVED').count()
        return int((approved_phases / total_phases) * 100)


class TeamMember(models.Model):
    """
    Junction model for project team members.

    Links users to projects with role information.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'},
        related_name='project_memberships',
        help_text="Student team member"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='team_members',
        help_text="Project this member belongs to"
    )

    # Member role in team
    ROLE_CHOICES = [
        ('LEADER', 'Team Leader'),
        ('MEMBER', 'Team Member'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='MEMBER',
        help_text="Role within the team"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'project']
        ordering = ['joined_at']
        indexes = [
            models.Index(fields=['project', 'role']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.title} ({self.get_role_display()})"

    def clean(self):
        """Ensure user is a student and not already on another active project."""
        if self.user and self.user.role != 'STUDENT':
            raise ValidationError("Only students can be team members.")

        # Check if user is already on another active project
        if self.user:
            existing_membership = TeamMember.objects.filter(
                user=self.user,
                project__status='ACTIVE'
            ).exclude(pk=self.pk)

            if existing_membership.exists():
                raise ValidationError(
                    f"{self.user.get_full_name()} is already a member of another active project."
                )


class Phase(models.Model):
    """
    Predefined project phases in sequential order.

    Phases must be completed in order, with feedback resolution required.
    """
    PHASE_CHOICES = [
        ('SYNOPSIS', 'Synopsis'),
        ('PHASE_1', 'Phase 1'),
        ('PHASE_2', 'Phase 2'),
        ('FINAL_REPORT', 'Final Report'),
        ('PUBLICATION', 'Publication'),
    ]

    name = models.CharField(
        max_length=50,
        choices=PHASE_CHOICES,
        unique=True,
        help_text="Phase identifier"
    )
    order = models.IntegerField(
        unique=True,
        help_text="Sequential order (1, 2, 3, 4, 5)"
    )
    description = models.TextField(
        blank=True,
        help_text="Phase description and requirements"
    )
    deadline_offset_days = models.IntegerField(
        default=30,
        help_text="Days from project creation for this phase deadline"
    )

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return self.get_name_display()

    def clean(self):
        """Validate phase order and uniqueness."""
        if self.order < 1:
            raise ValidationError("Phase order must be positive.")

        # Ensure order matches existing pattern
        if self.name == 'SYNOPSIS' and self.order != 1:
            raise ValidationError("Synopsis must be order 1.")
        elif self.name == 'PHASE_1' and self.order != 2:
            raise ValidationError("Phase 1 must be order 2.")
        elif self.name == 'PHASE_2' and self.order != 3:
            raise ValidationError("Phase 2 must be order 3.")
        elif self.name == 'FINAL_REPORT' and self.order != 4:
            raise ValidationError("Final Report must be order 4.")
        elif self.name == 'PUBLICATION' and self.order != 5:
            raise ValidationError("Publication must be order 5.")


class Submission(models.Model):
    """
    Version-controlled submission for a specific project phase.

    Implements non-destructive version history - never overwrites files.
    Each submission creates a new version with auto-incrementing version number.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Project this submission belongs to"
    )
    phase = models.ForeignKey(
        Phase,
        on_delete=models.CASCADE,
        help_text="Phase this submission is for"
    )

    # Status tracking
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text="Current submission status"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['project', 'phase']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'phase', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.project.title} - {self.phase.get_name_display()}"

    def clean(self):
        """Validate submission creation."""
        # Check if project can access this phase
        if not self.project.can_access_phase(self.phase):
            raise ValidationError(
                f"Cannot submit for {self.phase.get_name_display()}. "
                "Previous phase must be approved and all feedback resolved."
            )

    def get_latest_version(self):
        """Get the latest version of this submission."""
        return self.versions.order_by('-version_number').first()

    def get_version_count(self):
        """Get total number of versions for this submission."""
        return self.versions.count()

    def can_submit_new_version(self):
        """Check if a new version can be submitted."""
        # Cannot submit if project is COMPLETED
        if self.project.status == 'COMPLETED':
            return False

        # Can always submit if status is not approved
        if self.status != 'APPROVED':
            return True

        # If approved, check if there's unresolved feedback
        unresolved_feedback = self.feedback.filter(resolved=False).exists()
        return not unresolved_feedback

    def submit(self, user):
        """Mark submission as submitted for review."""
        if self.status == 'DRAFT':
            self.status = 'SUBMITTED'
            self.submitted_at = timezone.now()
            self.save()

    def approve(self, user):
        """Approve the submission."""
        if user.is_guide() or user.is_admin():
            self.status = 'APPROVED'
            self.approved_at = timezone.now()
            self.save()

    def reject(self, user):
        """Reject the submission."""
        if user.is_guide() or user.is_admin():
            self.status = 'REJECTED'
            self.save()


class Version(models.Model):
    """
    Non-destructive version history for submissions.

    Each file upload creates a new version with auto-incrementing number.
    Previous versions are preserved for audit trail.
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='versions',
        help_text="Submission this version belongs to"
    )
    version_number = models.IntegerField(
        help_text="Auto-incrementing version number per submission"
    )

    # File handling
    ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt', 'zip', 'rar', 'py', 'ipynb', 'jpg', 'jpeg', 'png']

    file = models.FileField(
        upload_to='submissions/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        help_text=f"Submission file ({', '.join(ALLOWED_EXTENSIONS)})"
    )
    change_summary = models.TextField(
        blank=True,
        help_text="What changed in this version?"
    )

    # Metadata
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who uploaded this version"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # File metadata stored as JSON
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="File metadata (size, type, etc.)"
    )

    class Meta:
        unique_together = ['submission', 'version_number']
        ordering = ['submission', 'version_number']
        indexes = [
            models.Index(fields=['submission', 'version_number']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"{self.submission} - v{self.version_number}"

    def save(self, *args, **kwargs):
        """Override save to set version number and metadata."""
        if not self.version_number:
            # Auto-increment version number
            last_version = Version.objects.filter(
                submission=self.submission
            ).order_by('-version_number').first()

            self.version_number = (last_version.version_number + 1) if last_version else 1

        # Store file metadata
        if self.file:
            self.metadata = {
                'filename': os.path.basename(self.file.name),
                'size': self.file.size,
                'content_type': getattr(self.file, 'content_type', 'unknown'),
                'extension': os.path.splitext(self.file.name)[1].lower().lstrip('.'),
            }

        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """Get human-readable file size."""
        size = self.metadata.get('size', 0)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"


class Feedback(models.Model):
    """
    Guide feedback on submissions.

    Implements FALS (Feedback Action Lock System) - feedback must be resolved
    before progressing to next phase.
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='feedback',
        help_text="Submission this feedback is for"
    )
    given_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['GUIDE', 'ADMIN']},
        related_name='feedback_given',
        help_text="Guide who provided this feedback"
    )

    comment = models.TextField(
        help_text="Feedback comment from guide"
    )
    
    version = models.ForeignKey(
        'Version',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
        help_text="The specific version this feedback refers to"
    )

    # Resolution tracking
    resolved = models.BooleanField(
        default=False,
        help_text="Has this feedback been resolved by the team?"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the feedback was resolved"
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_resolved',
        help_text="User who resolved this feedback"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['submission', 'resolved']),
            models.Index(fields=['given_by']),
            models.Index(fields=['resolved']),
        ]

    def __str__(self):
        status = "Resolved" if self.resolved else "Unresolved"
        return f"Feedback on {self.submission} by {self.given_by} ({status})"

    def resolve(self, user):
        """Mark feedback as resolved."""
        if not self.resolved:
            self.resolved = True
            self.resolved_at = timezone.now()
            self.resolved_by = user
            self.save()

    def can_resolve(self, user):
        """Check if user can resolve this feedback."""
        # Team members or guides can resolve feedback
        if user.is_student():
            # Check if user is on the project team
            return TeamMember.objects.filter(
                user=user,
                project=self.submission.project
            ).exists()
        elif user.is_guide() or user.is_admin():
            return True

        return False


class Evaluation(models.Model):
    """
    Evaluation by guide or coordinator with rating and comments.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='evaluations',
        help_text="Project being evaluated"
    )
    evaluator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evaluations_given',
        help_text="User who gave the evaluation"
    )
    phase = models.ForeignKey(
        Phase,
        on_delete=models.CASCADE,
        help_text="Phase this evaluation is for"
    )

    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Rating out of 5"
    )
    comments = models.TextField(
        help_text="Evaluation comments"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'evaluator', 'phase']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'phase']),
            models.Index(fields=['evaluator']),
        ]

    def __str__(self):
        return f"Evaluation by {self.evaluator} for {self.project.title} - {self.phase.get_name_display()}"



