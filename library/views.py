from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from library_project.settings import EMAIL_HOST_USER
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Book, Customer
from .serializers import BookSerializer, CustomerSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        customer = serializer.save()

        # Send Email
        send_mail(
            'Book Purchased',
            f'Hello {customer.name}, you purchased {customer.book.name}',
            'zeeshu108@gmail.com',
            [customer.email],
            fail_silently=False,
        )

        # WebSocket Notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "send_notification",
                "message": {
                    "message": f"New book purchased by {customer.name}"
                }
            }
        )
