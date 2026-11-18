#!/usr/bin/env python3
import argparse,fcntl,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RENDERER=ROOT/'renderer'

def run(args,cwd=ROOT,env=None):
    subprocess.run(list(map(str,args)),cwd=cwd,check=True,env=env)

def setup(n,isolated=False):
    dest=ROOT/'episodes'/f'{n:02d}'
    project=RENDERER
    if isolated:
        project=dest/'project'
        shutil.copytree(RENDERER,project,dirs_exist_ok=True,ignore=shutil.ignore_patterns('node_modules','dist','out','lesson.json'))
        if not (project/'node_modules').exists():(project/'node_modules').symlink_to((RENDERER/'node_modules').resolve())
    shutil.copy(dest/'lesson.json',project/'lesson.json')
    run(['npm','run','build'],project)
    return project

def verify(dest):
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest/'video.mp4')]))
    v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(1920,1080,'30/1','18000'),v
    assert abs(float(info['format']['duration'])-600)<.08,info['format']['duration']
    assert a['codec_name']=='aac' and v['codec_name']=='h264'
    (dest/'verification.json').write_text(json.dumps(dict(duration=info['format']['duration'],width=v['width'],height=v['height'],fps=v['r_frame_rate'],frames=v['nb_frames'],audio=a['codec_name'],video=v['codec_name'],bytes=(dest/'video.mp4').stat().st_size),indent=2)+'\n')
    print('VERIFIED 1920x1080 / 600s / 30 fps / H.264 + AAC',dest,flush=True)

def render(n,isolated=False):
    dest=ROOT/'episodes'/f'{n:02d}'
    if (dest/'video.mp4').exists():verify(dest);return
    if not (dest/'frames/frames.ffconcat').exists():
        project=setup(n,isolated)
        env=dict(os.environ,AGILE_EPISODE_DIR=str(dest))
        run(['node','tools/capture-longform.mjs'],project,env)
    lesson=json.loads((dest/'lesson.json').read_text())
    cmd=['ffmpeg','-y','-v','warning','-safe','0','-f','concat','-i',dest/'frames/frames.ffconcat']
    filters=[];labels=[]
    for i,c in enumerate(lesson['chapters']):
        cmd+=['-i',dest/'voice'/(c['id']+'.wav')]
        filters.append(f'[{i+1}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={round((c["start"]+.25)*1000)}:all=1[a{i}]');labels.append(f'[a{i}]')
    subindex=len(lesson['chapters'])+1
    cmd+=['-i',dest/'subtitles.srt']
    filters.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0:dropout_transition=0,apad,atrim=duration=600,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout]')
    cmd+=['-filter_complex',';'.join(filters),'-map','0:v','-map','[aout]','-map',f'{subindex}:s','-vf','fps=30,format=yuv420p','-c:v','libx264','-threads','4','-preset','veryfast','-crf','20','-c:a','aac','-b:a','192k','-c:s','mov_text','-metadata:s:s:0','language=eng','-t','600','-movflags','+faststart',dest/'video.partial.mp4']
    run(cmd)
    (dest/'video.partial.mp4').replace(dest/'video.mp4');verify(dest)
    shutil.rmtree(dest/'frames')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=1);ap.add_argument('--end',type=int,default=12);ap.add_argument('--stills',action='store_true');ap.add_argument('--isolated',action='store_true');args=ap.parse_args()
    lockpath=ROOT/'episodes'/f'{args.start:02d}'/'.render.lock' if args.isolated else ROOT/'.render.lock'
    with lockpath.open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for n in range(args.start,args.end+1):
            if args.stills:
                setup(n);run(['node','tools/capture-longform.mjs','--stills'],RENDERER);run(['node','tools/thumbnail.mjs'],RENDERER)
            else:render(n,args.isolated)

if __name__=='__main__':main()
