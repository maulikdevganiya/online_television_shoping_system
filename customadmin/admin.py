from django.contrib import admin
from app.models import Order, OrderItem, Payment, Address, UserRegister, Product, Brand, Carousel, Cart, CartItem
from customadmin.models import Collection, CollectionProduct

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__name', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f"{queryset.count()} order(s) marked as processing.")
    mark_as_processing.short_description = "Mark selected orders as Processing"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f"{queryset.count()} order(s) marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f"{queryset.count()} order(s) marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} order(s) marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    readonly_fields = ('total_price',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'payment_status', 'amount', 'payment_date')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('order__order_number', 'transaction_id')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'pincode', 'is_default')
    list_filter = ('is_default', 'state')
    search_fields = ('user__name', 'user__email', 'full_name', 'city', 'state')

@admin.register(UserRegister)
class UserRegisterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile_number', 'created_at')
    search_fields = ('name', 'email', 'mobile_number')
    readonly_fields = ('created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'original_price', 'final_price', 'stock', 'discount_percentage')
    list_filter = ('brand', 'discount_percentage')
    search_fields = ('title', 'brand__bname')
    readonly_fields = ('final_price',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('bname', 'b_status')
    list_filter = ('b_status',)
    search_fields = ('bname',)

@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('c_title', 'sort_order', 'c_status')
    list_filter = ('c_status',)
    search_fields = ('c_title',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price', 'created_at')
    search_fields = ('user__name', 'user__email')
    readonly_fields = ('total_items', 'total_price', 'created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    readonly_fields = ('total_price',)

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'subtitle')

@admin.register(CollectionProduct)
class CollectionProductAdmin(admin.ModelAdmin):
    list_display = ('collection', 'product')
    list_filter = ('collection',)
    search_fields = ('collection__title', 'product__title')
