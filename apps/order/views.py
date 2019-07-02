import datetime
import re
import json

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.db.models import Q

from django.contrib.auth.models import User
from .models import Channel
from .models import UserProfile
from .models import WorkOrder
from .models import WorkOrderPool
from .models import WorkOrderLog
from .models import OrderAttachFile
from .models import Consumer
from .models import ApplyVerifyCode
from .forms import RegisterForm, OrderCreatForm
from lib import excel2
from odman.settings import PAGE_LIMIT, WEB_HOST, WEB_PORT, ADMIN_MAIL


def my_login(request):

    if request.method == "GET":
        return render(request, 'login.html', locals())
    if request.method == "POST":
        username = request.POST.get("username")
        passwd = request.POST.get("password")
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except Exception as e:
            user = None
        # user = authenticate(username=username, password=passwd)

        if not user.is_staff:
            message = "用户未激活，请联系渠道管理员"
            return render(request, 'login.html', locals())
        if user is not None and user.check_password(passwd):
            login(request, user)
        else:
            message = "用户名或密码错误,请检查后重新输入"
            return render(request, 'login.html', locals())

        return HttpResponseRedirect('/order/orders/')



def my_logout(request):
    logout(request)

    return HttpResponseRedirect("/accounts/login/")


def register(request):
    if request.method == "POST":

        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.data
            # 检查MPN-ID
            try:
                channel = Channel.objects.get(mpn_ids=data.get("mpn_ids"))
            except ObjectDoesNotExist as e:
                channel = None
                message = f"MPN-ID验证失败,请联系您的代理商管理员核实MPN-ID"
                return render(request, "register.html", locals())
            # 创建用户
            try:
                user = User(
                    username=data.get("username"),
                    password=make_password(data.get("password")),
                    is_active=1,
                    email=data.get("email"),
                    # is_staff=1
                )
                user.save()
                if user:
                    profile = UserProfile.objects.create(
                        user=user,
                        phone=data.get("phone"),
                        email=data.get("email"),
                        channel=channel,
                        com_name=data.get("com_name"),
                    )
                    # 激活邮件：预留邮箱审核并激活
                    link = f"http://{WEB_HOST}:{WEB_PORT}/profile/{user.id}/"
                    content = f"管理员, 您好：\n 工单系统内，代理商：{channel.name}下有用户正在进行注册，请审批\n \
                        用户信息如下：\n \
                        用户名： {user.username}\n \
                        电  话： {user.userprofile.phone}\n \
                        邮  箱： {user.userprofile.email}\n \
                        邮  箱： {user.userprofile.com_name}\n \
                        如果确认信息无误，请点击下方链接激活：\n \
                        {link}"

                    send_mail(
                        "账号创建成功，请通过链接激活",
                        content,
                        "support@ecscloud.com",
                        [ADMIN_MAIL],   # 佳杰指定管理员邮箱进行激活
                        fail_silently=False
                    )
                return HttpResponse(
                    "注册成功，已经通知系统管理员进行账户审核，审核通过后会发送通知到您的邮箱，请您耐心等待邮件通知 ！"
                )
            except Exception as e:
                message = "请检查是否用户已存在，若存在可直接登陆。"
                return render(request, 'register.html', locals())
        else:
            print(form.errors)
            return render(request, "register.html", locals())
    return render(request, "register.html", locals())


@login_required
def profile(request, pk):
    try:
        user = User.objects.get(id=pk)
    except Exception as e:
        messages.warning("用户不存在")
        return render(request, "profile.html", locals())
    page_info = {
        "page_header": "个人信息",
        "page_des": "个人信息维护",
        "user": request.user,
    }
    return render(request, 'profile.html', locals())


def reset_passwd(request):

    if request.method == "POST":
        data = request.POST
        try:
            user = User.objects.get(email=data.get("email"))
        except Exception as e:
            user = None
        if not user:
            message = "用户不存在"
            return render(request, 'reset_passwd.html', locals())

        try:
            code = ApplyVerifyCode.objects.get(code=data.get("code"), user=user, status=1)
            code.status = 0
            code.save()
        except ObjectDoesNotExist as e:
            message = "验证码不存在或者失效，请重新申请"
            return render(request, 'reset_passwd.html', locals())

        user.password = make_password(data.get("passwd"))
        user.save()
        return HttpResponseRedirect("/accounts/login/")
    return render(request, "reset_passwd.html", locals())


