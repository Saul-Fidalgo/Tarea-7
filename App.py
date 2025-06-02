from flask import Flask, render_template, request
import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import re
from base64 import b64decode
import io

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CAPTURAS_FOLDER = 'capturas'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CAPTURAS_FOLDER, exist_ok=True)

# Ruta local a Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def procesar_imagen(ruta_imagen):
    img = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    texto = pytesseract.image_to_string(img_bin, config='--psm 6')
    return texto.strip()

def interpretar_operacion(texto):
    texto = texto.lower().replace('x', '*').replace('×', '*').replace('÷', '/')
    expresion = re.findall(r'\d+|\+|\-|\*|\/', texto)

    if len(expresion) != 3:
        return None, None, None, None

    try:
        num1, operador, num2 = expresion
        resultado = eval(f"{num1}{operador}{num2}")
        tipo_operacion = {
            '+': 'Suma',
            '-': 'Resta',
            '*': 'Multiplicación',
            '/': 'División'
        }.get(operador, 'Desconocida')
        return num1, operador, num2, resultado, tipo_operacion
    except:
        return None, None, None, None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    # Opción 1: imagen subida
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        ruta = os.path.join(UPLOAD_FOLDER, imagen.filename)
        imagen.save(ruta)
    # Opción 2: imagen capturada
    elif 'imagen_capturada' in request.form:
        data_url = request.form['imagen_capturada']
        if data_url.startswith('data:image'):
            header, encoded = data_url.split(',', 1)
            binary_data = b64decode(encoded)
            image = Image.open(io.BytesIO(binary_data))
            ruta = os.path.join(CAPTURAS_FOLDER, 'captura.png')
            image.save(ruta)
        else:
            return "Error en la imagen base64"
    else:
        return "No se recibió imagen"

    texto = procesar_imagen(ruta)
    num1, operador, num2, resultado, tipo_operacion = interpretar_operacion(texto)

    return render_template('resultado.html', texto=texto, num1=num1, num2=num2, operador=operador, resultado=resultado, tipo_operacion=tipo_operacion)

if __name__ == '__main__':
    app.run(debug=True)

