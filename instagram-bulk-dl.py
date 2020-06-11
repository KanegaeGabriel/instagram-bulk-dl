from time import time
from sys import argv
import requests
import shutil
import json
import re

def writeToFile(filename, filecontent):
    with open(filename, "wb") as f:
        filecontent.raw.decode_content = True
        shutil.copyfileobj(filecontent.raw, f)

    return

jsonPattern = re.compile('(?:<script type="text\/javascript">window\._sharedData *= *)(.*)(?:; *<\/script>)')
t0 = time()

if len(argv) < 2:
    print("  Usage: python3 {} (url_1) [url_2] ... [url_n]".format(argv[0]))
    exit()

urls = [url.rstrip("/") for url in argv[1:]]
mediaAmt = len(urls)

errors = []

for i, url in enumerate(urls):
    mediaCode = url.split("/")[-1]

    if "/" not in url:
        url = "https://www.instagram.com/p/" + url

    print("[{}/{}] {}".format(i+1, mediaAmt, mediaCode))
    
    # Get HTML
    response = requests.get(url)
    if response.status_code != 200:
        print("  [ERROR] {} ({})".format(response.status_code, url))
        errors.append(url)
        continue

    # Get window._sharedData from HTML
    try:
        match = re.search(jsonPattern, response.text)
        jsonObject = match.group(1)
        jsonObject = json.loads(jsonObject)
    except Exception as e:
        print("    [ERROR] JSON ({})".format(e))
        errors.append(url)
        continue

    # Handle multiple pictures/videos
    media = jsonObject["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]
    if "edge_sidecar_to_children" in media:
        media = [m["node"] for m in media["edge_sidecar_to_children"]["edges"]]
    else:
        media = [media]

    # Download all files
    error = False
    subMediaAmt = len(media)
    for i, m in enumerate(media):
        subMediaCode = m["shortcode"]
        mediaURL = m["video_url"] if m["is_video"] else m["display_url"]

        filename = mediaURL.split("?")[0].split("/")[-1]

        print("  [{}/{}] {} ({})".format(i+1, subMediaAmt, subMediaCode, filename))

        fileContent = requests.get(mediaURL, stream=True)

        if fileContent.status_code != 200:
            print("    [ERROR] {} ({})".format(fileContent.status_code, mediaURL))
            error = True
            continue

        writeToFile(filename, fileContent)
    
    if error:
        errors.append(url)

print()
print("{}/{} URLs successfully downloaded in {:.2f}s.".format(len(urls)-len(errors), len(urls), time()-t0))
if errors:
    print("Errors (e.g. connection error, private account):".format(len(errors)))
    for error in errors:
        print("  {}".format(error))