from flask import Flask, render_template, request, redirect, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            video_formats = []
            audio_formats = []

            for fmt in formats:
                filesize = fmt.get('filesize', 0)
                mb_size = round(filesize / (1024 * 1024), 1) if filesize else 0
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') == 'none':
                    video_formats.append({
                        'format_id': fmt['format_id'],
                        'ext': fmt['ext'],
                        'height': fmt.get('height', 'N/A'),
                        'filesize': mb_size
                    })
                elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    audio_formats.append({
                        'format_id': fmt['format_id'],
                        'ext': fmt['ext'],
                        'abr': fmt.get('abr', 'N/A'),
                        'filesize': mb_size
                    })
        return render_template('select.html', video_formats=video_formats, audio_formats=audio_formats, url=url)
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    video_format_id = request.form['video_format_id']
    audio_format_id = request.form['audio_format_id']
    output_filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(DOWNLOAD_DIR, output_filename)

    ydl_opts = {
        'format': f'{video_format_id}+{audio_format_id}',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(output_path, as_attachment=True)

# Development mode only:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)