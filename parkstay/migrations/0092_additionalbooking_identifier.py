# Generated by Django 3.2.4 on 2021-10-27 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0091_auto_20211026_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionalbooking',
            name='identifier',
            field=models.CharField(max_length=150, null=True, unique=True),
        ),
    ]