@csrf_exempt
def apply_verify_code(request):

    if request.method == "POST":
        data = request.POST
        email = data.get("email")
        try:
            user = UserProfile.objects.filter(email=email).last().user
        except Exception as e:
            user = None

        if user:
            code = ApplyVerifyCode.objects.create(
                user=user
            )
            send_mail(
                "请查收验证码",
                f"您的验证码已经创建成功: {code.code}",
                "support@ecscloud.com",
                [user.userprofile.email],
                fail_silently=False
            )
            code, message = 0, "验证码已发送，请通过邮箱查收。"
        else:
            code, message = 1, "用户异常或者不存在，请联系管理员"
        res = {
            "message": message,
            "code": code
        }
        return HttpResponse(json.dumps(res))


@login_required
def profile_confirm(request, pk):

    try:
        user = User.objects.get(id=pk)
        if not user.is_staff:
            user.is_staff = 1
            user.save()
            login_link = f"http://{WEB_HOST}:{WEB_PORT}/accounts/login"
            send_mail(
                "账户激活提醒",
                f"尊敬的 {user.username}: \n 您的账户已经激活，请登陆并访问工单系统： {login_link}",
                "support@ecscloud.com",
                [user.userprofile.email],
            )
            messages.warning(request, f"用户: {user.username} 已经激活")
        else:
            messages.warning(request, "用户已经激活，无需重复点击")
    except ObjectDoesNotExist as e:
        messages.error(request, "用户注册异常，请联系用户重新注册")
        return HttpResponseRedirect("/order/orders/")
    return HttpResponseRedirect(f"/profile/{user.id}/")


@login_required
def profile_update(request, pk):

    if request.method == "POST":
        data = request.POST
        try:
            user = User.objects.get(id=pk)
        except Exception as e:
            user = None
            messages.warning("用户可能不存在")
        if user:
            user.userprofile.email = data.get("email")
            user.userprofile.phone = data.get("phone")
            user.userprofile.cn_name = data.get("name")
            user.userprofile.job_title = data.get("job_title")
            user.userprofile.save()
        return HttpResponseRedirect(f'/profile/{pk}/')


@login_required
def channel_list(request):
    """
    渠道列表
    :param request:
    :return:
    """
    queryset = Channel.objects.filter()

    # 条件筛选 & 搜索
    if request.GET.get("mpn_ids"):
        queryset = queryset.filter(mpn_ids=str(request.GET.get("mpn_ids")))
    if request.GET.get("q"):
        queryset = queryset.filter(name__contains=request.GET.get("q"))
    # 排序

    # 处理分页
    paginator = Paginator(queryset, PAGE_LIMIT)
    page = request.GET.get('page') if request.GET.get('page') else 1
    try:
        contacts = paginator.page(page)  # contacts为Page对象！
    except PageNotAnInteger:
        # 页面不是整数时，返回第一页
        page = 1
        contacts = paginator.page(1)
    except EmptyPage:
        page = 1
        # page超出整数范围，返回最后一页
        contacts = paginator.page(1)

    page_info = {
        "page_header": "渠道管理",
        "page_des": "渠道信息维护",
        "user": request.user,
        "table_title": "渠道商列表"
    }

    return render(request, 'channel_tables.html', locals())


@login_required
def import_channel(request):
    if request.method == "POST":
        excel = excel2.Excel(title_line=1, data_line=2)  # 导入所用模板第二行为标题行，index=1
        data = excel.load_by_cont(request.FILES.get("file").read())

        new_create_count = 0
        for i in data:
            obj, _ = Channel.objects.get_or_create(name=i.get("Partner Name"))
            if _:
                try:
                    mpn_id = int(i.get("MPN-ID").split(".")[0])
                except ValueError as e:
                    messages.warning(request, f"{obj.name} 未分配MPN-ID")
                    mpn_id = None

                obj.address = i.get("Partner 城市")
                obj.contact = i.get("SA Sales")
                obj.phone = i.get("phone")
                obj.email = i.get("email")
                obj.mpn_ids = mpn_id
                obj.save()
                new_create_count += 1
        messages.success(request, f"新导入渠道{new_create_count}个")
        return HttpResponseRedirect('/order/channels/')


@login_required
def channel_detail(request, pk):
    channel = Channel.objects.get(id=pk)

    page_info = {
        "page_header": "渠道详情",
        "page_des": "渠道信息维护",
        "user": request.user,
    }

    return render(request, "channel_detail.html", locals())


@login_required
def channel_update(request, pk):
    channel = Channel.objects.get(id=pk)

    if request.method == "POST":
        org_id = request.POST.get("org_ids")
        if not org_id:
            messages.warning(request, "订阅ID不能为空")
            return HttpResponseRedirect(f"/order/channel/{pk}")
        p = re.compile('^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$')
        if not p.match(org_id):
            messages.warning(request, "订阅ID格式不匹配")
            return HttpResponseRedirect(f"/order/channel/{pk}")

        username = org_id.split("@")[0]
        user, created = User.objects.get_or_create(username=username)
        if not created:
            messages.error(request, f"用户：{username}，已经存在，用户名不可重复")
            return HttpResponseRedirect(f"/order/channel/{pk}")
        else:
            user.email = org_id
            user.is_staff = 1
            user.password = make_password("1234ABCabc")
            user.save()
            UserProfile.objects.create(
                user=user,
                channel=channel,
                phone=channel.phone,
                email=channel.email,
            )

        channel.org_ids = org_id
        channel.save()
        messages.success(request, f"订阅id维护成功；用户： {username}, 创建成功")

    return HttpResponseRedirect(f"/order/channel/{pk}")


