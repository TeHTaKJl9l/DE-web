from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class EquipmentType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Тип оборудования'
        verbose_name_plural = 'Типы оборудования'

    def __str__(self):
        return self.name

class RequestStatus(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Код')
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Статус заявки'
        verbose_name_plural = 'Статусы заявок'

    def __str__(self):
        return self.name

class Specialist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='specialist_profile')
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(unique=True, verbose_name='Email')
    hire_date = models.DateField(default=timezone.now, verbose_name='Дата найма')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'

    def __str__(self):
        return self.full_name

class Request(models.Model):
    request_number = models.CharField(max_length=20, unique=True, verbose_name='Номер заявки')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.PROTECT, verbose_name='Тип оборудования')
    model = models.CharField(max_length=100, verbose_name='Модель')
    problem_description = models.TextField(verbose_name='Описание проблемы')
    customer_name = models.CharField(max_length=150, verbose_name='ФИО заказчика')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон')
    status = models.ForeignKey(RequestStatus, on_delete=models.PROTECT, default=1, verbose_name='Статус')
    assigned_to = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ответственный')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if self.status.code == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status.code != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)

class Comment(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='comments', verbose_name='Заявка')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.author.username}"

class PartOrder(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='part_orders', verbose_name='Заявка')
    part_name = models.CharField(max_length=200, verbose_name='Наименование комплектующего')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Количество')
    ordered_at = models.DateTimeField(default=timezone.now, verbose_name='Дата заказа')
    received = models.BooleanField(default=False, verbose_name='Получено')

    class Meta:
        verbose_name = 'Заказ комплектующих'
        verbose_name_plural = 'Заказы комплектующих'

    def __str__(self):
        return f"{self.part_name} x{self.quantity}"

class Meta:
    permissions = [
        ("can_extend_deadline", "Может продлевать срок заявки"),
    ]