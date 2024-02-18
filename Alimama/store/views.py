from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Profile
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import Group, User
from .form import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .form import ProfileForm
from django.http import HttpResponseRedirect
from django.contrib import messages


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
    quantity_range = list(range(1, product.stock + 1))
    return render(request, 'product.html', {'product': product, 'quantity_range': quantity_range})

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
#         if cart_item.quantity < cart_item.product.stock:
#             cart_item.quantity += 1

#         cart_item.save()
#     except CartItem.DoesNotExist:
#         cart_item = CartItem.objects.create(
#             product=product,
#             quantity=1,
#             cart=cart
#         )
#     cart_item.save()

#     return redirect('cart_detail')
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    # Get the quantity from the request's query parameters
    # Default to 1 if quantity is not provided or not an integer
    # Default to 1 if not provided
    quantity = int(request.POST.get('quantity', 1))

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            # Ensure that the added quantity does not exceed the available stock
            new_quantity = min(cart_item.quantity + quantity,
                               cart_item.product.stock)
            cart_item.quantity = new_quantity
        else:
            # Optionally handle cases where adding more would exceed the available stock
            # For example, display a message to the user
            pass
    except CartItem.DoesNotExist:
        # Create a new cart item if it doesn't exist
        cart_item = CartItem.objects.create(
            product=product, quantity=quantity, cart=cart)

    cart_item.save()

    # return redirect('cart_detail')
    # Redirect to 'next' if present, or a default URL
    next_url = request.POST.get('next') or request.GET.get('next') or 'home'
    return HttpResponseRedirect(next_url)

# def cart_detail(request, total=0, counter=0, cart_items=None):
    # try:
    #     cart = Cart.objects.get(cart_id=_cart_id(request))
    #     cart_items = CartItem.objects.filter(cart=cart, active=True)
    #     for cart_item in cart_items:
    #         total += (cart_item.product.price * cart_item.quantity)
    #         counter += cart_item.quantity
    # except ObjectDoesNotExist:
    #     pass

    # stripe.api_key = settings.STRIPE_SECRET_KEY
    # stripe_total = int(total * 100)  # Convert total amount to cents for Stripe
    # description = 'EC-Store - New Order'
    # data_key = settings.STRIPE_PUBLISHABLE_KEY

#     if request.method == 'POST':
#         # Handle Stripe payment processing here
#         token = request.POST.get('stripeToken', '')
#         email = request.POST.get('stripeEmail', '')

#         # Create a Stripe customer and charge
#         try:
#             customer = stripe.Customer.create(email=email, source=token)
#             charge = stripe.Charge.create(
#                 amount=stripe_total,
#                 currency='eur',
#                 description=description,
#                 customer=customer.id
#             )

#             # If the charge is successful, create an order and order items
#             if charge.status == 'succeeded':
#                 order_details = Order.objects.create(
#                     total=total,
#                     emailAddress=email,
#                     # Add other necessary fields
#                 )
#                 for cart_item in cart_items:
#                     OrderItem.objects.create(
#                         product=cart_item.product,
#                         quantity=cart_item.quantity,
#                         price=cart_item.product.price,
#                         order=order_details
#                     )
#                     # Update stock and delete cart items
#                     cart_item.product.stock -= cart_item.quantity
#                     cart_item.product.save()
#                     cart_item.delete()

#                 # Redirect to a success page
#                 return redirect('success_view')

#         except stripe.error.CardError as e:
#             # Handle card errors
#             return HttpResponse(e.error.message)

#     return render(request, 'cart.html', {
#         'cart_items': cart_items,
#         'total': total,
#         'counter': counter,
#         'data_key': data_key,
#         'stripe_total': stripe_total,
#         'description': description
#     })


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
    stripe_total = int(total * 100)
    description = 'EC-Store - New Order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddress1 = request.POST['stripeBillingAddressLine1']
            billingCity = request.POST['stripeBillingAddressCity']
            billingPostcode = request.POST['stripeBillingAddressZip']
            billingCountry = request.POST['stripeBillingAddressCountryCode']
            shippingName = request.POST['stripeShippingName']
            shippingAddress1 = request.POST['stripeShippingAddressLine1']
            shippingCity = request.POST['stripeShippingAddressCity']
            shippingPostcode = request.POST['stripeShippingAddressZip']
            shippingCountry = request.POST['stripeShippingAddressCountryCode']

            customer = stripe.Customer.create(
                email=email,
                source=token)
            charge = stripe.Charge.create(
                amount=stripe_total,
                currency='eur',
                description=description,
                customer=customer.id

            )

            try:
                order_details = Order.objects.create(
                    token=token,
                    total=total,
                    emailAddress=email,
                    billingName=billingName,
                    billingAddress1=billingAddress1,
                    billingCity=billingCity,
                    billingPostcode=billingPostcode,
                    billingCountry=billingCountry,
                    shippingName=shippingName,
                    shippingAddress1=shippingAddress1,
                    shippingCity=shippingCity,
                    shippingPostcode=shippingPostcode,
                    shippingCountry=shippingCountry
                )
                order_details.save()
                for order_item in cart_items:
                    or_item = OrderItem.objects.create(
                        product=order_item.product.name,
                        quantity=order_item.quantity,
                        price=order_item.product.price,
                        order=order_details
                    )
                    or_item.save()

                    product = Product.objects.get(id=order_item.product.id)
                    product.stock = int(
                        order_item.product.stock - order_item.quantity)
                    product.save()
                    order_item.delete()

                    print('order created')

                return redirect('success_view', order_details.id)
            except ObjectDoesNotExist:
                pass

        except stripe.error.CardError as e:
            return False, e

    return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter, data_key=data_key, stripe_total=stripe_total, description=description))


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

