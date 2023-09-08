import os
from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

limiter = Limiter(
    app, 
    default_limits=["5 per minute"]
)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username == 'admin' and password == 'password':
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message='Authentication failed'), 401

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    if 'file' not in request.files:
        return jsonify(message='No file part'), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify(message='No selected file'), 400

    if file:
        # Securely save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(file_path)
            print(f"Saved file as {file_path}")  # Debugging: Check if file is saved correctly
            return jsonify(message='Image uploaded successfully', image_name=filename)
        except Exception as e:
            print(f"Error saving file: {str(e)}")  # Debugging: Print any exceptions that occur
            return jsonify(message='Error saving file'), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/list_uploaded_images')
@jwt_required()
@limiter.request_filter
def list_uploaded_images():
    uploaded_images = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(uploaded_images=uploaded_images)

if __name__ == '__main__':
     app.run(debug=True, port=5000, host='0.0.0.0')
