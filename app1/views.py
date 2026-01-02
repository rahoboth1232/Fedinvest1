from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from .models import UserProfile   # make sure Holding is imported
from .models import Account
from.serializers import UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Transaction
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt  # not used here, we use CSRF token normally

import random
from .models import Message
from django.http import JsonResponse
from decimal import Decimal
from .models import Stock
from .utils.prices import get_live_prices

from .models import Stock, Transaction
from .models import Stock, Transaction, Account
from .utils.prices import get_live_price
from django.http import JsonResponse
from django.shortcuts import render
from .models import Gold
from django.contrib.humanize.templatetags.humanize import intcomma
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Account   # Make sure Account model is imported
from django.shortcuts import render
from .models import CashAccount
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CashAccount  
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from .models import CashAccount
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import CashAccount
   
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse






# from .views import ActivityLogListView
# ===============================
# BASIC AUTHENTICATION VIEWS
# ===============================

def HomePage(request):
    return render(request, 'home.html')

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Your password and confirm password are not the same!")
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('login')

    return render(request, 'signup.html')

  # views.py

def login_view(request):

    request.session['login_form'] = request.get_full_path()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        otp_parts = [
            request.POST.get("otp1"),
            request.POST.get("otp2"),
            request.POST.get("otp3"),
            request.POST.get("otp4"),
            request.POST.get("otp5"),
            request.POST.get("otp6"),
        ]
        otp = "".join([x for x in otp_parts if x])

       
        if otp:
            user_id = request.session.get("user_id")

           
            if user_id:
                user = User.objects.get(id=user_id)
                login(request, user)
                request.session.pop("user_id", None)
                return redirect("dashboard")
            else:
                return render(request, "login.html", {
                    "show_otp": True,
                    "error": "Session expired, please log in again."
                })

       
        user = authenticate(request, username=username, password=password)
        if user is not None:
            request.session["user_id"] = user.id
            return render(request, "login.html", {"show_otp": True, "otp_stage": "set"})
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = request.session.get('otp')

        if entered_otp == session_otp:
            from django.contrib.auth.models import User
            username = request.session.get('username')
            user = User.objects.get(username=username)
            login(request, user)

            # cleanup session
            request.session.pop('otp', None)
            request.session.pop('username', None)
            return redirect('dashboard')
        else:
           messages.error(request,'Invalid OTP')
           return render(request,'login.html',{'show_otp': True})

    return render(request, 'login.html')

def LogoutPage(request):
    redirect_page = request.session.get('login_form','/')
    logout(request)
    return redirect(redirect_page)

@login_required(login_url='login')
def DashboardPage(request):
    accounts = Account.objects.filter(user=request.user)
    account_total = sum(a.amount for a in accounts)
    gold_holdings = Gold.objects.filter(user=request.user)
    gold_total = sum(h.amount for h in gold_holdings)
    cash_accounts = Account.objects.filter(user=request.user, account_type="Checking Account")
    cash_entries = CashAccount.objects.filter(user=request.user).order_by('-date')
    cash_total = cash_entries.first().account_balance if cash_entries.exists() else 0
    formatted_cash_total = intcomma(cash_total)
    saving_entries = SavingAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')
    saving_accounts = Account.objects.filter(user=request.user, account_type="Saving Account")

    saving_total = saving_entries.first().account_balance if saving_entries.exists() else 0
    formatted_saving_total = intcomma(saving_total) 
    # -------------------------------
    formatted_gold_total = intcomma(gold_total)
    formatted_amounts = {a.id: intcomma(a.amount) for a in accounts}
    total = account_total + gold_total + cash_total + saving_total
    formatted_total = intcomma(total)

   
    return render(request, 'dashboard.html', {
        'accounts': accounts,
        'formatted_amounts': formatted_amounts,
        'total': total,
        'formatted_total': formatted_total,
        'gold_total': gold_total,
        'formatted_gold_total': formatted_gold_total,
        "cash_entries": cash_entries,
        "cash_accounts": cash_accounts,
         "saving_accounts": saving_accounts,
        "cash_total": cash_total,
        "formatted_cash_total": formatted_cash_total,
        "saving_entries": saving_entries,
        "saving_total": saving_total,
        "formatted_saving_total": formatted_saving_total,
    })

