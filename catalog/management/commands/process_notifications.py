"""
Management command for notification processing.
Schedule via cron: python manage.py process_notifications
"""
from django.core.management.base import BaseCommand

from catalog.models import Notification
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Process notifications (placeholder for batch/digest logic)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        for profile in UserProfile.objects.filter(notification_frequency='weekly'):
            count = Notification.objects.filter(user=profile.user, is_read=False).count()
            if count and not options['dry_run']:
                self.stdout.write(f"User {profile.user.username}: {count} unread notifications")
        self.stdout.write(self.style.SUCCESS('Done'))
