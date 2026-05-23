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

    path('Qw91LmX2/login/', views.login_view, name='login'),

    path('Mn28ZxP0/signin/', views.login_email_view, name='signin'),

    path('Yt72LpQ9/password/', views.login_password_view, name='signin_password'),

    path('Kp44XsD2/logout/', views.LogoutPage, name='logout'),

    path('Vb21QaM7/verify-otp/', views.verify_otp, name='verify_otp'),

    # =========================
    # DASHBOARD
    # =========================
    path('Dx82LmQ1/dashboard/', views.DashboardPage, name='dashboard'),

    # =========================
    # USER PROFILE
    # =========================
    path(
        'Ua82LmP/profile/<int:user_id>/',
        views.get_profile,
        name='get_profile'
    ),

    path(
        'Ua82LmP/profile/edit/<int:user_id>/',
        views.update_profile,
        name='update_profile'
    ),

    # =========================
    # BENEFICIARY
    # =========================
    path(
        'Bn92QaX/beneficiary/<int:beneficiary_id>/',
        views.get_beneficiary_profile,
        name='get_beneficiary_profile'
    ),

    path(
        'Bn92QaX/beneficiary/edit/<int:beneficiary_id>/',
        views.update_beneficiary_profile,
        name='update_beneficiary'
    ),

    # =========================
    # TRANSACTIONS
    # =========================
    path(
        'Tx82LmP/transactions/',
        views.transactions,
        name='transactions'
    ),

    # =========================
    # HOLDINGS
    # =========================
    path(
        'Hd82LpQ/holdings/',
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
        'Pf82LmQ/portfolio/<int:account_id>/',
        views.portfolio_view,
        name='portfolio'
    ),

    # =========================
    # BUY / SELL
    # =========================
    path(
        'By82LpQ/buy/<int:account_id>/',
        views.buy_stock,
        name='buy'
    ),

    path(
        'sell/<int:account_id>/<str:symbol>/',
        views.sell_stock,
        name='sell_stock'
    ),

    # =========================
    # MESSAGES
    # =========================
    path(
        'Ms82LpQ/messages/',
        views.message_list,
        name='messages'
    ),

    path(
        'Ms82LpQ/messages/<int:pk>/',
        views.message_detail,
        name='message_detail'
    ),

    path(
        'Cp82QaX/compose/',
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
        'Gd82QaP/gold/',
        views.gold_view,
        name='gold'
    ),

    # =========================
    # ACCOUNTS
    # =========================
    path(
        'Ca82LpQ/cash-account/',
        views.cash_account_list,
        name='cash_account_list'
    ),

    path(
        'Sa82QaX/saving-account/',
        views.saving_account_list,
        name='saving_account'
    ),

    # =========================
    # CRYPTO
    # =========================
    path(
        'Cr82LmP/crypto/',
        views.crypto_list,
        name='crypto_list'
    ),

    # =========================
    # CALENDAR
    # =========================
    path(
        'Cl82QaP/calendar/',
        views.calendarPage,
        name='calendar'
    ),

    # =========================
    # LEGAL DOCUMENTS
    # =========================
    path(
        'Lg82QaM/legal-documents/',
        views.legal_documents_view,
        name='legal_documents'
    ),

    # =========================
    # STOCK DETAILS
    # =========================
    path(
        'St82LmQ/stock/<str:symbol>/',
        views.stock_detail,
        name='stock_detail'
    ),

    # =========================
    # ACTIVITY
    # =========================
    path(
        'Ac82QaX/activity/',
        views.activity_list,
        name='activity'
    ),

    # =========================
    # PERFORMANCE
    # =========================
    path(
        'Pf91LmX/performance/',
        views.performancePage,
        name='performance'
    ),

    # =========================
    # TRANSFER
    # =========================
    path(
        'Tr82QaP/transfer/',
        views.transfer_view,
        name='transfer'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )