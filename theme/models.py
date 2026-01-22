from django.db import models

class Theme(models.Model):
    SOURCES = [
        ('BrickLink','BrickLink'),
        ('BrickEconomy','BrickEconomy'),
    ]
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    source = models.CharField(choices=SOURCES, max_length=200)

    def __str__(self):
        return str(self.name)
