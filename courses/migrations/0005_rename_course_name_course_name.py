# Generated by Django 5.0.2 on 2024-02-22 06:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_textelement_videoelement'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='course_name',
            new_name='name',
        ),
    ]
