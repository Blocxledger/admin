import secrets
import markdown
import bleach
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings

from .models import Article, Category, Subscriber

ALLOWED_TAGS = list(bleach.ALLOWED_TAGS) + [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'hr', 'pre', 'code',
    'img', 'figure', 'figcaption',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'blockquote', 'details', 'summary',
    'dl', 'dt', 'dd',
]
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
    'code': ['class'],
}


def render_markdown(text):
    html = markdown.markdown(
        text,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
        ],
        output_format='html5',
    )
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)


def article_list(request):
    articles = Article.objects.filter(is_published=True).select_related('author', 'category')
    categories = Category.objects.all()

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/list.html', context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    article.content_html = render_markdown(article.content)

    related = Article.objects.filter(
        is_published=True, category=article.category
    ).exclude(pk=article.pk)[:4]

    context = {
        'article': article,
        'related': related,
    }
    return render(request, 'blog/detail.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(
        is_published=True, category=category
    ).select_related('author', 'category')

    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    categories = Category.objects.all()

    context = {
        'category': category,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/category.html', context)


def subscribe(request):
    if request.method != 'POST':
        return redirect('blog:list')

    email = request.POST.get('email', '').strip().lower()
    if not email:
        messages.error(request, 'Please enter a valid email address.')
        return redirect('blog:list')

    subscriber, created = Subscriber.objects.get_or_create(
        email=email,
        defaults={'token': secrets.token_hex(32)},
    )

    if created:
        messages.success(request, 'You are subscribed! You will receive notifications when new articles are published.')
    elif subscriber.is_active:
        messages.info(request, 'This email is already subscribed.')
    else:
        subscriber.is_active = True
        subscriber.save()
        messages.success(request, 'Your subscription has been reactivated!')

    return redirect('blog:list')


def unsubscribe(request, token):
    subscriber = Subscriber.objects.filter(token=token, is_active=True).first()
    if subscriber:
        subscriber.is_active = False
        subscriber.save()
        messages.success(request, 'You have been unsubscribed.')
    else:
        messages.info(request, 'Subscription not found or already inactive.')
    return redirect('blog:list')