# HOLDINGS PAGE (from model)
# ===============================
@login_required(login_url='login')
def holdings_view(request):
    accounts = Account.objects.filter(user=request.user)
    account_total = sum(a.amount for a in accounts)
    gold_holdings = Gold.objects.filter(user=request.user)
    gold_total = sum(h.amount for h in gold_holdings)
    cash_accounts = Account.objects.filter(user=request.user, account_type="Checking Account")
    cash_entries = CashAccount.objects.filter(user=request.user).order_by('-date', '-id')
    cash_total = cash_entries.first().account_balance if cash_entries.exists() else 0
    formatted_cash_total = intcomma(cash_total)
    saving_entries = SavingAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    saving_total = saving_entries.first().account_balance if saving_entries.exists() else 0
    formatted_saving_total = intcomma(saving_total)

    # =============================================
    formatted_gold_total = intcomma(gold_total)
    formatted_amounts = {a.id: intcomma(a.amount) for a in accounts}
    total = account_total + gold_total + cash_total + saving_total
    formatted_total = intcomma(total)

    return render(request, 'holdings.html', {
        'accounts': accounts,
        'formatted_amounts': formatted_amounts,
        'total': total,
        'formatted_total': formatted_total,
        'gold_total': gold_total,
        'formatted_gold_total': formatted_gold_total,
        "cash_entries": cash_entries,
        "cash_accounts": cash_accounts,
        "cash_total": cash_total,
        "formatted_cash_total": formatted_cash_total,
        "saving_entries": saving_entries,
        "saving_total": saving_total,
        "formatted_saving_total": formatted_saving_total,
    })
    
from django.utils import timezone
from datetime import timedelta
   
@login_required(login_url='login')

def transactions(request):

    # =========================
    # ✅ Handle POST (NO CHANGE)
    # =========================
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        stock_symbol = request.POST.get('stock_symbol') or ''
        quantity = request.POST.get('quantity') or 0
        price_per_share = request.POST.get('price_per_share') or 0
        amount = request.POST.get('amount') or 0
        notes = request.POST.get('notes') or ''

        Transaction.objects.create_transaction(
            user=request.user,
            transaction_type=transaction_type,
            stock_symbol=stock_symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            amount=amount,
            notes=notes
        )
        return redirect('transactions')
    
    cutoff_time = timezone.now() - timedelta(minutes=2)
    user_transactions = Transaction.objects.filter(
        user=request.user,
        date__lte=cutoff_time   
    ).order_by('-date')

    return render(request, 'transactions.html', {
        'transactions': user_transactions
    })

# ===============================
# API VIEWS (DRF)
# ===============================
def get_profile(request, user_id):
    profile = get_object_or_404(UserProfile, user_id=user_id)
    return render(request, 'profile.html', {'profile': profile})
@api_view(['POST'])
def update_profile(request, user_id):
    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        serializer = UserProfileSerializer(data=request.data)
    else:
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def message_list(request):
    messages = Message.objects.filter(user=request.user)
    return render(request, 'messages.html', {'messages': messages})
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk, user=request.user)
    # mark as read
    if not message.is_read:
        message.is_read = True
        message.save()
    return render(request, 'message_detail.html', {'message': message})
def compose_page(request):
    return render(request, "compose.html")


from django.http import JsonResponse
from django.core.cache import cache
from decimal import Decimal

import finnhub

client = finnhub.Client(api_key="d45gnf9r01qsugta9ai0d45gnf9r01qsugta9aig")  # <-- use your real key



from django.http import JsonResponse
from django.core.cache import cache
from decimal import Decimal

def get_live_prices(symbols):
    data = {}

    for symbol in symbols:
        try:
            q = client.quote(symbol)  # Live price data
            p = client.company_profile2(symbol=symbol)  # Company profile

            # Calculate percent change safely
            if q.get("dp") is not None:
                percent_change = round(q.get("dp"), 2)
            elif q.get("c") is not None and q.get("pc") is not None:
                percent_change = round(((q["c"] - q["pc"]) / q["pc"]) * 100, 2)
            else:
                percent_change = 0

            data[symbol] = {
                "symbol": symbol,
                "price": q.get("c"),
                "change": q.get("d"),
                "percent": percent_change,       # always a number
                "high": q.get("h"),
                "low": q.get("l"),
                "open": q.get("o"),
                "prev_close": q.get("pc"),
                "name": p.get("name", symbol)
            }
        except Exception:
            data[symbol] = {
                "symbol": symbol,
                "price": None,
                "change": None,
                "percent": 0,
                "high": None,
                "low": None,
                "open": None,
                "prev_close": None,
                "name": symbol
            }

    return data



