import subprocess
import os
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer


def install_packages():
    print("Installing required packages...")
    packages = [
        'v4l2loopback-dkms',  
        'ffmpeg',           
    ]
    

    for package in packages:
        subprocess.run(f"sudo apt-get install -y {package}", shell=True, check=True)
    print("Packages installed successfully!")


def start_ffmpeg():
    print("Starting ffmpeg to capture the entire screen...")
    command = [
        "ffmpeg",
        "-f", "x11grab",
        "-i", ":0.0",  
        "-vf", "scale=640:480",  
        "-pix_fmt", "yuv420p",  
        "-f", "v4l2",  
        "/dev/video2"
    ]
    subprocess.Popen(command)
    print("FFmpeg is capturing the screen and streaming to /dev/video2.")


def serve_html():

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Camera Input</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
            }
            #camera-preview {
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
                border: 2px solid black;
                border-radius: 8px;
            }
            select {
                display: block;
                margin: 10px auto;
                padding: 5px;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <h1>Camera Input</h1>
        <button id="start-button">Enable Camera</button>
        <select id="camera-select" style="display: none;"></select>
        <video id="camera-preview" autoplay playsinline style="display: none;"></video>

        <script>
            const startButton = document.getElementById('start-button');
            const video = document.getElementById('camera-preview');
            const cameraSelect = document.getElementById('camera-select');

            startButton.addEventListener('click', async () => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    startButton.style.display = 'none';
                    cameraSelect.style.display = 'block';
                    video.style.display = 'block';

                    stream.getTracks().forEach(track => track.stop());
                    loadCameras();
                } catch (error) {
                    console.error('Permission denied or error accessing camera:', error);
                    alert('Unable to access the camera. Please allow camera permissions.');
                }
            });

            async function loadCameras() {
                try {
                    const devices = await navigator.mediaDevices.enumerateDevices();
                    const videoInputs = devices.filter(device => device.kind === 'videoinput');
                    videoInputs.forEach((device, index) => {
                        const option = document.createElement('option');
                        option.value = device.deviceId;
                        option.textContent = device.label || `Camera ${index + 1}`;
                        cameraSelect.appendChild(option);
                    });

                    if (videoInputs.length > 0) {
                        startCamera(videoInputs[0].deviceId);
                    }

                    cameraSelect.addEventListener('change', () => {
                        startCamera(cameraSelect.value);
                    });
                } catch (error) {
                    console.error('Error enumerating devices:', error);
                    alert('Error accessing cameras. Please try again.');
                }
            }

            async function startCamera(deviceId) {
                if (video.srcObject) {
                    video.srcObject.getTracks().forEach(track => track.stop());
                }

                try {
                    const stream = await navigator.mediaDevices.getUserMedia({
                        video: { deviceId: { exact: deviceId } }
                    });
                    video.srcObject = stream;
                } catch (error) {
                    console.error('Error starting the video stream:', error);
                    alert('Unable to start the selected camera.');
                }
            }
        </script>
    </body>
    </html>
    """
    
    # Create and open server the file using http server by python, Yes I know you are waiting for this shit really hard
    with open("index.html", "w") as f:
        f.write(html_content)

 
    print("Serving the HTML page at http://localhost:8000")
    os.chdir(os.getcwd())  
    httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()


def main():
    install_packages()  
    start_ffmpeg() 
    time.sleep(2)  
    serve_html() 

if __name__ == "__main__":
    main()
