from flask import Flask, request, render_template, send_from_directory, jsonify
import boto3
import json
import logging
from datetime import datetime
from utils import validate_features, preprocess_features, format_prediction_result
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# AWS SageMaker Endpoint Name (replace with your endpoint name)
ENDPOINT_NAME = Config.SAGEMAKER_ENDPOINT

# Initialize AWS SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=Config.AWS_REGION)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Home page route:
    Displays the form for smartphone feature input
    and shows prediction results with an image.
    """
    prediction_text = None
    prediction_image = 'placeholder.svg'
    confidence_score = None

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
            is_valid, error_message = validate_features(features)
            if not is_valid:
                raise ValueError(error_message)
            
            # Preprocess features
            processed_features = preprocess_features(features)
            
            # Convert input data into model's expected JSON format
            payload_json = json.dumps([processed_features])
            
            # Call SageMaker endpoint
            start_time = datetime.now()
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=ENDPOINT_NAME,
                ContentType="application/json",
                Body=payload_json
            )
            end_time = datetime.now()
            
            # Parse the prediction response
            prediction = json.loads(response['Body'].read().decode())[0]
            prediction_time = (end_time - start_time).total_seconds() * 1000
            
            logger.info(f"Prediction received: {prediction} in {prediction_time:.2f}ms")
            
            # Get prediction result and image
            prediction_text, prediction_image = format_prediction_result(prediction)
            
            # Calculate confidence score (mock - in real scenario, model would provide this)
            confidence_score = calculate_confidence_score(features, prediction)
        
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
                         prediction_image=prediction_image,
                         confidence_score=confidence_score)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    API endpoint for single prediction.
    Accepts JSON input and returns JSON response.
    """
    try:
        data = request.get_json()
        if not data or 'features' not in data:
            return jsonify({'error': 'Missing features array'}), 400
        
        features = data['features']
        
        # Validate input features
        is_valid, error_message = validate_features(features)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Preprocess features
        processed_features = preprocess_features(features)
        
        # Convert to model format
        payload_json = json.dumps([processed_features])
        
        # Call SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=payload_json
        )
        
        # Parse response
        prediction = json.loads(response['Body'].read().decode())[0]
        prediction_text, prediction_image = format_prediction_result(prediction)
        
        return jsonify({
            'prediction': prediction,
            'prediction_text': prediction_text,
            'prediction_image': prediction_image,
            'confidence_score': calculate_confidence_score(features, prediction),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"API prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-predict', methods=['POST'])
def api_batch_predict():
    """
    API endpoint for batch predictions.
    Accepts multiple feature arrays and returns predictions for all.
    """
    try:
        data = request.get_json()
        if not data or 'features_list' not in data:
            return jsonify({'error': 'Missing features_list array'}), 400
        
        features_list = data['features_list']
        if not isinstance(features_list, list) or len(features_list) == 0:
            return jsonify({'error': 'features_list must be a non-empty array'}), 400
        
        if len(features_list) > 100:  # Limit batch size
            return jsonify({'error': 'Batch size cannot exceed 100'}), 400
        
        results = []
        for i, features in enumerate(features_list):
            try:
                # Validate features
                is_valid, error_message = validate_features(features)
                if not is_valid:
                    results.append({
                        'index': i,
                        'error': error_message
                    })
                    continue
                
                # Preprocess features
                processed_features = preprocess_features(features)
                
                # Convert to model format
                payload_json = json.dumps([processed_features])
                
                # Call SageMaker endpoint
                response = sagemaker_runtime.invoke_endpoint(
                    EndpointName=ENDPOINT_NAME,
                    ContentType="application/json",
                    Body=payload_json
                )
                
                # Parse response
                prediction = json.loads(response['Body'].read().decode())[0]
                prediction_text, prediction_image = format_prediction_result(prediction)
                
                results.append({
                    'index': i,
                    'prediction': prediction,
                    'prediction_text': prediction_text,
                    'prediction_image': prediction_image,
                    'confidence_score': calculate_confidence_score(features, prediction)
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'total_processed': len(features_list),
            'successful_predictions': len([r for r in results if 'error' not in r]),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    """
    try:
        # Test SageMaker endpoint connectivity
        response = sagemaker_runtime.describe_endpoint(EndpointName=ENDPOINT_NAME)
        endpoint_status = response['EndpointStatus']
        
        return jsonify({
            'status': 'healthy' if endpoint_status == 'InService' else 'degraded',
            'endpoint_status': endpoint_status,
            'timestamp': datetime.now().isoformat(),
            'version': '2.2.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'version': '2.2.0'
        }), 500

def calculate_confidence_score(features, prediction):
    """
    Calculate a mock confidence score based on feature values.
    In a real scenario, the model would provide confidence scores.
    """
    # Simple heuristic based on feature values
    battery_power = features[0]
    ram = features[13]
    clock_speed = features[2]
    
    # Higher values generally indicate better phones
    base_score = min(100, (battery_power / 5000) * 30 + (ram / 8000) * 40 + (clock_speed / 3) * 30)
    
    # Add some randomness to make it realistic
    import random
    random.seed(sum(features) + prediction)
    variation = random.uniform(-10, 10)
    
    return max(0, min(100, base_score + variation))

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon for the application."""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=app.config['DEBUG'])
