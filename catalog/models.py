from django.db import models
from django.contrib.auth.models import User

from set.models import SetId


class Watchlist(models.Model):
    """User's watchlist - sets they're tracking for notifications."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    set_obj = models.ForeignKey(SetId, on_delete=models.CASCADE, related_name='watchers')
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'set_obj']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} watching {self.set_obj.set_id}"


class Notification(models.Model):
    """In-app notifications for users."""
    NOTIFICATION_TYPES = [
        ('price_change', 'Price Change'),
        ('item_update', 'Item Update'),
        ('new_item', 'New Item in Watchlist'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    set_obj = models.ForeignKey(
        SetId,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"
