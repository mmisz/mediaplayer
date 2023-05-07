import os
import subprocess
from flask import Flask, render_template, redirect, request, session, flash
from builtins import zip

app = Flask(__name__)
app.secret_key = 'very_secret_key_2222'

CURRENT_IMAGE = None
HOME_DIR = "/var/www/html/mediaplayer/"
def get_current_album():
    return '/' + '/'.join(session['dir_path'].split('/')[3:])
   
def get_images(catalog_path_relative):
    catalog_path='/var/www/html/mediaplayer'+catalog_path_relative
    extensions = ['.jpg', '.png', '.bmp', 'jpeg', 'JPG']
    image_files = [f for f in os.listdir(catalog_path) if os.path.isfile(os.path.join(catalog_path, f)) and f.endswith(tuple(extensions))]
    return image_files
def get_thumbnails(thumbnails_path):
    extensions = ['.jpg']
    image_files = [f for f in os.listdir(thumbnails_path) if os.path.isfile(os.path.join(thumbnails_path, f)) and f.endswith(tuple(extensions))]
    return image_files
def compare_with_thumbnails(images, thumbnails):
    thumbnails_clear = []
    for thumbnail in thumbnails:
        thumbnails_clear.append(thumbnail.split('.')[0])
    for image in images:
        image_clear = image.split('.')[0]
        if image_clear not in thumbnails_clear:
            return False
    return True

def generate_thumbnails(image_files):
    
    dir_for_thumbnails = '/var/www/html/mediaplayer/static/images/thumbnails'+get_current_album()
    dir_with_images = '/var/www/html/mediaplayer' + session['dir_path'] 
    thumbnails = get_thumbnails(dir_for_thumbnails)
    if compare_with_thumbnails(image_files,thumbnails) == False:
        app.logger.error('generuje')
        for image_file in image_files:
            thumbnail_path = os.path.join(dir_for_thumbnails, image_file.split('.')[0]+'.jpg')
            subprocess.call(['convert', '-thumbnail', '250', os.path.join(dir_with_images, image_file), thumbnail_path])
            thumbnails.append(image_file.split('.')[0]+'.jpg')
            app.logger.error('generuje')
    app.logger.error('nie generuje')
    return thumbnails

def show_image(image_path):
    subprocess.Popen(['feh', '-F', '-Z', image_path])


@app.route('/')
def index():
    os.environ['DISPLAY'] = ':0' # set the DISPLAY environment variable
    return render_template('index.html', title = 'home')

@app.route('/images', methods=['POST', 'GET'])
def images():
    #app.logger.error('Weszlo')
    if 'dir_path' in request.form:
        #app.logger.error(request.form.get('dir_path'))
        session['dir_path'] = request.form.get('dir_path')
    #else:
    #    session['dir_path'] = None
    dir_path = session['dir_path']
    image_dir = '/var/www/html/mediaplayer' + dir_path
    folders = [name for name in os.listdir(image_dir) if os.path.isdir(os.path.join(image_dir, name)) and name != 'thumbnails']
    folder_paths = []
    for folder in folders:
        folder_paths.append(os.path.join('/'.join(dir_path.split('/')[2:]),folder))
    folder_data = zip(folders, folder_paths)
    # List all images in the IMAGE_DIR directory
    image_files = get_images(dir_path)
    thumbnails = generate_thumbnails(image_files)
    thumbnail_paths=[]
    for thumbnail in thumbnails:
        thumbnail_paths.append(os.path.join('/images/thumbnails'+get_current_album(),thumbnail))
    # Zip the image files and their corresponding thumbnails together
    image_data = zip(image_files, thumbnail_paths)
    dir_path=get_current_album()
    prev_folder = '/'.join(dir_path.split('/')[:-1])
    return render_template('images.html', image_data=image_data, title='images', h1 = 'Albumy zdjęć', dir_path=dir_path.split('/'), folder_data=folder_data, prev_folder=prev_folder )

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
        flash('File uploaded successfully', 'success')
        return redirect('/images')

@app.route('/delete', methods=['POST'])
def delete():
    filename = request.form['filename']
    # Get the filename from the form data
    file_to_remove = '/var/www/html/mediaplayer'+session['dir_path']+'/'+filename
    thumbnail_to_remove = '/var/www/html/mediaplayer/static/images/thumbnails'+get_current_album()+'/'+filename.split('.')[0]+'.jpg'
    os.remove(file_to_remove)
    os.remove(thumbnail_to_remove)

    return redirect('/images')

@app.route("/create-folder", methods=["POST"])
def create_folder():
    folder_name = request.form.get("folder-name")
    if not folder_name:
        flash("Please enter a folder name", 'error')
        return redirect('/images')
    
    folder_path = os.path.join('/var/www/html/mediaplayer'+session['dir_path'], folder_name)
    thumbnails_folder_path = os.path.join('/var/www/html/mediaplayer/static/images/thumbnails'+get_current_album(), folder_name)
    if os.path.isdir(folder_path):
        flash(f"{folder_name} already exists", 'warning')
        return redirect('/images')
    os.makedirs(thumbnails_folder_path)
    os.makedirs(folder_path)
    #app.logger.error(thumbnails_folder_path)
    
    flash(f"{folder_name} created successfully", 'success')
    return redirect('/images')
#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0')