from django.contrib import admin
from properties.models import Property, PropertyImage, Inquiry, Category
from managerial.models import Commission

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_count')
    search_fields = ('name',)
    
    def property_count(self, obj):
        return obj.properties.count()
    property_count.short_description = 'Properties'

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'manager', 'price', 'listing_status', 'category', 'approved', 'views_count', 'created_at')
    list_filter = ('listing_status', 'category', 'approved', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('views_count', 'created_at', 'slug')
    fieldsets = (
        ('Property Details', {
            'fields': ('title', 'slug', 'description', 'price', 'workflow_status', 'category', 'location', 'lat', 'lng')
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
