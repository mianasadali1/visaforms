from django.db import models


class VisaApplication(models.Model):
    session_id = models.CharField(max_length=50)
    succeed = models.BooleanField(default=False)

    def __str__(self):
        return self.session_id
