from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    return render(request, 'messaging/inbox.html', {'conversations': conversations})

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = conversation.messages.select_related('sender').all()

    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=body
            )
            return redirect('messaging:conversation_detail', conversation_id=conversation.id)

    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages
    })