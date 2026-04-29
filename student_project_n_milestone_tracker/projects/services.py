"""
Phase management and version control services
"""
from django.utils import timezone
from django.db.models import Q
from .models import Submission, Phase, Version, Feedback
import os


class PhaseService:
    """Manages phase workflow and unlocking logic"""
    
    @staticmethod
    def get_team_current_phase(team):
        """Get the current phase for a team (highest approved phase + 1)"""
        last_approved = team.submissions.filter(
            status='APPROVED'
        ).order_by('-phase__order').first()
        
        if not last_approved:
            # No phases completed, return first phase
            return Phase.objects.order_by('order').first()
        
        next_phase = Phase.objects.filter(
            order__gt=last_approved.phase.order
        ).order_by('order').first()
        
        return next_phase
    
    @staticmethod
    def can_unlock_phase(team, phase):
        """Check if a team can unlock/submit to a phase"""
        if phase.order == 1:
            # Synopsis is always unlocked
            return True
        
        # Get previous phase
        prev_phase = Phase.objects.filter(
            order=phase.order - 1
        ).first()
        
        if not prev_phase:
            return True
        
        # Check if previous phase is approved AND all feedback resolved
        prev_submission = team.submissions.filter(phase=prev_phase).first()
        
        if not prev_submission:
            return False
        
        if prev_submission.status != 'APPROVED':
            return False
        
        # Check all feedback on all versions of previous phase is resolved
        unresolved_feedback = Feedback.objects.filter(
            version__submission=prev_submission,
            resolved=False
        ).exists()
        
        return not unresolved_feedback
    
    @staticmethod
    def unlock_phase_if_eligible(team, phase):
        """Attempt to unlock next phase if current conditions met"""
        if phase.order < 5:  # Not the last phase
            next_phase = Phase.objects.filter(order=phase.order + 1).first()
            if next_phase:
                next_submission = team.submissions.filter(phase=next_phase).first()
                if next_submission and next_submission.status == 'DRAFT':
                    return PhaseService.can_unlock_phase(team, next_phase)
        
        return False
    
    @staticmethod
    def approve_submission(submission):
        """Approve a submission and check for phase unlock"""
        submission.status = 'APPROVED'
        submission.approved_at = timezone.now()
        submission.save()
        
        # Check if next phase should unlock
        team = submission.team
        next_phase = Phase.objects.filter(
            order=submission.phase.order + 1
        ).first()
        
        if next_phase and PhaseService.can_unlock_phase(team, next_phase):
            return {
                'approved': True,
                'next_phase_unlocked': True,
                'next_phase': next_phase.get_name_display(),
            }
        
        return {
            'approved': True,
            'next_phase_unlocked': False,
        }


class VersionService:
    """Manages version control and file uploads"""
    
    ALLOWED_EXTENSIONS = ['pdf', 'ppt', 'pptx']
    MAX_FILE_SIZE = 52428800  # 50MB in bytes
    
    @staticmethod
    def validate_file(file_obj):
        """Validate file type and size"""
        errors = []
        
        # Check file size
        if file_obj.size > VersionService.MAX_FILE_SIZE:
            errors.append(f'File size exceeds {VersionService.MAX_FILE_SIZE / (1024*1024):.0f}MB limit')
        
        # Check file extension
        _, ext = os.path.splitext(file_obj.name)
        ext = ext.lstrip('.').lower()
        
        if ext not in VersionService.ALLOWED_EXTENSIONS:
            errors.append(f'File type .{ext} not allowed. Allowed: {", ".join(VersionService.ALLOWED_EXTENSIONS)}')
        
        return errors
    
    @staticmethod
    def create_version(submission, file_obj, change_summary, uploaded_by):
        """Create a new version for a submission"""
        # Validate file
        errors = VersionService.validate_file(file_obj)
        if errors:
            return {'success': False, 'errors': errors}
        
        # Get next version number
        last_version = submission.versions.order_by('-version_number').first()
        next_version_num = (last_version.version_number + 1) if last_version else 1
        
        # Create version
        version = Version.objects.create(
            submission=submission,
            version_number=next_version_num,
            file=file_obj,
            change_summary=change_summary,
            uploaded_by=uploaded_by,
            metadata={
                'file_size': file_obj.size,
                'file_type': file_obj.content_type,
                'original_name': file_obj.name,
            }
        )
        
        # Update submission status
        submission.status = 'SUBMITTED'
        if not submission.submitted_at:
            submission.submitted_at = timezone.now()
        submission.save()
        
        return {
            'success': True,
            'version_id': version.id,
            'version_number': version.version_number,
        }
    
    @staticmethod
    def get_version_timeline(submission):
        """Get all versions with feedback for a submission"""
        versions = submission.versions.prefetch_related('feedbacks').order_by('version_number')
        
        timeline = []
        for version in versions:
            feedback_data = [
                {
                    'id': f.id,
                    'comment': f.comment,
                    'guide': f.guide.username if f.guide else None,
                    'resolved': f.resolved,
                    'created_at': f.created_at.isoformat(),
                }
                for f in version.feedbacks.all()
            ]
            
            timeline.append({
                'version_number': version.version_number,
                'uploaded_at': version.uploaded_at.isoformat(),
                'uploaded_by': version.uploaded_by.username if version.uploaded_by else None,
                'change_summary': version.change_summary,
                'file_name': os.path.basename(version.file.name) if version.file else None,
                'file_url': version.file.url if version.file else None,
                'metadata': version.metadata,
                'feedback_count': len(feedback_data),
                'feedback': feedback_data,
                'unresolved_feedback_count': sum(1 for f in feedback_data if not f['resolved']),
            })
        
        return timeline
