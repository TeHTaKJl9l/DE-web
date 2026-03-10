from django.forms import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
import qrcode
from io import BytesIO
import base64
from .models import Request, EquipmentType, RequestStatus, Comment, PartOrder, Specialist
from .forms import RequestForm, CommentForm, PartOrderForm


@login_required
def request_list(request):
    requests = Request.objects.all().select_related('equipment_type', 'status', 'assigned_to')
    status = request.GET.get('status')
    eq_type = request.GET.get('eq_type')
    search = request.GET.get('search')
    if status:
        requests = requests.filter(status_id=status)
    if eq_type:
        requests = requests.filter(equipment_type_id=eq_type)
    if search:
        requests = requests.filter(
            models.Q(request_number__icontains=search) |
            models.Q(problem_description__icontains=search) |
            models.Q(customer_name__icontains=search) |
            models.Q(model__icontains=search)
        )
    context = {
        'requests': requests,
        'statuses': RequestStatus.objects.all(),
        'equipment_types': EquipmentType.objects.all(),
        'selected_status': status,
        'selected_eq_type': eq_type,
    }
    return render(request, 'requests_app/request_list.html', context)


@login_required
def request_detail(request, pk):
    req = get_object_or_404(Request.objects.select_related('equipment_type', 'status', 'assigned_to'), pk=pk)
    comments = req.comments.all().select_related('author')
    part_orders = req.part_orders.all()

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.request = req
                comment.author = request.user
                comment.save()
                messages.success(request, 'Комментарий добавлен.')
                return redirect('request_detail', pk=pk)
        elif 'add_part' in request.POST:
            form = PartOrderForm(request.POST)
            if form.is_valid():
                part = form.save(commit=False)
                part.request = req
                part.save()
                messages.success(request, 'Комплектующее добавлено.')
                return redirect('request_detail', pk=pk)
    else:
        comment_form = CommentForm()
        part_form = PartOrderForm()

    context = {
        'request_obj': req,
        'comments': comments,
        'part_orders': part_orders,
        'comment_form': comment_form,
        'part_form': part_form,
    }
    return render(request, 'requests_app/request_detail.html', context)


@login_required
def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            last_req = Request.objects.filter(
                created_at__year=timezone.now().year,
                created_at__month=timezone.now().month
            ).order_by('-id').first()
            if last_req:
                last_num = int(last_req.request_number.split('-')[-1]) + 1
            else:
                last_num = 1
            req.request_number = f"REQ-{timezone.now().strftime('%Y-%m')}-{last_num:04d}"
            req.save()
            messages.success(request, 'Заявка успешно создана.')
            return redirect('request_detail', pk=req.pk)
    else:
        form = RequestForm()
    return render(request, 'requests_app/request_form.html', {'form': form, 'title': 'Новая заявка'})


@login_required
def request_update(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявка обновлена.')
            return redirect('request_detail', pk=req.pk)
    else:
        form = RequestForm(instance=req)
    return render(request, 'requests_app/request_form.html', {'form': form, 'title': 'Редактирование заявки'})


@login_required
def request_delete(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if request.method == 'POST':
        req.delete()
        messages.success(request, 'Заявка удалена.')
        return redirect('request_list')
    return render(request, 'requests_app/request_confirm_delete.html', {'object': req})


@login_required
def statistics(request):
    completed_count = Request.objects.filter(status__code='completed').count()

    completed_reqs = Request.objects.filter(status__code='completed', completed_at__isnull=False)
    total_days = 0
    count = 0
    for req in completed_reqs:
        delta = req.completed_at - req.created_at
        total_days += delta.days
        count += 1
    avg_days = total_days / count if count > 0 else 0

    type_stats = EquipmentType.objects.annotate(
        request_count=Count('request')
    ).values('name', 'request_count')

    context = {
        'completed_count': completed_count,
        'avg_days': round(avg_days, 1),
        'type_stats': type_stats,
    }
    return render(request, 'requests_app/statistics.html', context)

@login_required
@permission_required('requests_app.can_extend_deadline', raise_exception=True)
def extend_deadline(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if request.method == 'POST':
        new_deadline = request.POST.get('new_deadline')
        comment = Comment.objects.create(
            request=req,
            author=request.user,
            text=f"Продлён срок выполнения по согласованию с заказчиком. Новый срок: {new_deadline}"
        )
        messages.success(request, 'Срок продлён, комментарий добавлен.')
        return redirect('request_detail', pk=pk)
    return render(request, 'requests_app/extend_deadline.html', {'request_obj': req})

@login_required
def generate_qr(request, pk):
    req = get_object_or_404(Request, pk=pk)
    survey_url = "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform?usp=sf_link"
    qr = qrcode.make(survey_url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')
    return render(request, 'requests_app/qr_code.html', {'qr_code': graphic, 'request_obj': req})