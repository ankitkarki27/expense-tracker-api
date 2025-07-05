from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ExpenseIncome(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit','Debit'),
    ]
    
    TAX_TYPE_CHOICES = [
        ('flat','Flat'),
        ('percentage','Percentage'), 
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    tax_type = models.CharField(max_length=10, choices=TAX_TYPE_CHOICES, default='flat')
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def total_amount(self):
        if self.tax_type == 'flat':
            return self.amount + self.tax
        return self.amount + (self.amount * self.tax / 100)
    
    def __str__(self):
        return f"{self.title} - {self.transaction_type} - {self.user.username}"
