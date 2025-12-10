from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyImage, Inquiry, Category
from managerial.models import Commission
from accounts.models import User

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'date_joined', 'verified')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'verified')
    fieldsets = UserAdmin.fieldsets + (
        ('HouseFinder Info', {
            'fields': ('user_type', 'phone', 'national_id', 'kra_pin', 'verified', 'profile_image', 'bio')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('HouseFinder Info', {'fields': ('user_type', 'phone')}),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_count')
    search_fields = ('name',)
    
    def property_count(self, obj):
        return obj.properties.count()
    property_count.short_description = 'Properties'

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'manager', 'price', 'status', 'category', 'approved', 'views_count', 'created_at')
    list_filter = ('status', 'category', 'approved', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('views_count', 'created_at', 'slug')
    fieldsets = (
        ('Property Details', {
            'fields': ('title', 'slug', 'description', 'price', 'status', 'category', 'location', 'lat', 'lng')
        }),
        ('Features', {
            'fields': ('bedrooms', 'bathrooms', 'cover_image', 'is_featured')
        }),
        ('Manager & Status', {
            'fields': ('manager', 'approved', 'views_count', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images', 'manager')

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'is_primary', 'caption')
    list_filter = ('is_primary',)
    search_fields = ('property__title', 'caption')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('property__title', 'user__username', 'message')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('property', 'user')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('property', 'manager', 'amount', 'paid', 'mpesa_tx_id', 'paid_at')
    list_filter = ('paid', 'paid_at')
    search_fields = ('property__title', 'manager__username', 'mpesa_tx_id')
    readonly_fields = ('mpesa_tx_id', 'paid_at')
    fieldsets = (
        ('Commission Details', {
            'fields': ('property', 'manager', 'amount')
        }),
        ('Payment Status', {
            'fields': ('paid', 'mpesa_tx_id', 'paid_at')
        }),
    )
