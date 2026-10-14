from django.db import models
from django.conf import settings


class Task(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
        verbose_name="User"
    )
    title = models.CharField(max_length=200, default='', verbose_name="Task Title")
    description = models.TextField(blank=True, verbose_name="Description")
    completed = models.BooleanField(default=False, verbose_name="Completed")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'completed']),
        ]

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{self.title} ({username})"