from django.urls import path
from django.conf.urls import url
from .views import (
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    # PaymentView,
    AddCouponView,
    RequestRefundView,
    stripe_config,
    create_checkout_session,
    verify_checkout,
    successView,
    stripe_webhook,
    OrderSnippetView,
    ViewOrders,
    CategoriesView,
    searchposts,
    cancelledView,
    admin_view

)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('adminpanel/' , admin_view , name = 'admin-panel'),
    path('category/<slug:slug>/', CategoriesView, name='category'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    # path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

    path('view-orders/' ,ViewOrders.as_view()  , name='view-orders'),
    path('order-snippet/' , OrderSnippetView.as_view() , name='order-snippet'),
    path('config/', stripe_config),
    path('verify-checkout/', verify_checkout, name='verify-checkout'),
    path('create-checkout-session/',
         create_checkout_session.as_view(), name='create-checkout'),
    path('success/', successView , name='successUrl'),
    path('cancelled/', cancelledView , name='cancelledUrl'),
    path('webhook/', stripe_webhook ),

    path('search/', searchposts, name='search'),


]
