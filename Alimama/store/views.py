from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import Group, User
from .form import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout

# Create your views here.


def home(request, category_slug=None):
    category_page = None
    products = None
    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=category_page, available=True)
    else:
        products = Product.objects.all().filter(available=True)

    return render(request, 'home.html', {'category': category_page, 'products': products})


def about(request):
    return render(request, 'about.html')


def product(request, category_slug, product_slug):
    try:
        product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

    return render(request, 'product.html', {'product': product})

# def product(request, category_slug, product_slug):
#     try:
#         product = Product.objects.get(
#             category__slug=category_slug, slug=product_slug)
#     except Product.DoesNotExist:
#         product = None
#         # Optionally, handle the error or redirect
#     return render(request, 'product.html', {'product': product})


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# def add_cart(request, product_id):
#     product = Product.objects.get(id=product_id)
#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#     except Cart.DoesNotExist:
#         cart = Cart.objects.create(
#             cart_id=_cart_id(request)
#         )
#         cart.save()
#     try:
#         cart_item = CartItem.objects.get(product=product, cart=cart)
#         cart_item.quantity += 1
#         cart_item.save()
#     except CartItem.DoesNotExist:
#         cart_item = CartItem.objects.create(
#             product=product,
#             quantity=1,
#             cart=cart
#         )

#         cart.item.save()

#     return redirect('cart_detail')


# this work!!!!
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1

        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
    cart_item.save()

    return redirect('cart_detail')


def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total * 100)  # Convert total amount to cents for Stripe
    description = 'EC-Store - New Order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == 'POST':
        # Handle Stripe payment processing here
        token = request.POST.get('stripeToken', '')
        email = request.POST.get('stripeEmail', '')

        # Create a Stripe customer and charge
        try:
            customer = stripe.Customer.create(email=email, source=token)
            charge = stripe.Charge.create(
                amount=stripe_total,
                currency='eur',
                description=description,
                customer=customer.id
            )

            # If the charge is successful, create an order and order items
            if charge.status == 'succeeded':
                order_details = Order.objects.create(
                    total=total,
                    emailAddress=email,
                    # Add other necessary fields
                )
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price,
                        order=order_details
                    )
                    # Update stock and delete cart items
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()
                    cart_item.delete()

                # Redirect to a success page
                return redirect('success_view')

        except stripe.error.CardError as e:
            # Handle card errors
            return HttpResponse(e.error.message)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'counter': counter,
        'data_key': data_key,
        'stripe_total': stripe_total,
        'description': description
    })

# def cart_detail(request, total=0, counter=0, cart_items=None):
#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#         cart_items = CartItem.objects.filter(cart=cart, active=True)
#         for cart_item in cart_items:
#             total += (cart_item.product.price * cart_item.quantity)
#             counter += cart_item.quantity
#     except ObjectDoesNotExist:
#         pass

#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     stripe_total = int(total * 100)
#     description = 'EC-Store - New Order'
#     data_key = settings.STRIPE_PUBLISHABLE_KEY
#     if request.method == 'POST':
#         try:
#             token = request.POST['stripeToken']
#             email = request.POST['stripeEmail']
#             billingName = request.POST['stripeBillingName']
#             billingAddress1 = request.POST['stripeBillingLine1']
#             billingCity = request.POST['stripeBillingAddressCity']
#             billingPostcode = request.POST['stripeBillingAddressZip']
#             billingCountry = request.POST['stripeBillingCountryCode']
#             shippingName = request.POST['stripeShippingName']
#             shippingAddress1 = request.POST['stripeAddressLine1']
#             shippingCity = request.POST['stripeShippingAddressCity']
#             shippingPostcode = request.POST['stripeShippingAddressZip']
#             shippingCountry = request.POST['stripeShippingAddressCountryCode']

#             customer = stripe.Customer.create(
#                 email=email,
#                 source=token)
#             charge = stripe.Charge.create(
#                 amount=stripe_total,
#                 currency='eur',
#                 description=description,
#                 customer=customer.id

#             )

#             try:
#                 order_details = Order.objects.create(
#                     token=token,
#                     total=total,
#                     emailAddress=email,
#                     billingName=billingName,
#                     billingAddress1=billingAddress1,
#                     billingCity=billingCity,
#                     billingPostcode=billingPostcode,
#                     billingCountry=billingCountry,
#                     shippingName=shippingName,
#                     shippingAddress1=shippingAddress1,
#                     shippingCity=shippingCity,
#                     shippingPostcode=shippingPostcode,
#                     shippingCountry=shippingCountry
#                 )
#                 order_details.save()
#                 for order_item in cart_items:
#                     or_item = OrderItem.objects.create(
#                         product=order_item.product.name,
#                         quantity=order_item.quantity,
#                         price=order_item.product.price,
#                         order=order_details
#                     )
#                     or_item.save()