@login_required
def order_list(request):

    # 权限
    if request.user.userprofile.role == 2:
        queryset = WorkOrder.objects.filter(
            proposer=request.user  # 只能看到自己申请用户
        ).exclude(status=0)
    elif request.user.userprofile.role == 1:
        queryset = WorkOrder.objects.filter(
            processor=request.user
        ).exclude(status=0)  # 只能看到自己处理的单据
    else:
        queryset = WorkOrder.objects.filter().exclude(status=0)

    # 条件筛选 & 搜索
    try:
        if request.GET.get("mpn_ids"):
            queryset = queryset.filter(mpn_id=str(request.GET.get("mpn_ids")))
        if request.GET.get("q"):
            queryset = queryset.filter(title__contains=request.GET.get("q"))
        if request.GET.get("order_by"):
            queryset = queryset.order_by(request.GET.get("order_by"))
    except Exception as e:
        print(e)

    # 处理分页
    paginator = Paginator(queryset.order_by("-dt_created"), PAGE_LIMIT)
    page = request.GET.get('page') if request.GET.get("page") else 1
    try:
        contacts = paginator.page(page)  # contacts为Page对象！
    except PageNotAnInteger:
        # 页面不是整数时，返回第一页
        page = 1
        contacts = paginator.page(1)
    except EmptyPage:
        # page超出整数范围，返回最后一页
        page = 1
        contacts = paginator.page(paginator.num_pages)

    page_info = {
        "page_header": "工单管理",
        "page_des": "",
        "user": request.user,
        "table_title": "工单列表"
    }

    return render(request, 'order_tables.html', locals())


@login_required
def order_detail(request, pk):

    work_order = WorkOrder.objects.get(id=pk)
    process_logs = work_order.workorderlog_set.all()
    att_files = work_order.att_file.all()
    support_user_profile_list = UserProfile.objects.filter(role=1)  # 支持人员
    support_user_list = [i.user for i in support_user_profile_list]

    page_info = {
        "page_header": "工单详情",
        "page_des": "",
        "user": request.user,
    }

    # 请求人或者处理人可以看到工单
    if not (request.user == work_order.proposer or request.user == work_order.processor):
        page_info["page_header"] = "权限错误"
        message = "您无权访问该页面"
        return render(request, 'permission_error.html', locals())

    return render(request, "order_detail.html", locals())


@login_required
def order_update(request, pk):
    order = WorkOrder.objects.get(id=pk)
    if request.method == "POST":
        data = request.POST
        reply = data.get("reply")
        try:
            WorkOrderLog.objects.create(
                user=request.user,
                action="提交",
                field="处理记录",
                order=order,
                content=reply,
            )
        except Exception as e:
            messages.error(request, "处理记录提交失败，请重新提交")
        return HttpResponseRedirect(f"/order/order/{pk}")

    return HttpResponseRedirect('/order/orders/')


@login_required
def order_create(request):

    if request.method == "POST":
        form = OrderCreatForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.data
            # 创建订单
            try:
                order = WorkOrder(
                    title=data.get("title"),
                    content=data.get("content"),
                    status=1,
                    classify=int(data.get("classify")),
                    proposer=request.user,
                    channel=request.user.userprofile.channel
                )
                order.save()

                _number = str(order.id).zfill(5)
                _timestamp = datetime.datetime.now().strftime("%y%m%d")
                order.number = f"GD{_timestamp}{_number}"
                order.save()
            except Exception as e:
                order = None
                messages.warning(request, f"创建失败： {e}")
                return render(request, "order_create.html", locals())

            # 创建工单池对象\附件\客户信息入库
            if order:
                WorkOrderPool.objects.create(
                    order=order
                )
                OrderAttachFile.objects.create(
                    order=order,
                    file=request.FILES.get("file"),
                    title=request.FILES.get("file").name,
                )
                # 判断是否是最终客户
                is_consumer = 1 if data.get("is_consumer") == "1" else 0
                consumer, _ = Consumer.objects.get_or_create(
                    phone=data.get("phone"),
                )
                if _:
                    consumer.com_name = data.get("come_name")
                    consumer.email = data.get("email")
                    consumer.is_consumer = is_consumer
                    consumer.contact = data.get("contact")
                    consumer.channel = request.user.userprofile.channel
                    consumer.save()
                order.consumer = consumer
                order.save()

            messages.success(request, "工单提交成功")
            return HttpResponseRedirect(f"/order/order/{order.id}")
        else:
            print(form.errors)
            messages.warning(request, form.errors)
            return render(request, 'order_create.html', locals())

    page_info = {
        "page_header": "填写工单",
        "page_des": "",
        "user": request.user,
    }

    return render(request, "order_create.html", locals())


