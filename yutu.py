import argparse,re
from json import loads as jsnloads,dumps as jsndumps
from functools import partial
from yt_dlp import YoutubeDL 
from os import mkdir,getcwd
from os.path import abspath,isdir,isfile,exists,dirname,basename,join as osjoin,getsize
from os import getcwd,chdir,rename,remove as osremove
import time,re
from random import randint
from shutil import rmtree as srmtree


class progress:
  def __init__(self,pdict:dict):
    for k,v in pdict.items():
      self.__setattr__(k,v)



def myhook(p,d):
  if d['status']=='finished':
    p.stream_files['_file']=d.get('info_dict').get('_filename') 
  p.pdict['_speed_str']=d.get('_speed_str')
  p.pdict['_total_bytes_str']=d.get('_total_bytes_str')
  p.pdict['_elapsed_str']=d.get('_elapsed_str')
  p.pdict['_percent_str']=d.get('_percent_str')
  p.pdict['downloaded']=hbs(d.get('downloaded_bytes'))
  p.progress=progress(p.pdict)











"""
7.83KiB/sdict_keys(['downloaded_bytes', 'total_bytes', 'filename', 'status', 'elapsed', 'ctx_id', 'max_progress', 'progress_idx', 'info_dict', 'speed', '_speed_str', '_total_bytes_str', '_elapsed_str', '_percent_str', '_default_template'])
'VIDEO_10s_kt2D7xl06mk.mp4'"""
def make_safe_filename(filename):
    filename = re.sub(r'[^\w\s\.]', '', filename)
    filename = re.sub(r'\s+', ' ', filename).strip()
    MAX_FILENAME_LENGTH = 245 #255
    filename = filename[:MAX_FILENAME_LENGTH]
    RESERVED_NAMES = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1', 'LPT2', 'LPT3', 'CLOCK$']
    if filename.upper() in RESERVED_NAMES:
        filename='DefaultName'
    return filename 

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



class lzp:
  def remove(file_or_directory):
    """To remove a file or directory"""
    if isfile(file_or_directory):
      osremove(file_or_directory) 
    elif isdir(file_or_directory):
      srmtree(file_or_directory)
  def rename(file,new_name,safe=False):
    if dirname(file)==dirname(new_name):
      if file!=new_name:
        rename(file,new_name)
    else:
      new_name=osjoin(dirname(file),basename(new_name))
      if file!=new_name:
        rename(file,new_name)
  def makdir(dir_):
    """make directory and return created directory"""
    if not isdir(dir_):
      try:
        mkdir(dir_)
        return dir_
      except Exception:
        dir_=make_safe_filename(dir_)
        if not isdir(dir_):
          mkdir(dir_)
          return dir_ 
        else:
          dir_+=str(time.time())
          mkdir(dir_) 
          return dir_ 
    else:
      dir_+=str(time.time())
      dir_=make_safe_filename(dir_) 
      mkdir(dir_ )
      return dir_ 
 
 

