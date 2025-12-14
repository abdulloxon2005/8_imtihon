from django.contrib import admin
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import Food, Promokod,CustomUser





@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "phone", "role", "is_staff")
    search_fields = ("username", "phone")
    list_filter = ("role", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        ("malumot", {
            "fields": ("phone", "role")
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("malumot", {
            "fields": ("phone", "role")
        }),
    )


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ("id", "nomi", "narxi", "turi","mavjud","rasm")
    


@admin.register(Promokod)
class PromokodAdmin(admin.ModelAdmin):
    list_display = ("id", "nomi", "amount", "end_date")
    
    
