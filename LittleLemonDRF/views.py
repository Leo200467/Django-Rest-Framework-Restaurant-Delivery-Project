import datetime

from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, Category, MenuItem, Order, OrderItem
from .serializers import (
    MenuItemSerializer,
    CategorySerializer,
    UserSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
)

# Create your views here.


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.all()
        category_id = request.query_params.get("category")
        price = request.query_params.get("price")
        search = request.query_params.get("search")
        if category_id:
            print("filtering by category")
            items = MenuItem.objects.filter(category__id=category_id)
        if price:
            print("filtering by price")
            items = MenuItem.objects.filter(price=price)
        if search:
            print("filtering by search")
            items = MenuItem.objects.filter(title__startswith=search)
        serialized_items = MenuItemSerializer(items, many=True)
        return Response(serialized_items.data)
    if request.method == "POST":
        if request.user.groups.filter(name="Manager").exists():
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def single_menu_item(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "GET":
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    if request.user.groups.filter(name="Manager").exists():
        if request.method == "PATCH":
            serialized_item = MenuItemSerializer(item, data=request.data)
            if serialized_item.is_valid(raise_exception=True):
                serialized_item.save()
                return Response(serialized_item.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == "DELETE":
            item.delete()
            return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def category(request):
    if request.method == "GET":
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True)
        return Response(serialized_categories.data)
    if request.method == "POST":
        serialized_category = CategorySerializer(data=request.data)
        serialized_category.is_valid(raise_exception=True)
        serialized_category.save()
        return Response(serialized_category.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "GET":
        serialized_category = CategorySerializer(category)
        return Response(serialized_category.data)
    if request.method == "PUT":
        if request.user.groups.filter(name="Manager").exists():
            serialized_category = CategorySerializer(category, data=request.data)
            if serialized_category.is_valid(raise_exception=True):
                serialized_category.save()
                return Response(serialized_category.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def manage_users(request):
    if request.user.groups.filter(name="Manager").exists():
        manager_group = Group.objects.get(name="Manager")
        if request.method == "GET":
            users = manager_group.user_set.all()
            serialized_users = UserSerializer(users, many=True)
            return Response(serialized_users.data)
        username = request.data["username"]
        if username:
            user = get_object_or_404(User, username=username)
            if request.method == "POST":
                user.groups.add(manager_group)
                return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_users_detail(request, pk):
    if request.user.groups.filter(name="Manager").exists():
        manager_group = Group.objects.get(name="Manager")
        user = get_object_or_404(User, pk=pk)
        if user.groups.filter(name="Manager").exists():
            if request.method == "GET":
                serialized_user = UserSerializer(user)
                return Response(serialized_user.data)
            if request.method == "DELETE":
                user.groups.remove(manager_group)
                return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def manage_delivery_crew(request):
    if request.user.groups.filter(name="Manager").exists():
        delivery_crew_group = Group.objects.get(name="Delivery Crew")
        if request.method == "GET":
            users = delivery_crew_group.user_set.all()
            serialized_users = UserSerializer(users, many=True)
            return Response(serialized_users.data)
        username = request.data["username"]
        if username:
            user = get_object_or_404(User, username=username)
            if request.method == "POST":
                user.groups.add(delivery_crew_group)
                return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_delivery_crew_detail(request, pk):
    if request.user.groups.filter(name="Manager").exists():
        delivery_crew_group = Group.objects.get(name="Delivery Crew")
        user = get_object_or_404(User, pk=pk)
        if request.method == "GET":
            serialized_user = UserSerializer(user)
            return Response(serialized_user.data)
        if request.method == "DELETE":
            if user.groups.filter(name="Delivery Crew").exists():
                user.groups.remove(delivery_crew_group)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def cart_menu_items(request):
    if request.method == "GET":
        cart = get_object_or_404(Cart, user=request.user)
        serialized_cart = CartSerializer(cart)
        return Response(serialized_cart.data)

    if request.method == "POST":
        menu_item = MenuItem.objects.get(pk=request.data["menuitem_id"])
        Cart.objects.update_or_create(
            user=request.user,
            menuitem=menu_item,
            menuitem_id=request.data["menuitem_id"],
            quantity=request.data["quantity"],
            unit_price=menu_item.price,
            price=menu_item.price * request.data["quantity"],
        )
        return Response(status=status.HTTP_200_OK)

    if request.method == "DELETE":
        cart = get_object_or_404(Cart, user=request.user)
        cart.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def orders(request):
    if request.method == "GET":
        if request.user.groups.filter(name="Manager").exists():
            order_item = OrderItem.objects.all()
            serialized_order_item = OrderItemSerializer(order_item, many=True)
            return Response(serialized_order_item.data)

        elif request.user.groups.filter(name="Delivery Crew").exists():
            order_items = OrderItem.objects.filter(order__delivery_crew=request.user)
            serialized_order_items = OrderItemSerializer(order_items, many=True)
            return Response(serialized_order_items.data)

        else:
            order_items = OrderItem.objects.filter(order__user=request.user)
            if order_items:
                serialized_order_items = OrderItemSerializer(order_items, many=True)
                return Response(serialized_order_items.data)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        find_cart = Cart.objects.filter(user=request.user).exists()
        if find_cart:
            cart = Cart.objects.get(user=request.user)
            serialized_cart = CartSerializer(cart)
            print("serialzed cart", serialized_cart)
            print("serialized cart data", serialized_cart.data["menuitem"]["id"])
            new_order = Order.objects.create(
                user=request.user,
                delivery_crew=None,
                status=0,
                total=serialized_cart.data["price"],
                date=datetime.date.today(),
            )

            OrderItem.objects.create(
                order=new_order,
                menuitem=MenuItem.objects.get(
                    id=serialized_cart.data["menuitem"]["id"]
                ),
                quantity=serialized_cart.data["quantity"],
                unit_price=serialized_cart.data["unit_price"],
                price=serialized_cart.data["price"],
            )

            cart.delete()
            serialized_order_item = OrderSerializer(new_order)
            return Response(serialized_order_item.data)

        else:
            return Response(
                data={"Detail": "User cart not found"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def orders_detail(request, pk):
    if request.method == "GET":
        order_items = OrderItem.objects.filter(order__user=request.user, order__pk=pk)
        if order_items:
            serialized_order_items = OrderItemSerializer(order_items, many=True)
            return Response(serialized_order_items.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == "PUT":
        if request.user.groups.filter(name="Manager").exists():
            order = get_object_or_404(Order, pk=pk)
            serialized_order = OrderSerializer(
                order, data=request.data, context={"request": request}
            )
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    if request.method == "PATCH":
        order = get_object_or_404(Order, pk=pk)
        serialized_order = OrderSerializer(
            order, data=request.data, partial=True, context={"request": request}
        )
        serialized_order.is_valid(raise_exception=True)
        if request.user.groups.filter(name="Manager").exists():
            serialized_order.save()
            return Response(serialized_order.data)
        elif request.user.groups.filter(name="Delivery Crew").exists():
            order = Order.objects.filter(pk=pk)
            order.update(status=request.data["status"])
            serialized_order = OrderSerializer(order, many=True)
            return Response(serialized_order.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    if request.method == "DELETE":
        if request.user.groups.filter(name="Manager").exists():
            order = get_object_or_404(Order, pk=pk)
            order.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
