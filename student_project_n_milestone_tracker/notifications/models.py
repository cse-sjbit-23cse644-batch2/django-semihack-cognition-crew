from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    """In-app notifications"""
    TYPE_CHOICES = [
        ('PHASE_COMPLETE', 'Phase Completed'),
        ('NEW_SUBMISSION', 'New Submission'),
        ('DEADLINE', 'Deadline Alert'),
        ('FEEDBACK', 'New Feedback'),
        ('PHASE_UNLOCK', 'Phase Unlocked'),
        ('SIMILARITY_WARNING', 'Similarity Warning'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.CharField(max_length=500)
    link = models.CharField(max_length=500, blank=True)  # URL to relevant object

    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read']),
            models.Index(fields=['user', 'type']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_type_display()}"
