from django.urls import path
from .views import trigger_scraper, homepage

urlpatterns = [
    path('', homepage, name='homepage'),
    path('scrape/', trigger_scraper, name='scrape_linkedin'),
]
from django.views.generic import RedirectView
from django.urls import re_path

urlpatterns += [
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]