import re,json
import requests
import base64
from urllib.parse import unquote, urlparse, parse_qs
import time
import cloudscraper
from bs4 import BeautifulSoup
import hashlib

GDTOT_CRYPT="K0ZMaXFuTFYybkRqTktmVlBPVUxFQ3ROKzBSQW1LQml5TndwTGg4LzVFcz0%3D"
#_________________________________________________________________________________________________#
# Gdtot -->
def gdtot(url: str, GDTot_Crypt=GDTOT_CRYPT) -> str:
    client = requests.Session()
    client.cookies.update({"crypt": GDTot_Crypt})
    res = client.get(url)
    base_url = re.match('^.+?[^\/:](?=[?\/]|$\n)', url).group(0)
    res = client.get(f"{base_url}/dld?id={url.split('/')[-1]}")
    url = re.findall(r'URL=(.*?)"', res.text)[0]
    info = {}
    info["error"] = False
    params = parse_qs(urlparse(url).query)
    if "gd" not in params or not params["gd"] or params["gd"][0] == "false":
        info["error"] = True
        if "msgx" in params:
            info["message"] = params["msgx"][0]
        else:
            info["message"] = "Invalid link"
    else:
        decoded_id = base64.b64decode(str(params["gd"][0])).decode("utf-8")
        drive_link = f"https://drive.google.com/open?id={decoded_id}"
        info["gdrive_link"] = drive_link
    if not info["error"]:
        return info["gdrive_link"]
    else:
        return f"{info['message']}"
   
#_______________________________________________________________________#
# Shortlingly -->
def shortlingly(url):
    client = cloudscraper.create_scraper(allow_brotli=False)
    if 'shortingly.me' in url:
        DOMAIN = "https://go.gyanitheme.com"
    else:
        return "Incorrect Link"
    url = url[:-1] if url[-1] == '/' else url
    code = url.split("/")[-1] 
    final_url = f"{DOMAIN}/{code}"
    resp = client.get(final_url)
    soup = BeautifulSoup(resp.content, "html.parser") 
    try: inputs = soup.find(id="go-link").find_all(name="input")
    except: return "Incorrect Link"
    data = { input.get('name'): input.get('value') for input in inputs }
    h = { "x-requested-with": "XMLHttpRequest" }
    time.sleep(5)
    r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
    try:
        return r.json()['url']
    except: return "Something went wrong :("
    
#______________________________________________________________________________________________________________#
# Gofile -->
#https://gofile.io/d/0E9BRu
def gofile_dl(url,password=""):
    api_uri = 'https://api.gofile.io'
    client = requests.Session()
    res = client.get(api_uri+'/createAccount').json()
    
    data = {
        'contentId': url.split('/')[-1],
        'token': res['data']['token'],
        'websiteToken': '12345',
        'cache': 'true',
        'password': hashlib.sha256(password.encode('utf-8')).hexdigest()
    }
    res = client.get(api_uri+'/getContent', params=data).json()

    content = []
    for item in res['data']['contents'].values():
        content.append(item)
    
    return {
        'accountToken': data['token'],
        'files': content
    }["files"][0]["link"]
    
#______________________________________________________________________________________________________________#
# Anonfile -->
#https://anonfiles.com/t4p5G2M1yb/ffmconcat_txt
def anonfile(url):
    headersList = { "Accept": "*/*"}
    payload = ""
    response = requests.request("GET", url, data=payload,  headers=headersList).text.split("\n")
    for ele in response:
        if "https://cdn" in ele and "anonfiles.com" in ele and url.split("/")[-2] in ele:
            break

    return ele.split('href="')[1].split('"')[0]
    
#________________________________________________________________________________________________________________#
# Zippyshare
#https://www49.zippyshare.com/v/xhsI32c7/file.html

def zippyshare(url):
    resp = requests.get(url).text
    surl = resp.split("document.getElementById('dlbutton').href = ")[1].split(";")[0]
    parts = surl.split("(")[1].split(")")[0].split(" ")
    val = str(int(parts[0]) % int(parts[2]) + int(parts[4]) % int(parts[6]))
    surl = surl.split('"')
    burl = url.split("zippyshare.com")[0]
    furl = burl + "zippyshare.com" + surl[1] + val + surl[-2]
    return furl
    
#_________________________________________________________________________________________________________________#
# Mediafire
#https://www.mediafire.com/file/am4amdxuzty4lu0/book.txt/file

def mediafire(url):
    res = requests.get(url, stream=True)
    contents = res.text

    for line in contents.splitlines():
        m = re.search(r'href="((http|https)://download[^"]+)', line)
        if m:
            return m.groups()[0]

#_________________________________________________________________________________________________________________#
#tnlink
def tnlink(url):    
    client = cloudscraper.create_scraper(allow_brotli=False)
    DOMAIN = "https://gadgets.usanewstoday.club"
    url = url[:-1] if url[-1] == '/' else url
    code = url.split("/")[-1]
    final_url = f"{DOMAIN}/{code}"
    ref = "https://usanewstoday.club/"
    h = {"referer": ref}
    resp = client.get(final_url,headers=h)
    soup = BeautifulSoup(resp.content, "html.parser")
    inputs = soup.find_all("input")
    data = { input.get('name'): input.get('value') for input in inputs }
    h = { "x-requested-with": "XMLHttpRequest" }
    time.sleep(8)
    r = client.post(f"{DOMAIN}/links/go", data=data, headers=h)
    try:
        return r.json()['url']
    except: return "Something went wrong :("
