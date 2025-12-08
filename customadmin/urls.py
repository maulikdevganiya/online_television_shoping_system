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
    path("update-order-status/<int:order_id>/", views.update_order_status, name="update_order_status"),
    path("customer/", views.customer, name="customer"),
    path("add_product/", views.add_product, name="add_product"),
    path("edit_product/<int:id>/", views.edit_product, name="edit_product"),
    path("delete_product/<int:id>/", views.delete_product, name="delete_product"),
    path("admin_brands/", views.admin_brands, name="admin_brands"),
    path("add_brand/", views.add_brand, name="add_brand"),
    path("delete_brand/<int:id>/", views.delete_brand, name="delete_brand"),
    path("edit_brand/<int:id>/", views.edit_brand, name="edit_brand"),
    path("admin_filter/", views.admin_filter, name="admin_filter"),
    path("admin_slider/", views.admin_slider, name="admin_slider"),
    path("a_header/", views.a_header, name="a_header"),
    path("admin_collections/", views.admin_collections, name="admin_collections"),
    path("edit_collection/<int:id>/", views.edit_collection, name="edit_collection"),
    path("delete_collection/<int:id>/", views.delete_collection, name="delete_collection"),
    path("admin_image_sections/", views.admin_image_sections, name="admin_image_sections"),
    path("admin_footer/", views.admin_footer, name="admin_footer"),
    path("admin_msg/", views.admin_msg, name="admin_msg"),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('refund-payment/<int:payment_id>/', views.refund_payment, name='refund_payment'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
