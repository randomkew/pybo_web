# Generated by Django 3.1.3 on 2022-06-08 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0008_delete_questioncount'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='hit',
            field=models.IntegerField(default=0),
        ),
    ]