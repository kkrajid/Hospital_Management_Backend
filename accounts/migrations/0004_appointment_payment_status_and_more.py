# Generated by Django 4.2.5 on 2023-11-25 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_prescription_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed'), ('Refunded', 'Refunded')], default='Pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='icu_status',
            field=models.CharField(choices=[('ICU Admitted', 'ICU Admitted'), ('ICU Critical', 'ICU Critical'), ('ICU Recovered', 'ICU Recovered'), ('ICU Not Needed', 'ICU Not Needed'), ('ICU Discharged', 'ICU Discharged')], default='ICU Not Needed', max_length=20),
        ),
    ]