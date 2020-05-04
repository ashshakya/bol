# Generated by Django 3.0.5 on 2020-05-03 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transport',
            name='shipment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='shipments.Shipment'),
        ),
    ]
