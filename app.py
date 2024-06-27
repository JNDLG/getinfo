from flask import Flask, request, jsonify, render_template_string
import subprocess
import os
import logging
import json  # 添加这一行

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_video_info(url, language):
    if language == '英文':
        os.environ['LANG'] = 'en_US.UTF-8'
    else:
        os.environ['LANG'] = 'zh_CN.UTF-8'
    
    cmd = (
        f"mediainfo --Output=JSON "
        f"--Inform='{{{{General;%Duration/String3%,%OverallBitRate/String%,%Format%}},"
        f"{{Video;%CodecID%,%Width%,%Height%,%FrameRate%,%BitRate/String%}},"
        f"{{Audio;%CodecID%,%BitRate/String%,%Channels/String%,%Language/String%}}}}' {url}"
    )
    
    app.logger.debug(f"Running command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            app.logger.error(f"Error running mediainfo: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)

        mediainfo_output = result.stdout
        app.logger.debug(f"mediainfo output: {mediainfo_output}")
        if not mediainfo_output.strip():  # 如果输出为空
            raise ValueError("mediainfo returned an empty string")
        return json.loads(mediainfo_output)
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error running mediainfo: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        app.logger.error(f"Error decoding JSON: {e}")
        app.logger.error(f"mediainfo output: {mediainfo_output}")
        raise
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        raise

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Video Info</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
            <style>
                body { padding: 20px; }
                .container { max-width: 800px; margin: auto; }
                pre { white-space: pre-wrap; }
                .section-title { font-weight: bold; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-center">Enter Video URL</h1>
                <form id="videoForm" class="form-inline my-4">
                    <div class="form-group mx-sm-3 mb-2">
                        <label for="url" class="sr-only">Video URL</label>
                        <input type="text" class="form-control" id="url" name="url" placeholder="Enter video URL">
                    </div>
                    <div class="form-group mx-sm-3 mb-2">
                        <label for="language" class="sr-only">Language</label>
                        <select class="form-control" id="language">
                            <option value="中文">中文</option>
                            <option value="英文">英文</option>
                        </select>
                    </div>
                    <button type="button" class="btn btn-primary mb-2" onclick="getVideoInfo()">Get Info</button>
                </form>
                <h2>Video Info:</h2>
                <button class="btn btn-secondary mb-2" onclick="copyToClipboard()">Copy to Clipboard</button>
                <div id="info" class="border p-3"></div>
            </div>
            <script>
                function getVideoInfo() {
                    const url = document.getElementById('url').value;
                    const language = document.getElementById('language').value;
                    console.log(`Fetching video info for URL: ${url} with language: ${language}`);
                    fetch('/video_info', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ url: url, language: language })
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Received video info:', data);
                        displayInfo(data);
                    })
                    .catch(error => {
                        console.error('Error fetching video info:', error);
                        document.getElementById('info').innerText = 'Error: ' + error;
                    });
                }

                function displayInfo(data) {
                    const infoDiv = document.getElementById('info');
                    infoDiv.innerHTML = '';

                    const sections = ['General', 'Video', 'Audio', 'Text'];
                    sections.forEach(section => {
                        if (data[section]) {
                            const sectionTitle = document.createElement('h4');
                            sectionTitle.className = 'section-title';
                            sectionTitle.textContent = section;
                            infoDiv.appendChild(sectionTitle);

                            const table = document.createElement('table');
                            table.className = 'table table-striped';
                            Object.keys(data[section]).forEach(key => {
                                const row = table.insertRow();
                                const cell1 = row.insertCell(0);
                                const cell2 = row.insertCell(1);
                                cell1.textContent = key;
                                cell2.textContent = data[section][key];
                            });
                            infoDiv.appendChild(table);
                        }
                    });
                }

                function copyToClipboard() {
                    const infoDiv = document.getElementById('info');
                    const range = document.createRange();
                    range.selectNode(infoDiv);
                    window.getSelection().removeAllRanges(); 
                    window.getSelection().addRange(range);
                    document.execCommand('copy');
                    window.getSelection().removeAllRanges();
                    alert('Copied to clipboard');
                }
            </script>
        </body>
        </html>
    ''')

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    language = data.get('language')
    if not url:
        app.logger.error("No URL provided")
        return jsonify({'error': 'No URL provided'}), 400

    try:
        info = get_video_info(url, language)
        app.logger.debug(f"Video info fetched successfully for URL: {url}")
        return jsonify(info)
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error fetching video info for URL {url}: {e.stderr}")
        return jsonify({'error': e.stderr}), 500
    except ValueError as e:
        app.logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
