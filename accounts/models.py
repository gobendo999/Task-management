from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name="Bio")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    location = models.CharField(max_length=100, blank=True, verbose_name="Location")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
