"""
Simple test suite for the Mobile Price Predictor application.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from app import app
from utils import validate_features, preprocess_features, format_prediction_result

class TestMobilePricePredictor(unittest.TestCase):
    """Test cases for the Mobile Price Predictor application."""
    
    def setUp(self):
        """Set up test client."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page_get(self):
        """Test that home page loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Smartphone Price Predictor', response.data)
    
    def test_favicon_route(self):
        """Test favicon route."""
        response = self.app.get('/favicon.ico')
        self.assertEqual(response.status_code, 200)
    
    def test_validate_features_valid(self):
        """Test feature validation with valid data."""
        features = [1000, 1, 1.5, 1, 5, 1, 16, 0.1, 150, 4, 8, 1000, 2000, 2000, 10, 5, 10, 1, 1, 1]
        is_valid, message = validate_features(features)
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
    
    def test_validate_features_invalid_length(self):
        """Test feature validation with invalid length."""
        features = [1000, 1, 1.5]  # Too short
        is_valid, message = validate_features(features)
        self.assertFalse(is_valid)
        self.assertIn("Expected 20 features", message)
    
    def test_validate_features_negative(self):
        """Test feature validation with negative values."""
        features = [1000, -1, 1.5, 1, 5, 1, 16, 0.1, 150, 4, 8, 1000, 2000, 2000, 10, 5, 10, 1, 1, 1]
        is_valid, message = validate_features(features)
        self.assertFalse(is_valid)
        self.assertIn("non-negative", message)
    
    def test_preprocess_features(self):
        """Test feature preprocessing."""
        features = [1000, 1, 1.5, 1, 5, 1, 16, 0.1, 150, 4, 8, 1000, 2000, 2000, 10, 5, 10, 1, 1, 1]
        processed = preprocess_features(features)
        self.assertEqual(len(processed), 20)
        self.assertIsInstance(processed[2], float)  # clock_speed
        self.assertIsInstance(processed[7], float)  # m_dep
        self.assertIsInstance(processed[0], int)    # battery_power
    
    def test_format_prediction_result(self):
        """Test prediction result formatting."""
        text, image = format_prediction_result(0)
        self.assertEqual(text, "Budget mobile phone")
        self.assertEqual(image, "budget.jpg")
        
        text, image = format_prediction_result(3)
        self.assertEqual(text, "Premium phone")
        self.assertEqual(image, "premium.png")
        
        text, image = format_prediction_result(99)  # Invalid prediction
        self.assertEqual(text, "Unknown prediction result")
        self.assertEqual(image, "placeholder.svg")

if __name__ == '__main__':
    unittest.main() 