from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [
    path('Home/', views.HomeProductListView.as_view(), name='product_list'),
    path('Customer_Dashboard/', views.CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('Admin/Dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('Admin/Dashboard/product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('Admin/Dashboard/product/list/', views.ProductListView.as_view(), name='admin_product_list'),
    path('Admin/Dashboard/product/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('Admin/Dashboard/product/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('Admin/see-customers/', views.AllCustomersView.as_view(), name='all_customers'),
    path('Admin/see-customer-order/<int:pk>/', views.CustomerOrdersView.as_view(), name='customer_orders'),
    path('Registration/', views.CustomerRegistrationView.as_view(), name='register'),
    path('Login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('process-payment/', views.PaymentProcessView.as_view(), name='process_payment'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
]