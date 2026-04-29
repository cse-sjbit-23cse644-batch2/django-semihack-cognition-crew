from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from projects.models import Project
from .services import SimilarityDetector
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_title_similarity(request):
    """Check similarity of a project title against existing titles"""
    title = request.data.get('title', '').strip()

    if not title:
        return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Get all existing team titles
    existing_titles = Project.objects.exclude(title__isnull=True).exclude(title='').values_list('title', flat=True)

    # Check similarity
    detector = SimilarityDetector()
    results = detector.check_title_similarity(title, existing_titles)

    # Filter results with score > 0.3
    significant_matches = [r for r in results if r['score'] > 0.3][:5]  # Top 5 matches

    # Determine overall flag
    highest_score = max([r['score'] for r in significant_matches]) if significant_matches else 0.0
    flag_level = detector.get_similarity_flag(highest_score)

    return Response({
        'title': title,
        'matches': significant_matches,
        'highest_score': highest_score,
        'flag_level': flag_level,
        'can_proceed': flag_level != 'STRONG'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_similarity_report(request, submission_id):
    """Get similarity report for a submission"""
    try:
        from projects.models import Submission, SimilarityReport
        submission = Submission.objects.get(pk=submission_id)

        # Check permissions
        user = request.user
        if user.role == 'STUDENT' and user not in submission.team.members.all():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        if user.role == 'GUIDE' and submission.team.guide != user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        report = SimilarityReport.objects.filter(submission=submission).first()
        if not report:
            return Response({'error': 'No similarity report found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'submission_id': submission.id,
            'matches': report.matches,
            'highest_score': report.highest_score,
            'flag_level': report.flag_level,
            'checked_at': report.checked_at.isoformat(),
            'override_reason': report.override_reason
        })

    except Submission.DoesNotExist:
        return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
