from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from set.models import DailySetAverage, Sellers


def calculate_daily_averages():
    now = timezone.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    qs = (
        Sellers.objects
        .filter(
            scraped_at__gte=start,
            scraped_at__lt=end,
            usd_price__isnull=False
        )
        .values("set")   # ✅ only group by set
        .annotate(
            avg_price=Avg("usd_price"),
            total=Count("id")
        )
    )

    for row in qs:
        DailySetAverage.objects.update_or_create(
            set_id=row["set"],
            date=start.date(),
            defaults={
                "average_price": row["avg_price"],
                "sellers_count": row["total"]
            }
        )