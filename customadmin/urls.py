from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("",views.admin_login,name="adminlogin"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("product/", views.product, name="product"),
    path("payment/", views.payment, name="payment"),
    path("order/", views.order, name="order"),
    path("customer/", views.customer, name="customer"),
    path("add_product/", views.add_product, name="add_product"),
    path("admin_brands/", views.admin_brands, name="admin_brands"),
    path("admin_filter/", views.admin_filter, name="admin_filter"),
    path("admin_slider/", views.admin_slider, name="admin_slider"),
    path("a_header/", views.a_header, name="a_header"),
    path("admin_collections/", views.admin_collections, name="admin_collections"),
    path("admin_image_sections/", views.admin_image_sections, name="admin_image_sections"),
    path("admin_footer/", views.admin_footer, name="admin_footer"),
    path("admin_msg/", views.admin_msg, name="admin_msg"),
]