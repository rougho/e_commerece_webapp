# Generated by Django 5.0.1 on 2024-02-14 13:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_cart_cartitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=250)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='EUR Order Total')),
                ('emailAddress', models.EmailField(blank=True, max_length=250, verbose_name='Email Address')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('billingName', models.CharField(blank=True, max_length=250, verbose_name='Billing Name')),
                ('billingAddress1', models.CharField(blank=True, max_length=250, verbose_name='Billing Address 1')),
                ('billingCity', models.CharField(blank=True, max_length=250, verbose_name='Billing City')),
                ('billingPostcode', models.CharField(blank=True, max_length=250, verbose_name='Billing Postcode')),
                ('billingCountry', models.CharField(blank=True, max_length=250, verbose_name='Billing Country')),
                ('shippingName', models.CharField(blank=True, max_length=250, verbose_name='Shipping Name')),
                ('shippingAddress1', models.CharField(blank=True, max_length=250, verbose_name='Shipping Address 1')),
                ('shippingCity', models.CharField(blank=True, max_length=250, verbose_name='Shipping City')),
                ('shippingPostcode', models.CharField(blank=True, max_length=250, verbose_name='Shipping Postcode')),
                ('shippingCountry', models.CharField(blank=True, max_length=250, verbose_name='Shipping Country')),
            ],
            options={
                'db_table': 'Order',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='EUR Order Total')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.order')),
            ],
            options={
                'db_table': 'OrderItem',
            },
        ),
    ]
