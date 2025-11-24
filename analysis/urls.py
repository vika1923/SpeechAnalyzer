from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('about', views.about, name='about'),
    path('api/start-upload', views.start_upload, name='start_upload'),
    path('api/upload', views.upload_video, name='upload_video'),
    path('api/job/<str:job_id>', views.get_job_status, name='get_job_status'),
    path('api/jobs', views.list_jobs, name='list_jobs'),
    path('api/health', views.health_check, name='health_check'),
]