def holdings_api(request):
    user = request.user

    stocks = Stock.objects.filter(user=user)
    symbols = [s.symbol for s in stocks]

    cache_key = f"live_prices_{user.id}"
    prices = cache.get(cache_key)

    if not prices:
        prices = get_live_prices(symbols)
        cache.set(cache_key, prices, 60 * 10)  # cache 10 min

    holdings = []
    portfolio_total = Decimal('0')

    for s in stocks:
        price_data = prices.get(s.symbol) if prices else None
    

        if price_data and price_data.get("price") is not None:
            live_price = Decimal(str(price_data["price"]))
            total = live_price * Decimal(s.quantity)
            company_name= price_data.get("name")
            portfolio_total += total
            total_value = str(total)
            change_percent = float(price_data.get("percent", 0))
        else:
            live_price = None
            total_value = None
            change_percent = 0

        holdings.append({
            'symbol': s.symbol,
            'quantity': s.quantity,
            'company_name': company_name,
            'live_price': str(live_price) if live_price else None,
            'total_value': total_value,
            'change_percent': change_percent,

        })

    account = Account.objects.filter(
        user=user,
        account_type="Brokerage Account"
    ).order_by('-id').first()

    brokerage_balance = Decimal(str(account.amount)) if account else Decimal('0')

    net_portfolio_value = (brokerage_balance - portfolio_total).quantize(Decimal('0.01')) \
        if portfolio_total > 0 else brokerage_balance.quantize(Decimal('0.01'))

    if portfolio_total > brokerage_balance:
        return JsonResponse({
            'error': 'Account is not sufficient',
            'holdings': holdings,
            'portfolio_total': str(portfolio_total),
            'brokerage_balance': str(brokerage_balance),
            'raw_total': "0"
        })

    final_response = {
        'holdings': holdings,
        'raw_total': str(net_portfolio_value),
        'portfolio_total': str(portfolio_total),
        'brokerage_balance': str(brokerage_balance),
    }

    return JsonResponse(final_response)



def price_api(request, symbol):
    # Always fetch data as list input
    prices = get_live_prices([symbol])

    # THIS is the dict with price info
    price_data = prices.get(symbol)

    # If no price exists or price is None -> return error
    if not price_data or price_data.get("price") is None:
        return JsonResponse({"error": "Invalid or unsupported symbol"}, status=400)

    # Return only the clean float price
    return JsonResponse({
        "symbol": symbol,
        "price": float(price_data["price"])
    })


  

def buy_stock(request):
    if request.method == "POST":
        symbol = request.POST.get('symbol', '').upper()
        qty = int(request.POST.get('quantity', 0))

        # ================================
        # Get cached price if available
        # ================================
        cache_key = f"stock_price_{symbol}"
        price = cache.get(cache_key ,)

        if price is None:
            price = get_live_price(symbol)
            if price is None:
                return JsonResponse({"error": "Invalid symbol"}, status=400)

            cache.set(cache_key, price, 60 * 15)

        price = Decimal(str(price))
        total_cost = price * qty

        # Save transaction
        Transaction.objects.create(
            user=request.user,
            transaction_type="BUY",
            stock_symbol=symbol,
            quantity=qty,
            price_per_share=price,
            amount=total_cost
        )

        # Update holding
        stock, created = Stock.objects.get_or_create(
            user=request.user,
            symbol=symbol
        )
        stock.quantity = stock.quantity + qty

        if created and not stock.company_name:
            stock.company_name = symbol

        stock.save()

        # =============================================
        # 🚀 CLEAR HOLDINGS PRICE CACHE IMMEDIATELY
        # =============================================
        user_price_cache = f"live_prices_{request.user.id}"
        cache.delete(user_price_cache)

        return redirect("portfolio")

    return render(request, "buyStock.html")