class Ytube:
  def __init__(self,url):
    self.url=url 
    self.id=None 
    self.title=None 
    self.duration=None 
    self.duration_string=None 
    self.thumbnail=None 
    self.has_subtitles=None 
    self.subtitles=None
    self.ytinfo=None
    self.pdict={}
    self.formats=None 
    self.audios=None 
    self.videos=None 
    self.progressive=None
    self.stream_files={}
    self.my_hook=partial(myhook,self)
    self.aud=[22,32,48,64,96,128,160,192,224,256,320]
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
    self.id=self.ytinfo.id 
    self.title=self.ytinfo.title 
    self.duration=self.ytinfo.duration 
    self.duration_string=self.ytinfo.duration_string 
    self.thumbnail=self.ytinfo.thumbnail
    self.has_subtitles=self.ytinfo.has_subtitles 
    self.subtitles=self.ytinfo.subtitles
  def find_a_qual(self,bit_rate):
    bit_rate=round(bit_rate)
    tr,rt,rtt=[22,32,48,64,96,128,160,192,224,256],{},[]
    for i in tr:
      rtt.append(abs(bit_rate-i))
      rt[abs(bit_rate-i)]=i
    return rt.get(min(rtt))
  def find_audio_bt_rate(self,bt_rate):
    if not self.ytinfo:
      self.do_formats()
    aud=[]
    for i in self.audios:
      if (self.find_a_qual(i.abr)==bt_rate):
        aud.append(i)
    return aud
  def find_video_res(self,res:str):
    if not self.ytinfo:
      self.do_formats()
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
  def download_stream(self,streams:list,output_folder=None):
    if not self.ytinfo:
      self.do_formats()
    f_ormat=''
    for i in streams:
      f_ormat+=f'{i.format_id}+'
    opts={'quiet':True,'overwrites':False, 'noplaylist':True,'format':f_ormat[:-1],'outtmpl':f'%(title)s_%(id)s.%(ext)s','writesubtitles':True,'writeautomaticsub':True,'restrictfilenames': True,'subtitleslangs':['en','en-US','en-IN','en-UK'],'allow_multiple_audio_streams':True,'ignoreerrors':True,'progress_hooks':[self.my_hook],'postprocessors':[{'key':'FFmpegEmbedSubtitle'}]}
    if output_folder:
      if output_folder.endswith('/'):
        output_folder=output_folder[:-1]
      opts['outtmpl']=f'{output_folder}/%(title)s_[%(id)s].%(ext)s'
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
  def download_by_resolution(self,res,out_fol=None):
    if not self.ytinfo:
      self.do_formats()
    '''To download video and audio files together in one file by resolution e.g., 480p ''' 
    print(f'Trying to download --> {self.title}, Requested resolution: {res}')
    try:
      vid=self.find_video_res(res)[0]
      if vid.is_dash:
        aud=self.find_suitable_aud(vid)
        if aud is not None:
          return self.download_stream([vid,aud],output_folder=out_fol)
        else:
          return self.download_stream([vid,self.audios[0]],output_folder=out_fol)
      else:
        return self.download_stream([vid],output_folder=out_fol)
    except Exception as e:
      print(e)
      return None

#opts={'quiet':True,'format':self.format_id,'outtmpl':f'{tmp_dir}/%(title)s.%(ext)s','writesubtitles':True,'restrictfilenames': True,'subtitleslangs':['en','en-US','en-IN','en-UK'],'geo_bypass': True,'geo_bypass_country': 'IN','postprocessors':[{'key':'FFmpegEmbedSubtitle'}]}
# opts={'format':self.format_id,'outtmpl':f'{tmp_dir}/%(title)s.%(ext)s','writesubtitles':True,'subtitleslangs':['en','en-US','en-IN','en-UK'],'postprocessors':[{'key':'FFmpegEmbedSubtitle'}]}
class subt__: 
  def __init__(self,name,sub_):
    self.name=name 
    self.language=sub_[-1].get('name')
    self.url=sub_[-1].get('url') 
    self.ext=sub_[-1].get('ext')
  def __repr__(self):
    return f'<--{self.name}:{self.language}-->'
    
class subt:
  def __init__(self,sub): 
    self.subtitles=[] 
    for k,v in sub.items(): 
      self.subtitles.append(subt__(k,v))






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
    self.subtitles=subt(info.get('subtitles')).subtitles
    self.subtitles_dict=info.get('subtitles')
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

#https://m.youtube.com/watch?v=cdGuVTniKZ0&list=PLgWvG81FnMvjF6sYc2SKrCtjYPr85A05a

