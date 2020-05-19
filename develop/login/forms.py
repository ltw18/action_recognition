from django import forms 
class registing(forms.Form):
    gender_item = [(1,'female'),(2,'male'),(3,'other')]
    year_list = [i for i in range(1990,2020)]
    username = forms.CharField(max_length=8)
    password = forms.CharField(max_length=13)
    re_password = forms.CharField(max_length=13)
    phone = forms.CharField(max_length = 13)
class logining(forms.Form):
    username = forms.CharField(max_length=8,min_length=4,help_text='输入您的用户名',widget = forms.TextInput(attrs={'class':"custorm_form"}))
    password = forms.CharField(max_length=13,help_text='输入您的密码')
    # gender = forms.ChoiceField(choices=gender_item)
    # age =forms.IntegerField(widget=forms.SelectDateWidget(years=year_list))
    # birthday = forms.DateField()
    # email = forms.EmailField(widget = forms.TextInput(attrs={'class':"number_form"}))
class upload_video(forms.Form):
    actions = ((1,'kick'),(2,'daily'))
    myfile = forms.FileField()
    introduction = forms.CharField(max_length=100)
    uploader =forms.CharField(max_length=10)
    upload_time = forms.DateField()
    action_type = forms.ChoiceField(choices=actions)

class choose_video(forms.Form):
    # 打开那个摄像头
    place = ((1,'camera_1'),(2,'camera_2'))
    # 使用哪个算法
    actions = ((1,'kick'),(2,'daily'))
    place_open = forms.ChoiceField(choices=place)
    action_type = forms.ChoiceField(choices=actions)
    

    

