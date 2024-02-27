from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])


# class Product(models.Model):
#     name = models.CharField(max_length=250, unique=True)
#     slug = models.SlugField(max_length=250, unique=True)
#     description = models.TextField(blank=True)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     image = models.ImageField(upload_to='product', blank=True)
#     stock = models.IntegerField()
#     available = models.BooleanField(default=True)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ('name', )
#         verbose_name = 'product'
#         verbose_name_plural = 'products'

#     def get_url(self):
#         return reverse('product_detail', args=[self.category.slug, self.slug])

#     def __str__(self):
#         return self.name

class Product(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    # Assuming 'Category' is defined elsewhere
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product', blank=True)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    # Changed to auto_now for updates
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.stock < 0:
            raise ValidationError("Stock cannot be less than 0.")
        super(Product, self).save(*args, **kwargs)


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'CartItem'

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='orders', null=True)
    token = models.CharField(max_length=250, blank=True)
    total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='EUR Order Total')
    emailAddress = models.EmailField(
        max_length=250, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    billingName = models.CharField(
        max_length=250, blank=True)
    billingAddress1 = models.CharField(
        max_length=250, blank=True)
    billingCity = models.CharField(
        max_length=250, blank=True)
    billingPostcode = models.CharField(
        max_length=250, blank=True)
    billingCountry = models.CharField(
        max_length=250, blank=True)
    shippingName = models.CharField(
        max_length=250, blank=True)
    shippingAddress1 = models.CharField(
        max_length=250, blank=True)
    shippingCity = models.CharField(
        max_length=250, blank=True)
    shippingPostcode = models.CharField(
        max_length=250, blank=True)
    shippingCountry = models.CharField(
        max_length=250, blank=True)
    # item_name = models.CharField(max_length=350, blank=True)
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Canceled', 'Canceled'),
        ('Completed', 'Completed'),
    )

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='Active')

    class Meta:
        db_table = 'Order'
        ordering = ['-created']

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    product = models.CharField(max_length=250)
    quantity = models.IntegerField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='EUR Order Total')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        db_table = 'OrderItem'

    def sub_total(self):
        return self.quantity * self.price

    def __str__(self):
        return self.product


# class Profile(models.Model):
#     CUSTOMER = 1
#     SELLER = 2
#     S_ADMIN = 3
#     SUDO = 4
#     ROLE_CHOICE = (
#         (CUSTOMER, 'Customer'),
#         (SELLER, 'Seller'),
#         (S_ADMIN, 'Seller_admin'),
#         (SUDO, 'Sudo')

#     )
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # email = models.EmailField(max_length=250, blank=True)
#     address_street = models.CharField(max_length=200, blank=True)
#     address_houseNo = models.CharField(max_length=50, blank=True)
#     address_city = models.CharField(max_length=200, blank=True)
#     address_postcode = models.CharField(max_length=200, blank=True)
#     address_country = models.CharField(max_length=200, blank=True)
#     phone_number = models.CharField(max_length=200, blank=True)
#     birthday = models.DateField(null=True, blank=True)
#     role = models.PositiveSmallIntegerField(
#         choices=ROLE_CHOICE, null=True, blank=True)

#     def __str__(self):
#         return self.user.username

#     def save(self, *args, **kwargs):
#         if self.user.groups.filter(name="Customers").exists():
#             self.role = Profile.CUSTOMER
#         elif self.user.groups.filter(name="Sellers").exists():
#             self.role = Profile.SELLER
#         # Add more conditions as needed based on your group-to-role mapping
#         super(Profile, self).save(*args, **kwargs)


# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     instance.profile.save()


class Profile(models.Model):
    CUSTOMER = 1
    SELLER = 2
    S_ADMIN = 3
    SUDO = 4
    ROLE_CHOICE = (
        (CUSTOMER, 'Customer'),
        (SELLER, 'Seller'),
        (S_ADMIN, 'Seller_Admin'),
        (SUDO, 'Sudo'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_street = models.CharField(max_length=200, blank=True)
    address_houseNo = models.CharField(max_length=50, blank=True)
    address_city = models.CharField(max_length=200, blank=True)
    address_postcode = models.CharField(max_length=200, blank=True)
    address_country = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=200, blank=True)
    birthday = models.DateField(null=True, blank=True)
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICE, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Fetch the user's groups to minimize database queries
        user_groups = set(self.user.groups.values_list('name', flat=True))

        if "Customer" in user_groups:
            self.role = Profile.CUSTOMER
        elif "Seller" in user_groups:
            self.role = Profile.SELLER
        elif "Seller_admin" in user_groups:
            self.role = Profile.S_ADMIN
        elif "Sudo" in user_groups:
            self.role = Profile.SUDO

        super(Profile, self).save(*args, **kwargs)

# Signal to update the Profile role when a User's groups change


@receiver(m2m_changed, sender=User.groups.through)
def update_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
