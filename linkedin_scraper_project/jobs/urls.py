from django.urls import path
from .views import trigger_scraper, homepage, JobListAPIView
from django.views.generic import RedirectView
from django.urls import re_path

urlpatterns = [
    path('', homepage, name='homepage'),
    path('scrape/', trigger_scraper, name='scrape_linkedin'),

    # ✅ Add this API endpoint for GET request
    path('jobs/', JobListAPIView.as_view(), name='job-list'),
    
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]
