
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
mobile_validator = RegexValidator(
    regex=r'^\(\d{3}\)-\d{3}-\d{4}$',
    message="Phone number must be in the format (123)-456-7890"
)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=15, validators=[mobile_validator])
    email = models.EmailField(
        max_length=100,
        validators=[EmailValidator(message="Enter a valid email address")],
        unique=True
    )
    ssn = models.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{9}$', message="SSN must be exactly 9 digits")],
        verbose_name="Social Security Number",blank=True, null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    # ✅ Add profile image upload field
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    address = models.TextField(
        blank=True,
        help_text="Full address (optional)"
    )

    # ✅ Control visibility on frontend
    
    def masked_ssn(self):
        if self.ssn and len(self.ssn) == 9:
            return "XXX-XX-" + self.ssn[-4:]

    def masked_mobile(self):
        if self.mobile and len(self.mobile) >= 4:
            return "(XXX)-XXX-" + self.mobile[-4:]

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.full_name and self.user:
            self.full_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.user.username


from django.contrib.humanize.templatetags.humanize import intcomma

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    class Meta:
        verbose_name = "Holdings"
        verbose_name_plural = "Holdings"

    @property
    def formatted_amount(self):
        return f"{intcomma(self.amount)}"

    def __str__(self):
        return f"{self.name} - {self.account_type} - {self.formatted_amount}"
       
class TransactionManager(models.Manager):
    def create_transaction(self, user, transaction_type, stock_symbol=None,
                           quantity=0, price_per_share=0, amount=0, notes=''):
        # Ensure numeric values are valid
        quantity = quantity or 0
        price_per_share = price_per_share or 0
        amount = amount or 0
        if amount is None:
            amount = quantity * price_per_share
        return self.create(
            user=user,
            transaction_type=transaction_type,
            stock_symbol=stock_symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            amount=amount,
            notes=notes
        )
from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('DIVIDEND', 'Dividend'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    stock_symbol = models.CharField(max_length=10, blank=True, null=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_per_share = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)  # creation timestamp
    notes = models.TextField(blank=True, null=True)

    objects = TransactionManager()  # your custom manager

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"

    def total_value(self):
        return (self.quantity or 0) * (self.price_per_share or 0)

from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    
class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=0)
    account = models.ForeignKey('Account', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.company_name} ({self.symbol}) - {self.quantity}"
    

from django.db import models
from django.contrib.auth.models import User

class Gold(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gold_holdings")
    date = models.DateField()
    description = models.CharField(max_length=255)
    weight = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # amount = price * weight
        self.amount = self.price * self.weight
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.description}"


from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CashAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cash_accounts")
    date = models.DateField()
    account_number = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.CharField(max_length=255)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    class Meta:
        verbose_name = "Checking Accounts"
        verbose_name_plural = "Checking Accounts"

    def clean(self):
        # Ensure that only one of credit or debit is filled (non-zero)
        if (self.credit > 0 and self.debit > 0) or (self.credit == 0 and self.debit == 0):
            raise ValidationError("You must fill either Credit or Debit, but not both.")

    def save(self, *args, **kwargs):
     self.clean()  # Validate before saving
    
    # Get the last transaction for the user
     last_entry = CashAccount.objects.filter(user=self.user).order_by('-date', '-id').first()
     previous_balance = last_entry.account_balance if last_entry else 0
      
    # Calculate new balance
     self.account_balance = previous_balance + (self.credit or 0) - (self.debit or 0)
    
     super().save(*args, **kwargs)

def __str__(self):
    return f"{self.user.username} - {self.description}"

class SavingAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saving_accounts")
    date = models.DateField()
    account_number = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.CharField(max_length=255)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    class Meta:
        verbose_name = "Cash Equivalent"
        verbose_name_plural = "Cash Equivalents"

    def clean(self):
        if (self.credit > 0 and self.debit > 0) or (self.credit == 0 and self.debit == 0):
            raise ValidationError("You must fill either Credit or Debit, but not both.")

    def save(self, *args, **kwargs):
        self.clean()

        last_entry = SavingAccount.objects.filter(
            user=self.user
        ).order_by('-date', '-id').first()

        previous_balance = last_entry.account_balance if last_entry else 0

        self.account_balance = previous_balance + (self.credit or 0) - (self.debit or 0)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - Saving Account Transaction"


from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.contrib.auth.models import User

class Crypto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    amount = models.DecimalField(max_digits=24, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.amount = (self.price * self.quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    @property
    def formatted_amount(self):
        return f"${self.amount:,.2f}"  # US Dollar Format

    def __str__(self):
        return f"{self.description} - {self.formatted_amount}"
    from django.db import models

class LegalDocument(models.Model):
    DOCUMENT_TYPES = (
        ("PDF", "PDF"),
        ("PNG", "PNG"),
        ("JPEG", "JPEG"),
        ("DOCX", "DOCX"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    date = models.DateField()
    file = models.FileField(upload_to="legal_documents/")
    type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, default="PDF")

    class Meta:
        ordering = ['-date', 'title']

    def __str__(self):
        return self.title

