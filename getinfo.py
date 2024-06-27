import subprocess

def get_video_info(url):
    cmd = f"mediainfo --Output=JSON --Inform='{{{{General;%Duration/String3%,%OverallBitRate/String%,%Format%}},{{Video;%CodecID%,%Width%,%Height%,%FrameRate%,%BitRate/String%}},{{Audio;%CodecID%,%BitRate/String%,%Channels/String%,%Language/String%}}}}' {url}"
    # 执行命令
    mediainfo_output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    print(mediainfo_output)

# 获取用户输入的URL
url = input("请输入你的视频文件的URL：")
get_video_info(url)
