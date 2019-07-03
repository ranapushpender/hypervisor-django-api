# Generated by Django 2.0.5 on 2019-06-23 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('os', models.CharField(max_length=30)),
                ('image', models.ImageField(blank=True, default='default.png', upload_to='')),
            ],
        ),
    ]