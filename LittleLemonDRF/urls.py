from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.menu_items, name="menu-items"),
    path('menu-items/<int:pk>', views.single_menu_item),
    path('category', views.category, name="category"),
    path('category/<int:pk>', views.category_detail, name="detail-category"),
    path('cart/menu-items', views.cart_menu_items, name="cart"),
    path('cart/menu-items/<int:pk>', views.cart_menu_items, name="add-cart-items"),
    path("groups/manager/users", views.manage_users, name="manage-users"),
    path("groups/manager/users/<int:pk>", views.manage_users_detail, name="manage-users-detail"),
    path("groups/delivery-crew/users", views.manage_delivery_crew, name="delivery-crew"),
    path("groups/delivery-crew/users/<int:pk>", views.manage_delivery_crew_detail, name="delivery-crew-detail"),
    path("orders", views.orders, name="orders"),
    path("orders/<int:pk>", views.orders_detail, name="orders-detail"),
]
