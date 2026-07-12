from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Article, Subscriber


@receiver(post_save, sender=Article)
def notify_subscribers_on_publish(sender, instance, created, **kwargs):
    if not instance.is_published:
        return
    if not created:
        return

    subscribers = Subscriber.objects.filter(is_active=True).values_list('email', 'token')
    if not subscribers:
        return

    site_url = getattr(settings, 'SITE_URL', 'https://www.blocxledger.com')
    article_url = f"{site_url}/blog/{instance.slug}/"

    subject = f"New on Blocxledger: {instance.title}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@blocxledger.com')

    messages = []
    for email, token in subscribers:
        unsubscribe_url = f"{site_url}/blog/unsubscribe/{token}/"
        html_body = render_to_string('blog/email_notification.html', {
            'article': instance,
            'article_url': article_url,
            'unsubscribe_url': unsubscribe_url,
        })
        messages.append((subject, html_body, from_email, [email]))

    try:
        send_mass_mail(messages, fail_silently=True)
    except Exception:
        pass
