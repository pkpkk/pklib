video_codecs = {'h264': '.mp4', 'vp8': '.webm', 'vp9': '.webm', 'hevc': '.mp4',
'av1': '.webm', 'mpeg4': '.mp4', 'prores': '.mov', 'dnxhd': '.mov', 'h265': '.mp4',
'avc1': '.mp4', 'avc': '.mp4', 'm4v': '.m4v', 'mkv': '.mkv', 'mov': '.mov', '3gp': '.3gp'}

audio_codecs = {'mp3': '.mp3', 'aac': '.mka', 'wma': '.wma', 'wav': '.wav', 
'flac': '.flac', 'alac': '.m4a', 'opus': '.opus', 'ac3': '.ac3', 'dts': '.dts',
'amr': '.amr', 'm4a': '.m4a', 'mka': '.mka', 'mp2': '.mp2', 'pcm': '.wav', 
'ra': '.ra', 'tta': '.tta', 'ape': '.ape', 'mid': '.mid', 'ogg': '.ogg', 'webm': '.webm'}


supported_audio={'.mp4':['aac','mp4','mp3'],'.webm':['webm','opus']}
from subprocess import run as srun,check_output
from json import loads as jsnloads
from os.path import basename,dirname,join as osjoin,exists,getsize,isfile,isdir,basename
from os import getcwd,chdir,rename,remove as osremove
import time,re
from random import randint
from shutil import rmtree as srmtree

class lzp:
  def remove(file_or_directory):
    if isfile(file_or_directory):
      osremove(file_or_directory) 
    else:
      srmtree(file_or_directory)
  def rename(file,new_name,safe=False):
    if dirname(file)==dirname(new_name):
      if file!=new_name:
        os.rename(file,new_name)
    else:
      new_name=osjoin(dirname(file),basename(new_name))
      if file!=new_name:
        os.rename(file,new_name)
        #/\*:?< >


class stream:
  def __init__(self,stream:dict):
    self.codec_type=stream.get('codec_type')
    self.codec_name=stream.get('codec_name')
    self.language=stream.get('tags').get('language') if stream.get('tags') else None
    self.is_audio=True if (self.codec_type=='audio') else False
    self.is_video=True if (self.codec_type=='video') else False
    self.is_subtitle=True if (self.codec_type=='subtitle') else False
    self.index=None
    self.file_index=stream.get('file_index')
  def __repr__(self):
    return f'<{self.codec_type}:{self.codec_name}--{self.language if self.language else ""}>'
  @property 
  def map_in(self):
    e={'video':'v','audio':'a','subtitle':'s'}
    return f'{self.file_index}:{e.get(self.codec_type)}:{self.index}'


