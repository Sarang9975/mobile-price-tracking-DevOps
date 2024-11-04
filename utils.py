"""
Utility functions for the Mobile Price Predictor application.
"""

import logging
from typing import List, Tuple, Union
from config import Config

logger = logging.getLogger(__name__)

def validate_features(features: List[Union[int, float]]) -> Tuple[bool, str]:
    """
    Validate input features for mobile phone prediction.
    
    Args:
        features: List of feature values
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(features) != 20:
        return False, f"Expected 20 features, got {len(features)}"
    
    # Check for negative values
    if any(f < 0 for f in features):
        return False, "All features must be non-negative"
    
    # Validate specific feature ranges
    battery_power = features[0]
    if not (Config.MIN_BATTERY_POWER <= battery_power <= Config.MAX_BATTERY_POWER):
        return False, f"Battery power must be between {Config.MIN_BATTERY_POWER} and {Config.MAX_BATTERY_POWER}"
    
    clock_speed = features[2]
    if not (Config.MIN_CLOCK_SPEED <= clock_speed <= Config.MAX_CLOCK_SPEED):
        return False, f"Clock speed must be between {Config.MIN_CLOCK_SPEED} and {Config.MAX_CLOCK_SPEED}"
    
    ram = features[13]
    if not (Config.MIN_RAM <= ram <= Config.MAX_RAM):
        return False, f"RAM must be between {Config.MIN_RAM} and {Config.MAX_RAM}"
    
    return True, ""

def preprocess_features(features: List[Union[int, float]]) -> List[Union[int, float]]:
    """
    Preprocess features before sending to model.
    
    Args:
        features: Raw feature values
        
    Returns:
        Preprocessed feature values
    """
    # Convert to appropriate types
    processed = []
    for i, feature in enumerate(features):
        if i in [2, 7]:  # clock_speed and m_dep are floats
            processed.append(float(feature))
        else:
            processed.append(int(feature))
    
    logger.info(f"Preprocessed {len(processed)} features")
    return processed

def format_prediction_result(prediction: int) -> Tuple[str, str]:
    """
    Format prediction result for display.
    
    Args:
        prediction: Model prediction (0-3)
        
    Returns:
        Tuple of (prediction_text, prediction_image)
    """
    prediction_map = {
        0: ("Budget mobile phone", "budget.jpg"),
        1: ("Lower mid-range phone", "lower-mid.jpg"),
        2: ("Upper mid-range phone", "upper-mid.jpg"),
        3: ("Premium phone", "premium.png")
    }
    
    return prediction_map.get(prediction, ("Unknown prediction result", "placeholder.svg")) 