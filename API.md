# Mobile Price Predictor API Documentation

## Overview

The Mobile Price Predictor API is a Flask-based web service that predicts mobile phone price categories using a machine learning model deployed on AWS SageMaker.

## Base URL

```
http://localhost:80
```

## Endpoints

### 1. Home Page (GET /)

**Description**: Main application interface for inputting mobile phone specifications.

**Method**: `GET`

**Response**: HTML page with input form

**Example**:
```bash
curl http://localhost:80/
```

### 2. Prediction (POST /)

**Description**: Submit mobile phone specifications and receive price category prediction.

**Method**: `POST`

**Content-Type**: `application/x-www-form-urlencoded`

**Parameters**:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| battery_power | integer | Battery capacity in mAh | 1000 |
| blue | integer | Bluetooth support (0/1) | 1 |
| clock_speed | float | CPU clock speed in GHz | 1.5 |
| dual_sim | integer | Dual SIM support (0/1) | 1 |
| fc | integer | Front camera in MP | 5 |
| four_g | integer | 4G support (0/1) | 1 |
| int_memory | integer | Internal memory in GB | 16 |
| m_dep | float | Mobile depth in cm | 0.1 |
| mobile_wt | integer | Mobile weight in grams | 150 |
| n_cores | integer | Number of CPU cores | 4 |
| pc | integer | Primary camera in MP | 8 |
| px_height | integer | Pixel resolution height | 1000 |
| px_width | integer | Pixel resolution width | 2000 |
| ram | integer | RAM in MB | 2000 |
| sc_h | integer | Screen height in cm | 10 |
| sc_w | integer | Screen width in cm | 5 |
| talk_time | integer | Talk time in hours | 10 |
| three_g | integer | 3G support (0/1) | 1 |
| touch_screen | integer | Touch screen support (0/1) | 1 |
| wifi | integer | WiFi support (0/1) | 1 |

**Response**: HTML page with prediction result and image

**Example Request**:
```bash
curl -X POST http://localhost:80/ \
  -d "battery_power=1000&blue=1&clock_speed=1.5&dual_sim=1&fc=5&four_g=1&int_memory=16&m_dep=0.1&mobile_wt=150&n_cores=4&pc=8&px_height=1000&px_width=2000&ram=2000&sc_h=10&sc_w=5&talk_time=10&three_g=1&touch_screen=1&wifi=1"
```

### 3. Favicon (GET /favicon.ico)

**Description**: Serve the application favicon.

**Method**: `GET`

**Response**: Favicon image file

**Example**:
```bash
curl http://localhost:80/favicon.ico
```

## Prediction Categories

The API returns one of four price categories:

1. **Budget mobile phone** (0) - Affordable smartphones with essential features
2. **Lower mid-range phone** (1) - Good value devices with balanced features
3. **Upper mid-range phone** (2) - Premium features at competitive prices
4. **Premium phone** (3) - Top-tier smartphones with cutting-edge features

## Error Handling

The API includes comprehensive error handling:

- **Validation Errors**: Input validation for feature ranges and types
- **AWS Errors**: SageMaker endpoint connection issues
- **General Errors**: Unexpected application errors

All errors return user-friendly messages and appropriate HTTP status codes.

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Authentication

No authentication is required for the current endpoints. Consider adding authentication for production deployments.

## CORS

CORS is not configured by default. Configure CORS headers if the API needs to be accessed from different domains.

## Health Check

The application includes a health check endpoint for monitoring:

```bash
curl http://localhost:80/
```

A successful response (HTTP 200) indicates the service is healthy.

## Deployment

The application can be deployed using:

1. **Direct Python execution**: `python app.py`
2. **Docker**: `docker-compose up`
3. **Production server**: `gunicorn app:app`

## Monitoring

The application includes structured logging for monitoring:

- Request processing logs
- Prediction results
- Error logs with stack traces
- AWS SageMaker interaction logs

## Support

For issues and questions, please refer to the project documentation or create an issue in the repository. 