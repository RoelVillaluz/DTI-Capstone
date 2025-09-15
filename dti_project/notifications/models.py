from django.db import models
from users.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils import timezone
from django.utils.dateformat import DateFormat

# Create your models here.

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    message = models.TextField()
    url = models.URLField(blank=True, null=True) # optional: link to a page
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    # Generic relation fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    document = GenericForeignKey("content_type", "object_id")

    NOTIFICATION_TYPES = [
        ("update_request", "Update Request"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("info", "Info"),
    ]
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="info")

    def __str__(self):
        status = "Unread" if not self.is_read else "Read"
        return f"{status} Notification for {self.user.username}: {self.message[:20]}"
    
    def display_message(self):
        sender_name = self.sender.get_full_name() if self.sender else 'System'
        doc_name = (
            self.content_type.model_class()._meta.verbose_name.title()
            if self.content_type else "Document"
        )

        if self.type == 'update_request':
            msg = f'<strong>{sender_name}</strong> <span>wants to update your</span> <strong>{doc_name}</strong>'
        elif self.type == 'approved':
            msg = f'<span>Your</span> <strong>{doc_name}</strong> <span>has been approved.</span>'
        elif self.type == 'rejected':
            msg = f'<span>Your</span> <strong>{doc_name}</strong> <span>has been rejected.</span>'
        elif self.type == "info":
            msg = f'<span>{self.message}</span>' or f'<span>New notification regarding</span> <strong>{doc_name}</strong>.'
        else:
            msg = f'<span>{self.message}</span>' or "<span>You have a new notification.</span>"

        return mark_safe(msg)
    
    def time_display(self):
        """Return human-readable time since creation"""
        now = timezone.now()
        delta = now - self.date

        if delta.days == 0:
            return timesince(self.date, now) + ' ago'
        elif delta.days < 7:
            # Between 1–6 days → show "x days ago"
            return f'{delta.days} day{'s' if delta.days > 1 else ''} ago'
        else:
            return DateFormat(self.date).format("M d, Y")  # Example: Jan 13, 2025