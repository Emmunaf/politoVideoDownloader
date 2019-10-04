#!/usr/bin/python
# -*- coding: utf-8 -*-
"""poliVideoDownload.py: A client for video download automatizazion 
Edit accounts.txt file in the following format to use this script:

username:password
username2:password2

Requirements:
    pip install bs4
    pip install requests 
"""
#template_video.php?id_lez=35179&amp;inc=227523&amp;f=1&amp;id_corso=1049&amp;utente=S265060&amp;data=041020190849&amp;token=1c458be4cc1e5f810526bf8022de6620
"""Notes:
https://elearning.polito.it/gadgets/video/template_video.php?utente=<matricola>&inc=227523&data=041020190849&token=XXXXXXXXXXXXYYYYYYYZZZZZ

0) base_url for videopage is: base_url = "https://elearning.polito.it/gadgets/video/"
1) Search for: <ul class="lezioni">
2) Iterate over <li>
    <li><a href="template_video.php?id_lez=35050&amp;inc=227523&amp;f=1&amp;id_corso=1049&amp;utente=<matricola>&amp;data=041020190849&amp;token=XXXXXXXXXXXXYYYYYYYZZZZZ">2019_Lezione 01</a><br>&nbsp;&nbsp;<span style="font-size:10px;"> del&nbsp;2018-10-01</span></li>

3) Get href value

4) For each href value (aka lecture)
4a) Get the download link by searching in the <div id=content>
4b) Search for the needed quality download link
4c) start a thread to download that video

<div id="content"><h2>Download</h2><p>offline version (click con tasto dx sul file e salva con nome...)</p><ul>
        <li><a href="download.php?id=137809&amp;cidReq=2019_01SQMOV_0227523" id="video1">Video</a> </li>
              
                <li><a href="download.php?id=137811&amp;cidReq=2019_01SQMOV_0227523" id="video2">iPhone</a> </li>
              
                <li><a href="download.php?id=137810&amp;cidReq=2019_01SQMOV_0227523" id="video3">Audio</a> </li>
              
        
</ul>
</div>

"""

import datetime
import sys
import requests
from urllib.request import urlretrieve  # Needed for downoad
from bs4 import BeautifulSoup 
from threading import Thread
from threading import BoundedSemaphore
import os
import ssl # To fix certificate issue

thread_n = 4
sync = BoundedSemaphore(thread_n)


def hilite(string, status=False, bold=False):
    """If tty highligth the output."""

    if not sys.stdout.isatty():
        return string
    attr = []
    if status:
        attr.append('32')  # Green
    else:
        attr.append('31')  # Red
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)


def get_links(username, password):
    """Get video page download link.

    TODO: add filter by name, date, etc
    """
    
    base_url = "https://elearning.polito.it/gadgets/video/"
    # Start a new session, to preserve the cookie
    global s
    s = requests.session()
    # Take session 
    video_course_url = input("Insert the url of videolectures");
    t = s.get(video_course_url, verify=False)
    # The login POST payload
    login_payload = {
        'userID': username,
        'userPW': password
    }
    link_list = [];
    #try:
    l_response = s.post(video_course_url)
    print("Content response")
    if l_response.text.find("argoLink"):
        print(l_response.text)            
        soup = BeautifulSoup(l_response.text)
        video_list = soup.find('ul', {'class': 'lezioni'})
        for video_page_url in video_list.find_all('a'):
            if not 'javascript' in video_page_url.get("href"): 
                print(video_page_url.get("href")+"\n")
                link_list.append(base_url + video_page_url.get("href"))

    else:
        print(hilite("Authentication error for " + username))
                
    #except Exception as e:
    #    print(hilite("Exception for " + username+"\n"))
    #    print(e)
    return link_list

def download_page(video_page, folder_path):
    """Get video page download link.

    TODO: add filter by name, date, etc
    """
    
    base_url = "https://elearning.polito.it/gadgets/video/"
    # Take session     
    global s
    global sync    
    sync.acquire()
    #try:
    l_response = s.get(video_page, verify=False)
    print("Content videopage response")
    if "video-js-box" in l_response.text:
        #print(l_response.text)            
        soup = BeautifulSoup(l_response.text)
        download_list = soup.find('div', {'id': 'content'})
        for video_relative_url in download_list.find_all('a'):
            if 'video1' in video_relative_url.get("id"):  # video1: video, video2: iphone, video3: audio
                download_link = base_url + video_relative_url.get("href")
                ssl._create_default_https_context = ssl._create_unverified_context
                download_path = folder_path + "/" + soup.title.string + ".mp4";
                urlretrieve(download_link, download_path)
    sync.release()
    
def main():
    print(hilite("Polito Video Lectures Autodownloader " + username, status=True))  
    print(hilite("!!! NOTE: THIS SOFTWARE SHOULD BE USED FOR PERSONAL POURPOSE ONLY !!!", status=True))   
    print(hilite("**** Redistribution of videolectures can be punished by law ****", status=True))       
    global thread_n
    global sync
    # Get login data from file
    f = open("accounts.txt", 'r')
    for line in f.readlines():
        user, password = line.rstrip().split(":")
        print(hilite("User " + user + " data loaded!", True))
        todownload_list = get_links(user, password)
        
        # Create the folder (if not exist)
        folder_path = "./"+str("videolectures")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        else:
            "Dowloading also if the folder exists already!"
        
        for video_page in todownload_list:
            with sync:
                t = Thread(target=download_page, args=(video_page, folder_path))  # Page[0] is the n. of chapter
                t.start()

    print("Download completed: ", str(datetime.date.today()))

main()
