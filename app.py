from flask import Flask, request, render_template, send_from_directory
import boto3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# AWS SageMaker Endpoint Name (replace with your endpoint name)
ENDPOINT_NAME = "Custom-sklearn-model-2024-11-19-07-30-02"

# Initialize AWS SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name='ap-south-1')  # AWS Mumbai region

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Home page route:
    Displays the form for smartphone feature input
    and shows prediction results with an image.
    """
    prediction_text = None
    prediction_image = 'placeholder.svg'

    if request.method == 'POST':
        try:
            logger.info("Processing prediction request")
            # Collect input data from form
            features = [
                int(request.form['battery_power']),
                int(request.form['blue']),
                float(request.form['clock_speed']),
                int(request.form['dual_sim']),
                int(request.form['fc']),
                int(request.form['four_g']),
                int(request.form['int_memory']),
                float(request.form['m_dep']),
                int(request.form['mobile_wt']),
                int(request.form['n_cores']),
                int(request.form['pc']),
                int(request.form['px_height']),
                int(request.form['px_width']),
                int(request.form['ram']),
                int(request.form['sc_h']),
                int(request.form['sc_w']),
                int(request.form['talk_time']),
                int(request.form['three_g']),
                int(request.form['touch_screen']),
                int(request.form['wifi']),
            ]
            
            # Validate input features
            if any(f < 0 for f in features):
                raise ValueError("All features must be non-negative")
            
            # Convert input data into model's expected JSON format
            payload_json = json.dumps([features])
            
            # Call SageMaker endpoint
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=ENDPOINT_NAME,
                ContentType="application/json",
                Body=payload_json
            )
            
            # Parse the prediction response
            prediction = json.loads(response['Body'].read().decode())[0]
            logger.info(f"Prediction received: {prediction}")
            
            # Map prediction result to human-readable text and corresponding image
            if prediction == 0:
                prediction_text = "Budget mobile phone"
                prediction_image = "budget.jpg"
            elif prediction == 1:
                prediction_text = "Lower mid-range phone"
                prediction_image = "lower-mid.jpg"
            elif prediction == 2:
                prediction_text = "Upper mid-range phone"
                prediction_image = "upper-mid.jpg"
            elif prediction == 3:
                prediction_text = "Premium phone"
                prediction_image = "premium.png"
            else:
                prediction_text = "Unknown prediction result"
                prediction_image = "placeholder.svg"
        
        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            prediction_text = f"Input validation error: {ve}"
            prediction_image = "placeholder.svg"
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            prediction_text = f"Error: {e}"
            prediction_image = "placeholder.svg"

    return render_template('index.html', 
                         prediction=prediction_text,
                         prediction_image=prediction_image)

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon for the application."""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
