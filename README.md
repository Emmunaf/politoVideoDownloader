# politoVideoDownloader
A simple python script to download (in bulk) all the video lectures available for a course

# Usage
python3 poliVideoDownload.py

# How to get the videocourse url?
- Go to the page named "Materiale" (you can find it in the top bar) and scroll until you get "Materiale disponibile"
- Follow the istructions in the video
![](instructions.gif)
- Copy the url in the address bar and paste it when the software ask for it

# Where will the lectures be saved?
For now you can't customize the download location.
You can find the downloaded videos in the "videolectures" folder that will be created in the current folder (where the script was launched)

# TODOs

- [ ] Filter by title, date, etc
- [ ] Choose which type of video is needed (video, iphone, audio only)
- [ ] Customization of #thread (max concurrent downloads)
- [ ] Support a syncronization option (download just the missing lectures)
