from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from .forms import logining,registing,upload_video,choose_video
from .models import User, Video
import os
# from camera_show import camera_show
from video_analysis import analysis
# from .open_video import *
# Create your views here.
def regist(request):
    error = []
    if request.method == "GET":
        return render(request, 'regist.html', {'forms':registing, 'error':error})
    else:
    # 否则就是POST请求，获取表单中的数据
        name = request.POST.get('username')
        pwd = request.POST.get('password')
        phone = request.POST.get('phone')
        pwd2 = request.POST.get('re_password')      
        User.objects.create(username=str(name),password = str(pwd),phone = str(phone))
        if pwd2!=pwd:
            error.append('两次输入不统一')
        print(name,pwd)
    return render(request, 'regist.html', {'forms':registing,'error':str(error)})

def login(request):
    if request.method == "GET":
        return render(request, 'login.html', {'forms':logining})
    else:
        # 否则就是POST请求，获取表单中的数据
        name = request.POST.get('username')
        pwd = request.POST.get('password')
        # 进行数据库的查询，如果不存在或报异常
        try:
            user_obj = User.objects.get(username=str(name), password=str(pwd))
        except:
            # return HttpResponse("<script>alert('用户名或密码不正确');window.location.href='login.html'</script>")
            return render(request,'login.html',{'forms':logining})

        # return HttpResponse(user_obj.username + "您好，欢迎使用")
        return HttpResponseRedirect('/home/')

def home(request):
    return render(request,'home.html')

def data_platform(request):
    return render(request,'data_platform.html')

def upload(request):
    if request.method == 'POST':
        my_form = upload_video(request.POST, request.FILES)
        if my_form.is_valid():
            f = my_form.cleaned_data['myfile']
            alarm_action,alarm_date,suggestion = handle_uploaded_file(f)
            con = {
                'filename': f,
                'suggestion':suggestion,
                'alarm_action_1':alarm_action[0],
                'alarm_date_1':alarm_date[0],
                'alarm_action_2':alarm_action[1],
                'alarm_date_2':alarm_date[1],
            }
            return render(request,'analysis.html',context=con)
            # return render(request,'analysis.html',{'alarm_action':alarm_action,
            #     'alarm_date':alarm_date,
            #     'suggestion':suggestion})  
    return render(request, 'upload.html', {'forms': upload_video})
    
def handle_uploaded_file(f):
    path = '../upload/'+f.name
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    alarm_action,alarm_date,suggestion = analysis(path)
    return alarm_action,alarm_date,suggestion

    

def open_video(request):
    if request.method == "POST":
        # 否则就是POST请求，获取表单中的数据
        camera = request.POST.get('place_open')
        method = request.POST.get('action_type') 
        if camera =='1' and method =='2':
            # camera_show
            return HttpResponse('hello')
        else:return HttpResponse('service isnot prepared')
    return render(request, 'video_platform.html', {'forms':choose_video})

