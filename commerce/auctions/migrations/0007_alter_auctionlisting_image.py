# Generated by Django 5.0 on 2023-12-14 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_auctionlisting_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='image',
            field=models.ImageField(blank=True, default='auctions/images/default.jpg', null=True, upload_to='auctions/images/'),
        ),
    ]