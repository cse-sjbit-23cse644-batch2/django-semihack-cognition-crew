from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


@require_http_methods(["GET", "POST"])
def login_page(request):
    """Render login page and handle authentication"""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the 'next' parameter if it exists, otherwise to dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            return render(request, 'auth/login.html', {'error': 'Invalid username or password'})
            
    return render(request, 'auth/login.html')


@require_http_methods(["GET", "POST"])
def signup_page(request):
    """Render signup page and handle user registration"""
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'STUDENT')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'auth/signup.html', {'error': 'Username already exists'})
            
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        return redirect('dashboard')
        
    return render(request, 'auth/signup.html')


@require_http_methods(["GET"])
@login_required
def dashboard(request):
    """Render dashboard based on user role"""
    context = {'user': request.user}
    
    if request.user.role == 'ADMIN':
        return render(request, 'dashboards/admin_dashboard.html', context)
    elif request.user.role == 'GUIDE':
        return render(request, 'dashboards/guide_dashboard.html', context)
    else:
        return render(request, 'dashboards/student_dashboard.html', context)


@require_http_methods(["POST"])
def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login_page')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_tokens(request):
    """Get JWT tokens for authenticated user"""
    user = request.user
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'domain': user.domain.name if user.domain else None,
        'bio': user.bio,
    })

