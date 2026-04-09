from django.db import models


class POS(models.Model):
    """Model for a registered POS terminal."""
    pos_id = models.CharField(max_length=50, unique=True)
    api_key = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.pos_id


class POSCommand(models.Model):
    """Model representing a queued command for a POS terminal."""

    COMMAND_CHOICES = [
        ("OPEN", "Open Session"),
        ("OCCUPY", "Occupy"),
        ("RELEASE", "Release"),
        ("CLOSE", "Close"),
        ("STATUS", "Status"),
        ("CHANGE", "Change (Deposit / Dispense)"),
        ("RESET", "Reset"),
        ("CANCEL", "Cancel"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("LOCKED", "Locked"),
        ("DONE", "Done"),
        ("FAILED", "Failed"),
        ("DEAD", "Dead Letter"),
    ]

    pos = models.ForeignKey(POS, on_delete=models.CASCADE)
    # The command that the POS should execute.
    command = models.CharField(max_length=20, choices=COMMAND_CHOICES)

    # ✅ IMPORTANT: signed amount, used for CHANGE
    # Positive = deposit, Negative = dispense
    amount = models.IntegerField(
        null=True,
        blank=True,
        help_text="Amount in cents. Positive = deposit, negative = dispense."
    )

    # ✅ Optional future-use payload (NOT used for money anymore)
    payload = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    # lock_owner records which POS terminal currently holds the command.
    lock_owner = models.CharField(max_length=50, blank=True)
    # Number of fetch attempts the POS has made for this command.
    attempts = models.PositiveIntegerField(default=0)

    result_code = models.CharField(max_length=20, blank=True)
    result_text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.command} → {self.pos.pos_id} [{self.status}]"