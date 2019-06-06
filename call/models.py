from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from call.config import Constants


class Call(models.Model):
    type = models.CharField(max_length=5)
    timestamp = models.DateTimeField()
    call_id = models.PositiveIntegerField()
    source = models.CharField(max_length=11, blank=True, null=True)
    destination = models.CharField(max_length=11, blank=True, null=True)

    def __str__(self):
        return "Call from %s to %s" % (self.source, self.destination)

    class Meta:
        # same type and identifier means duplicate call
        unique_together = ('type', 'call_id')


class Bill(models.Model):
    """ This model it's necessary because:

        It's important to notice that the price rules can change from time to time, but an already calculated call
        price can not change.

    """

    destination = models.ForeignKey(
        Call,
        on_delete=models.SET_NULL,
        related_name='call_destination',
        null=True
    )
    start_date = models.DateField()
    start_time = models.TimeField()
    duration = models.CharField(max_length=10)
    month = models.IntegerField(default=datetime.now().month)
    year = models.IntegerField(default=datetime.now().year)
    price = models.CharField(max_length=10)

    def __str__(self):
        return "Bill for %s" % self.destination
