# Generated by Django 4.2.5 on 2023-11-22 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_doctorprofile_service_charge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prescription',
            name='appointment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.appointment'),
        ),
    ]