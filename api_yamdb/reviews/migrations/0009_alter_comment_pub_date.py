# Generated by Django 3.2 on 2024-11-26 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0008_alter_comment_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
    ]
