from flask import render_template, request, Blueprint
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from werkzeug.utils import secure_filename
import json

app_bp = Blueprint("app", __name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = load_model('best_model.keras')

with open("class_indices.json", "r", encoding="utf-8") as f:
    classes = json.load(f)  # Ex: {"futebol": 0, "basquete": 1}


index_to_class = {int(v): k for k, v in classes.items()}


@app_bp.route('/')
def index():
    return render_template('index.html')

@app_bp.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400

    file = request.files['file']
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        img = image.load_img(filepath, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        prediction = model.predict(img_array)
        predicted_index = int(np.argmax(prediction))
        predicted_class = index_to_class.get(predicted_index, "Classe desconhecida")

        return f'A imagem foi classificada como: {predicted_class}'

    except Exception as e:
        return f'Erro ao processar a imagem: {str(e)}', 500
