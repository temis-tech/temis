from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingFormViewSet, BookingSubmissionViewSet

router = DefaultRouter()
router.register(r'forms', BookingFormViewSet, basename='bookingform')
router.register(r'submissions', BookingSubmissionViewSet, basename='bookingsubmission')

urlpatterns = [
    path('', include(router.urls)),
]

