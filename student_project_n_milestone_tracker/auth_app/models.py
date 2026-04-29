"""
MilestoneTrack - User Authentication Models

Production-ready user model with role-based access control.
No external authentication - Django built-in auth only.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Supports role-based access control for the academic workflow system.
    Roles determine access levels and available actions.
    """

    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('GUIDE', 'Guide/Teacher'),
        ('COORDINATOR', 'Coordinator'),
        ('STUDENT', 'Student'),
    ]

    role = models.CharField(
        max_length=12,
        choices=ROLE_CHOICES,
        default='STUDENT',
        help_text="User role determines system access and permissions"
    )

    # Remove OAuth fields - using Django built-in auth only
    # oauth_provider = models.CharField(max_length=50, null=True, blank=True)

    # Optional profile fields
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Optional user biography"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="Profile picture (optional)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        """String representation showing full name and role."""
        full_name = self.get_full_name()
        display_name = full_name if full_name else self.username
        return f"{display_name} ({self.get_role_display()})"

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'ADMIN'

    def is_coordinator(self):
        """Check if user has coordinator role."""
        return self.role == 'COORDINATOR'

    def is_guide(self):
        """Check if user has guide role."""
        return self.role == 'GUIDE'

    def is_student(self):
        """Check if user has student role."""
        return self.role == 'STUDENT'

    def clean(self):
        """Custom validation for User model."""
        super().clean()

        # Ensure email is provided for all users
        if not self.email:
            raise ValidationError("Email address is required for all users.")

        # Admin and Guide roles require additional validation
        if self.role in ['ADMIN', 'GUIDE']:
            if not self.first_name or not self.last_name:
                raise ValidationError(
                    f"{self.get_role_display()}s must provide both first and last names."
                )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
