"""
Django signals for automated notifications
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Submission, Version, Feedback, Project, TeamMember, Evaluation
from notifications.models import Notification


@receiver(post_save, sender=Version)
def notify_new_submission(sender, instance, created, **kwargs):
    """Notify guide when a new version is uploaded"""
    if created:
        submission = instance.submission
        project = submission.project

        if project.guide:
            Notification.objects.create(
                user=project.guide,
                type='NEW_SUBMISSION',
                title=f'New Submission from {project.title}',
                message=f'New version uploaded for {submission.phase.get_name_display()}',
                link=f'/projects/submissions/{submission.id}/'
            )


@receiver(post_save, sender=Feedback)
def notify_feedback_given(sender, instance, created, **kwargs):
    """Notify team members when feedback is given"""
    if created:
        submission = instance.submission
        project = submission.project

        # Notify all team members
        for team_member in project.team_members.all():
            Notification.objects.create(
                user=team_member.user,
                type='FEEDBACK',
                title=f'New Feedback on {submission.phase.get_name_display()}',
                message=f'Your guide has provided feedback on your submission',
                link=f'/projects/submissions/{submission.id}/'
            )


@receiver(pre_save, sender=Submission)
def check_phase_completion(sender, instance, **kwargs):
    """Check if all projects under a guide have completed a phase"""
    if instance.pk:  # Only for updates
        old_instance = Submission.objects.get(pk=instance.pk)

        # If status changed to APPROVED, notify coordinator
        if old_instance.status != 'APPROVED' and instance.status == 'APPROVED':
            project = instance.project
            if project.coordinator:
                Notification.objects.create(
                    user=project.coordinator,
                    type='GUIDE_APPROVAL',
                    title=f'Guide Approved: {project.title}',
                    message=f'Guide has approved {instance.phase.get_name_display()}. Ready for coordinator review.',
                    link=f'/projects/{project.id}/'
                )


@receiver(post_save, sender=Evaluation)
def notify_evaluation(sender, instance, created, **kwargs):
    """Notify relevant users when evaluation is given"""
    if created:
        project = instance.project
        evaluator = instance.evaluator

        # If guide evaluated, notify coordinator if assigned
        if evaluator.is_guide() and project.coordinator:
            Notification.objects.create(
                user=project.coordinator,
                type='GUIDE_EVALUATION',
                title=f'Guide Evaluation: {project.title}',
                message=f'Guide has evaluated {instance.phase.get_name_display()} with rating {instance.rating}/5',
                link=f'/projects/{project.id}/'
            )
        # If coordinator evaluated, notify team members
        elif evaluator.is_coordinator():
            for team_member in project.team_members.all():
                Notification.objects.create(
                    user=team_member.user,
                    type='COORDINATOR_EVALUATION',
                    title=f'Coordinator Evaluation: {project.title}',
                    message=f'Coordinator has evaluated {instance.phase.get_name_display()} with rating {instance.rating}/5',
                    link=f'/projects/{project.id}/'
                )


@receiver(pre_save, sender=Project)
def notify_coordinator_approval(sender, instance, **kwargs):
    """Notify students when coordinator approves final project"""
    if instance.pk:
        old_instance = Project.objects.get(pk=instance.pk)

        # If publication status changed to APPROVED or PUBLISHED
        if (old_instance.publication_status in ['PENDING', 'REJECTED'] and
            instance.publication_status in ['APPROVED', 'PUBLISHED']):

            for team_member in instance.team_members.all():
                Notification.objects.create(
                    user=team_member.user,
                    type='PROJECT_APPROVED',
                    title=f'Project Approved: {instance.title}',
                    message=f'Your project has been approved by the coordinator with status: {instance.publication_status}',
                    link=f'/projects/{instance.id}/'
                )
        if old_instance.status != 'APPROVED' and instance.status == 'APPROVED':
            # Phase was just approved
            _check_guide_phase_completion(instance)


def _check_guide_phase_completion(submission):
    """Check if all projects under a guide have completed this phase"""
    project = submission.project
    if not project.guide:
        return

    phase = submission.phase
    guide_projects = Project.objects.filter(guide=project.guide)

    # Check if all projects have approved this phase
    total_projects = guide_projects.count()
    completed_projects = 0

    for guide_project in guide_projects:
        project_submission = Submission.objects.filter(
            project=guide_project,
            phase=phase,
            status='APPROVED'
        ).exists()
        if project_submission:
            completed_projects += 1

    if completed_projects == total_projects:
        # All projects completed this phase - notify coordinator (admin)
        from auth_app.models import User
        admins = User.objects.filter(role='ADMIN')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                type='PHASE_COMPLETE',
                title=f'Phase {phase.get_name_display()} Completed',
                message=f'All projects under {project.guide.get_full_name()} have completed {phase.get_name_display()}',
                link=f'/admin/projects/phase/{phase.id}/progress/'
            )