from hashlib import sha1
import random

from django.db import models
from django.contrib.auth.models import User

from odman import settings
from lib.models import BaseModel


class Channel(BaseModel):

    name = models.CharField("渠道商名称", max_length=128, null=True, blank=True)
    address = models.CharField("地址", max_length=256, null=True, blank=True)
    contact = models.CharField("联系人", max_length=128, null=True, blank=True)
    phone = models.CharField("电话", null=True, blank=True, max_length=128)
    email = models.EmailField("邮箱", null=True, blank=True)
    mpn_ids = models.IntegerField("MPN-ID", null=True, blank=True)
    org_ids = models.CharField("订阅ID", max_length=64, null=True, blank=True)

    class Meta:
        verbose_name = "渠道商"
        verbose_name_plural = "渠道商"

    def __str__(self):
        return str(self.id)


class Consumer(BaseModel):
    """
    客户信息表
    注意： 客户不是系统内账户
    """
    com_name = models.CharField("公司名称", max_length=128, null=True, blank=True)
    email = models.EmailField("联系邮箱", null=True, blank=True)
    phone = models.IntegerField("联系电话", null=True, blank=True)
    channel = models.ForeignKey(
        Channel, verbose_name="代理商", on_delete=models.DO_NOTHING, db_constraint=False, null=True, blank=True
    )
    contact = models.CharField("联系人", max_length=128, null=True, blank=True)
    is_consumer = models.BooleanField("是否客户", null=True, blank=True)

    class Meta:
        verbose_name = "客户"
        verbose_name_plural = "客户"

    def __str__(self):
        return self.contact


ROLE_CHOICE = (
    (0, "管理员"),
    (1, "支持人员"),
    (2, "普通用户"),
)


class UserProfile(BaseModel):

    user = models.OneToOneField(
        User, verbose_name="用户名", on_delete=models.DO_NOTHING, db_constraint=False
    )
    cn_name = models.CharField("中文姓名", max_length=128, null=True, blank=True)
    job_title = models.CharField("岗位", max_length=128, null=True, blank=True)
    phone = models.IntegerField("电话", null=True, blank=True)
    email = models.EmailField("邮箱", null=True, blank=True)
    com_name = models.CharField("公司名称", max_length=128, null=True, blank=True)
    channel = models.ForeignKey(
        Channel, verbose_name="渠道", on_delete=models.DO_NOTHING, db_constraint=False, null=True, blank=True
    )
    role = models.IntegerField(
        "角色", null=True, blank=True, choices=ROLE_CHOICE, help_text="系统用来判断权限", default=2
    )

    class Meta:
        verbose_name = "用户配置文件"
        verbose_name_plural = "用户配置文件"

    def __str__(self):
        return self.user.username


ORDER_STATUS_CHOICE = (
    (0, "草稿"),
    (1, "已提交"),
    (2, "处理中"),
    (3, "驳回"),
    (4, "结束")
)

ORDER_CFY_CHOICE = (
    (1, "商务"),
    (2, "技术"),
)

PRIORITY_CHOICE = (
    (0, "普通"),
    (1, "中等"),
    (2, "高"),
    (3, "极高"),
)


class WorkOrder(BaseModel):

    channel = models.ForeignKey(Channel, verbose_name="渠道商", on_delete=models.DO_NOTHING, db_constraint=False)
    number = models.CharField("表单号", max_length=32, null=True, blank=True)
    title = models.CharField("工单标题", max_length=128)
    classify = models.IntegerField(
        "工单类型", null=True, blank=True, choices=ORDER_CFY_CHOICE
    )
    content = models.TextField("工单正文")
    priority = models.IntegerField("优先级", default=0, choices=PRIORITY_CHOICE)
    status = models.IntegerField("状态", choices=ORDER_STATUS_CHOICE, default=0)
    proposer = models.ForeignKey(
        User, verbose_name="申请人", null=True, blank=True, db_constraint=False, on_delete=models.DO_NOTHING
    )
    consumer = models.ForeignKey(
        Consumer, verbose_name="客户", null=True, blank=True, db_constraint=False, on_delete=models.DO_NOTHING
    )
    processor = models.ForeignKey(
        User, verbose_name="当前处理人", null=True, blank=True, db_constraint=False,
        on_delete=models.DO_NOTHING, related_name="processor"
    )
    take_time = models.DateTimeField("领取时间", null=True, blank=True)
    actual_contact = models.CharField("实际联系人", null=True, blank=True, max_length=256)

    class Meta:
        verbose_name = "工单"
        verbose_name_plural = "工单"

    def __str__(self):
        return self.title


