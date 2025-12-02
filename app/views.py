from django.shortcuts import render,redirect
from django.contrib.auth.hashers import check_password
from .forms import RegisterForm
from django.contrib import messages
from .models import UserRegister,Brand,Carousel,Product,ProductFeature,Cart,CartItem,Order,OrderItem,Payment
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

def my_addrerss(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    return render(request, "my_addrerss.html", {"user": user, "active_page": "address"})

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
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.cart_items.all()

    total_price = cart.total_price
    total_items = cart.total_items

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items,
        'user': user
    })

def place_order(request):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method == 'POST':
        user = UserRegister.objects.get(id=request.session["user_id"])
        cart = Cart.objects.get(user=user)
        cart_items = cart.cart_items.all()

        # Create order
        import uuid
        order_number = str(uuid.uuid4())[:8].upper()
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            total_amount=cart.total_price,
            shipping_address=request.POST.get('address'),
            billing_address=request.POST.get('address'),  # Same as shipping for now
            phone=request.POST.get('phone'),
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

        # Create payment
        Payment.objects.create(
            order=order,
            payment_method=request.POST.get('payment_method'),
            amount=cart.total_price
        )

        # Clear cart
        cart.cart_items.all().delete()

        return redirect('order_confirmation', order_id=order.id)

    return redirect('checkout')

def order_confirmation(request, order_id):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    order = get_object_or_404(Order, id=order_id, user=user)

    return render(request, 'order_confirmation.html', {
        'order': order,
        'user': user
    })
