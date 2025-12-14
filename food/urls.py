from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView
from .import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("food",views.AdminFoodViewSet,basename='food'),
router.register("promokod",views.PromokodViewSet,basename="promokod")
urlpatterns = [
    path("signup/",views.SignUp.as_view(),name="signup"),
    path("login/",TokenObtainPairView.as_view(),name="login"),
    path("refresh/token/",TokenRefreshView.as_view(),name="refresh"),
    path("buyurtma/",views.UserBuyurtmaViewSet.as_view(),name="buyurtma"),
    path("foods/",views.FoodListView.as_view(),name="foods"),
    path("buyurtma/tarix/",views.BuyurtmaTarix.as_view(),name="tarix"),
    path('status/<int:pk>/', views.BuyurtmaStatusUpdate.as_view(), name="status"),
    path('food/status/<int:pk>/', views.AdminFoodStatusUpdate.as_view(), name="status-admin"),
    path("schema/",SpectacularAPIView.as_view(),name="schema"),
    path("docs/",SpectacularSwaggerView.as_view(),name='swagger-ui'),

    path("",include(router.urls)),
]
