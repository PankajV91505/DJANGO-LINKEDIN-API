from django.urls import path
from .views import trigger_scraper, homepage

urlpatterns = [
    path('', homepage, name='homepage'),
    path('scrape/', trigger_scraper, name='scrape_linkedin'),
]
