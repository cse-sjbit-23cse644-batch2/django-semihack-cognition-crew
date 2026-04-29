from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from projects.models import Project, Submission
from .models import Notification

@receiver(post_save, sender=Submission)
def notify_on_submission_approval(sender, instance, created, **kwargs):
    """Notify coordinator when guide approves a submission."""
    if not created:
        # Check if status changed to APPROVED
        # Note: Ideally we'd compare with previous status, but post_save doesn't provide it easily
        # For simplicity, we'll check if status is APPROVED and it's not the final approval
        if instance.status == 'APPROVED' and instance.project.coordinator:
            # Notify Coordinator
            title = f"Phase Approved: {instance.project.title}"
            message = f"Guide has approved {instance.phase.get_name_display()} for project '{instance.project.title}'. It is now ready for your review if all phases are complete."
            
            # In-app notification
            Notification.objects.create(
                user=instance.project.coordinator,
                type='PHASE_COMPLETE',
                title=title,
                message=message,
                link=f"/dashboard/coordinator/" # Or specific project detail link
            )
            
            # Email notification
            try:
                send_mail(
                    title,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.project.coordinator.email],
                    fail_silently=True,
                )
            except Exception:
                pass

@receiver(post_save, sender=Project)
def notify_on_coordinator_approval(sender, instance, created, **kwargs):
    """Notify students when coordinator approves the final submission (project completed)."""
    if not created:
        # Check if publication_status changed to APPROVED/PUBLISHED
        if instance.publication_status in ['APPROVED', 'PUBLISHED'] and instance.status == 'COMPLETED':
            # Notify Students (Team Members)
            title = f"Project Finalized: {instance.title}"
            message = f"Congratulations! Your project '{instance.title}' has been finalized and approved by the coordinator. Publication status: {instance.get_publication_status_display()}."
            
            for member in instance.team_members.all():
                # In-app notification
                Notification.objects.create(
                    user=member.user,
                    type='PHASE_COMPLETE',
                    title=title,
                    message=message,
                    link=f"/dashboard/student/"
                )
                
                # Email notification
                try:
                    send_mail(
                        title,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [member.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
