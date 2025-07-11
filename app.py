from flask import *
import os
from werkzeug.utils import secure_filename
from keras.models import load_model
import numpy as np
from PIL import Image
import pyttsx3
app = Flask(__name__)

# Classes of trafic signs
classes = { 0:'Speed limit (20km/h)',
			1:'Speed limit (30km/h)',
			2:'Speed limit (50km/h)',
			3:'Speed limit (60km/h)',
			4:'Speed limit (70km/h)',
			5:'Speed limit (80km/h)',
			6:'End of speed limit (80km/h)',
			7:'Speed limit (100km/h)',
			8:'Speed limit (120km/h)',
			9:'No passing',
			10:'No passing veh over 3.5 tons',
			11:'Right-of-way at intersection',
			12:'Priority road',
			13:'Yield',
			14:'Stop',
			15:'No vehicles',
			16:'Vehicle > 3.5 tons prohibited',
			17:'No entry',
			18:'General caution',
			19:'Dangerous curve left',
			20:'Dangerous curve right',
			21:'Double curve',
			22:'Bumpy road',
			23:'Slippery road',
			24:'Road narrows on the right',
			25:'Road work',
			26:'Traffic signals',
			27:'Pedestrians',
			28:'Children crossing',
			29:'Bicycles crossing',
			30:'Beware of ice/snow',
			31:'Wild animals crossing',
			32:'End speed + passing limits',
			33:'Turn right ahead',
			34:'Turn left ahead',
			35:'Ahead only',
			36:'Go straight or right',
			37:'Go straight or left',
			38:'Keep right',
			39:'Keep left',
			40:'Roundabout mandatory',
			41:'End of no passing',
			42:'End no passing vehicle > 3.5 tons',
			43:'No Sign Detected'
            }

def image_processing(img):
	model = load_model('./model/traffic.h5')
	data=[]
	image = Image.open(img)
	image = image.resize((30,30))
	data.append(np.array(image))
	X_test=np.array(data)
	Y_pred = model.predict(X_test)
	return Y_pred

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template("login.html")
@app.route('/first', methods=['GET'])
def first():
    # Main page
    return render_template('first.html')

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']
        file_path = secure_filename(f.filename)
        f.save(file_path)
        # Make prediction
        result = image_processing(file_path)
        a = np.argmax(result)  # Get the index of the maximum probability

        result_text = "Predicted Traffic Sign is: " + classes[a]
        
        if os.path.exists(file_path):
            os.remove(file_path)  # Check if the file exists and then remove it

        engineio = pyttsx3.init()
        engineio.say(result_text)
        engineio.runAndWait()
        
        return result_text

    return None


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        file_path = os.path.join("uploads", secure_filename(file.filename))
        file.save(file_path)

        # Make prediction
        result = image_processing(file_path)

        if result < 43:
            prediction = "Predicted Traffic Sign is: " + classes[result]
        else:
            prediction = "No Sign Detected"

        os.remove(file_path)

        engineio = pyttsx3.init()
        engineio.say(prediction)
        engineio.runAndWait()

        return prediction

    return "Error in prediction"

@app.route('/performance')
def performance():
    return render_template("performance.html")

@app.route('/chart')
def chart():
    return render_template("chart.html")    

if __name__ == '__main__':
    app.run(debug=True)