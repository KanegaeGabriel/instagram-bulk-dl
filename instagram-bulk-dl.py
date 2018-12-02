from urllib.request import urlopen
from sys import argv
import re

patternImg = '\"display_url\":'
patternVid = '\"video_url\":'
patternIsVideo = '\"is_video\":'

filename = argv[1] if len(argv) > 1 else "list.txt"
try:
    with open(filename) as f:
        urlList = [i.strip().split("?")[0] for i in f.readlines()]
except FileNotFoundError:
    print("File '{}' not found. Exiting...".format(filename))
    exit()

urlList = list(set(urlList)) # Remove URL duplicates
urlList.sort()

errors = []

current = 0
total = len(urlList)
for url in urlList:
    current += 1

    try:
        response = urlopen(url)
        html = response.read().decode('UTF-8')

        allImg = [m.start(0) for m in re.finditer(patternImg, html)]
        allVid = [m.start(0) for m in re.finditer(patternVid, html)]
        
        imgList = []
        vidList = []

        for i in allImg: # Finding all images
            s = i + len(patternImg) + 1
            e = s + re.search(".jpg", html[s:s+200]).end()

            isVideo = s + re.search(patternIsVideo, html[s:s+3000]).end()
            if html[isVideo:isVideo+4] != "true":
                imgList.append(html[s:e])

        for i in allVid: # Finding all videos
            s = i + len(patternVid) + 1
            e = s + re.search(".mp4", html[s:s+200]).end()
            vidList.append(html[s:e])

        # Remove first image as it's a duplicate (thumbnail)
        if len(imgList) > 1:
            imgList.pop(0)

        totalSub = len(imgList) + len(vidList)
        currentSub = 0

        if totalSub < 1:
            raise Exception("Empty page?")
        elif totalSub > 1:
            print("[{}/{}]    {}".format(current, total, url))

        for img in imgList: # Downloading all images
            currentSub += 1
            filename = img.split("/")[-1]
            f = open(filename, 'wb')
            f.write(urlopen(img).read())
            f.close()

            if totalSub > 1:
                print("\t[{}/{}]    ({})".format(currentSub, totalSub, filename))
            else:
                print("[{}/{}]    {} ({})".format(current, total, url, filename))

        for video in vidList: # Downloading all videos
            currentSub += 1
            filename = video.split("/")[-1]
            f = open(filename, 'wb')
            f.write(urlopen(video).read())
            f.close()

            if totalSub > 1:
                print("\t[{}/{}]    ({})".format(currentSub, totalSub, filename))
            else:
                print("[{}/{}]    {}    ({})".format(current, total, url, filename))
    except:
        print("[{}/{}]    [ERROR] {}".format(current, total, url))
        errors.append(url) # Error raised, append to error array

print("Finished.")

if len(errors) < 1:
    print("All links successfully downloaded.")
else:
    print()
    print("Errors (might be private accounts?):")
    for e in errors:
        print(e)