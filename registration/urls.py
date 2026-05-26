"""
URL configuration for registration project.
"""

from django.contrib import admin
from django.urls import path
from app1 import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path('a8Kx92Lm/admin/', admin.site.urls),

    # =========================
    # HOME
    # =========================
    path('xP92kaQ/home/', views.HomePage, name='home'),

    # =========================
    # AUTHENTICATION
    # =========================
    path('Lg82KsP1/signup/', views.SignupPage, name='signup'),

    path('idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/login/', views.login_view, name='login'),

    path('idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/signin/', views.login_email_view, name='signin'),

    path('idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/password/', views.login_password_view, name='signin_password'),

    path('idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/logout/', views.LogoutPage, name='logout'),

    path('idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/verify-otp/', views.verify_otp, name='verify_otp'),

    # =========================
    # DASHBOARD
    # =========================
    path('idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/dashboard/', views.DashboardPage, name='dashboard'),

    # =========================
    # USER PROFILE
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/profile/<int:user_id>/',
        views.get_profile,
        name='get_profile'
    ),

    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/profile/edit/<int:user_id>/',
        views.update_profile,
        name='update_profile'
    ),

    # =========================
    # BENEFICIARY
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/beneficiary/<int:beneficiary_id>/',
        views.get_beneficiary_profile,
        name='get_beneficiary_profile'
    ),

    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/beneficiary/edit/<int:beneficiary_id>/',
        views.update_beneficiary_profile,
        name='update_beneficiary'
    ),

    # =========================
    # TRANSACTIONS
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/transactions/',
        views.transactions,
        name='transactions'
    ),

    # =========================
    # HOLDINGS
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/holdings/',
        views.holdings_view,
        name='holdings'
    ),

    path(
        'api/holdings/',
        views.holdings_api,
        name='holdings_api'
    ),

    # =========================
    # PORTFOLIO
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/portfolio/<int:account_id>/',
        views.portfolio_view,
        name='portfolio'
    ),

    # =========================
    # BUY / SELL
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/buy/<int:account_id>/',
        views.buy_stock,
        name='buy'
    ),

    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/sell/<int:account_id>/<str:symbol>/',
        views.sell_stock,
        name='sell_stock'
    ),

    # =========================
    # MESSAGES
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/messages/',
        views.message_list,
        name='messages'
    ),

    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/messages/<int:pk>/',
        views.message_detail,
        name='message_detail'
    ),

    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/compose/',
        views.compose_page,
        name='compose'
    ),

    # =========================
    # STOCK API
    # =========================
    path(
        'api/price/<str:symbol>/',
        views.price_api,
        name='price_api'
    ),

    # =========================
    # GOLD
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/gold/',
        views.gold_view,
        name='gold'
    ),

    # =========================
    # ACCOUNTS
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/cash-account/',
        views.cash_account_list,
        name='cash_account_list'
    ),

    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/saving-account/',
        views.saving_account_list,
        name='saving_account'
    ),

    # =========================
    # CRYPTO
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/crypto/',
        views.crypto_list,
        name='crypto_list'
    ),

    # =========================
    # CALENDAR
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/calendar/',
        views.calendarPage,
        name='calendar'
    ),

    # =========================
    # LEGAL DOCUMENTS
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/legal-documents/',
        views.legal_documents_view,
        name='legal_documents'
    ),

    # =========================
    # STOCK DETAILS
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/stock/<str:symbol>/',
        views.stock_detail,
        name='stock_detail'
    ),

    # =========================
    # ACTIVITY
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/activity/',
        views.activity_list,
        name='activity'
    ),

    # =========================
    # PERFORMANCE
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/performance/',
        views.performancePage,
        name='performance'
    ),

    # =========================
    # TRANSFER
    # =========================
    path(
        'idmeTreasuryFedinvestSecureGov/TreasuryFedinvestHomeFedaccountGov/transfer/',
        views.transfer_view,
        name='transfer'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )