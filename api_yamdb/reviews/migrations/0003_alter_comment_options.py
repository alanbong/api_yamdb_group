# Generated by Django 3.2 on 2024-11-28 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_alter_customuser_role'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
    ]
