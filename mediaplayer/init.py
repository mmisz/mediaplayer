import os
import subprocess
from flask import Flask, render_template, redirect

app = Flask(__name__)

IMAGE_DIR = "/var/www/html/mediaplayer/static/images"
CURRENT_IMAGE = None

@app.route('/')
def index():
    global CURRENT_IMAGE
    # List all images in the IMAGE_DIR directory
    image_files = [f for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]
    return render_template('index.html', image_files=image_files, current_image=CURRENT_IMAGE)

@app.route('/display/<image>')
def display(image):
    global CURRENT_IMAGE
    os.environ['DISPLAY'] = ':0' # set the DISPLAY environment variable
    # Close the currently displayed image (if any)
    if CURRENT_IMAGE is not None:
        os.system("pkill feh")
    # Set the CURRENT_IMAGE variable to the new image
    CURRENT_IMAGE = image
    image_path = "/var/www/html/mediaplayer/static/images/"+image
    # Display the new image using feh
    retcode = subprocess.call(['feh', '-F', '-Z', image_path])
    if retcode != 0:
        app.logger.error('Error opening image: {}'.format(image_path))

    return redirect('/')

#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0')
