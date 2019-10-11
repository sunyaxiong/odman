import datetime

from django.contrib import admin

from .models import Channel
from .models import Consumer
from .models import UserProfile
from .models import WorkOrder
from .models import OrderAttachFile
from .models import WorkOrderPool
from .models import WorkOrderLog
from .models import SystemConf


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):

    list_display = ("name", "address", "phone", "email", "mpn_ids", "org_ids")
    list_filter = ("mpn_ids", )
    search_fields = ("mpn_ids", "phone", "email", "name", "org_ids")


@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "cn_name", "role")


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ("title", "number", "classify", "priority", "status", "proposer", "processor")

    def save_model(self, request, obj, form, change):
        if not obj.number:
            _number = str(obj.id).zfill(5)
            _timestamp = datetime.datetime.now().strftime("%y%m%d")
            obj.number = f"GD{_timestamp}{_number}"
            obj.save()


@admin.register(OrderAttachFile)
class OrderAttachFileAdmin(admin.ModelAdmin):
    list_display = ("title", "file", "file_url", "order")


@admin.register(WorkOrderPool)
class WorkOrderPoolAdmin(admin.ModelAdmin):

    list_display = ("order", "status")


@admin.register(WorkOrderLog)
class WorkOrderLogAdmin(admin.ModelAdmin):
    pass


@admin.register(SystemConf)
class SystemConfAdmin(admin.ModelAdmin):
    list_display = ["admin_mail", "service_mail"]


# @admin.register(SMTPConf)
# class SMTPConfAdmin(admin.ModelAdmin):
#     pass
