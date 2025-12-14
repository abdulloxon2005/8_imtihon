from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20,unique=True)
    role = models.CharField(max_length=20,choices=[
        ("user","User"),
        ("admin","Admin")
    ],default="user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Food(models.Model):
    nomi = models.CharField(max_length=50)
    narxi = models.DecimalField(max_digits=10,decimal_places=2)
    turi = models.CharField(max_length=20,choices=[
        ("ovqat","Ovqat"),
        ("ichimlik","Ichimliklar"),
        ("shirinlik","Shirinliklar")
    ],default="ovqat")
    mavjud = models.CharField(max_length=20,choices=[
        ("mavjud","Mavjud"),
        ("tugagan","Tugagan")
    ],default="mavjud")
    rasm = models.ImageField(upload_to="media/",null=True,blank=True)


class Promokod(models.Model):
    nomi = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

class Buyurtma(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    manzil = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,choices=[
        ("yangi","Yangi"),
        ("tayyorlanmoqda","Tayyorlanmoqda"),
        ("yolda","Yolda"),
        ("yetkazildi","Yetkazildi")
    ],default="yangi")
    promokod = models.ForeignKey(Promokod,on_delete=models.SET_NULL,null=True,blank=True)
    

class BuyurtmaItems(models.Model):
    food = models.ForeignKey(Food,on_delete=models.CASCADE)
    count = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    buyurtma = models.ForeignKey(Buyurtma,related_name="buyurtma",on_delete=models.CASCADE)

