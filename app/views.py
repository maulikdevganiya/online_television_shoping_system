from django.shortcuts import render,redirect
from django.contrib.auth.hashers import check_password
from .forms import RegisterForm, EditProfileForm
from django.contrib import messages
from .models import UserRegister,Brand,Carousel,Product,ProductFeature,Cart,CartItem,Order,OrderItem,Payment,Address
from customadmin.models import Collection
from django.views import View
from django.shortcuts import get_object_or_404, render,redirect
from django.db.models import Prefetch
from django.core.paginator import Paginator

def index(request):
    brands = Brand.objects.all()
    collections = Collection.objects.filter(status='Active').order_by('created_at').prefetch_related(
        Prefetch('collection_products__product', queryset=Product.objects.all())
    )
    total_items = 0
    if "user_id" in request.session:
        user = UserRegister.objects.get(id=request.session["user_id"])
        cart, created = Cart.objects.get_or_create(user=user)
        total_items = cart.total_items
    return render(request, 'index.html',{"brands": brands, "collections": collections, "total_items": total_items})
def filter(request):
    products = Product.objects.all()
    brands = Brand.objects.all()
    total_items = 0
    if "user_id" in request.session:
        user = UserRegister.objects.get(id=request.session["user_id"])
        cart, created = Cart.objects.get_or_create(user=user)
        total_items = cart.total_items

    return render(request, 'filter.html', {'products': products, 'brands': brands, 'total_items': total_items})
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 1. Check email exists
        try:
            user = UserRegister.objects.get(email=email)

            # 2. Validate hashed password
            if check_password(password, user.password):
                request.session["user_id"] = user.id
                request.session["user_email"] = user.email

                # messages.success(request, "Login Successful!")
                return redirect("index")  # redirect to homepage
            else:
                messages.error(request, "Incorrect Password!")

        except UserRegister.DoesNotExist:
            messages.error(request, "Email not found!")

    return render(request, "login.html")

def header(request):
    return render(request,"header.html")

def about_us(request):
    return render(request,"about_us.html")

def contact_us(request):
    return render(request,"contact_us.html")

def footer(request):
    return render(request,"footer.html")

def my_address(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    addresses = Address.objects.filter(user=user)
    return render(request, "my_address.html", {"user": user, "active_page": "address", "addresses": addresses})

def my_cart(request):
    return render(request, 'my_cart.html')

def my_cart2(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.cart_items.all()

    total_price = cart.total_price
    total_items = cart.total_items

    return render(request, 'my_cart2.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items,
        'user': user
    })

def add_to_cart(request, product_id):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', 'index'))

def buy_now(request, product_id):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    product = get_object_or_404(Product, id=product_id)

    # Get user's default address
    default_address = Address.objects.filter(user=user, is_default=True).first()
    if not default_address:
        messages.error(request, "Please add a shipping address first.")
        return redirect('my_address')

    # Build shipping address
    shipping_address = f"{default_address.full_name}, {default_address.address_line_1}"
    if default_address.address_line_2:
        shipping_address += f", {default_address.address_line_2}"
    shipping_address += f", {default_address.city}, {default_address.state}, {default_address.pincode}"
    phone = default_address.phone

    # Create order
    import uuid
    order_number = str(uuid.uuid4())[:8].upper()
    order = Order.objects.create(
        user=user,
        order_number=order_number,
        total_amount=product.final_price,
        shipping_address=shipping_address,
        billing_address=shipping_address,
        phone=phone,
        email=user.email
    )

    # Create order item
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.final_price
    )

    # Create payment (assuming cash on delivery for buy now)
    Payment.objects.create(
        order=order,
        payment_method='cash_on_delivery',
        payment_status='pending',
        amount=product.final_price
    )

    return redirect('order_confirmation', order_id=order.id)

