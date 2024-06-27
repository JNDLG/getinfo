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

            const media = data.media;
            if (!media) {
                infoDiv.innerText = 'No media information found';
                return;
            }

            const tracks = media.track;
            if (!tracks || tracks.length === 0) {
                infoDiv.innerText = 'No tracks found';
                return;
            }

            tracks.forEach(track => {
                const sectionTitle = document.createElement('h4');
                sectionTitle.className = 'section-title';
                sectionTitle.textContent = track['@type'];
                infoDiv.appendChild(sectionTitle);

                const table = document.createElement('table');
                table.className = 'table table-striped';
                Object.keys(track).forEach(key => {
                    if (key !== '@type') {
                        const row = table.insertRow();
                        const cell1 = row.insertCell(0);
                        const cell2 = row.insertCell(1);
                        cell1.textContent = key;
                        cell2.textContent = track[key];
                    }
                });
                infoDiv.appendChild(table);
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
