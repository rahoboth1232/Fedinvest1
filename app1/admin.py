
# Register your models here.
from django.contrib import admin
from .models import UserProfile, Transaction,Stock




from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('amount',)
    list_display = ('user', 'transaction_type', 'stock_symbol','quantity','price_per_share', 'amount', 'date')
    search_fields = ('user__username', 'stock_symbol', 'transaction_type')
    list_filter = ('transaction_type', 'date')


# app/admin.py
from django.contrib import admin
from .models import Account 

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'account_type', 'account_number', 'amount')
    list_filter = ('user', 'account_type')
    search_fields = ('name', 'account_number', 'user__username')


from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from .models import UserProfile

class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        
        import re
        pattern = r'^\+?[\d\s\-\(\)]{10,15}$'
        if not re.match(pattern, mobile):
            raise ValidationError("Enter a valid phone number (e.g. +1 (212) 555-1234 or 9876543210).")
        return mobile

    def clean_ssn(self):
        ssn = self.cleaned_data.get('ssn')
        # if not ssn.isdigit():
        #     raise ValidationError("SSN must contain digits only.")
        # if len(ssn) != 9:
        #     raise ValidationError("SSN must be exactly 9 digits.")
        return ssn


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm
    list_display = ('user', 'full_name', 'mobile', 'email', 'ssn', 'updated_at', 'address')
    search_fields = ('user__username', 'mobile', 'email','image','date_of_birth','address')

    def show_masked_ssn(self, obj):
        """Shows masked SSN in admin list but full in edit form"""
        return obj.masked_ssn()
    show_masked_ssn.short_description = "Masked SSN"
    def show_masked_mobile(self, obj):
        """Show only last 4 digits of phone number: XXX-XXX-1234"""
        return obj.masked_mobile()
    show_masked_mobile.short_description = "Masked Mobile"

admin.site.register(UserProfile, UserProfileAdmin)

from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'is_read')
    list_filter = ('is_read', 'date')
    search_fields = ('title', 'body', 'user__username')
    ordering = ('-date',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("company_name", "symbol", "quantity", "user")
    search_fields = ("company_name", "symbol")
    list_filter = ("user",)

from django.contrib import admin
from .models import Gold

class GoldAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'description', 'weight', 'price', 'amount')
    list_filter = ('user', 'date')
    search_fields = ('description', 'user__username')

admin.site.register(Gold, GoldAdmin)

from django.contrib import admin
from django import forms
from .models import CashAccount

class CashAccountAdminForm(forms.ModelForm):
    class Meta:
        model = CashAccount
        fields = '__all__'
        readonly_fields = ("account_balance",)
        readonly_fields = ("account_",)
    def clean(self):
        cleaned_data = super().clean()
        credit = cleaned_data.get("credit", 0)
        debit = cleaned_data.get("debit", 0)
        if (credit > 0 and debit > 0) or (credit == 0 and debit == 0):
            raise forms.ValidationError("You must fill either Credit or Debit, but not both.")
        return cleaned_data

@admin.register(CashAccount)
class CashAccountAdmin(admin.ModelAdmin):
    form = CashAccountAdminForm
    list_display = ('user', 'date', 'account_number', 'description', 'credit', 'debit', 'account_balance')
    list_filter = ('user', 'date')
    search_fields = ('user__username', 'description', 'account_number')

from django.contrib import admin
from .models import SavingAccount

@admin.register(SavingAccount)
class SavingAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'account_number', 'credit', 'debit', 'account_balance')
    list_filter = ('user', 'date')
    search_fields = ('user__username', 'account_number', 'description')


from django.contrib import admin
from .models import Crypto

class CryptoAdmin(admin.ModelAdmin):
    list_display = ("date", "description", "price", "formatted_quantity", "amount")
    readonly_fields = ("amount",)

    # Allow entering quantity with 3 decimals in the admin input box
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "quantity":
            field.widget.attrs["step"] = "0.001"   # allow 3 decimal places
        return field

    # Show formatted quantity in list view
    def formatted_quantity(self, obj):
        return f"{obj.quantity:.3f}"
    formatted_quantity.short_description = "Quantity"

admin.site.register(Crypto, CryptoAdmin)


from django.contrib import admin
from .models import LegalDocument

@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'user', 'date', 'type')
    list_filter = ('type', 'date', 'user')
    search_fields = ('title', 'slug', 'user__username')
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ('user',)