from typing import Any
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from .models import Product, Category, Order, OrderItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.conf import settings
from .models import Profile
from django.utils.html import format_html


# Define ProductAdmin to customize the admin interface for Products


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock',
                    'available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 15
    search_fields = ['name', 'description']
    list_filter = ['available', 'created', 'updated']
    date_hierarchy = 'created'


# Register Product model with ProductAdmin to apply the customizations
admin.site.site_header = "Alimama Administration"
admin.site.site_title = "Alimama Admin Portal"
admin.site.index_title = "Welcome to the Alimama Admin Portal"
admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    list_per_page = 15
    prepopulated_fields = {'slug': ('name',)}


# Register Category model with CategoryAdmin to apply the customizations
admin.site.register(Category, CategoryAdmin)


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False


# `@admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'billingName', 'emailAddress',
#                     'status', 'created']  # Added 'status' to the list
#     list_display_links = ('id', 'billingName')
#     search_fields = ['id', 'token', 'total', 'emailAddress',
#                      'status']  # Optionally add 'status' to search fields
#     readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created', 'billingName', 'billingAddress1', 'billingCity',
#                        'billingPostcode', 'billingCountry', 'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry', 'status']  # Include 'status' here if you want it read-only

#     fieldsets = [
#         # Added 'status' to the ORDER INFORMATION section
#         ('ORDER INFORMATION', {'fields': [
#          'id', 'token', 'total', 'status', 'created']}),
#         ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity',
#                                             'billingPostcode', 'billingCountry', 'emailAddress']}),
#         ('SHIPPING INFORMATION', {'fields': [
#          'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry']})
#     ]

#     inlines = [OrderItemAdmin,]

#     def has_add_permission(self, request):
#         return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_info', 'billingName',
                    'emailAddress', 'status', 'created']
    list_display_links = ('id', 'billingName')
    search_fields = ['id', 'token', 'total', 'emailAddress',
                     'status', 'user__username', 'user__email']  # Added user lookup
    readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created', 'billingName', 'billingAddress1', 'billingCity',
                       'billingPostcode', 'billingCountry', 'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry', 'status', 'user_info']

    fieldsets = [
        ('ORDER INFORMATION', {'fields': [
         'id', 'token', 'total', 'status', 'created', 'user_info']}),
        ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity',
                                            'billingPostcode', 'billingCountry', 'emailAddress']}),
        ('SHIPPING INFORMATION', {'fields': [
         'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry']})
    ]

    inlines = [OrderItemAdmin,]

    def user_info(self, obj):
        if obj.user:  # Checking if there's a user associated with the order
            return format_html(
                "<div><b>Username:</b> {}<br><b>Full Name:</b> {} {}<br><b>Email:</b> {}</div>",
                obj.user.username,
                obj.user.first_name,
                obj.user.last_name,
                obj.user.email
            )
        else:
            return "User account deleted"
    user_info.short_description = "User Info"

    def has_add_permission(self, request):
        return False


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


class ProfileInLine(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    # Optionally specify fields to include
    fields = ['address_street', 'address_houseNo', 'address_city',
              'address_postcode', 'address_country', 'phone_number', 'birthday', 'role']


class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInLine, )
    list_display = ('username', 'first_name',
                    'last_name', 'is_staff', 'get_groups', 'phone_number', 'address')

    def phone_number(self, obj):
        # Assuming every User has a Profile. If not, you might want to handle DoesNotExist exception.
        return obj.profile.phone_number
    phone_number.short_description = 'Phone Number'

    def address(self, instance):
        return f"{instance.profile.address_street}, {instance.profile.address_houseNo}, {instance.profile.address_city}, {instance.profile.address_postcode}, {instance.profile.address_country}"
    address.short_description = 'Address'

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Role'


# This ensures the extended functionality is correctly applied to the User model in the Django admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
