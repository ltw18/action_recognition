from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from .forms import logining,registing,upload_video,choose_video
from .models import User, Video
import os
import camera_show
import video_analysis
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
            context = {
                'alarm_action':alarm_action,
                'alarm_date':alarm_date,
                'suggestion':suggestion
            }
            return HttpResponseRedirect(request,'analysis.html',context = context)  
    return render(request, 'upload.html', {'forms': upload_video})
    
def handle_uploaded_file(f):
    with open('upload/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    alarm_action,alarm_date,suggestion = video_analysis(destination)
    return alarm_action,alarm_date,suggestion
    # frames = cv2.  
    # analysis(destination)
    
def analysis(request):
    
    return HttpResponse('hello')

def open_video(request):
    if request.method == "POST":
        # 否则就是POST请求，获取表单中的数据
        camera = request.POST.get('place_open')
        method = request.POST.get('action_type') 
        if camera =='1' and method =='2':
            camera_show
        else:return HttpResponse('service isnot prepared')
    return render(request, 'video_platform.html', {'forms':choose_video})
