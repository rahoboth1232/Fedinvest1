
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction, models
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.dateformat import DateFormat
from django.contrib.humanize.templatetags.humanize import intcomma
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from itertools import chain
import json
import random
import yfinance as yf
import finnhub
from .models import (
    UserProfile,
    BeneficiaryProfile,
    Account,
    AccountTransfer,
    CashAccount,
    SavingAccount,
    BankAccount,
    TransferRequest,
    Transaction,
    Stock,
    Gold,
    Crypto,
    Message,
    AdminCompose,
    LegalDocument,
    CashAccounts,
)
from .serializers import (
    UserProfileSerializer,
    BeneficiaryProfileSerializer,
)
from decimal import Decimal
from django.db.models import Sum
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q, Sum
from decimal import Decimal
from django.db import transaction
from .services.price_service import get_stock_price
from django.db.models import Q

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
    
@login_required(login_url='login')

def transactions(request):

    if request.method == 'POST':
        
        
        
        account_id = request.POST.get('account')

        account = Account.objects.get(id=account_id, user=request.user)
        transaction_type = request.POST.get('transaction_type')
        stock_symbol = request.POST.get('stock_symbol') or ''
        quantity = request.POST.get('quantity') or 0
        price_per_share = request.POST.get('price_per_share') or 0
        amount = request.POST.get('amount') or 0
        notes = request.POST.get('notes') or ''

        Transaction.objects.create_transaction(
            user=request.user,
            account=account,

            transaction_type=transaction_type,
            stock_symbol=stock_symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            amount=amount,
            notes=notes
        )
        return redirect('transactions')
    
    cutoff_time = timezone.now() - timedelta(seconds=30)
    user_transactions = Transaction.objects.filter(
        user=request.user,
        date__lte=cutoff_time   
    ).order_by('-date')

    return render(request, 'transactions.html', {
        'transactions': user_transactions
    })

def get_profile(request, user_id):
    profile = get_object_or_404(UserProfile, user_id=user_id)
    # Get the first beneficiary (optional)
    beneficiary = BeneficiaryProfile.objects.filter(user_id=user_id).first()
    return render(request, 'profile.html', {'profile': profile, 'beneficiary': beneficiary})

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

@login_required
def get_beneficiary_profile(request, beneficiary_id):
    beneficiary = get_object_or_404(BeneficiaryProfile, id=beneficiary_id, user=request.user)
    return render(request, 'beneficiaryprofile.html', {'beneficiary': beneficiary})

@login_required
@api_view(['POST'])
def update_beneficiary_profile(request, beneficiary_id):
    try:
        beneficiary = BeneficiaryProfile.objects.get(id=beneficiary_id, user=request.user)
    except BeneficiaryProfile.DoesNotExist:
        serializer = BeneficiaryProfileSerializer(data=request.data)
    else:
        serializer = BeneficiaryProfileSerializer(beneficiary, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def message_list(request):
    box = request.GET.get("box", "inbox")  # default to inbox
    accounts = Account.objects.filter(user=request.user)
    if box == "sent":
        # Show sent messages from AdminCompose
        messages = AdminCompose.objects.filter(user=request.user).order_by('-created_at')
    else:
        # Show inbox messages from Message
        messages = Message.objects.filter(user=request.user).order_by('-date')

    return render(request, "messages.html", {"messages": messages, "box": box , 'accounts': accounts,})
    return render(request, 'messages.html', {'messages': messages})
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk, user=request.user)
    # mark as read
    if not message.is_read:
        message.is_read = True
        message.save()
    return render(request, 'message_detail.html', {'message': message})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import AdminCompose

@login_required
def compose_page(request):
    print("COMPOSE VIEW HIT:", request.method)

    if request.method == "GET":
        return render(request, "compose.html")

    if request.method == "POST":
        to_field = request.POST.get("to", "").strip()
        title = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()

        if not to_field or not title or not body:
            # Optionally you can flash an error message instead of JSON for redirect flow
            return render(request, "compose.html", {"error": "All fields are required"})

        # Save message with 'to' as plain text
        AdminCompose.objects.create(
            user=request.user,
            to=to_field,
            subject=title,
            message=body,
            source="user"
        )

        # Redirect to the message list page after successful submission
        return render(request, "compose.html", {"success": True})

    return render(request, "compose.html")

