import os
import subprocess
from flask import Flask, render_template, redirect
from builtins import zip

app = Flask(__name__)

CURRENT_IMAGE = None
HOME_DIR = "/var/www/html/mediaplayer/static/images"

def get_images(catalog_path):
    extensions = ['.jpg', '.png', '.bmp', 'jpeg', 'JPG']
    image_files = [f for f in os.listdir(catalog_path) if os.path.isfile(os.path.join(catalog_path, f)) and f.endswith(tuple(extensions))]
    return image_files

def generate_thumbnails(image_files):
    thumbnails = []
    for image_file in image_files:
        thumbnail_path = os.path.join(HOME_DIR, 'thumbnails', f'{os.path.splitext(image_file)[0]}.jpg')
        subprocess.call(['convert', '-thumbnail', '250', os.path.join(HOME_DIR, image_file), thumbnail_path])
        thumbnails.append(os.path.relpath(thumbnail_path, HOME_DIR))
    return thumbnails

def show_image(image_path):
    subprocess.Popen(['feh', '-F', '-Z', image_path])

@app.route('/')
def index():
    os.environ['DISPLAY'] = ':0' # set the DISPLAY environment variable
    return render_template('index.html', title = 'home', h1 = 'Media Player')

@app.route('/images')
def images():
    # List all images in the IMAGE_DIR directory
    image_files = get_images(HOME_DIR)
    thumbnails = generate_thumbnails(image_files)
    # Zip the image files and their corresponding thumbnails together
    image_data = zip(image_files, thumbnails)
    return render_template('images.html', image_data=image_data, title='images', h1 = 'Albumy zdjęć')

@app.route('/movies')
def movies():
    
    return 0

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
    return redirect('/images')

#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0')