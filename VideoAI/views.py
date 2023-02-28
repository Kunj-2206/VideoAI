import re
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
import requests
from VideoAI.forms import TextInputForm
import os
from VideoAI.VideoGen import copy_templates, copy_user_images, generate_video, get_images, customized_images, get_templates, get_user_images, segment_audio
from .forms import DltImageForm, ImageForm, NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate 
import base64 as b64
from django.http import HttpResponse  
from django.core.signing import Signer, BadSignature
import datetime

def set_cookie(response, key, value, days_expire=90):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",)
    signer = Signer()
    cookie_value = signer.sign(value)
    response.set_cookie(key,cookie_value,max_age=max_age,expires=expires)

def index_view(request):
    return render(request, 'index.html')

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        messages.error(request, form.errors)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            print(email)
            user = form.save()
            login(request, user)
            response = HttpResponse("Registration successful. Click <a href='http://127.0.0.1:8000/VideoAI'>here</a> to continue.")
            set_cookie(response, 'id', username)
            set_cookie(response, 'auth', email)
            dirs = ['audio','images','uploads','video', 'templates']
            for dir in dirs:
                os.mkdir("VideoAI/static/src/" + dir + "/" + str(username))
            os.mkdir(os.path.join('media', str(username)))
            copy_templates(username)
            return response
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="register.html", context={"register_form":form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            response = HttpResponse("Login successful. Click <a href='http://127.0.0.1:8000/VideoAI'>here</a> to continue." )
            set_cookie(response, 'id', username)
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return response
            else:
                return HttpResponse('Unauthorized', status=401)
        else:
            return HttpResponse('Unauthorized', status=401)
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form})

def text_input_view(request):
    signer = Signer()
    my_cookie = request.COOKIES.get('id')
    if my_cookie:
        try:
            username = signer.unsign(my_cookie)
            if request.method == 'POST':
                form = TextInputForm(request.POST)
                if form.is_valid():
                    text_input = form.cleaned_data['text_input']
                    urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text_input)
                    for url in urls:
                        resp = requests.get(url)
                        if resp.status_code == 200:
                            text_input += resp.text
                    with open(f'VideoAI/static/src/uploads/{username}/user.txt', 'w') as f:
                        f.write(text_input)
                    return redirect('textview/')
                    # Do something with the text input here
            else:
                if request.user.is_authenticated:
                    form = TextInputForm()
                    print("y")
                else:
                    print("not authenticated")
                    redirect('login')
            return render(request, 'text_input.html', {'form': form})
        except BadSignature:
            print("except")
            return redirect('login')
    else:
        return redirect('login')

def text_view(request):
    signer = Signer()
    my_cookie = request.COOKIES.get('id')
    if my_cookie:
        try:
            username = signer.unsign(my_cookie)
            with open(f'VideoAI/static/src/uploads/{username}/user.txt', 'r') as f:
                text = f.read()
            if request.method == 'POST':
                if(request.POST.get('text_edit')):
                    text = request.POST.get('text_edit')
                    with open(f'VideoAI/static/src/uploads/{username}/user.txt', 'w') as f:
                        f.write(text)
                background_audio_choice = request.POST.get('background_audio')
                copy_user_images(username)
                sentences = customized_images(text, username)
                segment_audio(sentences, background_audio_choice, username)
                return redirect('image-view')
            else:
                background_voices = ['None', 'Lovely', 'Piano', 'Relax']
                return render(request, 'text_view.html', {'text': text, 'background_voices': background_voices})
        except BadSignature:
            return redirect('login')
    else:
        return redirect('login')

def upload_image(request):
    signer = Signer()
    my_cookie = request.COOKIES.get('id')
    if my_cookie:
        try:
            username = signer.unsign(my_cookie)
            user_images = get_user_images(username)
            if(len(user_images)>5):
                return render(request, 'upload.html',{'DltImgform': dltImgForm ,'user_images': user_images, 'no_of_uimg':no_of_uimg})
            if request.method == 'POST':
                form = ImageForm(request.POST, request.FILES)
                dltImgForm = DltImageForm(request.POST)
                if form.is_valid() | dltImgForm.is_valid():
                    form.instance.username = username
                    img_name = dltImgForm.cleaned_data['image_name']
                    if img_name in user_images:
                        print("in if")
                        os.remove(f'media/{username}/{img_name}')
                    form.save()
                    return redirect('text-view')
            else:
                no_of_uimg = len(user_images)
                form = ImageForm(use_required_attribute=False)
                dltImgForm = DltImageForm(use_required_attribute=False)
            return render(request, 'upload.html', {'form': form, 'DltImgform': dltImgForm ,'user_images': user_images, 'no_of_uimg':no_of_uimg})
        except BadSignature:
            return redirect('login')
    else:
        return redirect('login')

def image_view(request):
    signer = Signer()
    my_cookie = request.COOKIES.get('id')
    if my_cookie:
        try:
            username = signer.unsign(my_cookie)
            form = ImageForm()
            images = get_images(username)
            return render(request, 'image_view.html', {'images':images,'form':form})
        except BadSignature:
            return redirect('login')
    else:
        return redirect('login')

def create_video(request):
    signer = Signer()
    my_cookie = request.COOKIES.get('id')
    my_cookie2 = request.COOKIES.get('auth')
    if my_cookie:
        try:
            username = signer.unsign(my_cookie)
            email = signer.unsign(my_cookie2)
            generate_video(username, email)
        except:
            return redirect('login')
    else:
        return redirect('login')
    
def download_video(request):
    signer = Signer()
    my_cookie = request.COOKIES.get('id')
    if my_cookie:
        try:
            username = signer.unsign(my_cookie)
            video_path = os.path.join(f"VideoAI/static/src/video/{username}/{username}_Final.mp4")
            file_path = os.path.basename(video_path)
            with open(video_path, 'rb') as f:
                contents = f.read()
            response = HttpResponse(contents, content_type='application/pdf')
            response['Content-Length'] = os.path.getsize(video_path)
            response['Content-Disposition'] = f'attachment; filename="{file_path}"'
            return response 
        except BadSignature:
            return redirect('login')
    else:
        return redirect('login')    