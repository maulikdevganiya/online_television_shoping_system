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

]