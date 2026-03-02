from django.db import models
from  theme.models import Theme
# Create your models here.
class SetId(models.Model):
    set_id = models.CharField(max_length=100,  db_index=True)
    
    def __str__(self):
        return str(self.set_id)


class SetInfo(models.Model):
    bricklink_name = models.CharField(max_length=10485759, null=True, blank=True)
    lego_name = models.CharField(max_length=10485759, null=True, blank=True)
    brickeconomy_name = models.CharField(max_length=10485759, null=True, blank=True)
    bricksandminifigsanaheim_name = models.CharField(max_length=10485759, null=True, blank=True)
    set = models.ForeignKey(SetId, on_delete=models.CASCADE)
    year = models.IntegerField(null=True, blank=True)
    lego_price = models.FloatField(null=True, blank=True)
    brickeconomy_description = models.TextField(null=True, blank=True)
    lego_description = models.TextField(null=True, blank=True)
    bricksandminifigsanaheim_desctiption = models.TextField(null=True, blank=True)
    weight = models.CharField(max_length=10485759, null=True, blank=True)
    dim = models.CharField(max_length=10485759, null=True, blank=True)
    parts = models.CharField(max_length=10485759, null=True, blank=True)
    themes = models.ManyToManyField(Theme)
    bricklink_url = models.URLField(null=True, blank=True, max_length=10485759)
    lego_url = models.URLField(null=True, blank=True, max_length=10485759)
    bricksandminifigsanaheim_url = models.URLField(null=True, blank=True, max_length=10485759)
    brickeconomy_url = models.URLField(null=True, blank=True, max_length=10485759)
    view_count = models.PositiveIntegerField(default=0)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.bricklink_name or self.lego_name or  self.brickeconomy_name  or self.bricksandminifigsanaheim_name)


class Sellers(models.Model):
    SOURCES = [
        ('brickLink','brickLink'),
        ('brickEconomy','brickEconomy'),
    ]
    
    set = models.ForeignKey(SetId, on_delete=models.CASCADE)
    name = models.CharField(max_length=10485759, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    condition = models.CharField(max_length=10485759, null=True, blank=True)
    country = models.CharField(max_length=10485759, null=True, blank=True)
    complete = models.CharField(max_length=10485759, null=True, blank=True)
    usd_price = models.FloatField(null=True, blank=True)
    real_price = models.CharField(max_length=10485759,null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    buy_url = models.URLField(null=True, blank=True, max_length=10485759)
    source = models.CharField(choices=SOURCES, max_length=10485759, db_index=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)
    
class Images(models.Model):
    set = models.ForeignKey(SetId, on_delete=models.CASCADE)
    link = models.URLField(max_length=10485759)


    def __str__(self):
        return str(self.link)


#class DailySetAverage(models.Model):
#    set = models.ForeignKey(SetId, on_delete=models.CASCADE)
#    date = models.DateField(db_index=True)
#    average_price = models.FloatField()
#    sellers_count = models.IntegerField()
#
#    class Meta:
#        unique_together = ("set", "date")
#
#    def __str__(self):
#        return f"{self.set} - {self.date} - {self.average_price}"