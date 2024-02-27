from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Product, Category, Order, OrderItem, Profile
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied


# Assume these models are defined in your models.py
# from .models import Product, Category, Order, OrderItem

# Custom Admin for Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock',
                    'available', 'created', 'updated')
    list_editable = ('price', 'stock', 'available')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('available', 'created', 'updated')


admin.site.site_header = "Alimama Administration"
admin.site.site_title = "Alimama Admin Portal"
admin.site.index_title = "Welcome to the Alimama Admin Portal"
admin.site.register(Product, ProductAdmin)

# Custom Admin for Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)

# Inline Admin for Order Items within Order Admin


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False

# Custom Admin for Order


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'billingName', 'emailAddress', 'status', 'created')
#     search_fields = ('id', 'emailAddress', 'status')
#     readonly_fields = ('id', 'token', 'total', 'emailAddress', 'billingName', 'billingCity', 'billingPostcode',
#                        'billingCountry', 'shippingName', 'shippingCity', 'shippingPostcode', 'shippingCountry', 'status')
#     inlines = (OrderItemAdmin,)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'billingName', 'emailAddress',
                    'status', 'created']  # Added 'status' to the list
    list_display_links = ('id', 'billingName')
    search_fields = ['id', 'token', 'total', 'emailAddress',
                     'status']  # Optionally add 'status' to search fields
    readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created', 'billingName', 'billingAddress1', 'billingCity',
                       'billingPostcode', 'billingCountry', 'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry', 'status']  # Include 'status' here if you want it read-only

    fieldsets = [
        # Added 'status' to the ORDER INFORMATION section
        ('ORDER INFORMATION', {'fields': [
         'id', 'token', 'total', 'status', 'created']}),
        ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity',
                                            'billingPostcode', 'billingCountry', 'emailAddress']}),
        ('SHIPPING INFORMATION', {'fields': [
         'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry']})
    ]

    inlines = [OrderItemAdmin,]

    def has_add_permission(self, request):
        return False

# Custom Admin for User to restrict access


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ['address_street', 'address_houseNo', 'address_city',
              'address_postcode', 'address_country', 'phone_number', 'birthday', 'role']
    # Make role read-only if it's automatically determined
    readonly_fields = ['role']


# class CustomUserAdmin(BaseUserAdmin):
#     # Corrected from ProfileInLine to ProfileInline
#     inlines = (ProfileInline, )
#     list_display = ('username', 'first_name',
#                     'last_name', 'is_staff', 'get_groups', 'phone_number', 'address')

#     def phone_number(self, obj):
#         try:
#             return obj.profile.phone_number
#         except Profile.DoesNotExist:
#             return "No profile"
#     phone_number.short_description = 'Phone Number'

#     def address(self, instance):
#         return f"{instance.profile.address_street}, {instance.profile.address_houseNo}, {instance.profile.address_city}, {instance.profile.address_postcode}, {instance.profile.address_country}"
#     address.short_description = 'Address'

#     def get_groups(self, obj):
#         return ", ".join([group.name for group in obj.groups.all()])
#     get_groups.short_description = 'Role'

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.groups.filter(name='Seller_Admin').exists():
#             # Limit to users who are part of the 'Sellers' group only
#             return qs.filter(groups__name='Seller')
#         # If not 'Sellers Admin', return default queryset
#         return qs
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'first_name', 'last_name',
                    'is_staff', 'get_groups', 'phone_number', 'address')

    def phone_number(self, obj):
        try:
            return obj.profile.phone_number
        except Profile.DoesNotExist:
            return "No profile"
    phone_number.short_description = 'Phone Number'

    def address(self, instance):
        try:
            return f"{instance.profile.address_street}, {instance.profile.address_houseNo}, {instance.profile.address_city}, {instance.profile.address_postcode}, {instance.profile.address_country}"
        except Profile.DoesNotExist:
            return "No profile"
    address.short_description = 'Address'

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Seller_Admin').exists():
            return qs.filter(groups__name='Seller')
        return qs


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Optionally, customize the Group admin to restrict visibility of groups if needed


# class CustomGroupAdmin(admin.ModelAdmin):
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         # Example: limit visible groups for non-superusers
#         if not request.user.is_superuser:
#             return qs.exclude(name='Sudo')
#         return qs


# admin.site.unregister(Group)
# admin.site.register(Group, CustomGroupAdmin)


@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
    fk_name = 'user'
    exclude = ['user',]
    fields = ['address_street', 'address_houseNo', 'address_city',
              'address_postcode', 'address_country', 'phone_number', 'birthday', 'role']
    readonly_fields = ['role']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.is_staff:  # Assuming 'admin users' means staff users
            return qs.filter(user=request.user)
        return qs.none()  # Hide all profiles if conditions above are not met

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            self.exclude = ("user",)
        form = super(UserProfileAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)
# @admin.register(Profile)
# class UserProfileAdmin(admin.ModelAdmin):
#     fk_name = 'user'
#     # Exclude the user field from the form to prevent users from changing it.
#     exclude = ['user',]

#     fields = ['address_street', 'address_houseNo', 'address_city',
#               'address_postcode', 'address_country', 'phone_number', 'birthday', 'role']
#     # Make role read-only if it's automatically determined
#     readonly_fields = ['role']

#     # Customize this admin class as needed

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         return qs.filter(user=request.user)

#     def get_form(self, request, obj=None, **kwargs):
#         if not request.user.is_superuser:
#             self.exclude = ("user",)
#         form = super(UserProfileAdmin, self).get_form(request, obj, **kwargs)
#         return form

