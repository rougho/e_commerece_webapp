from django.contrib import admin
from .models import Product, Category
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

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