@login_required
def balance_page(request):
    accounts = Account.objects.filter(user=request.user)
    account_total = sum(a.amount for a in accounts)
    gold_holdings = Gold.objects.filter(user=request.user)
    gold_total = sum(h.amount for h in gold_holdings)
    cash_entries = CashAccount.objects.filter(user=request.user).order_by('-date')
    cash_total = cash_entries.first().account_balance if cash_entries.exists() else 0
    saving_entries = SavingAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    saving_total = saving_entries.first().account_balance if saving_entries.exists() else 0
    formatted_saving_total = intcomma(saving_total) 
    # -------------------------------
    total = account_total + gold_total + cash_total + saving_total
    formatted_total = intcomma(total)

   
    return render(request, 'Balance.html', {
        'accounts': accounts,
        'total': total,
        'formatted_total': formatted_total,
         "saving_entries": saving_entries,
        "saving_total": saving_total,
        "formatted_saving_total": formatted_saving_total,
    })




def portfolio(request):
  
    
    return render(request, "portfolio.html")

def sell_stock(request, symbol):
    stock = get_object_or_404(Stock, user=request.user, symbol=symbol)

    if request.method == "POST":
        qty = int(request.POST.get("quantity"))
        mode = request.POST.get("mode")
        custom_price = request.POST.get("custom_price")

        if qty > stock.quantity:
            messages.error(request, "You cannot sell more than you own.")
            return redirect("sell_stock", symbol=symbol)

        # ✅ A – SELL AT MARKET PRICE
        if mode == "market":
            sell_price = Decimal(get_live_price(symbol))

        # ✅ B – SELL AT BUY PRICE
        elif mode == "buyprice":
            sell_price = stock.buy_price

       
        elif mode == "custom":
            if not custom_price:
                messages.error(request, "Enter custom price.")
                return redirect("sell_stock", symbol=symbol)
            sell_price = Decimal(custom_price)

        total_sell_amount = sell_price * qty

        # ✅ UPDATE PORTFOLIO
        stock.quantity -= qty
        if stock.quantity == 0:
            stock.delete()
        else:
            stock.save()

        # ✅ UPDATE ACCOUNT 
        

        # ✅ SAVE SELL TRANSACTION
        Transaction.objects.create(
    user=request.user,
    transaction_type="SELL",
    stock_symbol=symbol,
    quantity=qty,
    price_per_share=sell_price,
    amount=total_sell_amount,
    notes="Sold stock"
)

        messages.success(request, f"Sold {qty} shares of {symbol} at ${sell_price}.")
        return redirect("portfolio")

    return render(request, "sell_stock.html", {"stock": stock})


def gold_view(request):
    user = request.user
    holdings = Gold.objects.filter(user=user).order_by('-date')

    gold_amount = sum(h.amount for h in holdings)
    formatted_gold_amount = intcomma(gold_amount)  # Formatted total

    return render(request, "gold.html", {
        "holdings": holdings,
        "gold_amount": gold_amount,  # original number
        "formatted_gold_amount": formatted_gold_amount,  # formatted number
        "title": "Gold Holdings"
    })


def login_email_view(request):
    request.session['login_form'] =  request.get_full_path()

    if request.method == "POST":
        email = request.POST.get("email")

        # Check if user exists using email
        if User.objects.filter(email=email).exists():
            request.session["signin_email"] = email
            return redirect("signin_password")
        else:
            return render(request, "signIn.html", {
                "error": "Email not found"
            })

    return render(request, "signIn.html")

def login_password_view(request):
    email = request.session.get("signin_email")

    # If user opens password page directly without email
    if not email:
        return redirect("signin")

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect("signin")

    if request.method == "POST":
        password = request.POST.get("password")

        # Authenticate using username + password
        user = authenticate(request, username=user_obj.username, password=password)

        if user:
            login(request, user)  # Django login
            request.session.pop("signin_email", None)
            return redirect("dashboard")
        else:
            return render(request, "Password.html", {
                "error": "Incorrect password"
            })

    return render(request, "Password.html")

@login_required
def cash_account_list(request):
    # CashAccount ledger entries with account info
    cash_entries = CashAccount.objects.filter(user=request.user).order_by('-date', '-id')

    # Cash accounts for dropdown or display
    cash_accounts = Account.objects.filter(user=request.user, account_type="Checkings Account")

    # Total balance per account or overall
    cash_total = cash_entries.last().account_balance if cash_entries.exists() else 0
    formatted_cash_total = intcomma(cash_total)

    return render(request, "cash_account.html", {
        "cash_entries": cash_entries,
        "cash_accounts": cash_accounts,
        "cash_total": cash_total,
        "formatted_cash_total": formatted_cash_total,
    })

