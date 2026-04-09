from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# pos_api/views.py
# REST API views for fetching POS commands and submitting execution results.
from .models import POSCommand
from .auth import POSAuthentication


# Maximum number of times a POS may attempt a command before it becomes dead.
MAX_ATTEMPTS = 3


class FetchNextCommand(APIView):
    authentication_classes = [POSAuthentication]

    def get(self, request):
        # The authenticated POS instance is returned by POSAuthentication.
        pos = request.auth

        cmd = POSCommand.objects.filter(
            pos=pos,
            status="PENDING",
            attempts__lt=MAX_ATTEMPTS
        ).order_by("created_at").first()

        if not cmd:
            return Response({"command": None})

        # Reserve the command for this POS and increment the attempt counter.
        cmd.status = "LOCKED"
        cmd.lock_owner = pos.pos_id
        cmd.attempts += 1
        cmd.save()

        # Update the POS last-seen timestamp for tracking.
        pos.last_seen = now()
        pos.save(update_fields=["last_seen"])

        return Response({
            "id": cmd.id,
            "command": cmd.command,
            "amount": cmd.amount,
        })


class SubmitResult(APIView):
    authentication_classes = [POSAuthentication]

    def post(self, request, command_id):
        pos = request.auth

        try:
            cmd = POSCommand.objects.get(id=command_id, pos=pos)
        except POSCommand.DoesNotExist:
            return Response({"error": "Invalid command"}, status=404)

        status_text = request.data.get("status")
        result_code = request.data.get("result_code", "")

        cmd.result_code = result_code
        cmd.result_text = request.data.get("result_text", "")
        cmd.executed_at = now()

        # ============================================================
        # ✅ SUCCESSFUL EXECUTION
        # ============================================================
        if status_text == "DONE":
            cmd.status = "DONE"

        else:
            # ============================================================
            # ✅ IMPORTANT FIX:
            # If CHANGE was cancelled by the machine (result_code == "1"),
            # this is a terminal state and must NEVER be retried.
            # ============================================================
            if cmd.command == "CHANGE" and result_code == "1":
                cmd.status = "DEAD"
                cmd.result_text = "Transaction cancelled by user"

            # ============================================================
            # ✅ Normal retry logic for all other failures
            # ============================================================
            elif cmd.attempts >= MAX_ATTEMPTS:
                cmd.status = "DEAD"

            else:
                cmd.status = "PENDING"

        cmd.save()
        return Response({"ok": True})