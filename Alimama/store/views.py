from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Profile
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import Group, User
from .form import SignUpForm, ContactForm, ProfileForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
import logging
from django.core.mail import EmailMessage
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.http import HttpResponseRedirect

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


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        # request.session.create()  # test
        cart = request.session.session_key
    return cart


@transaction.atomic
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)

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
    next_url = request.POST.get('next') or request.GET.get('next')
    return HttpResponseRedirect(next_url)


@transaction.atomic
def add_more_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # Retrieve the product by ID
    cart_id = _cart_id(request)  # Retrieve or create the cart ID

    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=cart_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1  # Correctly increment by 1
        else:
            # Optionally handle the case where adding another would exceed stock
            pass
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
                    user=request.user,
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


def signupView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            # Ensures the group is created if it doesn't exist
            customer_group, _ = Group.objects.get_or_create(name='Customers')
            customer_group.user_set.add(signup_user)

            # Assuming PROFILE_ROLE is a constant that holds the desired role value
            profile, created = Profile.objects.get_or_create(
                user=signup_user, defaults={'role': Profile.CUSTOMER})

            # Redirect to a success page or home
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


stripe.api_key = settings.STRIPE_SECRET_KEY


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

# 33


# @login_required(redirect_field_name='next', login_url='signin')
# def userDashboard(request):
#     # Retrieve order history
#     order_details = Order.objects.filter(emailAddress=request.user.email)

#     # Handle profile update form submission
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=request.user.profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Profile updated successfully.')
#             return redirect('user_dashboard')
#     else:
#         form = ProfileForm(instance=request.user.profile)

#     # Fetch user profile
#     user_profile = get_object_or_404(Profile, user=request.user)

#     # Prepare context
#     context = {
#         'order_details': order_details,
#         'form': form,
#         'profile': user_profile,  # No need for 'address' as 'profile' includes it
#     }

#     return render(request, 'user_dashboard.html', context)
@login_required(redirect_field_name='next', login_url='signin')
def userDashboard(request):
    # Retrieve order history based on the user relationship
    order_details = Order.objects.filter(
        user=request.user).order_by('-created')

    # Handle profile update form submission
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES,
                           instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_dashboard')
    else:
        form = ProfileForm(instance=request.user.profile)

    # Fetch user profile
    user_profile = get_object_or_404(Profile, user=request.user)

    # Prepare context
    context = {
        'order_details': order_details,
        'form': form,
        'profile': user_profile,
    }

    return render(request, 'user_dashboard.html', context)


@login_required(redirect_field_name='next', login_url='signin')
def viewOrder(request, order_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order = Order.objects.get(id=order_id, emailAddress=email)
        order_items = OrderItem.objects.filter(order=order)
    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items})
# @login_required(redirect_field_name='next', login_url='signin')
# def viewOrder(request, order_id):
#     # Use get_object_or_404 to ensure that the order exists and belongs to the logged-in user
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     order_details = OrderItem.objects.filter(order=order)
#     return render(request, 'order_detail.html', {'order': order, 'order_details': order_details})


def search(request):
    products = Product.objects.filter(name__icontains=request.GET['title'])
    return render(request, 'home.html', {'products': products})


# @require_POST
# @login_required
# def delete_account(request):
#     user = request.user

#     # Mark user's orders as canceled
#     Order.objects.filter(emailAddress=user.email).update(status='Canceled')

#     # Delete the user account
#     user.delete()
#     logout(request)
#     messages.success(
#         request, 'Your account and all associated orders have been successfully deleted.')
#     return redirect('home')  # Adjust 'home' to your actual home page URL name
@require_POST
@login_required
def delete_account(request):
    user = request.user

    # Update the status of all orders associated with the user to 'Canceled'
    Order.objects.filter(user=user).update(status='Canceled')

    # Proceed with deleting the user account
    user.delete()

    # Log the user out
    logout(request)

    # Inform the user of the successful deletion
    messages.success(
        request, 'Your account and all associated orders have been successfully deleted.')

    # Redirect to the home page
    # Make sure 'home' is correctly defined in your URLs
    return redirect('home')


def error_404_view(request, exception):
    # Optional: pass exception or other context to the template
    context = {'exception': exception}
    return render(request, 'store/404.html', context, status=404)


def error_500_view(request):
    logger = logging.getLogger(__name__)
    logger.error('Internal Server Error: %s', request.path,
                 exc_info=True, extra={'status_code': 500, 'request': request})
    return render(request, 'store/500.html', status=500)

# database test
# # Query all users
# users = User.objects.all()

# # Extract email addresses
# emails = [user.email for user in users]

# # Print each email
# for email in emails:
#     print(email)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Ensure from_email is set to a valid email address
            from_email = f"{name} via Alimama Contact Form <{settings.DEFAULT_FROM_EMAIL}>"

            # Create email message
            email_message = EmailMessage(
                subject=f"Message from {name}: {subject}",
                body=message,
                from_email=from_email,  # Use the valid from_email format
                to=[settings.DEFAULT_FROM_EMAIL],
                reply_to=[email]  # Use reply_to for the sender's email
            )

            # Send email
            email_message.send(fail_silently=False)

            # Redirect to a new URL or show a success message
            return redirect('contact_success')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def contact_success(request):
    return render(request, 'contact_success.html')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important to keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')
            # Redirect to a confirmation page
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def password_change_done(request):
    # Log out the user
    logout(request)
    return render(request, 'registration/password_change_done.html')
