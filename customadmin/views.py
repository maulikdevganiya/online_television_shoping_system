from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
import json
from app.forms import CarouselForm
# from app.middleware import admin_required
from datetime import *
from .models import Collection, CollectionProduct
from app.models import Admin, Brand,Carousel,Product,ProductFeature,Order,OrderItem,Payment
from django.utils.timezone import now
from decimal import Decimal
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
                request.session["admin_name"] = admin_user.name
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

def admin_header(request):
    # Check if admin is logged in
    if "admin_id" not in request.session:
        return redirect("admin_login")   # change URL name if needed

    # Pass session values to template (optional because request.session already works)
    context = {
        "admin_name": request.session.get("admin_name")
    }
    return render(request, "admin_header.html", context)

def product(request):
    products = Product.objects.all()
    return render(request,"admin_product.html", {"products": products} )

def payment(request):
    if "admin_id" not in request.session:
        return redirect("admin_login")

    # Fetch all payments with related order and user data
    payments = Payment.objects.select_related('order__user').all().order_by('-payment_date')

    # Calculate financial statistics
    total_revenue = payments.filter(payment_status='completed').aggregate(
        total=models.Sum('amount'))['total'] or 0

    total_transactions = payments.filter(payment_status='completed').count()

    refunded_amount = payments.filter(payment_status='refunded').aggregate(
        total=models.Sum('amount'))['total'] or 0

    failed_payments = payments.filter(payment_status='failed').count()

    # Get recent transactions (last 50)
    recent_payments = payments[:50]

    context = {
        'payments': recent_payments,
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'refunded_amount': refunded_amount,
        'failed_payments': failed_payments,
    }

    return render(request, "admin_payment.html", context)

def order(request):
    if "admin_id" not in request.session:
        return redirect("admin_login")

    # Fetch all orders with related data
    orders = Order.objects.select_related('user').prefetch_related('order_items__product', 'payment').all().order_by('-created_at')

    # Calculate statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    shipped_orders = orders.filter(status='shipped').count()
    cancelled_orders = orders.filter(status='cancelled').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': shipped_orders,
        'cancelled_orders': cancelled_orders,
    }

    return render(request, "admin_order.html", context)

def customer(request):
    return render(request,"admin_customer.html" )

def add_product(request):
    if "admin_id" not in request.session:
        return redirect("adminlogin")

    brands = Brand.objects.all()  # Fetch all brands for the dropdown

    if request.method == "POST":
        try:
            # 1. Get Basic Data
            title = request.POST.get('title')
            price = Decimal(request.POST.get('price'))
            description = request.POST.get('description')
            stock = int(request.POST.get('stock', 0))
            brand_id = request.POST.get('brand')

            # Handle Discount: If empty, set to 0, convert to int
            discount_str = request.POST.get('discount')
            if not discount_str:
                discount = 0
            else:
                discount = int(float(discount_str))

            # Get the brand instance
            brand = Brand.objects.get(id=brand_id)

            # 2. Create Product
            # IMPORTANT: We must pass the images and map 'description' to 'description_html'
            product = Product(
                title=title,
                original_price=price,
                discount_percentage=discount,
                stock=stock,
                brand=brand,
                description_html=description,  # FIXED: Model field is 'description_html'

                # FIXED: Added the images here
                main_image=request.FILES.get('main_image'),
                thumb_1=request.FILES.get('thumb_1'),
                thumb_2=request.FILES.get('thumb_2'),
                thumb_3=request.FILES.get('thumb_3'),
                thumb_4=request.FILES.get('thumb_4')
            )

            product.save() # This calculates final_price automatically via models.py

            # 3. Handle Features
            features_data = request.POST.get('features')
            if features_data:
                feature_list = features_data.split('\n')
                for f in feature_list:
                    clean_f = f.strip()
                    if clean_f:
                        ProductFeature.objects.create(product=product, feature_text=clean_f)

            messages.success(request, "Product Added Successfully!")
            return redirect('add_product')

        except Exception as e:
            # Print error to terminal so you can see exactly what's wrong
            print(f"Error Saving Product: {e}")
            messages.error(request, f"Error: {e}")

    return render(request, 'add_product.html', {'brands': brands})

