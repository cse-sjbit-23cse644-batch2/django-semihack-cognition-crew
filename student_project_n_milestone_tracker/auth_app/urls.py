from django.urls import path
from . import views

urlpatterns = [
    # Auth pages
    path('login/', views.login_page, name='login_page'),
    path('signup/', views.signup_page, name='signup_page'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/tokens/', views.get_tokens, name='get_tokens'),
    path('api/profile/', views.user_profile, name='user_profile'),
]
