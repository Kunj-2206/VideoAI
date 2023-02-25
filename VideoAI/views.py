import mimetypes
import re
from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
from VideoAI.forms import TextInputForm
import os
from VideoAI.VideoGen import copy_templates, copy_user_images, generate_video, get_images, customized_images, get_templates, segment_audio
from .forms import ImageForm, NewUserForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate 
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm 
import base64 as b64
from django.http import HttpResponse  

def base64_decode(enc):
    return b64.b64decode(enc.encode('ascii')).decode('ascii')
    
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        messages.error(request, form.errors)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            ubytes = str(username).encode('ascii')
            b64_bytes = b64.b64encode(ubytes)
            user = form.save()
            login(request, user)
            response = HttpResponse("Registration successful. Click <a href='http://127.0.0.1:8000/VideoAI'>here</a> to continue.")
            response.set_cookie('id', b64_bytes.decode('ascii'))
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
            ubytes = str(username).encode('ascii')
            b64_bytes = b64.b64encode(ubytes)
            response = HttpResponse("Login successful." )
            response.set_cookie('id', b64_bytes.decode('ascii'))
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return response
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    username = request.COOKIES.get('id')
    print(username)
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form})

def text_input_view(request):
    if request.method == 'POST':
        form = TextInputForm(request.POST)
        if form.is_valid():
            text_input = form.cleaned_data['text_input']
            urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text_input)
            username = base64_decode(request.COOKIES.get('id'))
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
            redirect('login')
    return render(request, 'text_input.html', {'form': form})

def text_view(request):
    username = base64_decode(request.COOKIES.get('id'))
    with open(f'VideoAI/static/src/uploads/{username}/user.txt', 'r') as f:
        text = f.read()
    if request.method == 'POST':
        if(request.POST.get('text_edit')):
            text = request.POST.get('text_edit')
            with open(f'VideoAI/static/src/uploads/{username}/user.txt', 'w') as f:
                f.write(text)
        background_audio_choice = request.POST.get('background_audio')
        print(text) 
        print(background_audio_choice)
        copy_user_images(username)
        sentences = customized_images(text, username)
        segment_audio(sentences, background_audio_choice, username)
        return redirect('image-view')
    else:
        background_voices = ['None', 'Lovely', 'Piano', 'Relax']
        return render(request, 'text_view.html', {'text': text, 'background_voices': background_voices})

def upload_image(request):
    username = base64_decode(request.COOKIES.get('id'))
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.username = username
            form.save()
            return redirect('text-view')
    else:
        form = ImageForm()
    return render(request, 'upload.html', {'form': form})

def image_view(request):
    username = base64_decode(request.COOKIES.get('id'))
    form = ImageForm()
    images = get_images(username)
    return render(request, 'image_view.html', {'images':images,'form':form})

def create_video(request):
    username = base64_decode(request.COOKIES.get('id'))
    generate_video(username)
    video_path = os.path.join(f"VideoAI/static/src/video/{username}_Final.mp4")
    path = open(video_path, 'r')
    mime_type, _ = mimetypes.guess_type(video_path)
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % video_path
    return response