from .models import SavingAccount
from django.contrib.humanize.templatetags.humanize import intcomma

@login_required
def saving_account_list(request):
    saving_entries = SavingAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    saving_total = saving_entries.last().account_balance if saving_entries.exists() else 0
    formatted_saving_total = intcomma(saving_total)
    saving_accounts = Account.objects.filter(user=request.user, account_type="Cash & Cash Equivalents")

    return render(request, "saving_account.html", {
        "saving_entries": saving_entries,
        "saving_total": saving_total,
        "formatted_saving_total": formatted_saving_total,
         "saving_accounts": saving_accounts,
    })

from django.shortcuts import render
from .models import Crypto

def crypto_list(request):
    cryptos = Crypto.objects.all().order_by("-date")
    total = sum(c.amount for c in cryptos)

    context = {
        "cryptos": cryptos,
        "total": f"${total:,.2f}",  # USD format
    }
    return render(request, "crypto.html", context)

def calendarPage(request):
     return render(request, "calendar.html")

from django.shortcuts import render
from django.utils import timezone

# def legal_documents(request):
#     """
#     Renders the Legal Documents page.
#     No DB changes. Documents are defined here (can be moved to settings or DB later).
#     """

#     # Example documents list - update file_url to your real static/media file paths
#     docs = [
#         {
#             "title": "Terms & Conditions",
#             "slug": "terms-conditions",
#             "date": timezone.datetime(2025, 1, 1).date(),
#             "file_url": "/static/docs/terms-and-conditions.pdf",
#             "type": "PDF"
#         },
#         {
#             "title": "Risk Disclosure Document",
#             "slug": "risk-disclosure",
#             "date": timezone.datetime(2025, 1, 1).date(),
#             "file_url": "/static/docs/risk-disclosure.pdf",
#             "type": "PDF"
#         },
#         {
#             "title": "Privacy Policy",
#             "slug": "privacy-policy",
#             "date": timezone.datetime(2025, 1, 1).date(),
#             "file_url": "/static/docs/privacy-policy.pdf",
#             "type": "PDF"
#         },
#         {
#             "title": "Investor Rights & Responsibilities",
#             "slug": "investor-rights",
#             "date": timezone.datetime(2025, 1, 1).date(),
#             "file_url": "/static/docs/investor-rights.pdf",
#             "type": "PDF"
#         },
#         {
#             "title": "Anti-Money Laundering Policy",
#             "slug": "aml-policy",
#             "date": timezone.datetime(2025, 1, 1).date(),
#             "file_url": "/static/docs/aml-policy.pdf",
#             "type": "PDF"
#         },
#         {
#             "title": "Trading Guidelines (F&O, Intraday)",
#             "slug": "trading-guidelines",
#             "date": timezone.datetime(2025, 1, 1).date(),
#             "file_url": "/static/docs/trading-guidelines.pdf",
#             "type": "PDF"
#         },
#         # Example: uploaded image file path from your session (dev will map to URL)
#         {
#             "title": "Admin Panel Screenshot (example file)",
#             "slug": "admin-screenshot",
#             "date": timezone.datetime(2025, 11, 20).date(),
#             "file_url": "/mnt/data/6e48a730-5038-48d5-88c6-6abf624479b6.png",
#             "type": "PNG"
#         },
#     ]

#     query = request.GET.get("q", "").strip()
#     if query:
#         docs = [d for d in docs if query.lower() in d["title"].lower()]

#     context = {
#         "docs": docs,
#         "query": query,
#     }
#     return render(request, "legal_documents.html", context)

from django.shortcuts import render
from .models import LegalDocument

def legal_documents_view(request):
    query = request.GET.get("q", "").strip()
    docs = LegalDocument.objects.all()
    if query:
        docs = docs.filter(title__icontains=query)

    context = {
        "docs": docs,
        "query": query,
    }
    return render(request, "legal_documents.html", context)
import json
from datetime import datetime
import yfinance as yf
from django.shortcuts import render
from django.shortcuts import render
from datetime import datetime, timedelta
import yfinance as yf
import json
from datetime import datetime, timedelta
import yfinance as yf
from django.shortcuts import render
import json

