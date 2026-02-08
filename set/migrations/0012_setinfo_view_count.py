from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('set', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='setinfo',
            name='view_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
