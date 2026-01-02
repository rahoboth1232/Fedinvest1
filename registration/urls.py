"""
URL configuration for registration project.
"""

from django.contrib import admin
from django.urls import path
from app1 import views
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.SignupPage, name='signup'),
    path('login/', views.login_view, name='login'),
    path('', views.HomePage, name='home'),
    path('logout/', views.LogoutPage, name='logout'),
     path('verify-otp/', views.verify_otp, name='verify_otp'),

    path('profile/<int:user_id>/', views.get_profile, name='get_profile'),
    path('profile/update/<int:user_id>/', views.update_profile, name='update_profile'),

    path('transactions/', views.transactions, name='transactions'),
    path('dashboard/', views.DashboardPage, name='dashboard'),

    path('holdings/', views.holdings_view, name='holdings'),
    path('api/holdings/', views.holdings_api, name='holdings_api'),

    path('portfolio/', views.portfolio, name='portfolio'),
    path('buy/', views.buy_stock, name='buy_stock'),

    path('messages/', views.message_list, name='messages'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('compose/', views.compose_page, name='compose'),

    path("api/price/<str:symbol>/", views.price_api, name="price_api"),
    path("sell/<str:symbol>/", views.sell_stock, name="sell_stock"),

    # ✅ ADD THIS NEW URL FOR GOLD HOLDINGS
    path('gold/', views.gold_view, name='gold'),
    path("balance/", views.balance_page, name="balance"),

    path('signin/', views.login_email_view, name='signin'),
    path('signin/password/', views.login_password_view, name='signin_password'),
   path('cash-account/', views.cash_account_list, name='cash_account_list'),
   path('saving-account/', views.saving_account_list, name='saving_account'),
   path("crypto/" , views.crypto_list, name="crypto_list"),
path("calender/", views.calendarPage, name="calendar"),
  path("legal-documents/", views.legal_documents_view, name="legal_documents"),
 path("stock/<str:symbol>/", views.stock_detail, name="stock_detail"),
 path("activity/", views.activity_list, name="activity"),
  path("performance/", views.performancePage, name="performance"),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