class media:
  def __init__(self,file,file_index=0):
    self.filename=basename(file)
    self.directory=dirname(file) if (dirname(file)!='') else getcwd()
    self.full_path=osjoin(self.directory,self.filename)
    self.processed=False
    self.codecs=None 
    self.streams=None 
    self.video_streams=None 
    self.audio_streams=None 
    self.subtitle_streams=None
    self.duration=None
    self.bit_rate=None
    self.is_only_subtitle=None 
    self.is_only_audio=None 
    self.is_only_video=None 
    self.has_audio=None 
    self.has_video=None 
    self.has_subtitle=None
    self.file_index=file_index
  def find_codecs(self):
    cmd = ['ffprobe','-hide_banner', '-show_entries', 'stream=codec_name,codec_type','-show_entries', 'stream_tags=language', '-print_format', 'json','-loglevel', 'error','-i',self.full_path]
    peo=srun(cmd,capture_output=True)
    if peo.returncode==0:
      return jsnloads(peo.stdout.decode()).get('streams')
    else:
      return []
  def get_duration(self):
    cmd=['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', self.full_path]
    peo = srun(cmd,capture_output=True)
    if (peo.returncode==0 and peo.stdout.decode()!='N/A\n'):
      return round(float(peo.stdout.decode()))
    else:
      return 1
  def get_bitrate(self):
    cmd=['ffprobe', '-v', 'error', '-hide_banner', '-show_entries', 'format=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', self.full_path]
    peo = srun(cmd,capture_output=True)
    if (peo.returncode==0 and peo.stdout.decode()!='N/A\n'):
      return round(float(peo.stdout.decode()))
    else:
      return 1
  def vi_au_streams(self):
    li=self.codecs
    streams__=[]
    for u in li:
      u['file_index']=self.file_index
    for u in li:
      streams__.append(stream(u))
    self.streams=streams__
    vi,au,su=[],[],[]
    for ent in self.streams:
      if ent.codec_type=='video':
        vi.append(ent)
      elif ent.codec_type=='audio':
        au.append(ent)
      elif ent.codec_type=='subtitle':
        su.append(ent)
    self.video_streams,self.audio_streams,self.subtitle_streams=vi,au,su
    return vi,au,su
  def set_index_stream(self):
    lk=[self.video_streams,self.audio_streams,self.subtitle_streams]
    for i in lk:
      for en in range(len(i)):
        i[en].index=en
  def get_video_resolution(self):
    try:
      result = check_output(['ffprobe', '-loglevel', 'error', '-select_streams', 'v:0','-show_entries', 'stream=width,height', '-of', 'json', self.full_path]).decode('utf-8')
      fields = jsnloads(result)['streams'][0]
      width = int(fields['width'])
      height = int(fields['height'])
      return width, height
    except Exception as e:
      print(f"get_video_resolution: {e}")
      return 480, 320
  @property 
  def __do(self):
    """ can do this by media(file)._media__do"""
    self.codecs=self.find_codecs()
    vi,au,su=self.vi_au_streams()
    self.is_only_video=True if (len(vi)>0 and len(au)==0 and len(su)==0) else False
    self.is_only_audio=True if (len(vi)==0 and len(au)>0 and len(su)==0) else False
    self.is_only_subtitle=True if (len(vi)==0 and len(au)==0 and len(su)>0) else False
    self.has_video=True if len(vi)!=0 else False
    self.has_audio=True if len(au)!=0 else False
    self.has_subtitle=True if len(su)!=0 else False
    self.duration=self.get_duration()
    self.bit_rate=self.get_bitrate()
    self.set_index_stream()
    self.processed=True

def hhmmss(seconds):
    x = time.strftime('%H:%M:%S',time.gmtime(seconds))
    return x

scodecs={'.mkv':'srt','.webm':'vtt','.mp4':'mov_text'}