class Ytlist:
  def __init__(self,playlist_url):
    if ('watch?v' in playlist_url) and ('&list=' in playlist_url):
      self.url=f'https://youtube.com/playlist?list={playlist_url.split("&list=")[-1]}' 
    else:
      self.url=playlist_url
    self.entries=[]
    self.urls_of_all_videos=[]
    self.playlist_count=None
    self.id=None 
    self.title=None
    self.webpage_url=None 
    self.uploader=None 
    self.uploader_url=None 
    self.uploader_id=None
    self.channel=None 
    self.channel_url=None 
    self.channel_id=None
    self.pk_opts={'skip_download':True,'extract_flat':True}
  def extract_info(self):
    with YoutubeDL(self.pk_opts) as ydl:
      e=ydl.extract_info(self.url, download=False)
      self.id=e.get('id')
      self.title=make_safe_filename(e.get('title'))
      self.webpage_url=e.get('webpage_url') 
      self.playlist_count=e.get('playlist_count') 
      self.uploader=e.get('uploader')
      self.uploader_url=e.get('uploader_url')
      self.uploader_id=e.get('uploader_id')
      self.channel=e.get('channel')
      self.channel_url=e.get('channel_url')
      self.channel_id=e.get('channel_id')
      for i in e.get('entries'):
        i['playlist_url']=self.url 
        i['playlist_title']=self.title
        self.entries.append(YtlistVid(i))
      for i in e.get('entries'):
        self.urls_of_all_videos.append(i.get('url'))
  def download_all_videos_by_resolution(self,res,out_fol=None,alt=None):
    """download all videos by resolution returns a dict containing files_list, dirrctory, no of successful and failed downloads 
    pass alt='some resolution' to download alternate resolution for videos which does not have requested resolution 
    do this to reduce no. of failed downloads"""
    downloaded_bytes=0
    if not (self.id or self.webpage_url):
      self.extract_info()
    if not out_fol:
      out_fol=self.title
    out_fol=lzp.makdir(out_fol)
    out_fol=abspath(out_fol)
    files=[]
    downloaded,failed=0,0
    for urls in self.urls_of_all_videos:
      file=Ytube(urls).download_by_resolution(res=res,out_fol=out_fol)
      if file:
        print('Downloaded ✓',file)
        downloaded+=1
        downloaded_bytes+=getsize(file)
        files.append(file)
      else: 
        if alt: 
          file=Ytube(urls).download_by_resolution(res=alt,out_fol=out_fol)
          if file:
            print('Downloaded ✓',file)
            downloaded+=1
            downloaded_bytes+=getsize(file)
            files.append(file)
          else: 
            failed+=1
        else: 
          failed+=1
    print(f'Downloaded {downloaded} videos of {self.playlist_count}.\nDirectory containing files: {out_fol}\n\n')
    return {'output_folder':out_fol,'files_list':files,'downloaded':downloaded,'failed':failed,'total':self.playlist_count,'size_downloaded':hbs(downloaded_bytes)}





class YtlistVid:
  def __init__(self,info:dict):
    self.id=info.get('id')
    self.url=info.get('url')
    self.title=make_safe_filename(info.get('title'))
    self.duration=info.get('duration')
    self.channel=info.get('channel')
    self.channel_id=info.get('channel_id')
    self.channel_url=info.get('channel_url') 
    self.playlist_url=info.get('playlist_url')
    self.playlist_title=info.get('playlist_title')
  def __repr__(self):
    return f'<-YtlistVid:{title[20:]}__{self.channel}->'

def main():
  parser=argparse.ArgumentParser()
  parser.add_argument('-a','--audio-only',action='store_true',help='Specify to download only url')
  parser.add_argument('url',help='provide url to download url')
  parser.add_argument('-vq','--video-quality',type=str, choices=['144p','240p','360p','480p','720p','1080p','1440p','2160p'],help='Provide video resolution like 480p or so')
  parser.add_argument('-aq','--audio-bitrate',type=int, choices=[32,48,64,96,128,160,192,224,256,320],help='Provide audio bitrate in kbps to download such as 128')
  parser.add_argument('-F','--formats',action='store_true',help='Specify to print Formats')
  parser.add_argument('-p','--playlist',action='store_true',help='Specify to download whole playlist') 
  parser.add_argument( '-alt','--alternate-video-resolution',type=str, choices=['144p','240p','360p','480p','720p','1080p','1440p','2160p'],help='Provide alternate video resolution to reduce no. of failed downloads while downloading playlist.')
  argsp=parser.parse_args()
  is_playlist=argsp.playlist if argsp.playlist else None 
  if not is_playlist:
    if ('watch?v' in argsp.url) and ('&list=' in argsp.url):
      is_playlist=False
      print('pass -p to download playlist')
    elif 'playlist?list=' in argsp.url: 
      is_playlist=True 
    else: 
      is_playlist=False
  if not is_playlist:
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
  elif is_playlist: 
    alt= argsp.alternate_video_resolution if argsp.alternate_video_resolution else None
    if argsp.video_quality:
      files=Ytlist(argsp.url)
      files.extract_info()
      files=files.download_all_videos_by_resolution(res=argsp.video_quality,alt=alt)
      print(f'''Downloaded {files['downloaded']} videos of {files['total']} in directory {files['output_folder']}. Files Downloaded {files['size_downloaded']}''')




if __name__=='__main__': 
  try:
    main() 
  except Exception as e:
    print(e)