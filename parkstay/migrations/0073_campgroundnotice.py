# Generated by Django 3.2.4 on 2021-09-07 03:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0072_auto_20210805_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampgroundNotice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, default='', max_length=70, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('campground', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campground_notice', to='parkstay.campground')),
            ],
        ),
    ]
