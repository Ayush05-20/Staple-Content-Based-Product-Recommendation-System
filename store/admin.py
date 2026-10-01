from django.contrib import admin
from .models import Product, Interaction


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category_display', 'price', 'created_at')
    search_fields = ('name', 'brand', 'category', 'tags')
    list_filter = ('brand',)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'action', 'timestamp')
    list_filter = ('action',)
