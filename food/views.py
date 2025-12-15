from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser,Food,Buyurtma,BuyurtmaItems,Promokod
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .serializers import FoodSerializers,PromokodSerializers,BuyurtmaSerializer,BuyurtmaStatusSerializer,FoodStatusSerializer,BuyurtmaCreateSerializer,SignUpSerializer
from .permissions import IsAdmin,IsUser
from decimal import Decimal
from rest_framework.generics import ListAPIView
from django.utils import timezone
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="Royxatdan otish Apisi",
    description="Bu yerda telefon raqam unique bolishi kerak"
)
class SignUp(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = SignUpSerializer(data=data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user_data = serializer.validated_data
        username = user_data.get("username")
        password = user_data.get("password")
        phone = user_data.get("phone")

        if CustomUser.objects.filter(username=username).exists():
            return Response(
                {"detail": "Bu username bor"},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_user = CustomUser.objects.create_user(
            username=username,
            password=password,
            phone=phone
        )

        response_data = {
            "detail": "Foydalanuvchi muvaffaqiyatli yaratildi",
            "username": new_user.username,
            "phone": new_user.phone,
            "role": new_user.role
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

@extend_schema(
    summary="Barcha mahsulotlarni korish uchu Api",
    description="Bu yerda royxatdan otish shart emas"
)
class FoodListView(ListAPIView):
    queryset = Food.objects.filter(mavjud="mavjud")
    serializer_class = FoodSerializers
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Food.objects.filter(mavjud="mavjud")
        turi = self.request.query_params.get("turi")
        search = self.request.query_params.get("search")  

        if turi:
            queryset = queryset.filter(turi=turi)
            
        if search:
            queryset = queryset.filter(nomi__icontains=search)
        return queryset 
    
@extend_schema(
    summary="Admin uchun CRUD Api",
    description="Bu APIni Admin rolli foydalanuvchi kirib ishlata oladi"
)
class AdminFoodViewSet(ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializers
    permission_classes = [IsAdmin]

@extend_schema(
    summary="Admin uchun promokod qoshish",
    description="Bu APIni Admin rolli foydalanuvchi kirib ishlata oladi"
)

class PromokodViewSet(ModelViewSet):
    queryset = Promokod.objects.all()
    serializer_class = PromokodSerializers
    permission_classes = [IsAdmin]

@extend_schema(
    summary="User uchun buyurtma qilish bo'limi",
    description="Bu APIni user rolli foydalanuvchi ishlata oladi"
)
class UserBuyurtmaViewSet(APIView):
    permission_classes = [IsAuthenticated, IsUser]
    serializer_class = BuyurtmaCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        manzil = serializer.validated_data["manzil"]
        items_data = serializer.validated_data["buyurtma"]
        promokod_code = serializer.validated_data.get("promokod")

        buyurtma = Buyurtma.objects.create(
            user=request.user,
            manzil=manzil,
            total_price=0
        )

        total_price = Decimal("0")

        for item in items_data:
            try:
                food = Food.objects.get(id=item["food_id"], mavjud="mavjud")
            except Food.DoesNotExist:
                buyurtma.delete()
                return Response(
                    {"error": "Mahsulot topilmadi yoki tugagan"},
                    status=status.HTTP_404_NOT_FOUND
                )

            count = item["count"]
            item_price = food.narxi * count
            total_price += item_price

            BuyurtmaItems.objects.create(
                buyurtma=buyurtma,
                food=food,
                count=count,
                total_price=item_price
            )

        if promokod_code:
            if total_price < 100000:
                buyurtma.delete()
                return Response(
                    {"error": "Promokod uchun minimal summa 100 000"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                promokod = Promokod.objects.get(
                    nomi__iexact=promokod_code,
                    start_date__lte=timezone.now(),
                    end_date__gte=timezone.now(),
                    is_active=True
                )
                total_price = max(total_price - promokod.amount, 0)
                buyurtma.promokod = promokod
            except Promokod.DoesNotExist:
                buyurtma.delete()
                return Response(
                    {"error": "Promokod notogri yoki muddati tugagan"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        buyurtma.total_price = total_price
        buyurtma.save()

        return Response(
            BuyurtmaSerializer(buyurtma).data,
            status=status.HTTP_201_CREATED
        )



@extend_schema(
    summary="User uchun buyurtma tarixini korish  bo'limi",
    description="Bu APIni user rolli foydalanuvchi ishlata oladi"
)
class BuyurtmaTarix(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        buyurtmalar = Buyurtma.objects.filter(user=request.user).order_by('-created_at')
        serializer = BuyurtmaSerializer(buyurtmalar, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

@extend_schema(
    summary="Admin uchun buyurtma statusini o'zgartrish  bo'limi",
    description="Bu APIni admin rolli foydalanuvchi ishlata oladi ,bunda statusni ozgartrish uchun PATCH sorov"
)
class BuyurtmaStatusUpdate(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            buyurtma = Buyurtma.objects.get(id=pk)
        except Buyurtma.DoesNotExist:
            return Response({"error":"buyurtma topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BuyurtmaStatusSerializer(buyurtma, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"buyurtma statusi yangilandi", "status": serializer.data['status']})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@extend_schema(
    summary="Admin uchun Ovqatlar mavjud statusni o'zgartrish bo'limi",
    description="Bu APIni admin rolli foydalanuvchi ishlata oladi,bunda mavjud bolimini statusni tugadi ga o'zgartrish mumkin"
)
class AdminFoodStatusUpdate(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            food = Food.objects.get(id=pk)
        except Food.DoesNotExist:
            return Response({"error": "taom topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FoodStatusSerializer(food, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "taom statusi yangilandi", "mavjud": serializer.data['mavjud']})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)