def admin_collections(request):
    if "admin_id" not in request.session:
        return redirect("admin_login")

    collections = Collection.objects.all().order_by('-created_at')
    products = Product.objects.all()

    if request.method == "POST":
        collection_id = request.POST.get('collection_id')
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle', '')
        status = request.POST.get('status', 'Active')
        selected_products = request.POST.getlist('products')

        if collection_id:
            # Edit existing collection
            collection = get_object_or_404(Collection, id=collection_id)
            collection.title = title
            collection.subtitle = subtitle
            collection.status = status
            collection.save()

            # Update products
            CollectionProduct.objects.filter(collection=collection).delete()
            for product_id in selected_products:
                CollectionProduct.objects.create(collection=collection, product_id=product_id)

            messages.success(request, "Collection updated successfully!")
        else:
            # Create new collection
            collection = Collection.objects.create(
                title=title,
                subtitle=subtitle,
                status=status
            )

            # Add products
            for product_id in selected_products:
                CollectionProduct.objects.create(collection=collection, product_id=product_id)

            messages.success(request, "Collection created successfully!")

        return redirect('admin_collections')

    context = {
        'collections': collections,
        'products': products,
    }
    return render(request, "admin_collections.html", context)

def admin_brands(request):
    if "admin_id" not in request.session:
        return redirect("admin_login")
    all_brands = Brand.objects.all()
    return render(request,"admin_brands.html", {"brands": all_brands})

def add_brand(request):
    if request.method == "POST":
        name = request.POST.get("bname")
        desc = request.POST.get("description")
        status = request.POST.get("status")
        image = request.FILES.get("bimage")

        Brand.objects.create(
            bname=name,
            description=desc,
            bimage=image,
            b_status=status
        )

        return redirect("admin_brands")

    return redirect("admin_brands")

def delete_brand(request, id):
    brand = Brand.objects.get(id=id)
    brand.delete()
    return redirect("admin_brands")

def edit_brand(request, id):
    brand = Brand.objects.get(id=id)

    if request.method == "POST":
        brand.bname = request.POST.get("bname")
        brand.description = request.POST.get("description")
        brand.b_status = request.POST.get("status")

        if "bimage" in request.FILES:
            brand.bimage = request.FILES["bimage"]

        brand.save()
        return redirect("brands")

    return render(request, "edit_brand.html", {"brand": brand})



def admin_filter(request):
    return render(request,"admin_filter.html" )

def admin_slider(request):
    if request.method == "POST":
        internal_name = request.POST.get("internal_name")
        link = request.POST.get("link")
        sort_order = request.POST.get("sort_order")
        status = request.POST.get("status")
        image = request.FILES.get("image")

        Carousel.objects.create(
            internal_name=internal_name,
            link=link,
            sort_order=sort_order,
            status=status,
            image=image
        )

        return redirect("admin_slider")

    slides = Carousel.objects.all().order_by("sort_order")

    return render(request, "admin_slider.html", {"slides": slides})

def a_header(request):
    return render(request,"a_header.html" )

def admin_image_sections(request):
    return render(request,"admin_image_sections.html" )

def admin_footer(request):
    return render(request,"admin_footer.html" )

def admin_msg(request):
    return render(request,"admin_msg.html" )

