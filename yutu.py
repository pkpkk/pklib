import argparse
from json import loads as jsnloads,dumps as jsndumps
from functools import partial
from yt_dlp import YoutubeDL 


def myhook(p,d):
  if d['status']=='finished':
    p.stream_files['_file']=d.get('info_dict').get('_filename')

def hbs(size):
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "B", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


 

class Ytube:
  def __init__(self,url):
    self.url=url 
    self.ytinfo=None
    self.formats=None 
    self.audios=None 
    self.videos=None 
    self.progressive=None
    self.stream_files={}
    self.my_hook=partial(myhook,self)
    self.aud=[32,48,64,96,128,160,192,224,256,320]
    self.suitable_aud_res={'144p':32,'240p':[22,32,48],'360p':[32,48,64],'480p':[48,64,96],'720p':[64,96,128],'1080p':[96,128,160],'1440p':[128,160,192],'2160p':[160,192,224]}
  def extract_info(self):
    info=YoutubeDL().extract_info(self.url,download=False)
    self.ytinfo=ytinfo(info)
  @property 
  def best_audio(self):
    if not self.audios:
      self.do_formats()
    rt,tr=[],{}
    for i in self.audios:
      rt.append(i.abr)
      tr[i.abr]=i 
    return tr.get(max(rt))
  @property 
  def worst_audio(self):
    if not self.audios:
      self.do_formats()
    rt,tr=[],{}
    for i in self.audios:
      rt.append(i.abr)
      tr[i.abr]=i 
    return tr.get(min(rt))
  def do_formats(self):
    self.extract_info()
    self.formats=self.ytinfo.formats if self.ytinfo.formats else self.ytinfo.formats_
    self.audios=[]
    self.videos=[]
    self.progressive=[]
    for i in self.formats:
      if i.is_audio_only:
        self.audios.append(i)
      elif i.is_video_only:
        self.videos.append(i)
      else:
        self.progressive.append(i)
  def find_a_qual(self,bit_rate):
    bit_rate=round(bit_rate)
    tr,rt,rtt=[22,32,48,64,96,128,160,192,224,256],{},[]
    for i in tr:
      rtt.append(abs(bit_rate-i))
      rt[abs(bit_rate-i)]=i
    return rt.get(min(rtt))
  def find_audio_bt_rate(self,bt_rate):
    aud=[]
    for i in self.audios:
      if (self.find_a_qual(i.abr)==bt_rate):
        aud.append(i)
    return aud
  def find_video_res(self,res:str):
    vid=[]
    for i in self.videos:
      if res in i.format_note:
        vid.append(i)
      elif res in i.format_d:
        vid.append(i)
    for i in self.progressive:
      if res in i.format_note:
        vid.append(i)
      elif res in i.format_d:
          vid.append(i)
    if  len(vid)==0:
      raise Exception('No requested resolution found')
    return vid
  def download_stream(self,streams:list):
    f_ormat=''
    for i in streams:
      f_ormat+=f'{i.format_id}+'
    opts={'quiet':True,'overwrites':False,'format':f_ormat[:-1],'outtmpl':f'%(title)s.%(ext)s','writesubtitles':True,'writeautomaticsub':True,'restrictfilenames': True,'subtitleslangs':['en','en-US','en-IN','en-UK'],'allow_multiple_audio_streams':True,'ignoreerrors':True,'progress_hooks':[self.my_hook],'postprocessors':[{'key':'FFmpegEmbedSubtitle'}]}
    with YoutubeDL(opts) as ydl:
      ydl.download(self.url)
    return self.stream_files.get('_file')
  def find_suitable_aud(self,video_stream):
    if len(self.audios)!=0:
      if (video_stream.is_video_only and video_stream.is_dash):
        if video_stream.format_note=='144p':
          return self.worst_audio
        suit_a=self.suitable_aud_res.get(video_stream.format_note)
        a2=self.find_audio_bt_rate(suit_a[0])
        if len(a2)!=0:
          return a2[0]
        else:
          a2=self.find_audio_bt_rate(suit_a[1])
          if len(a2)!=0:
            return a2[0]
          else:
            a2=self.find_audio_bt_rate(suit_a[2])
            if len(a2)!=0:
              return a2[0]
            else:
              return self.audios[0]
  def download_by_resolution(self,res):
    '''To download video and audio files together in one file by resolution e.g., 480p '''
    try:
      vid=self.find_video_res(res)[0]
      if vid.is_dash:
        aud=self.find_suitable_aud(vid)
        if aud is not None:
          return self.download_stream([vid,aud])
        else:
          return self.download_stream([vid])
      else:
        return self.download_stream([vid])
    except Exception as e:
      print(e)
      return None

