# Generated by Django 5.0.2 on 2024-02-24 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, upload_to='store/static/media/product/'),
        ),
    ]
