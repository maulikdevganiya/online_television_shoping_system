from django.urls import path,include
from app import views
from . import views
from django.conf.urls.static import static  
from django.conf import settings
# Create your views here.

urlpatterns = [
    path('', views.index, name='index'),
    path('filter', views.filter, name="filter" ),
    path('login', views.login, name="login" ),
    path("header/",views.header,name="header"),
    path("footer/",views.footer,name="footer"),
    path('my_address', views.my_address, name="my_address" ),
    path('my_cart', views.my_cart, name="my_cart" ),
    path('my_cart2', views.my_cart2, name="my_cart2" ),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name="add_to_cart" ),
    path('update_cart_quantity/<int:item_id>/', views.update_cart_quantity, name="update_cart_quantity" ),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name="remove_from_cart" ),
    path('my_wishlist', views.my_wishlist, name="my_wishlist" ),
    path('my_order', views.my_order, name="my_order" ),
    path('product_details/<int:product_id>/', views.product_details, name="product_details" ),
    path('profile', views.profile, name="profile" ),
    path('edit_profile', views.edit_profile, name="edit_profile" ),
    path('profile_sidebar', views.profile_sidebar, name="profile_sidebar" ),
    path('registration', views.registration, name="registration" ),
    path('about_us', views.about_us, name="about_us" ),
    path('contact_us', views.contact_us, name="contact_us" ),
    path('checkout', views.checkout, name="checkout" ),
    path('place_order', views.place_order, name="place_order" ),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name="order_confirmation" ),
    path('add_address', views.add_address, name="add_address" ),
    path('edit_address/<int:address_id>/', views.edit_address, name="edit_address" ),
    path('delete_address/<int:address_id>/', views.delete_address, name="delete_address" ),
    path('set_default_address/<int:address_id>/', views.set_default_address, name="set_default_address" ),
    path('payment_success/', views.payment_success, name="payment_success" ),
    path('payment_failure/', views.payment_failure, name="payment_failure" ),
    path('payment_cancel/', views.payment_cancel, name="payment_cancel" ),
    path("logout/", views.logout_view, name="logout"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)