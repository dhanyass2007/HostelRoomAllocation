
from django.contrib import admin
from .models import Block, Room, StudentProfile, Allocation


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("id", "block_name")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "room_number",
        "block",
        "capacity",
        "occupied",
        "vacancies",
    )

    list_filter = ("block",)

    search_fields = ("room_number",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "department",
        "year",
    )


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "room",
        "status",
        "requested_date",
    )

    list_filter = ("status", "room__block")


# Register your models here.