#                     product = Product.objects.get(id=order_item.product.id)
#                     product.stock = int(
#                         order_item.product.stock - order_item.quantity)
#                     product.save()
#                     order_item.delete()

#                     print('order created')

#                 return redirect('home')
#             except ObjectDoesNotExist:
#                 pass

#         except stripe.error.CardError as e:
#             return False, e

#     return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter, data_key=data_key, stripe_total=stripe_total, description=description))


# def cart_detail(request, total=0, counter=0, cart_items=None):
#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#         cart_items = CartItem.objects.filter(cart=cart, active=True)
#         for cart_item in cart_items:
#             total += (cart_item.product.price * cart_item.quantity)
#             counter += cart_item.quantity
#     except ObjectDoesNotExist:
#         pass

#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     # Stripe requires the amount to be in cents
#     stripe_total = int(total * 100)
#     description = 'EC-Store - New Order'
#     data_key = settings.STRIPE_PUBLISHABLE_KEY

#     if request.method == 'POST':
#         # Create a Stripe Checkout Session
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'eur',
#                     'product_data': {
#                         'name': 'Total Cart Amount',
#                     },
#                     'unit_amount': stripe_total,
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             success_url=request.build_absolute_uri(
#                 reverse('success_view')) + '?session_id={CHECKOUT_SESSION_ID}',

#         )

#         # Redirect to Stripe Checkout
#         return redirect(session.url, code=303)

#     context = {
#         'cart_items': cart_items,
#         'total': total,
#         'counter': counter,
#         'data_key': data_key,
#         'stripe_total': stripe_total,
#         'description': description
#     }

#     return render(request, 'cart.html', context)


# def cart_detail(request, total=0, counter=0, cart_items=None):
#     try:
#         # Assuming _cart_id is a helper function you have defined elsewhere
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#         cart_items = CartItem.objects.filter(cart=cart, active=True)
#         for cart_item in cart_items:
#             total += (cart_item.product.price * cart_item.quantity)
#             counter += cart_item.quantity
#     except ObjectDoesNotExist:
#         pass

#     # Stripe settings
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     # Stripe requires the amount to be in cents
#     stripe_total = int(total * 100)
#     description = 'EC-Store - New Order'
#     data_key = settings.STRIPE_PUBLISHABLE_KEY

#     if request.method == 'POST':
#         try:
#             # Retrieve the token, email, billing, and shipping information from the form
#             token = request.POST['stripeToken']
#             email = request.POST['stripeEmail']
#             # Additional customer information can be collected here as needed

#             # Create a Stripe customer
#             customer = stripe.Customer.create(
#                 email=email,
#                 source=token
#             )

#             # Create a charge
#             charge = stripe.Charge.create(
#                 amount=stripe_total,
#                 currency='eur',
#                 description=description,
#                 customer=customer.id
#             )

#             # Assuming Order and OrderItem are models related to your order processing system
#             order_details = Order.objects.create(
#                 token=token,
#                 total=total,
#                 emailAddress=email,
#                 # Include other billing and shipping details as necessary
#             )
#             order_details.save()

#             # Iterate through cart items and create order items
#             for order_item in cart_items:
#                 or_item = OrderItem.objects.create(
#                     product=order_item.product,
#                     quantity=order_item.quantity,
#                     price=order_item.product.price,
#                     order=order_details
#                 )
#                 or_item.save()

#                 # Update stock
#                 product = order_item.product
#                 product.stock = int(product.stock - order_item.quantity)
#                 product.save()

#                 # Clear the cart
#                 order_item.delete()

#             # Redirect to the home page after order completion
#             return redirect('home')

#         except stripe.error.CardError as e:
#             # Handle card error
#             return False, e

#     return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter, data_key=data_key, stripe_total=stripe_total, description=description))


def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')


def delete_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_detail')


def cart(request):
    return render(request, 'cart.html')


def success_view(request, order_id):
    # Add your success logic here
    if order_id:
        customer_order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'customer_order': customer_order})


def signupView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # This returns the User instance if your form is a ModelForm for the User model.
            form.save()
            username = form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            customer_group = Group.objects.get(name='Customers')
            customer_group.user_set.add(signup_user)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# def signupView(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             # Instead of saving the form directly, create a User instance first
#             user = form.save(commit=False)
#             # Use the email as the username
#             user.username = form.cleaned_data['email']
#             # Save the user instance
#             user.save()
#             # Add the user to the 'Customers' group
#             customer_group, created = Group.objects.get_or_create(
#                 name='Customers')
#             customer_group.user_set.add(user)
#             # Redirect to a new URL or show a success message
#             # Update 'some_view_name' to your desired redirect view
#             # return redirect('some_view_name')
#     else:
#         form = SignUpForm()
#     return render(request, 'signup.html', {'form': form})

def signinView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return redirect('signup')

    else:
        form = AuthenticationForm()
    return render(request, 'signin.html', {'form': form})


def signoutView(request):
    logout(request)
    return redirect('home')
