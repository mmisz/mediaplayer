import os
import subprocess
from flask import Flask, render_template, redirect

app = Flask(__name__)

HOME_DIR = "/var/www/html/mediaplayer/static/images"
CURRENT_IMAGE = None

def get_images(path):
    extensions = ['.jpg', '.png', '.bmp', 'jpeg']
    image_files = [f for f in os.listdir(HOME_DIR) if os.path.isfile(os.path.join(HOME_DIR, f)) and f.endswith(tuple(extensions))]
def show_image(image_path):
    subprocess.Popen(['feh', '-F', '-Z', image_path])

@app.route('/')
def index():
    global CURRENT_IMAGE
    os.environ['DISPLAY'] = ':0' # set the DISPLAY environment variable
    # List all images in the IMAGE_DIR directory
    image_files = get_images(HOME_DIR)
    return render_template('index.html', image_files=image_files, current_image=CURRENT_IMAGE)
@app.route('/close')
def close():
    # Close the currently displayed image
    if CURRENT_IMAGE is not None:
        os.system("pkill feh")

    return redirect('/')
@app.route('/display/<image>')
def display(image):
    global CURRENT_IMAGE
    # Close the currently displayed image
    if CURRENT_IMAGE is not None:
        os.system("pkill feh")
    # Set the CURRENT_IMAGE variable to the new image
    CURRENT_IMAGE = image
    image_path = "/var/www/html/mediaplayer/static/images/"+image
    show_image(image_path)
    return redirect('/')

#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0')
