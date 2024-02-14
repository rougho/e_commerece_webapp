from django.contrib import admin
from .models import Product, Category

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
