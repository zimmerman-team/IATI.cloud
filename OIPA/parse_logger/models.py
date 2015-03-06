from django.db import models

# Create your models here.

class ParseLog(models.Model):
    file_name = models.CharField(max_length=256)
    location = models.CharField(max_length=512)
    error_time = models.DateTimeField()
    error_text = models.TextField()
    error_hint = models.TextField()

