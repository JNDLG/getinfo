from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

def get_video_info(url):
    cmd = f"mediainfo --Output=JSON --Inform='{{{{General;%Duration/String3%,%OverallBitRate/String%,%Format%}},{{Video;%CodecID%,%Width%,%Height%,%FrameRate%,%BitRate/String%}},{{Audio;%CodecID%,%BitRate/String%,%Channels/String%,%Language/String%}}}}' {url}"
    mediainfo_output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    return mediainfo_output

@app.route('/video_info', methods=['POST'])
def video_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    info = get_video_info(url)
    return jsonify(info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
