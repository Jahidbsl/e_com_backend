from django.contrib import admin

# Register your models here.
from .models import Category, Product, UseerProfile, Order, OrderItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(UseerProfile)
admin.site.register(Order)
admin.site.register(OrderItem)
