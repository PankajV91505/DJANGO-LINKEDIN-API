from django.urls import path
from .views import trigger_scraper, homepage, JobListAPIView
from django.views.generic import RedirectView
from django.urls import re_path
from .views import job_create_list, job_update_delete

urlpatterns = [
    path('', homepage, name='homepage'),
    path('scrape/', trigger_scraper, name='scrape_linkedin'),

    # ✅ Add this API endpoint for GET request
    path('jobs/', job_create_list, name='job-create-list'),
    path('jobs/<int:pk>/', job_update_delete, name='job-update-delete'),

    
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]
