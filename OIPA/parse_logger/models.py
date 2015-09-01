from django.db import models

# Create your models here.

class ParseLog(models.Model):
    file_name = models.CharField(max_length=256)
    location = models.CharField(max_length=512)
    error_time = models.DateTimeField()
    error_text = models.TextField()
    error_msg = models.TextField()
    error_hint = models.TextField()
    function_name = models.CharField(max_length=512,null=True,blank=True)

    def __unicode__(self,):
        return "%s - %s %s" % (self.file_name, self.location,self.error_text)

