from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os
import random
from models import db, User
from typing import Dict, Any
from PIL import Image
import rembg

app = Flask(__name__)

CORS(app)

app.config["CORS_HEADERS"] = "Content-Type"
app.config['UPLOAD_FOLDER'] = 'images/uploads/'
app.config['CORS_ORIGINS'] = "localhost"
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://jasik:Rahmat2005@mysql-jasik.alwaysdata.net/jasik_studyamerica'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


def proccess_image(filepath, filename, remove_bg=False):
    image = Image.open(filepath)
    bgs = os.listdir('images/bgs')
    random_bg = random.choice(bgs)
    path_to_bg = os.path.join('images/bgs', random_bg)
    bg = Image.open(path_to_bg)
    if remove_bg:
        image = rembg.remove(image, alpha_matting=True)

    random_xy = random.randint(
        0, bg.size[0] - image.size[0]), random.randint(0, bg.size[1] - image.size[1])
    bg.paste(image, random_xy, image)
    bg.save(os.path.join(
        app.config["UPLOAD_FOLDER"], f"{filename}_processed.png"))

    return bg


def save_photo(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath, filename
    return None


@app.route('/images/uploads/<path:filename>', methods=['GET'])
def uploaded_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/images/<path:filename>', methods=['GET'])
def get_image(filename):
    return render_template('image.html', filename=filename, title='Image', url='https://rakhmat.ninja/images/uploads/' + filename, og_image='https://rakhmat.ninja/images/uploads/' + filename, og_title='Image', og_description='Image', og_url='https://rakhmat.ninja/images/uploads/' + filename, og_type='image', og_site_name='Image')


@app.route('/user', methods=['POST'])
def upload_user():

    email = request.form['email']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Пользователь уже существует"}), 409

    data: Dict[str, str] = {
        "name": request.form['name'],
        "email": request.form['email'],
        "phone": request.form['phone'],
        "studyPlan": request.form['studyPlan'],
        "studyProgram": request.form['studyProgram'],
        "factors": request.form['factors'],
        "campus": request.form['campus'],
        "rembg": True if request.form['rembg'] == 'true' else False,
    }

    photo = request.files['photo']
    photo_path, filename = save_photo(photo)
    if photo_path:
        data['photo'] = photo_path
    else:
        return jsonify({"message": "Неверный формат фото"}), 400

    try:
        data['processed_photo'] = os.path.join(
            app.config["UPLOAD_FOLDER"], f"{filename}_processed.png")
        new_user = User(**data)
        proccess_image(photo_path, filename=filename, remove_bg=(
            not not data['rembg'])).save(data['processed_photo'])
        db.session.add(new_user)
        db.session.commit()
        response = jsonify(
            {"filepath": data['processed_photo'], "message": "Пользователь успешно добавлен"})
        response.status_code = 200
        response.headers.add('Access-Control-Allow-Origin',
                             '*')
        return response

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Произошла ошибка"}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8400, host='::')
