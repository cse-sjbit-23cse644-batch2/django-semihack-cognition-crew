from django.urls import path
from . import views

urlpatterns = [
    path('check-title/', views.check_title_similarity, name='check_title_similarity'),
    path('report/<int:submission_id>/', views.get_similarity_report, name='get_similarity_report'),
]