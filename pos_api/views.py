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
        cmd.result_code = request.data.get("result_code", "")
        cmd.result_text = request.data.get("result_text", "")
        cmd.executed_at = now()

        if status_text == "DONE":
            # The POS successfully executed the command.
            cmd.status = "DONE"
        else:
            # A failed command may be retried unless it is a CHANGE command with a pending CANCEL.
            cancel_pending = POSCommand.objects.filter(
                pos=pos,
                command="CANCEL",
                status__in=["PENDING", "LOCKED"]
            ).exists()
            if cmd.attempts >= MAX_ATTEMPTS or (cmd.command == "CHANGE" and cancel_pending):
                # Stop retries and mark the command as dead.
                cmd.status = "DEAD"
            else:
                # Allow the command to re-enter the queue for another attempt.
                cmd.status = "PENDING"

        cmd.save()
        return Response({"ok": True})