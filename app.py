from flask import Flask, render_template, request, jsonify
from keras.utils import load_img, img_to_array
from keras.models import load_model
import numpy as np
import os

# Load trained model
model = load_model('models/generalModel.h5')
benign = load_model('models/benignModel.h5')
cancerous = load_model('models/cancerousModel.h5')
vascular = load_model('models/vascModel.h5')

def preprocess_image(img_path):
    img = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
disease_types = ['Benign (noncancerous) lesion', 'Precancerous or cancerous lesion', 'Vascular lesion']
benign_types = ['atypical nevi', 'becker nevus', 'unclassified benign skin lesion', 'blue nevus', 'congenital nevus', 'dermatofibroma', 'halo-nevus', 'melanocytic nevi']
cancerous_types = ['basal cell carcinoma', 'Bowen\'s disease', 'melanoma']
vascular_types = ['angiokeratomas', 'angiomas', 'kaposi sarcoma', 'pyogenic granulomas', 'telangiectasias', 'unclassified vascular lesion', 'venous malformation']

@app.route('/')
def index():
    return render_template('index.html')
@app.route("/diseaseTypes", methods=["GET", "POST"])
def diseaseTypes():
    return render_template('diseaseTypes.html')

@app.route("/findDermatologist", methods=["GET", "POST"])
def findDermatologist():
    return render_template('findDermatologist.html')
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    # Get the uploaded image file
    image = request.files['image']
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    print(image_path)
    image.save(image_path)

    # preprocess the image and make a prediction
    genPrediction = model.predict(preprocess_image(image_path))

    # Get the predicted disease type and probability
    category = np.argmax(genPrediction)
    genProbability = float(genPrediction[0][category])

    # Get the predicted disease type as a string
    if(category == 0):
        #run benign model
        benignPrediction = benign.predict(preprocess_image(image_path))
        disease = np.argmax(benignPrediction)
        probability = float(benignPrediction[0][disease])
    elif(category == 1):
        #run cancerous model
        cancerousPrediction = cancerous.predict(preprocess_image(image_path))
        disease = np.argmax(cancerousPrediction)
        probability = float(cancerousPrediction[0][disease])
    else:
        #run vascular model
        vascularPrediction = vascular.predict(preprocess_image(image_path))
        disease = np.argmax(vascularPrediction)
        probability = float(vascularPrediction[0][disease])
    
    if(genProbability < 0.6):
    #run the model for the next highest category if the probability is less than 60%
        if(category == 0):
            #run next highest category from genPrediction
            if(genPrediction[0][1] > genPrediction[0][2]):
                #run cancerous model
                category2 = 1
                c2_prob = float(genPrediction[0][1])
                cancerousPrediction = cancerous.predict(preprocess_image(image_path))
                disease_2 = np.argmax(cancerousPrediction)
                d2_prob = float(cancerousPrediction[0][disease_2])
            else:
                #run vascular model
                category2 = 2
                c2_prob = float(genPrediction[0][2])
                vascularPrediction = vascular.predict(preprocess_image(image_path))
                disease_2 = np.argmax(vascularPrediction)
                d2_prob = float(vascularPrediction[0][disease_2])
        elif(category == 1):
            #run next highest category from genPrediction
            if(genPrediction[0][0] > genPrediction[0][2]):
                #run benign model
                category2 = 0
                c2_prob = float(genPrediction[0][0])
                benignPrediction = benign.predict(preprocess_image(image_path))
                disease_2 = np.argmax(benignPrediction)
                d2_prob = float(benignPrediction[0][disease_2])
            else:
                #run vascular model
                category2 = 2
                c2_prob = float(genPrediction[0][2])
                vascularPrediction = vascular.predict(preprocess_image(image_path))
                disease_2 = np.argmax(vascularPrediction)
                d2_prob = float(vascularPrediction[0][disease_2])
        else:
            #run next highest category from genPrediction
            if(genPrediction[0][0] > genPrediction[0][1]):
                #run benign model
                category2 = 0
                c2_prob = float(genPrediction[0][0])
                benignPrediction = benign.predict(preprocess_image(image_path))
                disease_2 = np.argmax(benignPrediction)
                d2_prob = float(benignPrediction[0][disease_2])
            else:
                #run cancerous model
                category2 = 1
                c2_prob = float(genPrediction[0][1])
                cancerousPrediction = cancerous.predict(preprocess_image(image_path))
                disease_2 = np.argmax(cancerousPrediction)
                d2_prob = float(cancerousPrediction[0][disease_2])
    else:
        #if the probability is greater than 60%, set the second category to the same as the first and choose the next highest disease type
        category2 = category
        c2_prob = genProbability
        #find the next highest disease in the array of the original prediciton
        if(category == 0):
            #find second highest max in benignPrediction
            disease_2 = np.argpartition(benignPrediction[0], -2)[-2]
            d2_prob = float(benignPrediction[0][disease_2])
        elif(category == 1):
            #find second highest max in cancerousPrediction
            disease_2 = np.argpartition(cancerousPrediction[0], -2)[-2]
            d2_prob = float(cancerousPrediction[0][disease_2])
        else:
            #find second highest max in vascularPrediction
            disease_2 = np.argpartition(vascularPrediction[0], -2)[-2]
            d2_prob = float(vascularPrediction[0][disease_2])



    # Render the result template with the predicted disease type and probability
    return jsonify({
        'category': int(category),
        'probability': genProbability,
        'disease': int(disease),
        'disease_prob': probability,
        'category2': int(category2),
        'c2_prob': c2_prob,
        'disease2': int(disease_2),
        'd2_prob': d2_prob
    })
if __name__ == '__main__':
    app.run()
