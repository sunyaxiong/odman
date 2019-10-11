from django import forms


class ImportChannelForm(forms.Form):
    """
    导入渠道的form，废弃
    """
    file = forms.FileField(required=False)


class RegisterForm(forms.Form):
    """
    用户注册Form验证
    """
    mpn_ids = forms.CharField(required=True)
    username = forms.CharField(required=True)
    email = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    password = forms.PasswordInput()
    retype = forms.PasswordInput()


class OrderCreatForm(forms.Form):
    """
    订单创建Form验证
    """
    title = forms.CharField()
    classify = forms.CharField()
    content = forms.Textarea()
    priority = forms.CharField(required=False)
    file = forms.FileField(
        error_messages={"required": "请添加附件"}, required=False
    )
    com_name = forms.CharField(
        error_messages={"required": "请填写公司名称"}
    )
    contact = forms.CharField(
        error_messages={"required": "请填写联系人"}
    )
    email = forms.EmailField(
        error_messages={"required": "请填写邮箱"}
    )
    phone = forms.IntegerField(
        error_messages={"required": "请填写电话"}
    )
    is_consumer = forms.BooleanField()
