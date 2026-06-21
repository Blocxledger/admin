from django.db import models
from django.contrib.auth.models import User

from set.models import SetId


class HomeSection(models.Model):
    """A configurable section on the homepage (e.g., 'Trending', 'Newest Sets')."""
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0, help_text="Lower numbers appear first.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class HomeSectionItem(models.Model):
    """A product item within a home section."""
    section = models.ForeignKey(HomeSection, on_delete=models.CASCADE, related_name='items')
    set_obj = models.ForeignKey(SetId, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, help_text="Order within the section.")

    class Meta:
        ordering = ['order', 'id']
        unique_together = ['section', 'set_obj']

    def __str__(self):
        return f"{self.section.name} - {self.set_obj.set_id}"


class WatchlistGroup(models.Model):
    """User-defined groups for organizing watchlist items."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_groups')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username}'s {self.name} group"


class Watchlist(models.Model):
    """User's watchlist - sets they're tracking for notifications."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    set_obj = models.ForeignKey(SetId, on_delete=models.CASCADE, related_name='watchers')
    group = models.ForeignKey(
        WatchlistGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='items'
    )
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'set_obj', 'group']
        ordering = ['-created_at']

    def __str__(self):
        group_name = self.group.name if self.group else "General"
        return f"{self.user.username} watching {self.set_obj.set_id} in {group_name}"


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
