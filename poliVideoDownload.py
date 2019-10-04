#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""poliVideoDownload.py: A client for video download automatizazion 


Requirements:
    pip install bs4
    pip install requests 
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


def get_links():
    """Get video page download link.

    TODO: add filter by name, date, etc
    """
    
    base_url = "https://elearning.polito.it/gadgets/video/"
    # Start a new session, to preserve the cookie
    global s
    s = requests.session()
    # Take session 
    video_course_url = input("Insert the url of videolectures:\n");
    t = s.get(video_course_url, verify=False)
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
        print(hilite("Error "))
                
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
    print(hilite("Polito Video Lectures Autodownloader ", status=True))  
    print(hilite("!!! NOTE: THIS SOFTWARE SHOULD BE USED FOR PERSONAL POURPOSE ONLY !!!", status=True))   
    print(hilite("**** Redistribution of videolectures can be punished by law ****", status=True))      
    print("Instructions:\n1) Go to 'Materiale'\n2) Go to 'Materiale Didattico disponibile'\n3) Go to 'Lezioni online'\n4) Click on your section (Primo anno, secondo anno, ..., Magistrale)\n5) Click on your interested course \n6) When the page is loaded, just copy the url from the address bar\n\n")
    print(hilite("To be sure you can check that the url begins with 'https://elearning.polito.it/gadgets/video/'"))
    global thread_n
    global sync
    # Get login data from file
    todownload_list = get_links()
    
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

"""Notes:
https://elearning.polito.it/gadgets/video/template_video.php?utente=<matricola>&inc=227523&data=041020190849&token=XXXXXXXXXXXXYYYYYYYZZZZZ

0) base_url for videopage is: base_url = "https://elearning.polito.it/gadgets/video/"
1) Search for: <ul class="lezioni">
2) Iterate over <li>
    <li><a href="template_video.php?id_lez=<idlezione>&amp;inc=227523&amp;f=1&amp;id_corso=<idcorso>&amp;utente=<matricola>&amp;data=041020190849&amp;token=XXXXXXXXXXXXYYYYYYYZZZZZ">2019_Lezione 01</a><br>&nbsp;&nbsp;<span style="font-size:10px;"> del&nbsp;2018-10-01</span></li>

3) Get href value

4) For each href value (aka lecture)
4a) Get the download link by searching in the <div id=content>
4b) Search for the needed quality download link
4c) start a thread to download that video

<div id="content"><h2>Download</h2><p>offline version (click con tasto dx sul file e salva con nome...)</p><ul>
        <li><a href="download.php?id=..&amp;cidReq=.." id="video1">Video</a> </li>
              
                <li><a href="download.php?id=..&amp;cidReq=.." id="video2">iPhone</a> </li>
              
                <li><a href="download.php?id=..&amp;cidReq=.." id="video3">Audio</a> </li>
              
        
</ul>
</div>

TODO: 
    filter by title, date, etc
    choose wich type of video is needed (video, iphone, audio only)
    customization of #thread 
    support the other type of videolectures
"""

