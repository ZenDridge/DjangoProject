# Generated by Django 5.1.2 on 2025-01-02 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_remove_membership_payment_proof_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='payment_proof',
            field=models.ImageField(blank=True, null=True, upload_to='payment_proofs/'),
        ),
    ]
