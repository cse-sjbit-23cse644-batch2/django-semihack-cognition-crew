from django.db import models
from projects.models import Submission

class SimilarityReport(models.Model):
    """Stores similarity detection results for submissions"""
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='similarity_report')

    # List of matched submission IDs and scores
    matches = models.JSONField(default=list, blank=True)  # [{'submission_id': 123, 'score': 0.85, 'reasons': {...}}, ...]

    highest_score = models.FloatField(default=0.0)
    flag_level = models.CharField(max_length=20, choices=[
        ('STRONG', 'Strong Warning'),
        ('MEDIUM', 'Suggestion'),
        ('NONE', 'No Warning')
    ], default='NONE')

    checked_at = models.DateTimeField(auto_now_add=True)
    override_reason = models.TextField(blank=True)  # If team chose to proceed anyway

    class Meta:
        ordering = ['-checked_at']

    def __str__(self):
        return f"Similarity report for {self.submission}"
