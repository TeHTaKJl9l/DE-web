import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from requests_app.models import Specialist
from django.utils import timezone

class Command(BaseCommand):
    help = 'Импорт пользователей из CSV-данных'

    def handle(self, *args, **options):
        groups = ['Менеджер', 'Специалист', 'Оператор', 'Заказчик']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)

        users_data = [
            [1, 'Широков Василий Матвеевич', '89210563128', 'login1', 'pass1', 'Менеджер'],
            [2, 'Кудрявцева Ева Ивановна', '89535078985', 'login2', 'pass2', 'Специалист'],
            [3, 'Гончарова Ульяна Ярославовна', '89210673849', 'login3', 'pass3', 'Специалист'],
            [4, 'Гусева Виктория Данииловна', '89990563748', 'login4', 'pass4', 'Оператор'],
            [5, 'Баранов Артём Юрьевич', '89994563847', 'login5', 'pass5', 'Оператор'],
            [6, 'Овчинников Фёдор Никитич', '89219567849', 'login6', 'pass6', 'Заказчик'],
            [7, 'Петров Никита Артёмович', '89219567841', 'login7', 'pass7', 'Заказчик'],
            [8, 'Ковалева Софья Владимировна', '89219567842', 'login8', 'pass8', 'Заказчик'],
            [9, 'Кузнецов Сергей Матвеевич', '89219567843', 'login9', 'pass9', 'Заказчик'],
            [10, 'Беспалова Екатерина Даниэльевна', '89219567844', 'login10', 'pass10', 'Специалист'],
        ]

        for row in users_data:
            user_id, fio, phone, login, password, user_type = row

            name_parts = fio.split()
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

            user, created = User.objects.get_or_create(
                username=login,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f"{login}@example.com",
                }
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {login}'))
            else:
                self.stdout.write(f'Пользователь {login} уже существует, пропускаем')

            group = Group.objects.get(name=user_type)
            user.groups.add(group)

            if user_type == 'Специалист':
                specialist, spec_created = Specialist.objects.get_or_create(
                    user=user,
                    defaults={
                        'full_name': fio,
                        'phone': phone,
                        'email': f"{login}@example.com",
                        'hire_date': timezone.now().date(),
                        'is_active': True,
                    }
                )
                if spec_created:
                    self.stdout.write(self.style.SUCCESS(f'Создан специалист: {fio}'))
                else:
                    self.stdout.write(f'Специалист {fio} уже существует')

        self.stdout.write(self.style.SUCCESS('Импорт пользователей завершён!'))