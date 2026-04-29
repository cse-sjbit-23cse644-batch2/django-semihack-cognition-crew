from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Notification


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """Get user's notifications"""
    user = request.user
    notifications = Notification.objects.filter(user=user)

    # Mark as read if requested
    if request.query_params.get('mark_read', '').lower() == 'true':
        unread = notifications.filter(read=False)
        unread.update(read=True, read_at=timezone.now())

    # Serialize
    data = []
    for notification in notifications[:20]:  # Limit to 20 most recent
        data.append({
            'id': notification.id,
            'type': notification.type,
            'title': notification.title,
            'message': notification.message,
            'link': notification.link,
            'created_at': notification.created_at.isoformat(),
            'read': notification.read,
            'read_at': notification.read_at.isoformat() if notification.read_at else None,
        })

    return Response({
        'notifications': data,
        'unread_count': notifications.filter(read=False).count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(pk=notification_id, user=request.user)
        notification.read = True
        notification.read_at = timezone.now()
        notification.save()

        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all user's notifications as read"""
    Notification.objects.filter(user=request.user, read=False).update(
        read=True,
        read_at=timezone.now()
    )

    return Response({'success': True})
