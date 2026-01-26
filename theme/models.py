from django.db import models

class Theme(models.Model):
    SOURCES = [
        ('bricklink','bricklink'),
        ('brickeconomy','brickeconomy'),
        ('lego','lego'),
        ('bricksandminifigsanaheim','bricksandminifigsanaheim'),
    ]
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=4000)
    source = models.CharField(choices=SOURCES, max_length=4000)

    def __str__(self):
        return str(self.name)