client = finnhub.Client(api_key="d45gnf9r01qsugta9ai0d45gnf9r01qsugta9aig")  


def get_live_prices(symbols):
  
    data = {}

    for symbol in symbols:
        try:
            q = client.quote(symbol)

            if not q or q.get("c") is None:
                continue

            # Percent change
            if q.get("dp") is not None:
                percent_change = round(q["dp"], 2)
            elif q.get("pc"):
                percent_change = round(((q["c"] - q["pc"]) / q["pc"]) * 100, 2)
            else:
                percent_change = 0

            data[symbol] = {
                "price": q.get("c"),
                "change": q.get("d"),
                "percent": percent_change,
                "high": q.get("h"),
                "low": q.get("l"),
                "open": q.get("o"),
                "prev_close": q.get("pc"),
            }

        except Exception as e:
            # Log if needed; don't crash
            print(f"[PRICE ERROR] {symbol}: {e}")

    return data


def holdings_api(request):
    user = request.user
    account_id = request.GET.get("account_id")

   
    try:
        account = Account.objects.get(id=account_id, user=user)
    except Account.DoesNotExist:
        return JsonResponse({"error": "Invalid account"}, status=400)

    if account.account_type == "Brokerage Account":
        stocks = Stock.objects.filter(
            user=user
        ).filter(
            Q(account=account) | Q(account__isnull=True)
        )
    else:
        stocks = Stock.objects.filter(
            user=user,
            account=account
        )

    live_prices = batch_update_stock_prices(stocks)
    if live_prices is None:
        live_prices = {}

    holdings = []
    portfolio_total = Decimal("0")
    previous_portfolio_total = Decimal("0")

    for s in stocks:
        live = live_prices.get(s.symbol, {}) or {}

        last_price = s.last_price
        percent = live.get("percent") or s.change_percent

        if last_price:
            total_value = last_price * Decimal(s.quantity)
            portfolio_total += total_value
        else:
            total_value = None

        if s.avg_buy_price:
            previous_value = s.avg_buy_price * Decimal(s.quantity)
            previous_portfolio_total += previous_value
        else:
            previous_value = None

        holdings.append({
            "symbol": s.symbol,
            "company_name": s.company_name,
            "quantity": s.quantity,
            "avg_buy_price": str(s.avg_buy_price),
            "current_price": str(s.last_price) if s.last_price else None,
            "total_value": str(total_value) if total_value else None,
            "previous_total_value": str(previous_value) if previous_value else None,
            "change_percent": percent,
            "last_updated": s.last_price_updated.isoformat() if s.last_price_updated else None,
        })

    cash_amount = (
        CashAccounts.objects
        .filter(user=user, account_id=account_id)
        .aggregate(total=Sum("amount"))
    )['total'] or Decimal("0")
    
    net_portfolio_value = (
        cash_amount - previous_portfolio_total
        if portfolio_total > 0 else cash_amount
    ).quantize(Decimal("0.01"))

    new_brokerage_balance = (net_portfolio_value + portfolio_total).quantize(Decimal("0.01"))

    with transaction.atomic():
          account=Account.objects.filter(
              user=user,
              id=account_id
          ).first()
          if account:
              account.amount=new_brokerage_balance
              account.save(update_fields=["amount"])

    return JsonResponse({
        "holdings": holdings,
        "portfolio_total": str(portfolio_total),
        "raw_total": str(net_portfolio_value),
       
    })
    
# def can_call_any_price_api(seconds=60):
   
#     key = "global_price_api_lock"

#     if cache.get(key):
#         return False

#     cache.set(key, True, seconds)
#     return True

from django.http import JsonResponse
from .services.price_service import get_stock_price

def price_api(request, symbol):
    try:
        data = get_stock_price(symbol)

        if not data:
            return JsonResponse({
                "symbol": symbol,
                "price": 0
            })

        price = data.get("price")

        # 🔥 FINAL SAFETY
        if isinstance(price, dict):
            price = price.get("price")

        return JsonResponse({
            "symbol": symbol,
            "price": float(price) if price else 0
        })

    except Exception as e:
        print("🔥 PRICE API ERROR:", e)
        return JsonResponse({
            "symbol": symbol,
            "price": 0
        })


