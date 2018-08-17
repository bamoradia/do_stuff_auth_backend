from django.shortcuts import render
from django.http import JsonResponse
from .models import User, Event, Category, UserEvent, UserCategory, EventCategory

# Create your views here.

class