def order_file_upload_to(instance, filename):
    content = instance.file.file.read()
    content_hash = sha1(content).hexdigest()
    suffix = filename.split('.')[-1]
    args = [
            'order_files',
            '%s.%s' % (content_hash, suffix),
            ]
    return '/'.join(args)


class OrderAttachFile(BaseModel):

    title = models.CharField(max_length=32, blank=True, verbose_name="文件名")
    file = models.FileField(upload_to=order_file_upload_to, blank=True, verbose_name="文件")
    file_url = models.URLField(max_length=512, null=True, blank=True, verbose_name="文件url")
    order = models.ForeignKey(
        WorkOrder, verbose_name="工单", on_delete=models.DO_NOTHING, db_constraint=False, related_name="att_file"
    )

    class Meta:
        verbose_name = "工单附件"
        verbose_name_plural = "工单附件"

    def __str__(self):
        return self.title


ORDER_POOL_STATUS = (
    (0, "待领取"),
    (1, "已领取"),
)


class WorkOrderPool(BaseModel):

    order = models.OneToOneField(WorkOrder, on_delete=models.DO_NOTHING, db_constraint=False)
    status = models.BooleanField("领取状态", default=0, choices=ORDER_POOL_STATUS)

    class Meta:
        verbose_name = "工单池"
        verbose_name_plural = "工单池"

    def __str__(self):
        return self.order.title


class WorkOrderLog(BaseModel):

    user = models.ForeignKey(User, verbose_name="操作人", on_delete=models.DO_NOTHING, db_constraint=False)
    action = models.CharField("操作", max_length=128, null=True, blank=True)
    field = models.CharField("字段", max_length=128, null=True, blank=True)
    order = models.ForeignKey(
        WorkOrder, verbose_name="工单", on_delete=models.DO_NOTHING, db_constraint=False, null=True, blank=True
    )
    content = models.TextField("内容", null=True, blank=True)

    class Meta:
        verbose_name = "工单日志"
        verbose_name_plural = "工单日志"

    def __str__(self):
        return self.order.title


class UserAlert(BaseModel):
    pass


class ApplyVerifyCode(BaseModel):

    user = models.ForeignKey(User, verbose_name="申请人", on_delete=models.DO_NOTHING, db_constraint=False)
    code = models.IntegerField("验证码", help_text="4位随机数字")
    status = models.BooleanField("是否有效", default=1)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.code:
            self.code = random.randint(1024, 9999)
        super(self.__class__, self).save()


class SystemConf(BaseModel):

    admin_mail = models.TextField("审核邮箱", null=True, blank=True, help_text="此处邮箱接收审核邮件")
    service_mail = models.EmailField(
        "客服邮箱", null=True, blank=True, help_text="此邮箱显示在注册失败时"
    )
    public_mail = models.TextField("公共邮箱", null=True, blank=True, help_text="此处邮箱接收新工单提醒")

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = "系统设置"

    def __str__(self):
        return "配置详情"


# class SMTPConf(BaseModel):
#
#     smtp_host = models.CharField("EMAIL_HOST", null=True, blank=True, max_length=128)
#     smtp_port = models.IntegerField("EMAIL_PORT", null=True, blank=True, default=25)
#     smtp_user = models.CharField("EMAIL_HOST_USER", null=True, blank=True, max_length=128)
#     smtp_pass = models.CharField("EMAIL_HOST_PASSWORD", null=True, blank=True, max_length=128)
#     smtp_prefix = models.CharField("EMAIL_SUBJECT_PREFIX", null=True, blank=True, max_length=128)
#     smtp_tls = models.BooleanField("EMAIL_USE_TLS", null=True, blank=True, default=True)
#
#     class Meta:
#         verbose_name = "SMTP配置"
#         verbose_name_plural = "SMTP配置"
#
#     def __str__(self):
#         return "SMTP配置"
