from django.contrib import admin
from .models import CustomerProfile, Product, Category, CartItem, Cart, Payment, Order, OrderItem
# Register your models here.

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'slug', 'image_preview', 'created_at')  # Add image preview
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    
    fields = ('name', 'price', 'stock', 'category', 'description', 'slug', 'image')
    
    add_fieldsets = (
        (None, {
            'fields': ('name', 'price', 'stock', 'category', 'description', 'slug', 'image')
        }),
    )
    
    # Add a method to preview the image in the admin list display
    def image_preview(self, obj):
        return f'<img src="{obj.image.url}" width="50" height="50" />' if obj.image else 'No image'

    image_preview.allow_tags = True 

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Payment)
admin.site.register(OrderItem)
admin.site.register(Order)
