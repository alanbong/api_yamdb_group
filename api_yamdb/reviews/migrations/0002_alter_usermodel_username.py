# Generated by Django 3.2 on 2024-11-29 11:28

from django.db import migrations, models
import reviews.models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[reviews.models.validate_username], verbose_name='Username'),
        ),
    ]
