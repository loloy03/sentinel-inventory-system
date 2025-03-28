from django.db import models
from django.conf import settings # To link to the User model (optional but recommended)

# Existing FromsStock model...
class FromsStock(models.Model):
    warehouse_id = models.CharField(max_length=100, primary_key=True) # Keep as PK for current state
    production_code = models.CharField(max_length=100)
    date = models.DateField() # Date the stock item *was originally created or last updated significantly*
    product = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    item_code = models.CharField(max_length=100)
    quantity = models.IntegerField() # Represents the CURRENT quantity at this warehouse_id
    pallet_position = models.CharField(max_length=50)
    status = models.CharField(max_length=50) # Current or last known status

    def __str__(self):
        return f"{self.warehouse_id} - {self.item_code} - Qty: {self.quantity}"


# --- NEW MODEL for Transaction History ---
class StockHistory(models.Model):
    TRANSACTION_TYPES = [
        ('RECEIVE', 'Receive'),
        ('RELEASE', 'Release'),
        # You could add other types like 'ADJUSTMENT', 'INITIAL_STOCK' later
    ]

    # Auto-generated fields for logging
    id = models.AutoField(primary_key=True) # Simple auto-incrementing ID for history
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the transaction was recorded in the system")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)

    # Optional: Link to the user who performed the action
    # Make sure your views using this require login (@login_required)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Keep history even if user is deleted
        null=True,
        blank=True,
        related_name='stock_history_actions',
        help_text="User who performed the transaction"
    )

    # Details *at the time* of the transaction (copied from the form/stock item)
    # We don't use a ForeignKey to FromsStock because FromsStock represents the *current* state
    # and might be deleted or changed later. History should be immutable.
    warehouse_id = models.CharField(max_length=100, db_index=True, help_text="Identifier of the stock batch/location involved")
    production_code = models.CharField(max_length=100)
    date_of_transaction = models.DateField(help_text="Date entered on the form for this transaction")
    product = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    item_code = models.CharField(max_length=100)
    pallet_position = models.CharField(max_length=50)
    status = models.CharField(max_length=50, help_text="Status associated with this specific transaction (e.g., NEW, DELIVERY)")

    quantity_change = models.IntegerField(help_text="The amount received (+) or released (-)")
    # Optional: You could also store quantity_before and quantity_after for easier auditing

    def __str__(self):
        user_str = f" by {self.user.username}" if self.user else ""
        return (f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.transaction_type} "
                f"{abs(self.quantity_change)} x {self.item_code} ({self.warehouse_id}){user_str}")

    class Meta:
        ordering = ['-timestamp'] # Show most recent history first
        verbose_name_plural = "Stock History"