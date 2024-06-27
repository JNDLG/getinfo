from flask import Flask, request, jsonify, render_template_string
import subprocess
import json

app = Flask(__name__)

def get_video_info(url):
    cmd = f"mediainfo --Output=JSON {url}"
    mediainfo_output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    return json.loads(mediainfo_output)

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Video Info</title>
        </head>
        <body>
            <h1>Enter Video URL</h1>
            <form id="videoForm">
                <label for="url">Video URL:</label>
                <input type="text" id="url" name="url">
                <button type="button" onclick="getVideoInfo()">Get Info</button>
            </form>
            <h2>Video Info:</h2>
            <pre id="info"></pre>
            <script>
                function getVideoInfo() {
                    const url = document.getElementById('url').value;
                    fetch('/video_info', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ url: url })
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('info').innerText = JSON.stringify(data, null, 2);
                    })
                    .catch(error => {
                        document.getElementById('info').innerText = 'Error: ' + error;
                    });
                }
            </script>
        </body>
        </html>
    ''')

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        info = get_video_info(url)
        return jsonify(info)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