class Ffmpeg:
  def __init__(self):
    self.scodecs={'.mkv':'srt','.webm':'vtt','.mp4':'mov_text'}
    self.supported_audio={'.mp4':['aac','mp4','mp3'],'.webm':['webm','opus']}
  def ssgen(self,video, time_stamp):
    out = osjoin(getcwd(),str(time.time())+ ".jpg")
    cmd =['ffmpeg', '-ss', f'{hhmmss(time_stamp)}', '-i', video, '-vframes', '1', '-loglevel', 'error', out, '-y' ]
    peo=srun(cmd,capture_output=True)
    if peo.returncode==0:
      if isfile(out):
        return out
    else:
      return  None
  def sshotfunc(self,file,count=10):
    picts=[]
    duration=media(file).get_duration()
    for i in range(count):
      sshot = ffmpeg.ssgen(file, round((duration-1)*random())) 
      if sshot is not None:
        picts.append(sshot)
    return picts
  def cret_thumb(self,file):
    duration=media(file).get_duration()
    return self.ssgen(file,randint(1,duration-1))
  def extract_audios(self,file,output_folder=None):
    meed=media(file)
    meed._media__do
    output_folder=output_folder if output_folder else meed.directory
    if meed.has_audio:
      count,files=0,[]
      for i in meed.audio_streams:
        f_nam=meed.filename[:-4] + f'__a{count}__' + audio_codecs.get(i.codec_name)
        f_nam=osjoin(output_folder,f_nam)
        cmd=['ffmpeg','-i',file,'-c:a','copy','-loglevel','error','-map',i.map_in,f_nam,'-y']
        peo=srun(cmd,capture_output=False)
        count+=1
        if isfile(f_nam):
          files.append(f_nam)
      return files
    else: 
      raise Exception('There is no audio stream in provided media file')
  def extract_videos(self,file,output_folder=None):
    meed=media(file)
    meed._media__do
    output_folder=output_folder if output_folder else meed.directory
    if meed.has_video:
      count,files=0,[]
      for i in meed.video_streams:
        f_nam=meed.filename[:-4] + f'__v{count}__' + video_codecs.get(i.codec_name)
        f_nam=osjoin(output_folder,f_nam)
        cmd=['ffmpeg','-i',file,'-c:v','copy','-loglevel','error','-map',i.map_in,f_nam,'-y']
        peo=srun(cmd,capture_output=False)
        count+=1
        if isfile(f_nam):
          files.append(f_nam)
      return files
    else: 
      raise Exception('There is no video stream in provided media file') 
  def generate_sample(self,file,length=30):
    meed=media(file)
    meed._media__do 
    if meed.duration <=180:
      raise Exception(f'File is just {meed.duration} seconds long')
    else:
      ss=randint(30,meed.duration-60) 
      outf=osjoin(meed.directory,f'sample_{meed.filename}')
      cmd=['ffmpeg', '-i' ,file, '-ss', f'{ss}', '-t',f'{length}', '-c', 'copy','-map' ,'0', '-loglevel', 'error', outf, '-y']
      peo=srun(cmd,capture_output=True) 
      if peo.returncode==0: 
        if isfile(outf):
          return outf 
      else:
        raise Exception(peo.stderr.decode())
  def merge_streams(self,video=None,audio=None,subtitle=None,replace_audio=False,output_folder=None):
    if (video and audio and subtitle):
      vcod,acod,scod=media(video),media(audio,file_index=1),media(subtitle,file_index=2) 
      vcod._media__do
      acod._media__do
      scod._media__do
      if not vcod.has_video:
        raise Exception('No video stream in video file')
      if not vcod.has_audio:
        raise Exception('No audio stream in audio file')
      if not vcod.has_subtitle:
        raise Exception('No subtitle in subtitle file')
      ext=video_codecs.get(vcod.codec_name)
      supp_a=self.supported_audio.get(ext)
      if (supp_a and (acod.codec_name in supp_a)):
        ext=ext
      else:
        ext='.mkv'
      scof=self.scodecs.get(ext)
      if not scof:
        ext,scof='.mkv','srt'
      map=[]
      if replace_audio:
        for i in vcod.video_streams:
          map.append('-map')
          map.append(i.map_in)
        for i in acod.audio_streams:
          map.append('-map')
          map.append(i.map_in)
        for i in scod.subtitle_streams:
          map.append('-map') 
          map.append(i.map_in)
        if not output_folder:
          output_folder=vcod.directory
        outf=vcod.filename[:-4]+'_mer_v_a_s_'+ext
        outf=osjoin(output_folder,outf)
        cmd=['ffmpeg', '-i', video, '-i',audio,'-i', subtitle, *map, '-c:s', scof, '-c:a','copy', '-c:v', 'copy', '-loglevel', 'error', outf, '-y']
      else:
        for i in vcod.streams:
          map.append('-map')
          map.append(i.map_in)
        for i in acod.streams:
          map.append('-map')
          map.append(i.map_in)
        for i in scod.streams:
          map.append('-map') 
          map.append(i.map_in)
        if not output_folder:
          output_folder=vcod.directory
        outf=vcod.filename[:-4]+'_mer_v_a_s_'+ext
        outf=osjoin(output_folder,outf)
        cmd=['ffmpeg', '-i', video, '-i',audio,'-i', subtitle, *map, '-c:s', scof, '-c:a','copy', '-c:v', 'copy', '-loglevel', 'error', outf, '-y']
      peo=srun(cmd,capture_output=True)
      if peo.returncode==0:
        if isfile(outf):
          return outf
      else:
        raise Exception(peo.stderr.decode())
    elif (video and audio):
      vcod,acod=media(video),media(audio,file_index=1) 
      vcod._media__do
      acod._media__do
      if not vcod.has_video:
        raise Exception('No video stream in video file')
      if not vcod.has_audio:
        raise Exception('No audio stream in audio file')
      ext=video_codecs.get(vcod.codec_name)
      supp_a=self.supported_audio.get(ext)
      if (supp_a and (acod.codec_name in supp_a)):
        ext=ext
      else:
        ext='.mkv'
      map=[]
      if replace_audio:
        for i in vcod.video_streams:
          map.append('-map')
          map.append(i.map_in)
        for i in acod.audio_streams:
          map.append('-map') 
          map.append(i.map_in)
        if not output_folder:
          output_folder=vcod.directory
        outf=vcod.filename[:-4]+'_mer_v_a_'+ext
        outf=osjoin(output_folder,outf)
        cmd=['ffmpeg', '-i', video, '-i', audio, *map, '-c:a', 'copy', '-c:v', 'copy', '-c:a','copy','-loglevel', 'error', outf, '-y']
      else:
        for i in vcod.streams:
          map.append('-map')
          map.append(i.map_in)
        for i in acod.streams:
          map.append('-map') 
          map.append(i.map_in)
        if not output_folder:
          output_folder=vcod.directory
        outf=vcod.filename[:-4]+'_mer_v_a_'+ext
        outf=osjoin(output_folder,outf)
        cmd=['ffmpeg', '-i', video, '-i', audio, *map, '-c:a', 'copy', '-c:v', 'copy', '-loglevel', 'error', outf, '-y']
      peo=srun(cmd,capture_output=True)
      if peo.returncode==0:
        if isfile(outf):
          return outf
      else:
        raise Exception(peo.stderr.decode())
    elif (video and subtitle):
      vcod,scod=media(video),media(subtitle,file_index=1) 
      vcod._media__do
      scod._media__do
      if not vcod.has_video:
        raise Exception('No video stream in video file')
      ext=video_codecs.get(vcod.video_streams[0].codec_name)
      scof=self.scodecs.get(ext)
      if not scof:
        ext,scof='.mkv','srt'
      map=[]
      if replace_audio:
        for i in vcod.video_streams:
          map.append('-map')
          map.append(i.map_in)
        for i in scod.subtitle_streams:
          map.append('-map') 
          map.append(i.map_in)
        if not output_folder:
          output_folder=vcod.directory
        outf=vcod.filename[:-4]+'_mer_v_s_'+ext
        outf=osjoin(output_folder,outf)
        cmd=['ffmpeg', '-i', video, '-i', subtitle, *map, '-c:s', scof, '-c:v', 'copy', '-c:a','copy', '-loglevel', 'error', outf, '-y']
      else:
        for i in vcod.streams:
          map.append('-map')
          map.append(i.map_in)
        for i in scod.streams:
          map.append('-map') 
          map.append(i.map_in)
        if not output_folder:
          output_folder=vcod.directory
        outf=vcod.filename[:-4]+'_mer_v_s_'+ext
        outf=osjoin(output_folder,outf)
        cmd=['ffmpeg', '-i', video, '-i', subtitle, *map, '-c:s', scof, '-c:v', 'copy','-c:a','copy', '-loglevel', 'error', outf, '-y']
      peo=srun(cmd,capture_output=True)
      if peo.returncode==0:
        if isfile(outf):
          return outf
      else:
        raise Exception(peo.stderr.decode())
        #cmd='ffmpeg -i video -i subtitle -map 0:v:0 -map 1:s:0 -c:s scod -c:v copy -loglevel error outf -y'
    elif (audio and subtitle):
        raise Exception('I will get in problem if I did that')
  def concat_files(self,files,output_folder=None):
    outf=f'{time.time()}.concat'
    with open(outf,'a',encoding='utf-8') as w:
      for i in files:
        if '\'' not in i:
          w.write(f'file \'{i}\'\n')
        else:
          w.write(f'file \"{i}\"\n')
    if not output_folder:
      output_folder=dirname(files[0])
    fnam=files[0][:-6]+'__concat__.mkv'
    fnam=osjoin(output_folder,fnam)
    cmd=['ffmpeg','-hide_banner', '-nostdin', '-f', 'concat', '-safe', '0', '-i',outf,'-c:s', 'srt', '-c:v', 'copy','-c:a','copy','-loglevel','error', fnam,'-y']
    peo=srun(cmd,capture_output=True)
    if peo.returncode==0:
      if isfile(fnam):
        return fnam
    else:
      raise Exception(peo.stderr.decode())




