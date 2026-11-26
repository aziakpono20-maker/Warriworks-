
from django.urls import path

from .views import (
    RegisterView,
    ArtisanRegisterView,
    LoginView,
    LogoutView,
    MeView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/customer/', RegisterView.as_view(), name='register-customer'),
    path('register/artisan/', ArtisanRegisterView.as_view(), name='register-artisan'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
]