#     def save_model(self, request, obj, form, change):
#         if not obj.user_id:
#             obj.user = request.user
#         super().save_model(request, obj, form, change)
# 3 ########################################
# from typing import Any
# from django.contrib import admin
# from django.contrib.admin.options import InlineModelAdmin
# from .models import Product, Category, Order, OrderItem
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

# from django.contrib.auth.models import User
# from django.utils.html import format_html_join
# from django.utils.safestring import mark_safe
# from django.conf import settings
# from .models import Profile
# from django.utils.html import format_html
# from guardian.admin import GuardedModelAdmin


# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'price', 'stock',
#                     'available', 'created', 'updated']
#     list_editable = ['price', 'stock', 'available']
#     prepopulated_fields = {'slug': ('name',)}
#     list_per_page = 15
#     search_fields = ['name', 'description']
#     list_filter = ['available', 'created', 'updated']
#     date_hierarchy = 'created'


# # Register Product model with ProductAdmin to apply the customizations
# admin.site.site_header = "Alimama Administration"
# admin.site.site_title = "Alimama Admin Portal"
# admin.site.index_title = "Welcome to the Alimama Admin Portal"
# admin.site.register(Product, ProductAdmin)


# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'slug', 'description']
#     list_per_page = 15
#     prepopulated_fields = {'slug': ('name',)}


# # Register Category model with CategoryAdmin to apply the customizations
# admin.site.register(Category, CategoryAdmin)


# class OrderItemAdmin(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     readonly_fields = ['product', 'quantity', 'price']
#     can_delete = False


# # `@admin.register(Order)
# # class OrderAdmin(admin.ModelAdmin):
# #     list_display = ['id', 'billingName', 'emailAddress',
# #                     'status', 'created']  # Added 'status' to the list
# #     list_display_links = ('id', 'billingName')
# #     search_fields = ['id', 'token', 'total', 'emailAddress',
# #                      'status']  # Optionally add 'status' to search fields
# #     readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created', 'billingName', 'billingAddress1', 'billingCity',
# #                        'billingPostcode', 'billingCountry', 'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry', 'status']  # Include 'status' here if you want it read-only

# #     fieldsets = [
# #         # Added 'status' to the ORDER INFORMATION section
# #         ('ORDER INFORMATION', {'fields': [
# #          'id', 'token', 'total', 'status', 'created']}),
# #         ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity',
# #                                             'billingPostcode', 'billingCountry', 'emailAddress']}),
# #         ('SHIPPING INFORMATION', {'fields': [
# #          'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry']})
# #     ]

# #     inlines = [OrderItemAdmin,]

# #     def has_add_permission(self, request):
# #         return False

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user_info', 'billingName',
#                     'emailAddress', 'status', 'created']
#     list_display_links = ('id', 'billingName')
#     search_fields = ['id', 'token', 'total', 'emailAddress',
#                      'status', 'user__username', 'user__email']  # Added user lookup
#     readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created', 'billingName', 'billingAddress1', 'billingCity',
#                        'billingPostcode', 'billingCountry', 'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry', 'status', 'user_info']

#     fieldsets = [
#         ('ORDER INFORMATION', {'fields': [
#          'id', 'token', 'total', 'status', 'created', 'user_info']}),
#         ('BILLING INFORMATION', {'fields': ['billingName', 'billingAddress1', 'billingCity',
#                                             'billingPostcode', 'billingCountry', 'emailAddress']}),
#         ('SHIPPING INFORMATION', {'fields': [
#          'shippingName', 'shippingAddress1', 'shippingCity', 'shippingPostcode', 'shippingCountry']})
#     ]

#     inlines = [OrderItemAdmin,]

#     def user_info(self, obj):
#         if obj.user:  # Checking if there's a user associated with the order
#             return format_html(
#                 "<div><b>Username:</b> {}<br><b>Full Name:</b> {} {}<br><b>Email:</b> {}</div>",
#                 obj.user.username,
#                 obj.user.first_name,
#                 obj.user.last_name,
#                 obj.user.email
#             )
#         else:
#             return "User account deleted"
#     user_info.short_description = "User Info"

#     def has_add_permission(self, request):
#         return False


# class UserAdmin(BaseUserAdmin):
#     # Extend the existing list_display to include 'group_names'
#     list_display = BaseUserAdmin.list_display + ('group_names',)

#     def group_names(self, obj):
#         # Returns a comma-separated list of groups the user belongs to.
#         groups = obj.groups.all()
#         return ', '.join(group.name for group in groups)
#     group_names.short_description = 'Groups'

#     def get_queryset(self, request):
#         # Optimize query to prefetch related groups
#         queryset = super().get_queryset(request)
#         queryset = queryset.prefetch_related('groups')
#         return queryset


# # Unregister the original User admin and register the customized one
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)


# class ProfileInLine(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     # Optionally specify fields to include
#     fields = ['address_street', 'address_houseNo', 'address_city',
#               'address_postcode', 'address_country', 'phone_number', 'birthday', 'role']


# class CustomUserAdmin(BaseUserAdmin):
#     inlines = (ProfileInLine, )
#     list_display = ('username', 'first_name',
#                     'last_name', 'is_staff', 'get_groups', 'phone_number', 'address')

#     def phone_number(self, obj):
#         # Assuming every User has a Profile. If not, you might want to handle DoesNotExist exception.
#         return obj.profile.phone_number
#     phone_number.short_description = 'Phone Number'

#     def address(self, instance):
#         return f"{instance.profile.address_street}, {instance.profile.address_houseNo}, {instance.profile.address_city}, {instance.profile.address_postcode}, {instance.profile.address_country}"
#     address.short_description = 'Address'

#     def get_groups(self, obj):
#         return ", ".join([group.name for group in obj.groups.all()])
#     get_groups.short_description = 'Role'


# # This ensures the extended functionality is correctly applied to the User model in the Django admin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
