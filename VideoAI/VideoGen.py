from django.http import HttpResponse
from moviepy.editor import *
import os
from mutagen.mp3 import MP3
from PIL import Image, ImageDraw, ImageFont
from moviepy import editor
from fontTools.ttLib import TTFont
import textwrap
from TTS.api import TTS
import numpy
from pydub import AudioSegment
import math 
import cv2
from gtts import gTTS
import mimetypes
import shutil

def get_images(username):
    # Get images from a folder
    images_folder = os.path.join(f'VideoAI/static/src/images/{username}')
    images = [os.path.join(f"/src/images/{username}/", image) for image in os.listdir(images_folder)]
    images.sort()
    return images

def get_templates(username):
    templates_folder = os.path.join(f'VideoAI/static/src/templates/{username}')
    templates = [os.path.join(templates_folder, temp) for temp in os.listdir(templates_folder)]
    templates.sort()
    return templates

def get_user_images(username):
    user_images_folder = os.path.join(f"media/{username}")
    user_images = [os.path.join(uimg) for uimg in os.listdir(user_images_folder)]
    user_images.sort()
    return user_images
    
def add_background_voice(audio_path,background_voice):
    sound1 = AudioSegment.from_file(f"VideoAI/static/src/audio/background_{background_voice}_audio.mp3")
    sound2 = AudioSegment.from_file(audio_path)
    sound1 = sound1 - 18
    combined = sound1.overlay(sound2)
    StrtMin = 0
    StrtSec = 0
    EndMin = 0
    EndSec = sound2.duration_seconds
    StrtTime = StrtMin*60*1000+StrtSec*1000
    EndTime = StrtMin*60*1000+EndSec*1000
    extract = combined[StrtTime:EndTime]
    extract.export(audio_path, format='mp3')
    
def segmented_sentences(text, username):
    print(os.getcwd())
    no_of_templates = 0
    for temp in os.listdir(f"VideoAI/static/src/templates/{username}"):
        no_of_templates+=1
    no_of_sent = text.count(".")
    
    all_sentences = text.split(".")
    
    sent_per_temp = math.ceil(no_of_sent/no_of_templates)
    sentences = list()
    print(no_of_sent)
    print(no_of_templates)
    print(sent_per_temp)
    if(sent_per_temp>7):
        sent_per_temp = 7
    for i in range(0,len(all_sentences),sent_per_temp):
        sentences.append('.'.join(all_sentences[i:i+sent_per_temp])+".")
    sentences = [x.replace("\n","") for x in sentences]
    
    for trunc in sentences:
        if(len(trunc.strip())<10):
            sentences.remove(trunc)
            
    for sent in sentences:
        print("----------------------------------------")
        print(sent)
        print("----------------------------------------")
    return sentences

def customized_images(text,username):
    sentences = segmented_sentences(text, username)
    print("len" + str(len(sentences)))
    images = get_templates(username)
    for sen_index in range(0, len(sentences)):
        image = images[sen_index % len(images)]
        cv_image = cv2.imread(os.path.join(image))
        height, width = cv_image.shape[:2]
        if(width != 3536):
            cv_image = cv2.resize(cv_image, (3536, 2357))
            width = 3536
            height = 2357
            cv2.imwrite(image, cv_image)
        segmented_text = sentences[sen_index]
        img = Image.open(os.path.join(image))
        img_draw = ImageDraw.Draw(img)
        myFont = ImageFont.truetype('VideoAI/static/src/fonts/Code_New_Roman.ttf', 66)
        wrapper = textwrap.TextWrapper(width=40,break_long_words=True)
        wrap_text = wrapper.fill(text=segmented_text)
        is_dark = numpy.mean(cv_image) > 127
        if is_dark:
            fill = (0,0,0)
        else:
            fill = (255,255,255)
        img_draw.text((width/2+70, height/20), wrap_text, font=myFont, fill = fill)
        img_name,ext = image.split("/")[-1].split(".")
        img.save(os.path.join(f'VideoAI/static/src/images/{username}/image_part_{sen_index}.{ext}'))
    return sentences
        
def copy_templates(username):
    templates_dir = f"VideoAI/static/src/templates/"
    for temp in os.listdir(templates_dir + "admin/"):
        src_path = templates_dir + "admin/" + temp
        dst_path = templates_dir + username + "/"
        print(src_path)
        print(dst_path)
        print()
        shutil.copy(src_path, dst_path)

def copy_user_images(username):
    media_dir = f"media/{username}/"
    for media in os.listdir(media_dir):
        src_path = media_dir + media
        dst_path = f"VideoAI/static/src/templates/{username}/"
        shutil.copy(src_path, dst_path)

def segment_audio(sentences,background_voice, username):
    durations = list()
    for i in range(0,len(sentences)):
        tts = gTTS(text=sentences[i], lang='en')
        audio_path = f"VideoAI/static/src/audio/{username}/seg_{i}.mp3"
        tts.save(os.path.join(audio_path))
        sent_audio = AudioSegment.from_file(audio_path)
        durations.append(sent_audio.duration_seconds)
        if(background_voice is ['Piano', 'Lovely', 'Relax']):
            add_background_voice(audio_path,background_voice.lower())
    return durations

def generate_video(username, email):
    os.system(f"python3 VideoMaker.py {username} {email}")
    
    

