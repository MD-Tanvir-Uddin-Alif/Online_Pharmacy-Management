from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, View, DetailView
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import CustomerProfile, Product, Category, Cart, CartItem, Payment, Order, OrderItem
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from .forms import CustomerRegistrationForm, CustomLoginForm, ProductForm
# Create your views here.

class CustomerRegistrationView(CreateView):
    model = User
    template_name = 'register.html'  
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('login')  

    def form_valid(self, form):
        user = form.save(commit=False)  
        password = form.cleaned_data['password']
        user.set_password(password)  
        user.save()

        CustomerProfile.objects.create(
            user=user,
            phone_number=form.cleaned_data['phone_number'],
            image=form.cleaned_data['image'],
            gender=form.cleaned_data['gender'],
        )

        messages.success(self.request, "Registration successful! You can now log in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission. Please try again.")
        return super().form_invalid(form)
    

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomLoginForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('request', None)  
        return kwargs

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)

            if user.is_superuser:
                messages.success(self.request, "Login successful! Welcome to the admin panel.")
                return redirect('admin_dashboard')  
            else:
                messages.success(self.request, "Login successful! Welcome to your dashboard.")
                return redirect('customer_dashboard') 
        else:
            messages.error(self.request, "Invalid username or password.")
            return redirect('login')
        


class CustomerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'customer_dashboard.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        context['first_name'] = user.first_name
        context['last_name'] = user.last_name
        context['email'] = user.email

        customer_profile = getattr(user, 'customer_profile', None)
        if customer_profile:
            context['phone_number'] = customer_profile.phone_number or 'N/A'
            context['gender'] = customer_profile.gender or 'Not Specified'

            if customer_profile.image:
                context['profile_image'] = customer_profile.image.url 
            else:
                context['profile_image'] = None  
        else:
            context['phone_number'] = 'N/A'
            context['gender'] = 'Not Specified'
            context['profile_image'] = None  

        return context



    


# admin 
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin = self.request.user
        context['admin_details'] = {
            'first_name': admin.first_name,
            'last_name': admin.last_name,
            'username': admin.username,
            'email': admin.email,
        }
        context['customers'] = CustomerProfile.objects.select_related('user').all()
        return context
    

class ProductListView(ListView, LoginRequiredMixin):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        if category_id and category_id != 'all':
            queryset = queryset.filter(category__id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', 'all')
        return context


class ProductUpdateView(UpdateView, LoginRequiredMixin):
    model = Product
    form_class = ProductForm
    template_name = 'product_edit.html'
    context_object_name = 'product'

    def get_success_url(self):
        return reverse_lazy('admin_product_list')
    

class ProductDeleteView(DeleteView, LoginRequiredMixin):
    model = Product
    template_name = 'product_confirm_delete.html'
    context_object_name = 'product'
    success_url = reverse_lazy('admin_product_list')


class ProductCreateView(CreateView, LoginRequiredMixin):
    model = Product
    form_class = ProductForm
    template_name = 'product_create.html'
    success_url = reverse_lazy('admin_product_list')  

    def form_valid(self, form):
        return super().form_valid(form)


class AllCustomersView(ListView):
    model = User
    template_name = 'customers.html'
    context_object_name = 'customers'

    def get_queryset(self):
        return User.objects.filter(is_staff=False)



class CustomerOrdersView(DetailView):
    model = User
    template_name = 'customer_orders.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.object)
        return context


    



class HomeProductListView(ListView):
    model = Product 
    template_name = 'home_product_list.html'  
    context_object_name = 'products'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset


# cart 

class CartDetailView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'cart_detail.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = cart
        return context
    

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)

        if product.stock == 0:
            messages.error(request, "This product is out of stock.")
            return redirect('product_list')

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(request, f"{product.name} was added to your cart.")
        return redirect('cart_detail')
    

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs['product_id']
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()

        messages.success(request, "Item was removed from your cart.")
        return redirect('cart_detail')
    

# payment 
@method_decorator(login_required, name='dispatch')
class CheckoutView(TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_cart = self.request.user.cart  
            cart_items = user_cart.items.all()  
            total_price = user_cart.total_price()  
        except Cart.DoesNotExist:
            cart_items = []
            total_price = 0

        context['cart_items'] = cart_items
        context['total_price'] = total_price
        return context

    

@method_decorator(login_required, name='dispatch')
class PaymentProcessView(View):
    def post(self, request, *args, **kwargs):
        payment_method = request.POST.get('payment_method')

        if not payment_method:
            messages.error(request, "Please select a payment method!")
            return redirect('checkout')

        try:
            user_cart = request.user.cart
            cart_items = user_cart.items.all()
            total_price = user_cart.total_price()
        except Cart.DoesNotExist:
            messages.error(request, "Your cart is empty!")
            return redirect('checkout')

        payment = Payment.objects.create(
            user=request.user,
            method=payment_method,
            amount=total_price,
        )

        order = Order.objects.create(
            user=request.user,
            payment=payment,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()

        return render(request, "memo.html", {
            'payment': payment,
            'cart_items': [  
                {
                    "product": item.product,
                    "quantity": item.quantity,
                    "total_price": item.total_price(),
                }
                for item in cart_items
            ],
            'total_price': total_price,
            'customer_name': request.user.username,
            'phone_number': request.user.customer_profile.phone_number,
        })




# order 

class OrderListView(ListView, LoginRequiredMixin):
    model = Order
    template_name = "order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at') 
    

class OrderDetailView(DetailView):
    model = Order
    template_name = "order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)