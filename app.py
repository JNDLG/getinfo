from flask import Flask, request, jsonify, render_template_string
import subprocess
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_video_info(url):
    app.logger.debug(f"Fetching video info for URL: {url}")
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
                    <button type="button" class="btn btn-primary mb-2" onclick="getVideoInfo()">Get Info</button>
                </form>
                <h2>Video Info:</h2>
                <button class="btn btn-secondary mb-2" onclick="copyToClipboard()">Copy to Clipboard</button>
                <div id="info" class="border p-3"></div>
            </div>
            <script>
                function getVideoInfo() {
                    const url = document.getElementById('url').value;
                    console.log(`Fetching video info for URL: ${url}`);
                    fetch('/video_info', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ url: url })
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
    if not url:
        app.logger.error("No URL provided")
        return jsonify({'error': 'No URL provided'}), 400

    try:
        info = get_video_info(url)
        app.logger.debug(f"Video info fetched successfully for URL: {url}")
        return jsonify(info)
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error fetching video info for URL {url}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
