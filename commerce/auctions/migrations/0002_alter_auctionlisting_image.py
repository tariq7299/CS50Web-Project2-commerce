# Generated by Django 5.0 on 2023-12-14 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='auctions/images/'),
        ),
    ]