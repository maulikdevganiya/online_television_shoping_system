from django.shortcuts import render,redirect
from django.contrib.auth.hashers import check_password
from .forms import RegisterForm
from django.contrib import messages
from .models import UserRegister,Brand,Carousel,Product,ProductFeature
from django.views import View
from django.shortcuts import get_object_or_404, render,redirect

def index(request):
    brands = Brand.objects.all()
    return render(request, 'index.html',{"brands": brands})
def filter(request):
    return render(request, 'filter.html')
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

def my_wishlist(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    return render(request, "my_wishlist.html", {"user": user, "active_page": "wishlist"})
    

def my_order(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = UserRegister.objects.get(id=request.session["user_id"])
    return render(request, "my_order.html", {"user": user, "active_page": "order"})

def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    features = product.features.all()
    return render(request, 'product_details.html', {
        'product': product,
        'features': features
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