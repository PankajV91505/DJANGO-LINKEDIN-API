from django.db import models
from datetime import datetime

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    time_posted = models.CharField(max_length=255)
    description = models.TextField()
    scraped_date = models.DateField(default=datetime.today)
    scraped_time = models.TimeField(default=datetime.now)

    def __str__(self):
        return self.title
