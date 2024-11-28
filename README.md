# Mobile Price Predictor using AWS SageMaker

A Flask web application that predicts mobile phone price categories using a machine learning model deployed on AWS SageMaker.

## Features

- **Smartphone Price Classification**: Predicts if a phone is Budget, Lower Mid-range, Upper Mid-range, or Premium
- **Interactive Web Interface**: User-friendly form for inputting phone specifications
- **AWS SageMaker Integration**: Uses deployed ML model for real-time predictions
- **Input Validation**: Comprehensive validation of user inputs
- **Error Handling**: Robust error handling with detailed logging
- **Responsive Design**: Modern, mobile-friendly UI

## Recent Updates

### v2.1.0 - Enhanced Error Handling & Validation
- Added comprehensive input validation for all features
- Implemented structured logging throughout the application
- Added feature range validation (battery power, RAM, clock speed)
- Improved error messages and user feedback

### v2.0.0 - Code Refactoring & Configuration
- Separated configuration into dedicated config.py module
- Created utility functions for data validation and preprocessing
- Added type hints for better code maintainability
- Updated dependencies to latest stable versions

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Mobile-Price-Predictor-using-AWS-Sagemaker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (optional):
```bash
export AWS_REGION=ap-south-1
export SAGEMAKER_ENDPOINT=your-endpoint-name
export FLASK_DEBUG=True
```

4. Run the application:
```bash
python app.py
```

## Usage

1. Open your browser and navigate to `http://localhost:80`
2. Fill in the smartphone specifications form
3. Click "Predict Price Category" to get the result
4. View the prediction with corresponding category image

## Model Features

The model accepts 20 features including:
- Battery Power (mAh)
- Bluetooth support
- Clock Speed (GHz)
- Dual SIM support
- Front Camera (MP)
- 4G support
- Internal Memory (GB)
- Mobile Weight (g)
- Number of Cores
- Primary Camera (MP)
- Pixel Resolution
- RAM (MB)
- Screen Dimensions
- Talk Time (hours)
- 3G support
- Touch Screen
- WiFi support

## Architecture

- **Frontend**: HTML/CSS with responsive design
- **Backend**: Flask web framework
- **ML Model**: AWS SageMaker endpoint
- **Validation**: Custom validation utilities
- **Configuration**: Environment-based configuration management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.




