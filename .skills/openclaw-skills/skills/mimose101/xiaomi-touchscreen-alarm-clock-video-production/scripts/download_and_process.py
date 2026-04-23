"""B站视频下载裁剪压缩脚本"""
import argparse, subprocess, os, sys, shutil

def get_duration(fp):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",fp], capture_output=True, text=True)
    return float(r.stdout.strip())

def size_mb(fp):
    return os.path.getsize(fp)/(1024*1024)

def download(url, out, fmt=None):
    cmd = [sys.executable,"-m","yt_dlp","-o",out,"--merge-output-format","mp4"]
    if fmt: cmd.extend(["-f",fmt])
    cmd.append(url)
    subprocess.run(cmd)

def crop(inp, out, params):
    subprocess.run(["ffmpeg","-y","-i",inp,"-vf",f"crop={params}","-c:v","libx264","-crf","18","-c:a","copy",out])

def compress(inp, out, max_mb):
    if size_mb(inp)<=max_mb:
        if inp!=out: shutil.copy2(inp,out)
        return
    dur=get_duration(inp)
    vbr=max(int((max_mb*0.9*8*1024)/dur-64),100)
    subprocess.run(["ffmpeg","-y","-i",inp,"-c:v","libx264","-b:v",f"{vbr}k","-maxrate",f"{int(vbr*1.25)}k","-bufsize",f"{int(vbr*2.5)}k","-c:a","aac","-b:a","64k","-ar","44100",out])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--output_dir",default=os.path.join(os.path.expanduser("~"),"Documents"))
    p.add_argument("--max_size_mb",type=float,default=10)
    p.add_argument("--crop",default=None)
    p.add_argument("--format_id",default=None)
    p.add_argument("--filename",default="bilibili_video")
    a=p.parse_args()
    os.makedirs(a.output_dir,exist_ok=True)
    raw=os.path.join(a.output_dir,f"{a.filename}_raw.mp4")
    download(a.url,raw,a.format_id)
    cur=raw
    if a.crop:
        crp=os.path.join(a.output_dir,f"{a.filename}_cropped.mp4")
        crop(cur,crp,a.crop);cur=crp
    final=os.path.join(a.output_dir,f"{a.filename}.mp4")
    compress(cur,final,a.max_size_mb)
    for t in[raw,os.path.join(a.output_dir,f"{a.filename}_cropped.mp4")]:
        if os.path.exists(t)and t!=final:os.remove(t)
    print(f"Done: {final} ({size_mb(final):.2f}MB)")

if __name__=="__main__":
    main()
