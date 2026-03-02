from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator

from set.models import SetId, SetInfo, Images, Sellers
from theme.models import Theme
from .models import Watchlist, Notification
from .forms import ItemSearchForm, BrowseFilterForm
from django.db.models.functions import TruncDate

def _get_set_display(set_info):
    """Get display name, price, description, image from SetInfo."""
    name = (set_info.bricklink_name or set_info.lego_name or set_info.brickeconomy_name or
            set_info.bricksandminifigsanaheim_name or 'Unknown')
    price = set_info.lego_price
    desc = (set_info.lego_description or set_info.brickeconomy_description or
            set_info.bricksandminifigsanaheim_desctiption or '')
    img = Images.objects.filter(set=set_info.set).first()
    image_url = img.link if img else ''
    return {'name': name, 'price': price, 'description': desc, 'image': image_url}


def home_view(request):
    """Home page with trending and recent sets."""
    set_infos = SetInfo.objects.select_related('set').prefetch_related('themes')
    trending = set_infos.order_by('-view_count')[:8]
    recent = set_infos.order_by('-id')[:8]
    themes = Theme.objects.filter(parent__isnull=True)[:8]

    def _item(set_info):
        d = _get_set_display(set_info)
        d['set_info'] = set_info
        d['code'] = set_info.set.set_id
        d['themes'] = set_info.themes.all()
        return d

    context = {
        'trending_items': [_item(s) for s in trending],
        'recent_items': [_item(s) for s in recent],
        'categories': themes,
    }
    return render(request, 'catalog/home.html', context)


def search_view(request):
    """Search sets by code or name."""
    form = ItemSearchForm(request.GET or None)
    items = []

    if form.is_valid() and form.cleaned_data.get('code'):
        q = form.cleaned_data['code'].strip()
        set_infos = SetInfo.objects.filter(
            Q(set__set_id__icontains=q) |
            Q(bricklink_name__icontains=q) |
            Q(lego_name__icontains=q) |
            Q(brickeconomy_name__icontains=q)
        ).select_related('set').prefetch_related('themes')[:20]

        for s in set_infos:
            d = _get_set_display(s)
            d['set_info'] = s
            d['code'] = s.set.set_id
            d['themes'] = s.themes.all()
            items.append(d)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        q = request.GET.get('q', '')[:50]
        suggestions = list(
            SetInfo.objects.filter(
                Q(set__set_id__icontains=q) | Q(bricklink_name__icontains=q) |
                Q(lego_name__icontains=q) | Q(brickeconomy_name__icontains=q)
            ).values('set__set_id', 'bricklink_name', 'lego_name', 'lego_price')[:10]
        )
        out = [{'code': x['set__set_id'], 'name': x['bricklink_name'] or x['lego_name'], 'price': x['lego_price']} for x in suggestions]
        return JsonResponse({'suggestions': out})

    context = {'form': form, 'items': items}
    return render(request, 'catalog/search.html', context)