# custom


def success_view(request, order_id):
    if order_id:
        customer_order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'customer_order': customer_order})

# gpt
# def success_view(request: HttpRequest):
#     session_id = request.GET.get('session_id', None)
#     if session_id:
#         # Process the session_id to find the corresponding order
#         # Your logic here
#         return render(request, 'order_success.html', {'session_id': session_id})
#     else:
#         # Handle the case where session_id is not provided
#         return render(request, 'error_page.html', {'error': 'Session ID not provided.'})


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


stripe.api_key = settings.STRIPE_SECRET_KEY


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


# OLD PROFILE

# @login_required(redirect_field_name='next', login_url='signin')
# def profile(request):
#     user_profile = Profile.objects.get(user=request.user)
#     return render(request, 'user_profile.html', {'profile': user_profile})
#     # Optionally handle the case where the user is somehow not authenticated
#     # This is more of a fallback, as @login_required should take care of this


# PROFILE
# @login_required(redirect_field_name='next', login_url='signin')
# def profile(request):
#     user_profile = get_object_or_404(Profile, user=request.user)

#     if request.method == 'POST':
#         # Handling form submission.
#         form = ProfileForm(request.POST, instance=request.user.profile)
#         if form.is_valid():
#             form.save()
#             # Redirect to the profile page with a success message, or elsewhere as needed.
#             # Assuming 'profile' is the name of the URL pattern for this view.
#             return redirect('profile')
#     else:
#         # Handling a GET request, displaying the form with existing data.
#         form = ProfileForm(instance=request.user.profile)

#     # Pass the form to the template.
#     return render(request, 'order_detail.html', {'form': form, 'profile': user_profile})


# @login_required(redirect_field_name='next', login_url='signin')
# def profile(request):

#     return render(request, 'orders_list.html', {'form': form, 'profile': user_profile})


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


@login_required(redirect_field_name='next', login_url='signin')
def userDashboard(request):
    # Retrieve order history
    order_details = Order.objects.filter(emailAddress=request.user.email)

    # Handle profile update form submission
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_and_orders')
    else:
        form = ProfileForm(instance=request.user.profile)

    # Fetch user profile
    user_profile = get_object_or_404(Profile, user=request.user)

    # Prepare context
    context = {
        'order_details': order_details,
        'form': form,
        'profile': user_profile,  # No need for 'address' as 'profile' includes it
    }

    return render(request, 'user_dashboard.html', context)
#     # retrive order
#     if request.user.is_authenticated:
#         email = str(request.user.email)
#         order_details = Order.objects.filter(emailAddress=email)

# # retrive profile info
#     user_profile = get_object_or_404(Profile, user=request.user)

#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=request.user.profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Profile updated successfully.')
#             return redirect('profile')
#     else:
#         form = ProfileForm(instance=request.user.profile)
#     print(user_profile)

#     # address
#     user_address = request.user.profile

#     return render(request, 'user_dashboard.html', {'order_details': order_details, 'form': form, 'profile': user_profile, 'address': user_address})


@login_required(redirect_field_name='next', login_url='signin')
def viewOrder(request, order_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order = Order.objects.get(id=order_id, emailAddress=email)
        order_items = OrderItem.objects.filter(order=order)
    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items})


def search(request):
    products = Product.objects.filter(name__icontains=request.GET['title'])
    return render(request, 'home.html', {'products': products})

# database test
# # Query all users
# users = User.objects.all()

# # Extract email addresses
# emails = [user.email for user in users]

# # Print each email
# for email in emails:
#     print(email)
