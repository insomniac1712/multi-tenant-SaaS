from django.shortcuts import render
from .serializers import RegisterSerializer
from rest_framework import generics,permissions
# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]