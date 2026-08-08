from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework import status
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
)
from rest_framework import status
from decimal import Decimal


# PRODUCTS API VIEWS
@api_view(["GET"])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_product(request, pk):
    try:
        product = Product.objects.get(id=pk)
        setrializer = ProductSerializer(product, context={"request": request})
        return Response(setrializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)


# CATEGORIES API VIEWS
@api_view(["GET"])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# CART API VIEWS
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id = request.data.get("product_id")
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user) 
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return Response(
        {"message": "Product added to cart", "cart": CartSerializer(cart).data}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    item_id = request.data.get("item_id")
    CartItem.objects.filter(id=item_id).delete()
    return Response({"message": "Item removed from cart"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_cart_quantity(request):
    item_id = request.data.get("item_id")
    quantity = request.data.get("quantity")
    if not item_id or not quantity:
        return Response({"error": "Item ID and quantity are required"}, status=400)
    try:
        item = CartItem.objects.get(id=item_id)
        if int(quantity) < 1:
            item.delete()
            return Response({"error": "Quantity must be at least 1"}, status=400)

        item.quantity = quantity
        item.save()
        serializer = CartItemSerializer(item)
        return Response(serializer.data)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=404)


# ORDERS API VIEWS
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        data = request.data
        name = data.get("full_name")
        address = data.get("shipping_address")
        phone = data.get("phone_number")
        payment_method = data.get("payment_method", "COD")
        cart_items = data.get("items", [])

        # validation phone
        cleaned_phone = "".join(filter(str.isdigit, phone)) if phone else ""
        if not phone or len(cleaned_phone) < 10:
            return Response({"error": "Invalid phone number"}, status=400)

        # get users cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response({"error": "Cart is Empty"}, status=400)

        total = sum([item.product.price * item.quantity for item in cart.items.all()])
        order = Order.objects.create(
            user=request.user,
            name=name,
            address=address,
            phone=phone,
            payment_method=payment_method,
            total_amount=total
        )
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        cart.items.all().delete()
        return Response({"message": "Order Created Successfully", "order_id": order.id, "success": True})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# reg
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
   
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "User Created Successfully", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
