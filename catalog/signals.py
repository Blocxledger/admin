from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from set.models import SetInfo
from .models import Watchlist, Notification

_old_prices = {}


@receiver(pre_save, sender=SetInfo)
def store_old_price(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = SetInfo.objects.get(pk=instance.pk)
            _old_prices[instance.pk] = old.lego_price
        except SetInfo.DoesNotExist:
            pass


@receiver(post_save, sender=SetInfo)
def notify_on_price_change(sender, instance, created, **kwargs):
    """Notify watchers when lego_price changes."""
    if created or instance.lego_price is None:
        if instance.pk in _old_prices:
            del _old_prices[instance.pk]
        return
    old_price = _old_prices.pop(instance.pk, None)
    if old_price is None or float(old_price) == float(instance.lego_price):
        return
    watchers = Watchlist.objects.filter(set_obj=instance.set).select_related('user')
    for watch in watchers:
        if watch.user.profile.notification_frequency != 'none':
            Notification.objects.create(
                user=watch.user,
                set_obj=instance.set,
                notification_type='price_change',
                message=f"Price update for {instance.set.set_id}: ${old_price} → ${instance.lego_price}",
            )
