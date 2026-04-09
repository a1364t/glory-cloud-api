# pos_api/admin.py
from django.contrib import admin
from .models import POS, POSCommand


@admin.register(POS)
class POSAdmin(admin.ModelAdmin):
    """Admin configuration for registered POS terminals."""
    list_display = ("pos_id", "description", "last_seen")
    search_fields = ("pos_id",)


@admin.register(POSCommand)
class POSCommandAdmin(admin.ModelAdmin):
    """Admin configuration for POS command queue entries."""
    list_display = (
        "id",
        "command",
        "amount",
        "pos",
        "status",
        "attempts",
        "created_at",
        "executed_at",
    )
    list_filter = ("command", "status", "pos")

