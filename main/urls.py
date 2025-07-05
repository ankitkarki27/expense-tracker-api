from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ExpenseIncomeViewSet, UserRegistrationViewSet, MyTokenObtainPairView

router = DefaultRouter()
router.register(r"expenses", ExpenseIncomeViewSet, basename="expense")
  
urlpatterns = [
   # Authentication
    # path("auth/register/", UserRegistrationViewSet.as_view({"post": "register"}), name="register"),  
    path("auth/register/", UserRegistrationViewSet.as_view({"post": "register"}), name="register"),                              
    path("auth/login/",   TokenObtainPairView.as_view(), name="login"),   
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("", include(router.urls)),
]
# urlpatterns += router.urls