from django.http import JsonResponse

def stock_detail(request, symbol):
    ticker = yf.Ticker(symbol)
    company_name = ticker.info.get("longName", symbol)

    timeframe = request.GET.get("timeframe")  # 1d, 1w, 1m, 3m
    start = request.GET.get("start")
    end = request.GET.get("end")

    end_date = datetime.today()

    if start and end:
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
        delta_days = (end_date - start_date).days
        interval = "1m" if delta_days <= 1 else "60m" if delta_days <= 7 else "1d"
    elif timeframe:
        if timeframe == "1d":
            start_date = end_date - timedelta(days=3)
            interval = "1m"
        elif timeframe == "1w":
            start_date = end_date - timedelta(weeks=1)
            interval = "30m"
        elif timeframe == "1m":
            start_date = end_date - timedelta(days=30)
            interval = "60m"
        elif timeframe == "3m":
            start_date = end_date - timedelta(days=90)
            interval = "1d"
        elif timeframe == "6m":
            start_date = end_date - timedelta(days=180)
            interval = "1d"
        else:
            start_date = end_date - timedelta(days=30)
            interval = "1d"
    else:
        start_date = end_date - timedelta(days=30)
        interval = "1d"

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # -------------------------
    # 2️⃣ Fetch historical data
    # -------------------------
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    except Exception as e:
        print("Error fetching data:", e)
        data = None

    history = []
    if data is not None and not data.empty:
        for idx, row in data.iterrows():
            time_val = idx.strftime("%Y-%m-%d") if interval in ["1d", "1wk", "1mo"] else int(idx.timestamp())
            history.append({
                "time": time_val,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            })

    # -------------------------
    # 3️⃣ Return JSON if AJAX
    # -------------------------
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"history": history})

    # -------------------------
    # 4️⃣ Render template
    # -------------------------
    context = {
        "symbol": symbol,
        "start": start_str,
        "end": end_str,
        "history": json.dumps(history),
        "company_name": company_name
    }
    return render(request, "stock_detail.html", context)


from django.utils import timezone
from django.shortcuts import render
from django.db.models import F
from django.db import models
from django.shortcuts import render
from django.contrib.humanize.templatetags.humanize import intcomma

from itertools import chain
from django.utils.timezone import localtime

# def activity_list(request):
#     cash_entries = CashAccount.objects.filter(user=request.user)
#     saving_entries = SavingAccount.objects.filter(user=request.user)

#     # Add a type label to each object so template can identify
#     for c in cash_entries:
#         c.entry_type = "Checking Account"

#     for s in saving_entries:
#         s.entry_type = "Cash & Cash Equivalent Account"

#     # Combine & sort by date desc
#     combined_entries = sorted(
#         chain(cash_entries, saving_entries),
#         key=lambda x: (x.date, x.id),
#         reverse=True
#     )

#     return render(request, "activity.html", {
#         "entries": combined_entries,
#     })

from django.utils.dateformat import DateFormat
from django.contrib.humanize.templatetags.humanize import intcomma

def activity_list(request):

    cash_entries = CashAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    saving_entries = SavingAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    cash_accounts = Account.objects.filter(
        user=request.user, account_type="Checkings Account"
    )

    saving_accounts = Account.objects.filter(
        user=request.user, account_type="Cash & Cash Equivalents"
    )

    # Get actual account numbers
    cash_acc_number = cash_accounts.first().account_number if cash_accounts.exists() else ""
    saving_acc_number = saving_accounts.first().account_number if saving_accounts.exists() else ""

    # Convert objects → unified entry list
    entries = []

    for c in cash_entries:
        entries.append({
            "date": c.date,
            "description": c.description,
            "credit": c.credit,
            "debit": c.debit,
            "balance": c.account_balance,
            "entry_type": "Cash Account",
            "account_number": cash_acc_number,
        })

    for s in saving_entries:
        entries.append({
            "date": s.date,
            "description": s.description,
            "credit": s.credit,
            "debit": s.debit,
            "balance": s.account_balance,
            "entry_type": "Saving Account",
            "account_number": saving_acc_number,
        })

    # Sort newest first
    entries = sorted(entries, key=lambda x: x["date"], reverse=True)

    return render(request, "activity.html", {
        "entries": entries,
    })

def performancePage(request):
     return render(request, "Performance.html")