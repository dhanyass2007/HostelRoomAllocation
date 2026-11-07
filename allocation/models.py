
from django.db import models
from django.conf import settings
from django.db.models import Q


class Block(models.Model):
    block_name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.block_name


class Room(models.Model):
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
        related_name="rooms"
    )

    room_number = models.CharField(max_length=20)

    capacity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["block", "room_number"],
                name="unique_room_in_block"
            ),
            models.CheckConstraint(
                condition=Q(capacity__gt=0),
                name="room_capacity_positive"
            ),
        ]

    @property
    def occupied(self):
        return self.allocations.filter(
            status="APPROVED"
        ).count()

    @property
    def vacancies(self):
        return max(0, self.capacity - self.occupied)

    def __str__(self):
        return f"{self.block} - {self.room_number}"


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15)

    department = models.CharField(max_length=100)

    year = models.PositiveIntegerField()

    def __str__(self):
        return self.user.username


class Allocation(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hostel_allocations"
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="allocations"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    requested_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student"],
                condition=Q(status="APPROVED"),
                name="one_approved_room_per_student"
            )
        ]

    def __str__(self):
        return (
            f"{self.student.username} - "
            f"{self.room.room_number} - {self.status}"
        )


# Create your models here.
