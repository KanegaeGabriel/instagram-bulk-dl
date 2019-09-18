import requests
import shutil
from sys import argv
import re

patternImg = '\"display_url\":'
patternVid = '\"video_url\":'
patternIsVideo = '\"is_video\":'

def writeToFile(filename, filecontent):
    with open(filename, 'wb') as f:
        filecontent.raw.decode_content = True
        shutil.copyfileobj(filecontent.raw, f)

def downloadFromList(urlList):
    urlList = list(set(urlList)) # Remove URL duplicates
    urlList.sort()

    errors = []

    current = 0
    total = len(urlList)
    for url in urlList:
        current += 1

        try:
            response = requests.get(url)
            html = str(response.text)

            allImg = [m.start(0) for m in re.finditer(patternImg, html)]
            allVid = [m.start(0) for m in re.finditer(patternVid, html)]
            
            imgList = []
            vidList = []

            for i in allImg: # Finding all images
                s = i + len(patternImg) + 1
                e = s + re.search("\",", html[s:s+300]).end() - 2

                isVideo = s + re.search(patternIsVideo, html[s:s+3000]).end()
                if html[isVideo:isVideo+4] != "true":
                    imgList.append(html[s:e])

            for i in allVid: # Finding all videos
                s = i + len(patternVid) + 1
                e = s + re.search("\",", html[s:s+300]).end() - 2
                vidList.append(html[s:e])

            # Remove first image as it's a duplicate (thumbnail)
            if len(imgList) > 1:
                imgList.pop(0)

            countTotal = len(imgList) + len(vidList)
            countCurrent = 0

            if countTotal < 1:
                raise Exception("Empty page?")
            
            print("[{}/{}] {}".format(current, total, url))

            for img in imgList: # Downloading all images
                countCurrent += 1
                filename = img.split("/")[-1].split("?")[0]

                img = img.replace("\\u0026", "&") # TODO Fix encoding
                fileContent = requests.get(img, stream=True)
                writeToFile(filename, fileContent)

                print("\t[{}/{}] {}".format(countCurrent, countTotal, filename))

            for vid in vidList: # Downloading all videos
                countCurrent += 1
                filename = vid.split("/")[-1].split("?")[0]

                vid = vid.replace("\\u0026", "&") # TODO Fix encoding
                fileContent = requests.get(vid, stream=True)
                writeToFile(filename, fileContent)

                print("\t[{}/{}] {}".format(countCurrent, countTotal, filename))
        except Exception as e:
            errors.append(url) # Error raised, append to error array
            print("[{}/{}] [ERROR] {}".format(current, total, url))
            print("\t{}".format(e))

    print()
    print("Finished.")

    if len(errors) < 1:
        print("All links successfully downloaded.")
    else:
        print("Errors (might be private accounts):")
        for e in errors:
            print(e)

def main():
    filename = argv[1] if len(argv) > 1 else "list.txt"
    
    try:
        with open(filename) as f:
            urlList = [i.strip().split("?")[0] for i in f.readlines()]
    except FileNotFoundError:
        print("File '{}' not found. Exiting...".format(filename))
        return

    downloadFromList(urlList)

if __name__ == "__main__":
    main()