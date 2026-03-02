# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction


from theme.models import Theme
from .models import (
    SetId,
    Images,
    SetInfo,
    Sellers,
)


@csrf_exempt
def ingest_set(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    with transaction.atomic():

        # -------------------
        # SET ID
        # -------------------
        set_obj, _ = SetId.objects.get_or_create(
            set_id=data.get("set_id")
        )

        # -------------------
        # THEMES (hierarchy)
        # category = ["City", "Town"]
        # -------------------
        parent = None
        category = data.get("category", [])
        if category:
            if isinstance(category, list):
                for name in category:
                    parent, _ = Theme.objects.get_or_create(
                        name=name,
                        parent=parent,
                        source=data["source"]
                    )
            else:
                parent, _ = Theme.objects.get_or_create(
                        name=category,
                        source=data["source"]
                    )
        else:
            print(data)
        

        # -------------------
        # SET INFO
        # -------------------
        set_info, _ = SetInfo.objects.update_or_create(
            set=set_obj,
            defaults={
                "lego_name": data["name"] if data["source"] == "LEGO" else None,
                "year": data.get("year"),
                "weight": data.get("weight"),
                "dim": data.get("dim"),
                "parts": data.get("parts"),
                "bricklink_name": data["name"] if data["source"].lower() == "bricklink" else None,
                'bricklink_url': data.get("url") if data["source"].lower() == "bricklink" else None,
                'brickeconomy_url': data.get("url") if data["source"].lower() == "brickeconomy" else None,
                "brickeconomy_name": data["name"] if data["source"].lower() == "brickeconomy" else None,
                "brickeconomy_description": data.get("description") if data["source"].lower() == "brickeconomy" else None,
                'bricksandminifigsanaheim_desctiption': data.get("description") if data["source"].lower() == "bricksandminifigsanaheim" else None,
                'bricksandminifigsanaheim_name': data.get("name") if data["source"].lower() == "bricksandminifigsanaheim" else None,
                'bricksandminifigsanaheim_url': data.get("url") if data["source"].lower() == "bricksandminifigsanaheim" else None,
                'lego_url': data.get("url") if data["source"] == "LEGO" else None,
                "lego_description": data.get("description") if data["source"] == "LEGO" else None,
            }
        )
        if not set_info.themes.filter(id=parent.id).exists():
            set_info.themes.add(parent)

        # -------------------
        # IMAGES
        # -------------------
        for img in data.get("images", []):
            Images.objects.get_or_create(
                set=set_obj,
                link=img
            )
        if img := data.get('image'):
            Images.objects.get_or_create(
                set=set_obj,
                link=img
            )
        # -------------------
        # SELLERS
        # -------------------
        Sellers.objects.filter(
            set=set_obj,
            source=data.get("source")
        ).update(active=False)

        for s in data.get("sellers", []):
            Sellers.objects.create(
                set=set_obj,
                name=s.get("seller_name"),
                description=s.get("seller_description"),
                condition=s.get("condition"),
                country=s.get("country"),
                complete=s.get("complete"),
                usd_price=s.get("usd_price"),
                real_price=s.get("real_price"),
                quantity=s.get("quantity"),
                buy_url=s.get("buy_url"),
                source=data.get("source"),
                active=True
            )

    return JsonResponse({
        "status": "ok",
        "set_id": set_obj.set_id
    })

from django.http import JsonResponse
from django.db.models import Avg
from django.db.models.functions import TruncDate
from .models import Sellers

def avg_prices_per_date(request, set_id):
    """
    Returns JSON with average USD price per day for a given set
    """
    # Filter active sellers with valid price for the given set
    qs = (
        Sellers.objects
        .filter(set_id=set_id, active=True, usd_price__isnull=False)
        # Truncate datetime to date
        .annotate(date=TruncDate('scraped_at'))
        # Group by date and calculate average price
        .values('date')
        .annotate(avg_price=Avg('usd_price'))
        .order_by('date')
    )

    # Convert queryset to list of dicts for JSON
    data = list(qs)

    return JsonResponse(data, safe=False)