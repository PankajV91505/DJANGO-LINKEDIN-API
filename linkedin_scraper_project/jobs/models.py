from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    link = models.URLField()  # ✅ Must be here
    time_posted = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title