def edit_product(request, id):
    if "admin_id" not in request.session:
        return redirect("adminlogin")

    product = get_object_or_404(Product, id=id)
    brands = Brand.objects.all()

    if request.method == "POST":
        try:
            # Update basic data
            product.title = request.POST.get('title')
            product.original_price = Decimal(request.POST.get('price'))
            product.description_html = request.POST.get('description')
            product.stock = int(request.POST.get('stock', 0))

            discount_str = request.POST.get('discount')
            if not discount_str:
                product.discount_percentage = 0
            else:
                product.discount_percentage = int(float(discount_str))

            brand_id = request.POST.get('brand')
            product.brand = Brand.objects.get(id=brand_id)

            # Handle image updates
            if request.FILES.get('main_image'):
                product.main_image = request.FILES.get('main_image')
            if request.FILES.get('thumb_1'):
                product.thumb_1 = request.FILES.get('thumb_1')
            if request.FILES.get('thumb_2'):
                product.thumb_2 = request.FILES.get('thumb_2')
            if request.FILES.get('thumb_3'):
                product.thumb_3 = request.FILES.get('thumb_3')
            if request.FILES.get('thumb_4'):
                product.thumb_4 = request.FILES.get('thumb_4')

            product.save()

            # Handle features update
            features_data = request.POST.get('features')
            if features_data:
                # Delete existing features
                ProductFeature.objects.filter(product=product).delete()
                feature_list = features_data.split('\n')
                for f in feature_list:
                    clean_f = f.strip()
                    if clean_f:
                        ProductFeature.objects.create(product=product, feature_text=clean_f)

            messages.success(request, "Product Updated Successfully!")
            return redirect('product')

        except Exception as e:
            print(f"Error Updating Product: {e}")
            messages.error(request, f"Error: {e}")

    return render(request, 'edit_product.html', {'product': product, 'brands': brands})

def delete_product(request, id):
    if "admin_id" not in request.session:
        return redirect("adminlogin")

    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "Product Deleted Successfully!")
    return redirect('product')

def edit_collection(request, id):
    if "admin_id" not in request.session:
        return redirect("admin_login")

    collection = get_object_or_404(Collection, id=id)
    products = Product.objects.all()
    selected_products = [cp.product.id for cp in collection.collection_products.all()]

    if request.method == "POST":
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle', '')
        status = request.POST.get('status', 'Active')
        selected_products = request.POST.getlist('products')

        collection.title = title
        collection.subtitle = subtitle
        collection.status = status
        collection.save()

        # Update products
        CollectionProduct.objects.filter(collection=collection).delete()
        for product_id in selected_products:
            CollectionProduct.objects.create(collection=collection, product_id=product_id)

        messages.success(request, "Collection updated successfully!")
        return redirect('admin_collections')

    context = {
        'collection': collection,
        'products': products,
        'selected_products': selected_products,
    }
    return render(request, "admin_collections.html", context)

def delete_collection(request, id):
    if "admin_id" not in request.session:
        return redirect("admin_login")

    collection = get_object_or_404(Collection, id=id)
    collection.delete()
    messages.success(request, "Collection deleted successfully!")
    return redirect('admin_collections')

def update_order_status(request, order_id):
    print(f"--- UPDATE STATUS CALLED FOR ORDER {order_id} ---") # Debug print

    # 1. Check Authentication (Support both custom session AND standard Django User)
    is_custom_admin = "admin_id" in request.session
    is_django_admin = request.user.is_authenticated and request.user.is_staff

    if not (is_custom_admin or is_django_admin):
        print("Error: User not authorized")
        return JsonResponse({'success': False, 'error': 'Unauthorized access'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            print(f"Attempting to set status to: {new_status}") # Debug print

            # Validate status
            valid_statuses = ['pending', 'processing', 'shipped', 'cancelled']
            if new_status not in valid_statuses:
                return JsonResponse({'success': False, 'error': f'Invalid status. Must be one of {valid_statuses}'})

            # Update order
            order = get_object_or_404(Order, id=order_id)
            order.status = new_status
            order.save()
            
            print("Success: Database updated") # Debug print
            return JsonResponse({'success': True, 'message': f'Order {order_id} updated to {new_status}'})

        except Exception as e:
            print(f"Exception Occurred: {str(e)}") # Debug print
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def refund_payment(request, payment_id):
    """
    Handle payment refund requests from admin panel
    """
    # Check admin authentication
    if "admin_id" not in request.session:
        return JsonResponse({'success': False, 'error': 'Unauthorized access'}, status=403)

    if request.method == 'POST':
        try:
            # Get the payment object
            payment = get_object_or_404(Payment, id=payment_id)

            # Check if payment can be refunded
            if payment.payment_status not in ['completed', 'pending']:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot refund payment with status: {payment.payment_status}'
                })

            # Update payment status to refunded
            payment.payment_status = 'refunded'
            payment.save()

            # Optionally update order status if needed
            # payment.order.status = 'cancelled'
            # payment.order.save()

            return JsonResponse({
                'success': True,
                'message': f'Payment {payment_id} has been refunded successfully'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

