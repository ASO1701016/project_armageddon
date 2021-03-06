from django.shortcuts import render
from django.shortcuts import HttpResponse
from armageddon_system.models.dynamo_manager import DynamoManager as db
import qrcode
import hashlib


def display_pay_logs(request):
    context = {}
    if 'user_id' not in request.session:
        context['error'] = "ログインしてください"
        return render(request, 'armageddon_system/user/login.html', context)
    dbm = db()
    context['pay_logs'], context['total'] = dbm.get_pay_log_all()

    return render(request, 'armageddon_system/pay/log.html', context)


def display_form(request):
    context = {}
    if 'user_id' not in request.session:
        context['error'] = "ログインしてください"
        return render(request, 'armageddon_system/user/login.html', context)
    dbm = db()
    context['forms'] = dbm.get_form_all()
    context['max_id'] = dbm.get_next_form_id()
    # context['count'] = 1
    # {{forms.0.form_id}}でjs取得可能

    return render(request, 'armageddon_system/pay/item/list.html', context)


def display_qrcode(request):
    context = {}
    if 'user_id' not in request.session:
        context['error'] = "ログインしてください"
        return render(request, 'armageddon_system/user/login.html', context)
    context['form_name'] = request.POST['form_name']
    context['fee'] = request.POST['fee']
    qr = hashlib.md5(request.POST['form_name'].encode()).hexdigest()
    img = qrcode.make(qr)
    img.save('armageddon_system/static/armageddon_system/qr_code.png')

    return render(request, 'armageddon_system/pay/item/qr.html', context)


def save_form(request):
    context = {}
    if 'user_id' not in request.session:
        context['error'] = "ログインしてください"
        return render(request, 'armageddon_system/user/login.html', context)
    dbm = db()
    try:
        context['form_id'] = request.GET['form_id']
        context['form_name'] = request.GET['form_name']
        context['fee'] = request.GET['fee']
        context['issuance_days'] = request.GET['issuance_days']
        dbm.save_form(context)
    except KeyError:
        pass
    return HttpResponse("保存成功")


def delete_form(request):
    context = {}
    if 'user_id' not in request.session:
        context['error'] = "ログインしてください"
        return render(request, 'armageddon_system/user/login.html', context)
    dbm = db()
    try:
        dbm.del_form(request.GET['form_id'])
    except KeyError:
        pass
    return HttpResponse("削除成功")