#opts={'quiet':True,'format':self.format_id,'outtmpl':f'{tmp_dir}/%(title)s.%(ext)s','writesubtitles':True,'restrictfilenames': True,'subtitleslangs':['en','en-US','en-IN','en-UK'],'geo_bypass': True,'geo_bypass_country': 'IN','postprocessors':[{'key':'FFmpegEmbedSubtitle'}]}
# opts={'format':self.format_id,'outtmpl':f'{tmp_dir}/%(title)s.%(ext)s','writesubtitles':True,'subtitleslangs':['en','en-US','en-IN','en-UK'],'postprocessors':[{'key':'FFmpegEmbedSubtitle'}]}


class ytinfo:
  def __init__(self,info:dict):
    self.id=info.get('id')
    self.title=info.get('title')
    self.thumbnail=info.get('thumbnail')
    self.duration=info.get('duration')
    self.view_count=info.get('view_count')
    self.webpage_url=info.get('webpage_url')
    self.duration_string=info.get('duration_string')
    self.fmt___=info.get('formats')
    self.formats=None
    self.subtitles=info.get('subtitles').keys()
    self.has_subtitles=True if (len(info.get('subtitles').keys())>0) else False
  @property 
  def formats_(self):
    ii=[]
    for ent in self.fmt___:
      if ent.get('container'):
        st=ytstream(ent,self.webpage_url)
        if st.format_id.startswith('sb'):
          del st 
        else:
          ii.append(st) 
    self.formats=ii
    self.fmt___=None
    return ii


class ytstream:
  def __init__(self,fmt:dict,url:str):
    self.url=url
    self.format_id=fmt.get('format_id')
    self.format_d=fmt.get('format')
    self.format_note=fmt.get('format_note')
    self.container=fmt.get('container')
    self.abr=fmt.get('abr')
    self.vbr=fmt.get('vbr')
    self.tbr=fmt.get('tbr')
    self.filesize=fmt.get('filesize')
    self.filesize_readable=hbs(fmt.get('filesize'))
    self.acodec=fmt.get('acodec')
    self.vcodec=fmt.get('vcodec')
    self.fps=fmt.get('fps')
    self.resolution=fmt.get('resolution')
    self.is_dash=True if ('dash' in fmt.get('container')) else False
  def __repr__(self):
    return f'[{self.format_d}-{self.container}-{hbs(self.filesize)}]'
  @property
  def is_video_only(self):
    if self.is_dash:
      if ((self.acodec=='none') and (self.vcodec!='none')) :
        return True
      elif (self.vbr and not self.abr):
        return True
      else:
        return False
    else:
      return False
  @property
  def is_audio_only(self):
    if self.is_dash:
      if ((self.vcodec=='none') and (self.acodec!='none')) :
        return True
      elif (self.abr and not self.vbr):
        return True
      else:
        return False
    else:
      return False

def main():
  parser=argparse.ArgumentParser()
  parser.add_argument('-a','--audio-only',action='store_true',help='Specify to download only url')
  parser.add_argument('url',help='provide url to download url')
  parser.add_argument('-vq','--video-quality',type=str, choices=['144p','240p','360p','480p','720p','1080p','1440p','2160p'],help='Provide video resolution like 480p or so')
  parser.add_argument('-aq','--audio-bitrate',type=int, choices=[32,48,64,96,128,160,192,224,256,320],help='Provide audio bitrate in kbps to download such as 128')
  parser.add_argument('-F','--formats',action='store_true',help='Specify to print Formats')
  argsp=parser.parse_args()
  if argsp.formats:
    yt=Ytube(argsp.url)
    yt.do_formats()
    for i in yt.formats:
      print(i)
  if argsp.audio_only:
    yt=Ytube(argsp.url)
    yt.do_formats()
    if argsp.audio_bitrate:
      file=yt.download_stream(yt.find_audio_bt_rate(argsp.audio_bitrate))
      print(file)
    else:
      file=yt.download_stream([yt.best_audio])
      print(file)
  if argsp.video_quality:
    yt=Ytube(argsp.url)
    yt.do_formats()
    if argsp.audio_bitrate:
      streams=[yt.find_video_res(argsp.video_quality)[0]]
      if streams[0].is_dash:
        aud=argsp.audio_bitrate
        aud=yt.find_audio_bt_rate(aud)
        if len(aud)!=0:
          streams.append(aud[0])
          file=yt.download_stream(streams)
        else:
          file=yt.download_by_resolution(argsp.video_quality)
      else:
        file=yt.download_stream(streams)
    else:
      file=yt.download_by_resolution(argsp.video_quality)
    print(file)
    
if __name__=='__main__':
  try:
    main() 
  except Exception as e:
    print(e)