def update_cart_quantity(request, item_id):
    if "user_id" not in request.session:
        return redirect("login")

    cart_item = get_object_or_404(CartItem, id=item_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('my_cart2')

def remove_from_cart(request, item_id):
    if "user_id" not in request.session:
        return redirect("login")

    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()

    return redirect('my_cart2')

def my_wishlist(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    return render(request, "my_wishlist.html", {"user": user, "active_page": "wishlist"})
    

def my_order(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    orders = Order.objects.filter(user=user).select_related('payment').order_by('-created_at')
    return render(request, "my_order.html", {"user": user, "active_page": "order", "orders": orders})

def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    features = product.features.all()
    total_items = 0
    if "user_id" in request.session:
        user = UserRegister.objects.get(id=request.session["user_id"])
        cart, created = Cart.objects.get_or_create(user=user)
        total_items = cart.total_items
    return render(request, 'product_details.html', {
        'product': product,
        'features': features,
        'total_items': total_items
    })

def profile_sidebar(request):
    if "user_id" not in request.session:
        return redirect("login")
    user = UserRegister.objects.get(id=request.session["user_id"])
    return render(request,'profile_sidebar.html',{"user": user})

def profile(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    return render(request, "profile.html", {"user": user, "active_page": "profile"})

def edit_profile(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'edit_profile.html', {
        'form': form,
        'user': user,
        'active_page': 'profile'
    })

def registration(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Registration Successful!")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "registration.html", {"form": form})


def logout_view(request):
    request.session.flush()
    return redirect("index")


def checkout(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_items = cart.cart_items.all()
    total_price = cart.total_price
    total_items = cart.total_items
    addresses = Address.objects.filter(user=user)
    default_address = Address.objects.filter(user=user, is_default=True).first()

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items,
        'user': user,
        'addresses': addresses,
        'default_address': default_address,
    })




def place_order(request):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method == 'POST':
        user = UserRegister.objects.get(id=request.session["user_id"])
        cart = Cart.objects.get(user=user)
        cart_items = cart.cart_items.all()

        # Get selected shipping address
        shipping_address_id = request.POST.get('shipping_address')
        if not shipping_address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect('checkout')

        try:
            selected_address = Address.objects.get(id=shipping_address_id, user=user)
        except Address.DoesNotExist:
            messages.error(request, "Invalid shipping address selected.")
            return redirect('checkout')

        # Build shipping address from selected address
        shipping_address = f"{selected_address.full_name}, {selected_address.address_line_1}"
        if selected_address.address_line_2:
            shipping_address += f", {selected_address.address_line_2}"
        shipping_address += f", {selected_address.city}, {selected_address.state}, {selected_address.pincode}"
        phone = selected_address.phone

        # Create order
        import uuid
        order_number = str(uuid.uuid4())[:8].upper()
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            total_amount=cart.total_price,
            shipping_address=shipping_address,
            billing_address=shipping_address,  # Same as shipping for now
            phone=phone,
            email=request.POST.get('email')
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.final_price
            )

        # Create payment with appropriate status based on payment method
        payment_method = request.POST.get('payment_method')
        if payment_method in ['credit_card', 'debit_card', 'paypal']:
            # For online payments, set status to completed (assuming payment gateway success)
            payment_status = 'completed'
        elif payment_method == 'cash_on_delivery':
            # For COD, set status to pending until delivery
            payment_status = 'pending'
        else:
            payment_status = 'pending'

        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            payment_status=payment_status,
            amount=cart.total_price
        )

        # Clear cart
        cart.cart_items.all().delete()

        return redirect('order_confirmation', order_id=order.id)

    return redirect('checkout')

def add_address(request):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method == 'POST':
        user = UserRegister.objects.get(id=request.session["user_id"])

        address = Address.objects.create(
            user=user,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address_line_1=request.POST.get('address_line_1'),
            address_line_2=request.POST.get('address_line_2'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            is_default=request.POST.get('is_default') == 'on'
        )

        messages.success(request, "Address added successfully!")
        return redirect('my_address')

    return render(request, 'add_address.html', {"active_page": "address"})

def edit_address(request, address_id):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    address = get_object_or_404(Address, id=address_id, user=user)

    if request.method == 'POST':
        address.full_name = request.POST.get('full_name')
        address.phone = request.POST.get('phone')
        address.address_line_1 = request.POST.get('address_line_1')
        address.address_line_2 = request.POST.get('address_line_2')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.pincode = request.POST.get('pincode')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()

        messages.success(request, "Address updated successfully!")
        return redirect('my_address')

    return render(request, 'edit_address.html', {"active_page": "address", "address": address})

def delete_address(request, address_id):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    address = get_object_or_404(Address, id=address_id, user=user)
    address.delete()

    messages.success(request, "Address deleted successfully!")
    return redirect('my_address')

def set_default_address(request, address_id):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    address = get_object_or_404(Address, id=address_id, user=user)
    address.is_default = True
    address.save()

    messages.success(request, "Default address updated successfully!")
    return redirect('my_address')

def order_confirmation(request, order_id):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    order = get_object_or_404(Order, id=order_id, user=user)

    return render(request, 'order_confirmation.html', {
        'order': order,
        'user': user
    })

def payment_success(request):
    """
    Handle successful payment callback from payment gateway (PayPal, Stripe, etc.)
    """
    if request.method == 'POST' or request.method == 'GET':
        # Get payment details from request parameters
        payment_id = request.GET.get('payment_id') or request.POST.get('payment_id')
        order_id = request.GET.get('order_id') or request.POST.get('order_id')
        transaction_id = request.GET.get('transaction_id') or request.POST.get('transaction_id')

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                payment = Payment.objects.get(order=order)

                # Update payment status to completed
                payment.payment_status = 'completed'
                if transaction_id:
                    payment.transaction_id = transaction_id
                payment.save()

                # Update order status if needed
                if order.status == 'pending':
                    order.status = 'processing'
                    order.save()

                messages.success(request, "Payment completed successfully!")
                return redirect('order_confirmation', order_id=order.id)

            except (Order.DoesNotExist, Payment.DoesNotExist):
                messages.error(request, "Payment verification failed. Please contact support.")
                return redirect('index')

    messages.error(request, "Invalid payment callback.")
    return redirect('index')

def payment_failure(request):
    """
    Handle failed payment callback from payment gateway
    """
    if request.method == 'POST' or request.method == 'GET':
        order_id = request.GET.get('order_id') or request.POST.get('order_id')

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                payment = Payment.objects.get(order=order)

                # Update payment status to failed
                payment.payment_status = 'failed'
                payment.save()

                messages.error(request, "Payment failed. Please try again or choose a different payment method.")
                return redirect('checkout')

            except (Order.DoesNotExist, Payment.DoesNotExist):
                messages.error(request, "Payment verification failed.")
                return redirect('index')

    messages.error(request, "Payment failed.")
    return redirect('index')

def payment_cancel(request):
    """
    Handle payment cancellation by user
    """
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            payment = Payment.objects.get(order=order)

            # Update payment status to cancelled
            payment.payment_status = 'cancelled'
            payment.save()

            messages.warning(request, "Payment was cancelled.")
            return redirect('checkout')

        except (Order.DoesNotExist, Payment.DoesNotExist):
            pass

    messages.warning(request, "Payment cancelled.")
    return redirect('checkout')