"""
def concat_files(self, in_files, out_file, concat_opts=None):
        
        Use concat demuxer to concatenate multiple files having identical streams.

        Only inpoint, outpoint, and duration concat options are supported.
        See https://ffmpeg.org/ffmpeg-formats.html#concat-1 for details
        
        concat_file = f'{out_file}.concat'
        self.write_debug(f'Writing concat spec to {concat_file}')
        with open(concat_file, 'wt', encoding='utf-8') as f:
            f.writelines(self._concat_spec(in_files, concat_opts))

        out_flags = list(self.stream_copy_opts(ext=determine_ext(out_file)))

        self.real_run_ffmpeg(
            [(concat_file, ['-hide_banner', '-nostdin', '-f', 'concat', '-safe', '0'])],
            [(out_file, out_flags)])
        self._delete_downloaded_files(concat_file)

def find_codecs(file):
  cmd = ['ffprobe','-hide_banner', '-show_entries', 'stream=codec_name,codec_type', '-print_format', 'json','-loglevel', 'error','-i',file]
  peo=srun(cmd,capture_output=True)
  if peo.returncode==0:
    return jsnloads(peo.stdout.decode()).get('streams')
  else:
    return []

def get_bitrate(file):
    cmd=['ffprobe', '-v', 'error', '-hide_banner', '-show_entries', 'format=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', file]
    peo = srun(cmd,capture_output=True)
    if (peo.returncode==0 and peo.stdout.decode()!='N/A\n'):
      return round(float(peo.stdout.decode()))
    else:
      return 1

def do_m(func,*args):
  tup=()
  for i in args:
    e=(func(i),)
    tup+=e 
  return tup
    
scodecs={'.mkv':'srt','.webm':'vtt','.mp4':'mov_text'}
def merge(video=None,audio=None,subtitle=None,replace_audio=False):
  if replace_audio:
    if (video and audio and subtitle):
      vcod,acod,scod=do_m(find_codecs,video,audio, subtitle) 
      v=[]
      for i in vcod:
        if vcod['codec_type']=='video':
          v.append(i)
      if len(v)==0:
        raise Exception('No video in provided video file')
      else:
        ext=video_codecs.get(vcod[0]['codec_type'])
      supp_a=supported_audio.get(ext)
      if (supp_a and (acod[0]['codec_type'] in supp_a)):
        ext=ext
      else:
        ext='.mkv'
    elif (video and audio):
      vcod,acod=do_m(find_codecs,video,audio) 
      v=[]
      for i in vcod:
        if vcod['codec_type']=='video':
          v.append(i)
      if len(v)==0:
        raise Exception('No video in provided video file')
      else:
        ext=video_codecs.get(vcod[0]['codec_type'])
      supp_a=supported_audio.get(ext)
      if supp_a:
        if acod[0]['codec_type'] in supp_a:
          ext=ext
        else:
          ext='.mkv'
    elif (video and subtitle):
      vcod,scod=do_m(find_codecs,video,subtitle) 
      v=[]
      for i in vcod:
        if vcod['codec_type']=='video':
          v.append(i)
      if len(v)==0:
        raise Exception('No video in provided video file')
      else:
        ext=video_codecs.get(vcod[0]['codec_type'])
      scod=scodecs.get(ext)
      cmd='ffmpeg -i video -i subtitle -map 0:v:0 -map 1:s:0 -c:s scod -c:v copy -loglevel error outf -y'
    elif (audio and subtitle):
      raise Exception('I will get in problem if I did that')
  else:
    pass


import os,json,subprocess,asyncio
from pkhelper import bash
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser 
from pkhelper import bash_async as bashf

def durationfunc(file):
 metadata = extractMetadata(createParser(f'{file}'))
 if metadata.has("duration"):
   duration = metadata.get('duration').seconds
 else:
     duration = 1
 return duration

video_codecs = {
    'h264': '.mp4',
    'vp8': '.webm',
    'vp9': '.webm',
    'hevc': '.mp4',
    'av1': '.webm',
    'mpeg4': '.mp4',
    'prores': '.mov',
    'dnxhd': '.mov',
    'h265': '.mp4',
    'avc1': '.mp4',
    'avc': '.mp4',
    'm4v': '.m4v',
    'mkv': '.mkv',
    'mov': '.mov',
    '3gp': '.3gp'
}
audio_codecs = {
    'mp3': '.mp3',
    'aac': '.aac',
    'wma': '.wma',
    'wav': '.wav',
    'flac': '.flac',
    'alac': '.m4a',
    'opus': '.opus',
    'ac3': '.ac3',
    'dts': '.dts',
    'amr': '.amr',
    'm4a': '.m4a',
    'mka': '.mka',
    'mp2': '.mp2',
    'pcm': '.wav',
    'ra': '.ra',
    'tta': '.tta',
    'ape': '.ape',
    'mid': '.mid',
    'ogg': '.ogg',
    'webm': '.webm'
}
supported_audio={'.mp4':['aac','mp4','mp3'],'.webm':['webm','opus']}
from subprocess import run as srun,check_output
from json import loads as jsnloads
from os.path import basename,dirname,join as osjoin
from os import getcwd,chdir

class stream:
  def __init__(self,stream:dict):
    self.codec_type=stream.get('codec_type')
    self.codec_name=stream.get('codec_name')
    self.language=stream.get('tags').get('language')
    self.is_audio=True if (self.codec_type=='audio') else False
    self.is_video=True if (self.codec_type=='video') else False
    self.is_subtitle=True if (self.codec_type=='subtitle') else False



class media:
  def __init__(self,file):
    self.filename=basename(file)
    self.directory=dirname(file) if (dirname(file)!='') else getcwd()
    self.full_path=osjoin(self.directory,self.filename)
    self.codecs=None 
    self.video_streams=None 
    self.audio_streams=None 
    self.subtitle_streams=None
    self.duration=None
    self.bit_rate=None
    self.is_only_subtitle=None 
    self.is_only_audio=None 
    self.is_only_video=None 
    self.has_audio=None 
    self.has_video=None 
    self.has_subtitle=None
  def find_codecs(self):
    cmd = ['ffprobe','-hide_banner', '-show_entries', 'stream=codec_name,codec_type','-show_entries', 'stream_tags=language', '-print_format', 'json','-loglevel', 'error','-i',self.full_path]
    peo=srun(cmd,capture_output=True)
    if peo.returncode==0:
      return jsnloads(peo.stdout.decode()).get('streams')
    else:
      return []
  def get_duration(self):
    cmd=['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', self.full_path]
    peo = srun(cmd,capture_output=True)
    if (peo.returncode==0 and peo.stdout.decode()!='N/A\n'):
      return round(float(peo.stdout.decode()))
    else:
      return 1
  def get_bitrate(self):
    cmd=['ffprobe', '-v', 'error', '-hide_banner', '-show_entries', 'format=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', self.full_path]
    peo = srun(cmd,capture_output=True)
    if (peo.returncode==0 and peo.stdout.decode()!='N/A\n'):
      return round(float(peo.stdout.decode()))
    else:
      return 1
  def vi_au_streams(self):
    li=self.codecs
    vi,au,su=[],[],[]
    for ent in li:
      if ent.get('codec_type')=='video':
        vi.append(ent)
      elif ent.get('codec_type')=='audio':
        au.append(ent)
      elif ent.get('codec_type')=='subtitle':
        su.append(ent)
    self.video_streams,self.audio_streams,self.subtitle_streams=vi,au,su
    return vi,au,su
  def set_index_stream(self):
    lk=[self.video_streams,self.audio_streams,self.subtitle_streams]
    for i in lk:
      for en in range(len(i)):
        i[en]['index']=en
  @property 
  def __do(self):
    self.codecs=self.find_codecs()
    vi,au,su=self.vi_au_streams()
    self.is_only_video=True if (len(vi)>0 and len(au)==0 and len(su)==0) else False
    self.is_only_audio=True if (len(vi)==0 and len(au)>0 and len(su)==0) else False
    self.is_only_subtitle=True if (len(vi)==0 and len(au)==0 and len(su)>0) else False
    self.has_video=True if len(vi)!=0 else False
    self.has_audio=True if len(au)!=0 else False
    self.has_subtitle=True if len(su)!=0 else False
    self.duration=self.get_duration()
    self.bit_rate=self.get_bitrate()
    self.set_index_stream()
def find_codecs(file):
  cmd = ['ffprobe','-hide_banner', '-show_entries', 'stream=codec_name,codec_type', '-print_format', 'json','-loglevel', 'error','-i',file]
  peo=srun(cmd,capture_output=True)
  if peo.returncode==0:
    return jsnloads(peo.stdout.decode()).get('streams')
  else:
    return []

def get_bitrate(file):
    cmd=['ffprobe', '-v', 'error', '-hide_banner', '-show_entries', 'format=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', file]
    peo = srun(cmd,capture_output=True)
    if (peo.returncode==0 and peo.stdout.decode()!='N/A\n'):
      return round(float(peo.stdout.decode()))
    else:
      return 1

def do_m(func,*args):
  tup=()
  for i in args:
    e=(func(i),)
    tup+=e 
  return tup
    
scodecs={'.mkv':'srt','.webm':'vtt','.mp4':'mov_text'}
def merge(video=None,audio=None,subtitle=None,replace_audio=False):
  if replace audio:
    if (video and audio and subtitle):
      vcod,acod,scod=do_m(find_codecs,video,audio, subtitle) 
      v=[]
      for i in vcod:
        if vcod['codec_type']='video':
          v.append(i)
      if len(v)==0:
        raise Exception('No video in provided video file')
      else:
        ext=video_codecs.get(vcod[0]['codec_type'])
      supp_a=supported_audio.get(ext)
      if (supp_a and (acod[0]['codec_type'] in supp_a)):
        ext=ext
      else:
        ext='.mkv'
    elif (video and audio):
      vcod,acod=do_m(find_codecs,video,audio) 
      v=[]
      for i in vcod:
        if vcod['codec_type']='video':
          v.append(i)
      if len(v)==0:
        raise Exception('No video in provided video file')
      else:
        ext=video_codecs.get(vcod[0]['codec_type'])
      supp_a=supported_audio.get(ext)
      if supp_a:
        if acod[0]['codec_type'] in supp_a:
          ext=ext
        else:
          ext='.mkv'
    elif (video and subtitle):
      vcod,scod=do_m(find_codecs,video,subtitle) 
      v=[]
      for i in vcod:
        if vcod['codec_type']='video':
          v.append(i)
      if len(v)==0:
        raise Exception('No video in provided video file')
      else:
        ext=video_codecs.get(vcod[0]['codec_type'])
      scod=scodecs.get(ext)
      cmd='ffmpeg -i video -i subtitle -map 0:v:0 -map 1:s:0 -c:s scod -c:v copy -loglevel error outf -y'
    elif (audio and subtitle):
      raise Exception('I will get in problem if I did that')
  else:
    



def list_streams(file):
  st=[]
  cmd = f'ffprobe -hide_banner -show_entries stream=codec_type -show_entries stream_tags=language -print_format json -loglevel 0 -i "{file}" '
  #cmd=cmd.split()
  #r = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode()
  #print(r)
  r=bash(cmd)
  output = r
  for su in output["streams"]:
    #for k,v #in su.items():
    try:
      for i in range(1):
        st.append(su["codec_type"]+"@"+su["tags"]["language"]) 
    except KeyError:
      for i in range(1):
         st.append(su["codec_type"])
  v=[]
  a=[]
  s=[]
  for el in range(len(st)):
   if st[el].startswith('video'):
    v.append(st[el])
   elif st[el].startswith('audio'):
    a.append(st[el])
   elif st[el].startswith('subtitle'):
    s.append(st[el])
   else:
    pass
  v1=[]
  a1=[]  
  s1=[]
  for uy in range(len(v)):
    v1.append(f"{v[uy]}@{uy}")
  
  for uy in range(len(a)):
    a1.append(f"{a[uy]}@{uy}")
    
  for uy in range(len(s)):
    s1.append(f"{s[uy]}@{uy}")
  streams=a1+s1
  st.clear()
  return str(streams)

def generate_sample(file):
  dur=durationfunc(file)
  ext=str(file).split(".")[-1]
  out=f'{str(file).replace(ext,"")+'sample.'}{ext}'
  if int(dur)<180:
     bash(f'ffmpeg -y -i "{file}" -ss 00:00:20 -t 30 -c copy -map 0 -loglevel 0 "{out}" ')
  else:
     bash(f'ffmpeg -y -i "{file}" -ss 00:01:40 -t 50 -c copy -map 0 -loglevel 0 "{out}" ')
  return out
"""