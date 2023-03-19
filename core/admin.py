from django.contrib import admin

from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ref_code',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'badge', 'price', 'discount_price', 'category', 'brand', 'label', 'slug',
        'descriptionFo', 'image', 'stripe_key'
    ]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ordered', 'item', 'quantity', 'ordered_date',
    ]


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ref_code', 'stripe_charge_id', 'amount', 'timestamp'
    ]


class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'amount'
    ]


class RefundAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'reason', 'accepted', 'email'
    ]


admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Refund, RefundAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
