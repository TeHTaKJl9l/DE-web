import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from requests_app.models import Request, EquipmentType, RequestStatus, Specialist, User

class Command(BaseCommand):
    help = 'Импорт заявок из предоставленных данных'

    def handle(self, *args, **options):

        clients_data = {
            6: {'fio': 'Овчинников Фёдор Никитич', 'phone': '89219567849'},
            7: {'fio': 'Петров Никита Артёмович', 'phone': '89219567841'},
            8: {'fio': 'Ковалева Софья Владимировна', 'phone': '89219567842'},
            9: {'fio': 'Кузнецов Сергей Матвеевич', 'phone': '89219567843'},
        }

        equipment_map = {}
        for eq_name in ['Кондиционер', 'Увлажнитель воздуха', 'Сушилка для рук']:
            eq, created = EquipmentType.objects.get_or_create(name=eq_name)
            equipment_map[eq_name] = eq
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан тип оборудования: {eq_name}'))

        status_map = {
            'Новая заявка': 'open',
            'В процессе ремонта': 'in_progress',
            'Готова к выдаче': 'completed',
        }
        for status_name, code in status_map.items():
            status, created = RequestStatus.objects.get_or_create(
                code=code,
                defaults={'name': status_name}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан статус: {status_name} (code={code})'))

        requests_data = [
            # requestID, startDate, climateTechType, model, problemDesc, requestStatus, completionDate, repairParts, masterID, clientID
            (1, '2023-06-06', 'Кондиционер', 'TCL TAC-12CHSA/TPG-W белый',
             'Не охлаждает воздух', 'В процессе ремонта', None, '', 2, 7),
            (2, '2023-05-05', 'Кондиционер', 'Electrolux EACS/I-09HAT/N3_21Y белый',
             'Выключается сам по себе', 'В процессе ремонта', None, '', 3, 8),
            (3, '2022-07-07', 'Увлажнитель воздуха', 'Xiaomi Smart Humidifier 2',
             'Пар имеет неприятный запах', 'Готова к выдаче', '2023-01-01', '', 3, 9),
            (4, '2023-08-02', 'Увлажнитель воздуха', 'Polaris PUH 2300 WIFI IQ Home',
             'Увлажнитель воздуха продолжает работать при предельном снижении уровня воды', 'Новая заявка', None, '', None, 8),
            (5, '2023-08-02', 'Сушилка для рук', 'Ballu BAHD-1250',
             'Не работает', 'Новая заявка', None, '', None, 9),
        ]

        for row in requests_data:
            (req_id, start_date_str, eq_name, model, problem, status_name,
             completion_date_str, repair_parts, master_id, client_id) = row

            equipment = equipment_map[eq_name]

            status_code = status_map[status_name]
            status = RequestStatus.objects.get(code=status_code)

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            created_at = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))

            completed_at = None
            if completion_date_str:
                comp_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                completed_at = timezone.make_aware(datetime.combine(comp_date, datetime.min.time()))

            assigned_to = None
            if master_id:
                try:
                    username = f'login{master_id}'
                    user = User.objects.get(username=username)
                    assigned_to = Specialist.objects.get(user=user)
                except (User.DoesNotExist, Specialist.DoesNotExist):
                    self.stdout.write(
                        self.style.WARNING(f'Специалист с master_id={master_id} не найден. Заявка {req_id} будет без ответственного.')
                    )

            client_info = clients_data.get(client_id)
            if not client_info:
                self.stdout.write(
                    self.style.ERROR(f'Клиент с client_id={client_id} не найден в справочнике. Заявка {req_id} пропущена.')
                )
                continue
            customer_name = client_info['fio']
            customer_phone = client_info['phone']

            year = start_date.year
            request_number = f"REQ-{year}-{req_id:04d}"

            request_obj, created = Request.objects.update_or_create(
                request_number=request_number,
                defaults={
                    'created_at': created_at,
                    'equipment_type': equipment,
                    'model': model,
                    'problem_description': problem,
                    'customer_name': customer_name,
                    'customer_phone': customer_phone,
                    'status': status,
                    'assigned_to': assigned_to,
                    'completed_at': completed_at,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана заявка {request_number}'))
            else:
                self.stdout.write(self.style.WARNING(f'Заявка {request_number} уже существует, обновлена'))

        self.stdout.write(self.style.SUCCESS('Импорт заявок завершён!'))