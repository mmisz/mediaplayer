import os
import subprocess
from flask import Flask, render_template, redirect, request, session, flash
from builtins import zip

app = Flask(__name__)
app.secret_key = 'very_secret_key_2222'

CURRENT_IMAGE = None
HOME_DIR = "/var/www/html/mediaplayer/static/images"

def get_images(catalog_path_relative):
    catalog_path='/var/www/html/mediaplayer'+catalog_path_relative
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

@app.route('/images', methods=['POST', 'GET'])
def images():
    if 'dir_path' in request.form:
        session['dir_path'] = request.form.get('dir_path')
    #else:
    #    session['dir_path'] = None
    dir_path = session['dir_path']
    # List all images in the IMAGE_DIR directory
    image_files = get_images(dir_path)
    thumbnails = generate_thumbnails(image_files)
    # Zip the image files and their corresponding thumbnails together
    image_data = zip(image_files, thumbnails)
    return render_template('images.html', image_data=image_data, title='images', h1 = 'Albumy zdjęć', dir_path=dir_path)

@app.route('/movies')
def movies():
    
    return 0

@app.route('/close')
def close():
    global CURRENT_IMAGE
    # Close the currently displayed image
    if CURRENT_IMAGE is not None:
        os.system("pkill feh")
        CURRENT_IMAGE = None

    return redirect('/images')

@app.route('/display/<image>')
def display(image):
    global CURRENT_IMAGE
    # Close the currently displayed image
    if CURRENT_IMAGE is not None:
        os.system("pkill feh")
    # Set the CURRENT_IMAGE variable to the new image
    CURRENT_IMAGE = image
    image_path = '/var/www/html/mediaplayer/'+session['dir_path']+'/'+image
    show_image(image_path)
    return redirect('/images')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If user does not select file, browser also submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        save_dir = '/var/www/html/mediaplayer'+session['dir_path']
        # Save the uploaded file to the specified folder
        file.save(os.path.join(save_dir, file.filename))
        flash('File uploaded successfully')
        return redirect('/images')

#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0')