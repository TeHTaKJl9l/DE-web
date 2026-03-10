from django.core.management.base import BaseCommand
from requests_app.models import Comment, Request, Specialist

class Command(BaseCommand):
    help = 'Импорт комментариев из предоставленных данных'

    def handle(self, *args, **options):
        #(commentID, message, masterID, requestID)
        comments_data = [
            (1, 'Всё сделаем!', 2, 1),
            (2, 'Всё сделаем!', 3, 2),
            (3, 'Починим в момент.', 3, 3),
        ]

        for comment_id, message, master_id, request_id in comments_data:
            try:
                request = Request.objects.get(id=request_id)
            except Request.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Заявка с ID {request_id} не найдена. Пропускаем.')
                )
                continue

            try:
                specialist = Specialist.objects.get(id=master_id)
                author = specialist.user
            except Specialist.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Специалист с ID {master_id} не найден. Пропускаем.')
                )
                continue

            comment, created = Comment.objects.get_or_create(
                request=request,
                author=author,
                text=message,
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Комментарий {comment_id} успешно добавлен.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Комментарий {comment_id} уже существует (пропущено).')
                )

        self.stdout.write(self.style.SUCCESS('Импорт комментариев завершён!'))