def get_company_name(symbol):
    cache_key = f"company_name_{symbol}"
    name = cache.get(cache_key)

    if name:
        return name

    try:
        profile = client.company_profile2(symbol=symbol)
        name = profile.get("name", symbol)

        
        cache.set(cache_key, name, 60 * 60 * 24 * 30)

        return name

    except Exception:
        return symbol

CACHE_TTL = 3600  # 5 minutes
def batch_update_stock_prices(stocks):
    print("batch_update_stock_prices called")
   

    cached_prices = {}
    symbols_to_update = []

    # Step 1: Load cache & decide what needs fetching
    for s in stocks:
        cached = cache.get(f"stock_live_{s.symbol}")

        # Save cached value if exists
        if cached:
            cached_prices[s.symbol] = cached

        # Decide if we must fetch from API
        needs_fetch = (
            not cached
            or cached.get("percent") is None
            or not s.last_price_updated
            or timezone.now() - s.last_price_updated > timedelta(seconds=30)
        )

        if needs_fetch:
            symbols_to_update.append(s.symbol)

    
    if not symbols_to_update:
        return cached_prices
    
    prices = get_live_prices(symbols_to_update) or {}

    for s in stocks:
        price_data = prices.get(s.symbol)

        if price_data and price_data.get("price") is not None:
            live = {
                "price": Decimal(str(price_data["price"])),
                "percent": price_data.get("percent"),
                "updated": timezone.now().isoformat(),
            }

            # Save price to DB (price persistence)
            s.last_price = live["price"]
            s.last_price_updated = timezone.now()
            s.save(update_fields=["last_price", "last_price_updated"])

            # Cache price + percent
            cache.set(
                f"stock_live_{s.symbol}",
                live,
                timeout=CACHE_TTL
            )

            cached_prices[s.symbol] = live
            print("CACHE CHECK:", cached_prices)


    return cached_prices

def buy_stock(request, account_id):

    account = get_object_or_404(
        Account,
        id=account_id,
        user=request.user
    )
    
    symbol_from_url = request.GET.get("symbol", "")
    

    if request.method == "POST":

        # ✅ Clean input
        symbol = request.POST.get("symbol", "").strip().upper()
        qty = int(request.POST.get("quantity", 0))

        if not symbol:
            return JsonResponse({"error": "Symbol required"}, status=400)

        if qty <= 0:
            return JsonResponse({"error": "Invalid quantity"}, status=400)

        # ✅ USE CACHE + SERVICE (THIS FIXES EVERYTHING)
        live_data = get_stock_price(symbol)

        if not live_data:
            return JsonResponse({"error": "Invalid symbol"}, status=400)

        price = Decimal(str(live_data["price"]))
        percent = live_data.get("percent", 0)

        total_cost = price * qty

        if account.amount < total_cost:
            return JsonResponse({"error": "Insufficient balance"}, status=400)

        company_name = get_company_name(symbol)

        with transaction.atomic():

            # ✅ Deduct balance
            account.amount -= total_cost
            account.save()

            Transaction.objects.create(
                user=request.user,
                account=account,
                transaction_type="BUY",
                stock_symbol=symbol,
                quantity=qty,
                price_per_share=price,
                amount=total_cost
            )

            stock = Stock.objects.filter(
                user=request.user,
                symbol=symbol
            ).filter(
                Q(account=account) | Q(account__isnull=True)
            ).first()

            if stock:
                if stock.account is None:
                    stock.account = account
            else:
                stock = Stock.objects.create(
                    user=request.user,
                    account=account,
                    symbol=symbol,
                    company_name=company_name,
                    quantity=0,
                    avg_buy_price=Decimal("0"),
                )

            total_qty = stock.quantity + qty
            total_cost_all = (stock.avg_buy_price * stock.quantity) + total_cost

            stock.avg_buy_price = total_cost_all / total_qty
            stock.quantity = total_qty
            stock.last_price = price
            stock.change_percent = percent
            stock.last_price_updated = timezone.now()
            stock.save()

        # ✅ Update cache (optional but good)
        cache.set(
            f"stock_live_{symbol}",
            {
                "price": price,
                "percent": percent,
                "updated": timezone.now().isoformat(),
            },
            timeout=60
        )

       

    return render(request, "buyStock.html", {
        "account_id": account.id,
         "symbol": symbol_from_url
        
    })