@login_required
def order_pool_list(request):

    queryset = WorkOrderPool.objects.filter(
        status=0  # 未领取
    )

    # # 条件筛选 & 搜索
    # if request.GET.get("mpn_id"):
    #     queryset = queryset.filter(mpn_id=str(request.GET.get("mpn_id")))

    # 处理分页
    paginator = Paginator(queryset.order_by("-dt_created"), PAGE_LIMIT)
    page = request.GET.get('page') if request.GET.get('page') else 1
    try:
        contacts = paginator.page(page)  # contacts为Page对象！
    except PageNotAnInteger:
        # 页面不是整数时，返回第一页
        contacts = paginator.page(1)
    except EmptyPage:
        # page超出整数范围，返回最后一页
        contacts = paginator.page(paginator.num_pages)

    page_info = {
        "page_header": "工单池管理",
        "page_des": "",
        "user": request.user,
        "table_title": "工单池"
    }

    return render(request, 'order_pool_tables.html', locals())


@login_required
def order_pool_take(request, pk):
    order_pool_obj = WorkOrderPool.objects.get(id=pk)

    if order_pool_obj.order.status == 2:
        messages.success(request, "不要重复领取")
        return HttpResponseRedirect("/order/orders/")

    order_pool_obj.status = 1
    order_pool_obj.order.status = 2  # ORDER_STATUS_CHOICE 处理中
    order_pool_obj.order.take_time = datetime.datetime.now()
    order_pool_obj.order.processor = request.user  # 当前处理人
    order_pool_obj.save()
    order_pool_obj.order.save()
    messages.success(request, f"工单：{order_pool_obj.order.title} 已经被领取")
    return HttpResponseRedirect("/order/orders/")


@login_required
def end_order(request, pk):
    """
    结束工单
    :param request:
    :param pk: 工单id
    :return:
    """
    try:
        order = WorkOrder.objects.get(id=pk)
    except Exception as e:
        order = None
        messages.error(request, f"{e}-请重试")
        return HttpResponseRedirect(f"/order/order/{pk}")
    if order:
        # 检查是否有当前用户处理记录，否则无法结束
        if not WorkOrderLog.objects.filter(order=order, user=request.user).exists():
            messages.warning(request, "您未对单据进行答复，请先提交答复")
            return HttpResponseRedirect(f"/order/order/{pk}")
        # 发送邮件
        send_mail(
            "工单结束提醒", f"您的工单: {order.title} 处理完成，请登陆查看处理结果",
            "support@ecscloud.com", [order.proposer.userprofile.email]
        )
        order.status = 4
        order.save()
    return HttpResponseRedirect(f"/order/order/{pk}")


@login_required
def pass_order(request, order_pk):
    """
    转交他人处理
    :param request:
    :param pk: 用户id
    :return:
    """
    if request.method == "POST":
        data = request.POST
        try:
            order = WorkOrder.objects.get(id=order_pk)
            user = User.objects.get(id=data.get("user_id"))  # 支持人员
        except Exception as e:
            order = None
            messages.error(request, f"{e}-订单或者用户不存在，请重试")
            return HttpResponseRedirect(request.get_full_path)
        if order:
            order.processor = user
            order.save()
        messages.success(request, f"订单:{order.title} 转交成功")
        return HttpResponseRedirect("/order/orders")


@login_required
def reject_order(request, pk):

    try:
        order = WorkOrder.objects.get(id=pk)
    except ObjectDoesNotExist as e:
        order = None
        messages.error(request, "工单不存在，请刷新并检查该工单状态")
        return HttpResponseRedirect(f"/order/order/{pk}/")
    if order:
        if not WorkOrderLog.objects.filter(order=order, user=request.user).exists():
            messages.warning(request, "您未对单据进行答复，请先提交答复")
            return HttpResponseRedirect(f"/order/order/{pk}")
        order.status = 3
        order.save()
        messages.success(request, "工单驳回成功")
        send_mail(
            "工单驳回提醒",
            f"您好，您的工单：{order.title}, 已经被驳回，请登陆系统查看驳回原因",
            "support@ecscloud.com",
            [order.proposer.userprofile.email]
        )
        return HttpResponseRedirect(f"/order/order/{pk}")
