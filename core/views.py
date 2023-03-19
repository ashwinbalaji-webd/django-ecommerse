import random
import string
from django.http import JsonResponse, response, HttpResponse
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test

from django.urls import reverse
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

DATETIME = datetime.today().date()


@login_required
def verify_checkout(request):
    if request.method == 'GET':
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            # form = CheckoutForm()
            context = {
                'order': order,
            }
            return render(request, "verify_checkout.html", context)
        except:
            return Http404


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        print('----->GET checkout')
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        print('----->POST checkout')
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # print("==>order==>" , order)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                        return redirect('core:checkout')

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")
                        return redirect('core:checkout')

                # payment_option = form.cleaned_data.get('payment_option')

                # if payment_option == 'S':
                #     return redirect('core:payment', payment_option='stripe')
                # elif payment_option == 'P':
                #     return redirect('core:payment', payment_option='paypal')
                # else:
                #     messages.warning(
                #         self.request, "Invalid payment option selected")
            return redirect('core:verify-checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")



class create_checkout_session(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        orderedItems = []
        for order_item in order.items.all():
            orderedItems.append(
                {
                    'price': order_item.item.stripe_key,
                    'quantity': order_item.quantity
                }
            )
        domain_url = 'http://' + self.request.META['HTTP_HOST'] + '/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
        
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=self.request.user.id if self.request.user.is_authenticated else None,
                success_url=domain_url +
                'success?session_id={CHECKOUT_SESSION_ID}&',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=orderedItems
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        


def successView(request):

    checkout_detail = stripe.checkout.Session.retrieve(
        request.GET.get('session_id'),
    )
    order = Order.objects.filter(user=request.user, ordered = False)
    ref_id = order[0].ref_code
    amount_paid = checkout_detail['amount_total']//100
    payment_intent = checkout_detail['payment_intent']
    now = timezone.localtime(timezone.now())
    payment = Payment.objects.create(user=request.user, ref_code=ref_id,
                                     stripe_charge_id=payment_intent, amount=amount_paid, timestamp=now)
    Order.objects.filter(user=request.user, ordered=False).update(ordered=True)
    OrderItem.objects.filter(user=request.user, ordered=False).update(
        ordered=True, ordered_date=DATETIME)

    if (payment):
        messages.info(request, 'Order Placed')
        return redirect('/')
    else:
        return redirect('cancelled/')


def cancelledView(self, *args, **kwargs):
    messages.error(self.request, 'Payment unsuccessful')
    return redirect('/verify-checkout/')





class OrderSnippetView(View, LoginRequiredMixin):
    # def get(self, *args , **kwargs):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_snippet.html', context)
        except ObjectDoesNotExist:
            print('from snippet')
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")
        # return render(self.request , 'order_snippet.html')


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


@csrf_exempt
def stripe_webhook(request):
    # to login : $ stripe login / stripe listen --forward-to localhost:8000/webhook/
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

# de6th3qvhyrvjz2k0si4

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # ref_id = create_ref_code()
        # print('ref===============>' ,ref_id )
        print('event==============>', event.data.object.payment_intent)
        # print('amount=============>' , event.data.object.amount_total//100)
        # print(request.user)

        # test = Order.objects.filter(user=request.user, ordered=False).update(ordered = True)
        # print('sdsa',test)

        # now = timezone.localtime(timezone.now())

        # Payment.objects.create(stripe_charge_id = event.data.object.payment_intent,
        # user = 'admin' , amount = event.data.object.amount_total//100 , timestamp = now )

        # TODO: run some cu
        # stom code here

    return HttpResponse(status=200)


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"


def CategoriesView(request, slug):
    item = Item.objects.filter(category=slug)
    return render(request, 'home.html', {'object_list': item})


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }

            print("====>", order.items.all())
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            print('from cart')
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class ViewOrders(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        try:
            orders = Order.objects.filter(user=self.request.user, ordered=True)

            order_items = []

            # for order in orders:
            #     items = order.items.all()
            #     order_items.append(items[0])

            # context = {
            #     'order_items': orders,
            # }

            order_items = []
            for order in orders:
                items = order.items.all()
                order_items.append({
                    'order': order,
                    'items': items,
                })

            context = {
                'order_items': order_items,
            }

            return render(self.request, 'view_orders.html', context)
        except ObjectDoesNotExist:
            print('from orders')
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            # messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            # messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.localtime(timezone.now())
        ref_id = create_ref_code()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date, ref_code=ref_id)
        order.items.add(order_item)
        # messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            # messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            # messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        print("coupon===>", coupon)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                print("code=====>", code)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")


def searchposts(request):
    if request.method == 'POST':  # this will be GET now
        item_name = request.POST['search']  # do some research what it does
        # filter returns a list so you might consider skip except part
        result = Item.objects.filter(title__icontains=item_name)
        print("======>", result)
        return render(request, "home.html", {"object_list": result})
    else:
        return redirect("core:home")


@user_passes_test(lambda u: u.is_superuser)
def admin_view(request):
    return redirect('/admin/')