def portfolio_view(request, account_id):
    return render(request, "portfolio.html", {
        "account_id": account_id
    })

from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Account, Stock, Transaction
from .services.price_service import get_stock_price


def sell_stock(request, account_id, symbol):

    # ✅ Step 1: Get Account
    account = get_object_or_404(
        Account,
        id=account_id,
        user=request.user
    )

    # ✅ Step 2: Get Stock (handle old NULL account stocks also)
    stock = Stock.objects.filter(
        user=request.user,
        symbol=symbol
    ).filter(
        Q(account=account) | Q(account__isnull=True)
    ).first()

    if not stock:
        messages.error(request, "Stock not found.")
        return redirect("portfolio", account_id=account.id)

    # ✅ Step 3: Handle POST (Sell Logic)
    if request.method == "POST":

        # 🔹 Validate quantity
        try:
            qty = int(request.POST.get("quantity"))
        except (TypeError, ValueError):
            messages.error(request, "Invalid quantity.")
            return redirect("sell_stock", account_id=account.id, symbol=symbol)

        if qty <= 0:
            messages.error(request, "Quantity must be greater than 0.")
            return redirect("sell_stock", account_id=account.id, symbol=symbol)

        if qty > stock.quantity:
            messages.error(request, "You cannot sell more than you own.")
            return redirect("sell_stock", account_id=account.id, symbol=symbol)

        # 🔹 Get mode
        mode = request.POST.get("mode")
        custom_price = request.POST.get("custom_price")

        # ✅ Step 4: Determine Sell Price
        if mode == "market":
            live_data = get_stock_price(symbol)

            if not live_data or not live_data.get("price"):
                messages.error(request, "Live price not available.")
                return redirect("sell_stock", account_id=account.id, symbol=symbol)

            sell_price = Decimal(str(live_data["price"]))

        elif mode == "buyprice":
            sell_price = stock.avg_buy_price

        elif mode == "custom":
            if not custom_price:
                messages.error(request, "Enter custom price.")
                return redirect("sell_stock", account_id=account.id, symbol=symbol)

            try:
                sell_price = Decimal(custom_price)
            except InvalidOperation:
                messages.error(request, "Invalid custom price.")
                return redirect("sell_stock", account_id=account.id, symbol=symbol)

        else:
            messages.error(request, "Invalid sell mode selected.")
            return redirect("sell_stock", account_id=account.id, symbol=symbol)

        # 🔥 SAFETY CHECK (important)
        if not isinstance(sell_price, Decimal):
            sell_price = Decimal(str(sell_price))

        # ✅ Step 5: Calculate total
        total_sell_amount = sell_price * qty

        # ✅ Step 6: Add money back to SAME account
        account.amount += total_sell_amount
        account.save(update_fields=["amount"])

        # ✅ Step 7: Reduce stock quantity
        stock.quantity -= qty

        if stock.account is None:
            stock.account = account

        if stock.quantity == 0:
            stock.delete()
        else:
            stock.save()

        # ✅ Step 8: Create Transaction
        Transaction.objects.create(
            user=request.user,
            account=account,
            transaction_type="SELL",
            stock_symbol=symbol,
            quantity=qty,
            price_per_share=sell_price,
            amount=total_sell_amount,
            notes="Sold stock"
        )

        # ✅ Success message
        messages.success(
            request,
            f"Sold {qty} shares of {symbol} at ${sell_price}."
        )

        return redirect("portfolio", account_id=account.id)

    # ✅ Step 9: Render Page
    return render(request, "sell_stock.html", {
        "stock": stock,
        "account_id": account.id
    })

