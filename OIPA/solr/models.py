from django.db import models


class ActivityDelete(models.Model):
    activity_id = models.IntegerField(default=0)
    last_updated_model = models.DateTimeField(
        null=True, blank=True, auto_now=True
    )


class TransactionDelete(models.Model):
    transaction_id = models.IntegerField(default=0)
    last_updated_model = models.DateTimeField(
        null=True, blank=True, auto_now=True
    )


class ResultDelete(models.Model):
    result_id = models.IntegerField(default=0)
    last_updated_model = models.DateTimeField(
        null=True, blank=True, auto_now=True
    )


class DatasetNoteDelete(models.Model):
    dataset_note_id = models.IntegerField(default=0)
    last_updated_model = models.DateTimeField(
        null=True, blank=True, auto_now=True
    )
