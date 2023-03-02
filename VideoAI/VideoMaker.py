from email.message import EmailMessage
from moviepy.editor import *
import os
from moviepy import editor
from pydub import AudioSegment
import sys

import smtplib
import os
from email.message import EmailMessage

abs_path = "/home/kunj/freelance_prj/text_to_video/web_app/Web_VideoAI/VideoAI/static"
os.chdir(abs_path)
username = sys.argv[1]
images_folder = os.path.join(f'src/images/{username}')
images = [image for image in os.listdir(images_folder)]
images.sort()

for i in range(0, len(images)):
    audio_seg_path = os.path.join(f"src/audio/{username}/seg_{i}.mp3")
    sound = AudioSegment.from_file(audio_seg_path)
    image_clip = ImageClip(os.path.join(images_folder, images[i])).set_duration(sound.duration_seconds)
    audio_clip = AudioFileClip(audio_seg_path)
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.write_videofile(os.path.join(abs_path, f"src/video/{username}/seg_{i}.mp4"), threads=8, fps=24)
    
final_video = concatenate_videoclips([VideoFileClip(os.path.join(abs_path, f"src/video/{username}/seg_{i}.mp4")) for i in range(0, len(images))])
final_video.write_videofile(os.path.join(abs_path, f"src/video/{username}/Final_video.mp4"), threads = 8 , fps=24)

msg = EmailMessage()
msg['Subject'] = 'Your video is ready for download'
msg['From'] = 'freelancetestk@gmail.com' 
msg['To'] = sys.argv[2]

msg.set_content(f'''
<!DOCTYPE html>
<html>
    <body>
        <div style="background-color:#eee;padding:10px 20px;">
            <h2 style="font-family:Georgia, 'Times New Roman', Times, serif;color:#454349;text-align:center;">VideoAI</h2>
        </div>
        <div style="padding:20px 0px">
            <div style="height: 100%;width:100%">
                <img src="https://cdn.pixabay.com/photo/2020/11/07/10/25/machine-learning-5720531_960_720.png" style="height: 500px; width: 500px; justify:center;">
                <div style="text-align:center;">
                    <h3>click to download your video</h3>
                    <p>Hello {username}, We generated high definition video for you as per you wanted</p>
                    <form action="http://127.0.0.1:8000/VideoAI/download/">
                        <input type="submit" value="Download Video" />
                    </form>

                   </div>
            </div>
        </div>
    </body>
</html>
''', subtype='html')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.ehlo()
    smtp.login("freelancetestk@gmail.com", "fngougxcjbbzjdvr")
    smtp.send_message(msg)
    