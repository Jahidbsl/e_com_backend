from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Category, Product, Cart,CartItem
from .serializers import CategorySerializer, ProductSerializer,CartSerializer, CartItemSerializer


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
        setrializer = ProductSerializer(product,context={'request': request})
        return Response(setrializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

  
#CATEGORIES API VIEWS
@api_view(["GET"])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# CART API VIEWS
@api_view(["GET"])
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=None) 
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(["POST"])
def add_to_cart(request):
    product_id = request.data.get("product_id")
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=None)  # Assuming a single cart
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return Response({"message": "Product added to cart", "cart": CartSerializer(cart).data}) 
   
@api_view(["POST"])
def remove_from_cart(request):
    item_id = request.data.get("item_id")
    CartItem.objects.filter(id=item_id).delete()
    return Response({"message": "Item removed from cart"})

@api_view(["POST"])
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
        
        
       
    

    
   
