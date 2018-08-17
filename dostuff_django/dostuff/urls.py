from . import views
from django.urls import path


urlpatterns = [
  path('api/event/', views.EventList.as_view(), name='event-list'),
  path('api/event/<int:pk>', views.EventDetail.as_view(), name='event-detail'),
]