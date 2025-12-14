from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser,Food,Buyurtma,BuyurtmaItems,Promokod
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .serializers import FoodSerializers,PromokodSerializers,BuyurtmaSerializer,BuyurtmaStatusSerializer,FoodStatusSerializer
from .permissions import IsAdmin,IsUser
from decimal import Decimal
from rest_framework.generics import ListAPIView
from django.utils import timezone

class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        username = request.data.get("username")
        password = request.data.get("password")
        phone = request.data.get("phone")

        if not username or not password or not phone:
            return Response({"error":"malumotlarni hato kiritildi"},status = status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(username=username).exists():
            return Response({"error":"Username allaqchon bor"},status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.create_user(username=username,password=password,phone=phone)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return Response({"message":"User  muvaffaqiyatli yaratildi","username":user.username,"phone": user.phone,"role": user.role},status=status.HTTP_201_CREATED)


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

class AdminFoodViewSet(ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializers
    permission_classes = [IsAdmin]

class PromokodViewSet(ModelViewSet):
    queryset = Promokod.objects.all()
    serializer_class = PromokodSerializers
    permission_classes = [IsAdmin]

class UserBuyurtmaViewSet(APIView):
    permission_classes = [IsUser]

    def post(self, request):
        manzil = request.data.get("manzil")
        items_data = request.data.get("buyurtma")  
        promokod_id = request.data.get("promokod_id")

        if not manzil or not items_data:
            return Response({"error":"Malumotlar toliq emas"},status=status.HTTP_400_BAD_REQUEST)

        buyurtma = Buyurtma.objects.create(user=request.user, manzil=manzil, total_price=0)
        total_price = Decimal("0")

        for item in items_data:
            try:
                food = Food.objects.get(id=item["food_id"], mavjud="mavjud")
            except Food.DoesNotExist:
                buyurtma.delete()
                return Response({"error":f"Mahsulot id={item.get('food_id')} topilmadi yoki tugagan"},status=404)

            count = int(item["count"])
            item_price = food.narxi * count
            total_price += item_price


            BuyurtmaItems.objects.create(
                buyurtma=buyurtma,
                food=food,
                count=count,
                total_price=item_price
            )



        if promokod_id and total_price >= 100000:
            try:
                promokod = Promokod.objects.get(
                    id=promokod_id,
                    start_date__lte=timezone.now(),
                    end_date__gte=timezone.now()
                )
                total_price -= promokod.amount
                buyurtma.promokod = promokod
            except Promokod.DoesNotExist:
                pass

        buyurtma.total_price = max(total_price, 0)
        buyurtma.save()



        return Response(
            {
                "message":"Buyurtma muvaffaqiyatli yaratildi",
                "buyurtma_id":buyurtma.id,
                "total_price":buyurtma.total_price
            },
            status=status.HTTP_201_CREATED
        )


class BuyurtmaTarix(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        buyurtmalar = Buyurtma.objects.filter(user=request.user).order_by('-created_at')
        serializer = BuyurtmaSerializer(buyurtmalar, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        


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