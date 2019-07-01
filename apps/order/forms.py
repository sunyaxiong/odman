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
    file = forms.FileField()
    com_name = forms.CharField()
    contact = forms.CharField()
    email = forms.EmailField()
    phone = forms.IntegerField()
    is_consumer = forms.BooleanField()
