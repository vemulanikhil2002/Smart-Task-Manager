from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high',   '🔴 High'),
        ('medium', '🟡 Medium'),
        ('low',    '🟢 Low'),
    ]
    STATUS_CHOICES = [
        ('pending',     '⏳ Pending'),
        ('in_progress', '🔄 In Progress'),
        ('completed',   '✅ Completed'),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'priority']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def to_dict(self):
        return {
            'id':          self.id,
            'title':       self.title,
            'description': self.description,
            'priority':    self.priority,
            'status':      self.status,
            'created_at':  self.created_at.strftime('%Y-%m-%d %H:%M'),
        }