def browse_view(request):
    """Browse sets with filters and pagination."""
    form = BrowseFilterForm(request.GET or None)
    set_infos = SetInfo.objects.select_related('set').prefetch_related('themes')

    if form.is_valid():
        if form.cleaned_data.get('category'):
            theme_ids = [form.cleaned_data['category'].id]
            theme_ids.extend(Theme.objects.filter(parent=form.cleaned_data['category']).values_list('id', flat=True))
            set_infos = set_infos.filter(themes__id__in=theme_ids).distinct()
        if form.cleaned_data.get('min_price') is not None:
            set_infos = set_infos.filter(lego_price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data.get('max_price') is not None:
            set_infos = set_infos.filter(lego_price__lte=form.cleaned_data['max_price'])
        sort = form.cleaned_data.get('sort_by') or '-view_count'
        set_infos = set_infos.order_by(sort)

    paginator = Paginator(set_infos, 24)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    def _item(s):
        d = _get_set_display(s)
        d['set_info'] = s
        d['code'] = s.set.set_id
        d['themes'] = s.themes.all()
        return d

    context = {
        'form': form,
        'page_obj': page_obj,
        'categories': Theme.objects.filter(parent__isnull=True),
        'items': [_item(s) for s in page_obj],
    }
    return render(request, 'catalog/browse.html', context)


def item_detail_view(request, code):
    """Set detail page."""
    set_obj = get_object_or_404(SetId, set_id=code)
    set_info = SetInfo.objects.filter(set=set_obj).select_related('set').prefetch_related('themes').first()
    if not set_info:
        return render(request, 'catalog/item_detail.html', {'item': None, 'code': code})

    # Increment view count
    set_info.view_count += 1
    set_info.save(update_fields=['view_count'])

    # Prepare item dict
    item = _get_set_display(set_info)
    item['set_info'] = set_info
    item['code'] = code
    item['themes'] = set_info.themes.all()
    item['images'] = list(Images.objects.filter(set=set_obj).values_list('link', flat=True))

    # Fetch sellers
    sellers = Sellers.objects.filter(set=set_obj).order_by('usd_price')

    # Watchlist info
    in_watchlist = False
    is_favorite = False
    if request.user.is_authenticated:
        w = Watchlist.objects.filter(user=request.user, set_obj=set_obj).first()
        if w:
            in_watchlist = True
            is_favorite = w.is_favorite

    # --- Calculate daily average prices for this set ---
    qs = (
        Sellers.objects
        .filter(set=set_obj, active=True, usd_price__isnull=False)
        .annotate(date=TruncDate('scraped_at'))
        .values('date')
        .annotate(avg_price=Avg('usd_price'))
        .order_by('date')
    )
    daily_avg_data = list(qs)  # list of dicts with 'date' and 'avg_price'

    # Pass all to template
    context = {
        'item': item,
        'code': code,
        'sellers': sellers,
        'in_watchlist': in_watchlist,
        'is_favorite': is_favorite,
        'daily_avg_data': daily_avg_data,  # <- this is for chart.js
    }

    return render(request, 'catalog/item_detail.html', context)


@login_required
def watchlist_view(request):
    """User's watchlist and favorites."""
    watchlist = Watchlist.objects.filter(user=request.user).select_related('set_obj')
    favorites = [w for w in watchlist if w.is_favorite]
    watching = [w for w in watchlist if not w.is_favorite]

    def _wrap(w):
        si = SetInfo.objects.filter(set=w.set_obj).prefetch_related('themes').first()
        if not si:
            return None
        d = _get_set_display(si)
        d['set_info'] = si
        d['code'] = w.set_obj.set_id
        d['watch'] = w
        return d

    context = {
        'favorites': [x for x in (_wrap(w) for w in favorites) if x],
        'watching': [x for x in (_wrap(w) for w in watching) if x],
    }
    return render(request, 'catalog/watchlist.html', context)


@login_required
def watchlist_add(request, code):
    set_obj = get_object_or_404(SetId, set_id=code)
    from django.urls import reverse
    Watchlist.objects.get_or_create(user=request.user, set_obj=set_obj, defaults={'is_favorite': False})
    messages.success(request, f'Added {code} to your watchlist.')
    return redirect(request.META.get('HTTP_REFERER') or reverse('catalog:item_detail', kwargs={'code': code}))


@login_required
def watchlist_remove(request, code):
    set_obj = get_object_or_404(SetId, set_id=code)
    Watchlist.objects.filter(user=request.user, set_obj=set_obj).delete()
    messages.success(request, f'Removed {code} from your watchlist.')
    from django.urls import reverse
    return redirect(request.META.get('HTTP_REFERER') or reverse('catalog:watchlist'))


@login_required
def watchlist_toggle_favorite(request, code):
    set_obj = get_object_or_404(SetId, set_id=code)
    w, created = Watchlist.objects.get_or_create(user=request.user, set_obj=set_obj)
    w.is_favorite = not w.is_favorite
    w.save()
    messages.success(request, f'Marked {code} as {"favorite" if w.is_favorite else "watchlist"}.')
    from django.urls import reverse
    return redirect(request.META.get('HTTP_REFERER') or reverse('catalog:watchlist'))


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).select_related('set_obj')[:50]
    return render(request, 'catalog/notifications.html', {'notifications': notifications})


@login_required
def notification_mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    return redirect('catalog:notifications')


@login_required
def notification_mark_all_read(request):
    Notification.objects.filter(user=request.user).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('catalog:notifications')


def autocomplete_view(request):
    q = request.GET.get('q', '')[:50]
    set_infos = SetInfo.objects.filter(
        Q(set__set_id__icontains=q) | Q(bricklink_name__icontains=q) |
        Q(lego_name__icontains=q) | Q(brickeconomy_name__icontains=q)
    ).select_related('set')[:10] if q else []
    items = [{'code': s.set.set_id, 'name': s.bricklink_name or s.lego_name, 'price': s.lego_price} for s in set_infos]
    return render(request, 'components/autocomplete_results.html', {'items': items})