def gold_view(request):
    user = request.user
    holdings = Gold.objects.filter(user=user).order_by('-date')
    gold_amount = sum(h.amount for h in holdings)
    formatted_gold_amount = intcomma(gold_amount)  
    return render(request, "gold.html", {
        "holdings": holdings,
        "gold_amount": gold_amount,  
        "formatted_gold_amount": formatted_gold_amount,  
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

    if not email:
        return redirect("signin")

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect("signin")

    if request.method == "POST":
        password = request.POST.get("password")

        user = authenticate(request, username=user_obj.username, password=password)

        if user:
            login(request, user) 
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




def activity_list(request):
    # Get entries
    cash_entries = CashAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    saving_entries = SavingAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    # Get account numbers
    checking_account = Account.objects.filter(
        user=request.user,
        account_type="Checkings Account"
    ).first()

    cash_equivalent_account = Account.objects.filter(
        user=request.user,
        account_type="Cash & Cash Equivalents"
    ).first()

    checking_acc_number = checking_account.account_number if checking_account else ""
    cash_equivalent_acc_number = cash_equivalent_account.account_number if cash_equivalent_account else ""

    entries = []

    for c in cash_entries:
        entries.append({
            "date": c.date,
            "description": c.description,
            "credit": c.credit,
            "debit": c.debit,
            "balance": c.account_balance,
            "entry_type": "Checkings Account",
            "account_number": checking_acc_number,
        })

    for s in saving_entries:
        entries.append({
            "date": s.date,
            "description": s.description,
            "credit": s.credit,
            "debit": s.debit,
            "balance": s.account_balance,
            "entry_type": "Cash & Cash Equivalents",
            "account_number": cash_equivalent_acc_number,
        })
    entries = sorted(entries, key=lambda x: x["date"], reverse=True)

    return render(request, "activity.html", {
        "entries": entries
    })


def performancePage(request):
     return render(request, "Performance.html")

@login_required
def transfer_view(request):
    user = request.user
    accounts = Account.objects.filter(user=user)
    bank_accounts = BankAccount.objects.filter(user=user, is_active=True)

    gold_holdings = Gold.objects.filter(user=user)
    gold_total = sum(h.amount for h in gold_holdings)

    cash_entries = CashAccount.objects.filter(user=user).order_by('-date')
    cash_total = cash_entries.first().account_balance if cash_entries.exists() else 0

    transfer_requests = TransferRequest.objects.filter(
        user=user
    ).order_by('-created_at')

    saving_entries = SavingAccount.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    saving_total = saving_entries.first().account_balance if saving_entries.exists() else 0
    formatted_saving_total = intcomma(saving_total)

    submitted_data = None

    if request.method == "POST":
        action = request.POST.get("action")  # internal / withdraw
        from_id = request.POST.get("from_account")
        to_id = request.POST.get("to_account")
        bank_id = request.POST.get("bank_account")
        amount_raw = request.POST.get("amount")

        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise ValueError
        except:
            messages.error(request, "Invalid amount")
            return redirect("transfer")

        try:
            from_account = Account.objects.get(id=from_id, user=user)
        except Account.DoesNotExist:
            messages.error(request, "Invalid source account")
            return redirect("transfer")

        if from_account.account_type == "Gold Holdings":
            available_balance = gold_total

        elif from_account.account_type == "Cash & Cash Equivalents":
            available_balance = saving_total

        else:
            available_balance = from_account.amount

        if available_balance < amount:
            messages.error(request, "Insufficient balance")
            return redirect("transfer")

        submitted_data = {
            "from_id": from_id,
            "to_id": to_id,
            "bank_id": bank_id,
            "amount_raw": amount_raw,
        }

        if action == "internal":
            try:
                to_account = Account.objects.get(id=to_id, user=user)
            except Account.DoesNotExist:
                messages.error(request, "Invalid destination account")
                return redirect("transfer")

            TransferRequest.objects.create(
                user=user,
                from_account=from_account,
                to_account=to_account,
                to_bank=None,
                amount=amount,
                status="pending"
            )

        elif action == "withdraw":
            try:
                bank_account = BankAccount.objects.get(
                    id=bank_id,
                    user=user,
                    is_active=True
                )
            except BankAccount.DoesNotExist:
                messages.error(request, "Invalid bank account")
                return redirect("transfer")

            TransferRequest.objects.create(
                user=user,
                from_account=from_account,
                to_account=None,
                to_bank=bank_account,
                amount=amount,
                status="pending"
            )

        if available_balance < amount:
            messages.error(request, "Insufficient balance")
            return redirect("transfer")

        messages.success(request, "Transfer request sent successfully")
        return redirect("transfer")

    return render(
        request,
        "transfer.html",
        {
            "accounts": accounts,
            "bank_accounts": bank_accounts,
            "transfer_requests": transfer_requests,
            "submitted_data": submitted_data,
            "gold_total": gold_total,
            "cash_total": cash_total,
            "saving_entries": saving_entries,
            "saving_total": saving_total,
            "formatted_saving_total": formatted_saving_total,
        }
    )
    