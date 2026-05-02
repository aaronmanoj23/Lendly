from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from listings.models import Listing

from .models import Conversation, Message

User = get_user_model()


@login_required
def inbox(request):
    convos = (
        Conversation.objects.filter(participants=request.user)
        .prefetch_related("participants", "messages")
        .order_by("-updated_at")
    )
    return render(request, "messaging/inbox.html", {"convos": convos})


@login_required
def thread(request, pk):
    convo = get_object_or_404(Conversation, pk=pk, participants=request.user)
    msgs = convo.messages.select_related("sender")
    return render(
        request,
        "messaging/thread.html",
        {"convo": convo, "msgs": msgs, "other": convo.other_participant(request.user)},
    )


@login_required
def start_conversation(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.owner == request.user:
        return redirect("listing_detail", slug=listing.slug)
    convo = (
        Conversation.objects.filter(
            participants=request.user, listing=listing
        )
        .filter(participants=listing.owner)
        .first()
    )
    if not convo:
        convo = Conversation.objects.create(listing=listing)
        convo.participants.add(request.user, listing.owner)
    return redirect("thread", pk=convo.pk)


@login_required
@require_POST
def send_message(request, pk):
    convo = get_object_or_404(Conversation, pk=pk, participants=request.user)
    body = (request.POST.get("body") or "").strip()
    if not body:
        return JsonResponse({"error": "empty"}, status=400)
    msg = Message.objects.create(conversation=convo, sender=request.user, body=body)
    convo.save()  # bump updated_at
    return JsonResponse(
        {
            "id": msg.pk,
            "body": msg.body,
            "sender_id": msg.sender_id,
            "created_at": msg.created_at.isoformat(),
        }
    )


@login_required
def poll_messages(request, pk):
    convo = get_object_or_404(Conversation, pk=pk, participants=request.user)
    after = request.GET.get("after")
    qs = convo.messages.all()
    if after:
        qs = qs.filter(pk__gt=after)
    data = [
        {
            "id": m.pk,
            "body": m.body,
            "sender_id": m.sender_id,
            "created_at": m.created_at.isoformat(),
        }
        for m in qs
    ]
    return JsonResponse({"messages": data})
