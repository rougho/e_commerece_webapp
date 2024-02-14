from django.contrib import admin
from django.http import HttpRequest
from .models import Product, Category, Order, OrderItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
import stripe
from django.conf import settings


# Define ProductAdmin to customize the admin interface for Products


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock',
                    'available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 15


# Register Product model with ProductAdmin to apply the customizations
admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    list_per_page = 15
    prepopulated_fields = {'slug': ('name',)}


# Register Category model with CategoryAdmin to apply the customizations
admin.site.register(Category, CategoryAdmin)


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    fieldsets = [
        ('Product', {'fields': ['product'], }),
        ('Quantity', {'fields': ['quantity'], }),
        ('Price', {'fields': ['price'], }),
    ]
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'billingName', 'emailAddress', 'created']
    list_display_links = ('id', 'billingName')
    search_fields = ['id', 'token', 'total', 'emailAddress']
    readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created', 'billingName', 'billingAddress1', 'billingCity',
                       'billingPostcode', 'billingCountry', 'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry']

    fieldsets = [
        ('ORDER INFORMATION', {'fields': ['id', 'token', 'total', 'created']}),
        ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity',
                                            'billingPostcode', 'billingCountry', 'emailAddress']}),
        ('SHIPPING INFORMATION', {'fields': [
         'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry']})
    ]

    inlines = [
        OrderItemAdmin,
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


# stripe.api_key = settings.STRIPE_SECRET_KEY


# class OrderItemAdmin(admin.TabularInline):
#     model = OrderItem
#     fieldsets = [
#         ('Product', {'fields': ['product'], }),
#         ('Quantity', {'fields': ['quantity'], }),
#         ('Price', {'fields': ['price'], }),
#     ]
#     readonly_fields = ['product', 'quantity', 'price']


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'billingName', 'emailAddress',
#                     'total', 'stripe_charge_id', 'created']
#     list_display_links = ('id', 'billingName')
#     search_fields = ['id', 'token', 'total', 'emailAddress']
#     readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created', 'billingName', 'billingAddress1', 'billingCity',
#                        'billingPostcode', 'billingCountry', 'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry', 'stripe_charge_id']

#     fieldsets = [
#         ('ORDER INFORMATION', {'fields': ['id', 'token', 'total', 'created']}),
#         ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity',
#                                             'billingPostcode', 'billingCountry', 'emailAddress']}),
#         ('SHIPPING INFORMATION', {'fields': [
#          'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry']})
#     ]

#     inlines = [
#         OrderItemAdmin,
#     ]

#     def has_delete_permission(self, request, obj=None):
#         return False

#     def has_add_permission(self, request):
#         return False

#     def stripe_charge_id(self, obj):
#         # Retrieve the stripe charge id based on the order token
#         try:
#             charge = stripe.Charge.retrieve(obj.token)
#             return charge.id
#         except stripe.error.StripeError as e:
#             return None

#     stripe_charge_id.short_description = 'Stripe Charge ID'


class UserAdmin(BaseUserAdmin):
    # Extend the existing list_display to include 'group_names'
    list_display = BaseUserAdmin.list_display + ('group_names',)

    def group_names(self, obj):
        # Returns a comma-separated list of groups the user belongs to.
        groups = obj.groups.all()
        return ', '.join(group.name for group in groups)
    group_names.short_description = 'Groups'

    def get_queryset(self, request):
        # Optimize query to prefetch related groups
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('groups')
        return queryset


# Unregister the original User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
