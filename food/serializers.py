from rest_framework import serializers
from .models import CustomUser,Promokod,BuyurtmaItems,Food,Buyurtma

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','password','phone','role',]
        read_only_fields = ["role"]


class FoodSerializers(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = "__all__"

class PromokodSerializers(serializers.ModelSerializer):
    class Meta:
        model = Promokod
        fields = "__all__"



class BuyurtmaItemsSerializer(serializers.ModelSerializer):
    food_nomi = serializers.CharField(source='food.nomi', read_only=True)
    narxi = serializers.DecimalField(source='food.narxi', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = BuyurtmaItems
        fields = ['food_nomi', 'narxi', 'count', 'total_price']


    class Meta:
        model = BuyurtmaItems
        fields = [
            "food_id",
            "count"
        ]

class BuyurtmaSerializer(serializers.ModelSerializer):
    items = BuyurtmaItemsSerializer(many=True, read_only=True)
    promokod = serializers.CharField(source='promokod.nomi', read_only=True)

    class Meta:
        model = Buyurtma
        fields = ['id', 'manzil', 'total_price', 'status', 'promokod', 'created_at', 'items']


class BuyurtmaStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyurtma
        fields = ['status']

class FoodStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['mavjud']