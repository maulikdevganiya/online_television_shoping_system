from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
# from app.middleware import admin_required 
from datetime import *
from app.models import Admin
from django.utils.timezone import now
# Create your views here.


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("pass")
        try:
            admin_user = Admin.objects.get(email=email)
            print("DB PASSWORD:", admin_user.passw)

            if password == admin_user.passw:
                print("STATUS: LOGIN SUCCESS")
                request.session["admin_id"] = admin_user.A_id
                request.session["is_admin"] = True
                return redirect("dashboard")
            else:
                print("STATUS: WRONG PASSWORD")
                messages.error(request, "Invalid password.")
                return redirect("adminlogin")

        except Admin.DoesNotExist:
            print("STATUS: EMAIL NOT FOUND")
            messages.error(request, "Invalid email.")
            return redirect("adminlogin")

    return render(request, "admin_login.html")



def dashboard(request):
    # Check if admin is logged in
    if "admin_id" not in request.session:
        return redirect("admin_login")   # change URL name if needed

    # Pass session values to template (optional because request.session already works)
    context = {
        "admin_name": request.session.get("admin_name")
    }

    return render(request, "dashboard.html", context)

def product(request):
    return render(request,"product.html" )

def payment(request):
    return render(request,"payment.html" )

def order(request):
    return render(request,"order.html" )

def customer(request):
    return render(request,"customer.html" )