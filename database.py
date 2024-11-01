"""
Database module for caching predictions and managing user sessions.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)

class PredictionCache:
    """SQLite-based cache for storing prediction results."""
    
    def __init__(self, db_path: str = "predictions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create predictions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        feature_hash TEXT UNIQUE NOT NULL,
                        features TEXT NOT NULL,
                        prediction INTEGER NOT NULL,
                        prediction_text TEXT NOT NULL,
                        confidence_score REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_count INTEGER DEFAULT 1,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create user_sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        user_agent TEXT,
                        ip_address TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        prediction_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Create prediction_logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS prediction_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        feature_hash TEXT,
                        prediction INTEGER,
                        response_time_ms REAL,
                        success BOOLEAN,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_feature_hash ON predictions(feature_hash)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON predictions(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON user_sessions(session_id)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_feature_hash(self, features: List) -> str:
        """Generate a hash for the feature array."""
        feature_str = json.dumps(features, sort_keys=True)
        return hashlib.md5(feature_str.encode()).hexdigest()
    
    def cache_prediction(self, features: List, prediction: int, 
                        prediction_text: str, confidence_score: float = None) -> bool:
        """Cache a prediction result."""
        try:
            feature_hash = self.get_feature_hash(features)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if prediction already exists
                cursor.execute('''
                    SELECT id, access_count FROM predictions 
                    WHERE feature_hash = ?
                ''', (feature_hash,))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing prediction
                    cursor.execute('''
                        UPDATE predictions 
                        SET access_count = access_count + 1,
                            last_accessed = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (existing[0],))
                else:
                    # Insert new prediction
                    cursor.execute('''
                        INSERT INTO predictions 
                        (feature_hash, features, prediction, prediction_text, confidence_score)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (feature_hash, json.dumps(features), prediction, 
                          prediction_text, confidence_score))
                
                conn.commit()
                logger.info(f"Prediction cached successfully for hash: {feature_hash}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to cache prediction: {e}")
            return False
    
    def get_cached_prediction(self, features: List) -> Optional[Dict]:
        """Retrieve a cached prediction if it exists."""
        try:
            feature_hash = self.get_feature_hash(features)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT prediction, prediction_text, confidence_score, 
                           created_at, access_count
                    FROM predictions 
                    WHERE feature_hash = ?
                ''', (feature_hash,))
                
                result = cursor.fetchone()
                
                if result:
                    # Update access count and timestamp
                    cursor.execute('''
                        UPDATE predictions 
                        SET access_count = access_count + 1,
                            last_accessed = CURRENT_TIMESTAMP
                        WHERE feature_hash = ?
                    ''', (feature_hash,))
                    conn.commit()
                    
                    return {
                        'prediction': result[0],
                        'prediction_text': result[1],
                        'confidence_score': result[2],
                        'cached_at': result[3],
                        'access_count': result[4],
                        'from_cache': True
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve cached prediction: {e}")
            return None
    
    def create_user_session(self, session_id: str, user_agent: str = None, 
                           ip_address: str = None) -> bool:
        """Create a new user session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    (session_id, user_agent, ip_address, last_activity)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (session_id, user_agent, ip_address))
                
                conn.commit()
                logger.info(f"User session created: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            return False
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session activity timestamp and prediction count."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE user_sessions 
                    SET last_activity = CURRENT_TIMESTAMP,
                        prediction_count = prediction_count + 1
                    WHERE session_id = ?
                ''', (session_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to update session activity: {e}")
            return False
    
    def log_prediction(self, session_id: str, feature_hash: str, prediction: int,
                      response_time_ms: float, success: bool, error_message: str = None):
        """Log a prediction request for analytics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO prediction_logs 
                    (session_id, feature_hash, prediction, response_time_ms, 
                     success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, feature_hash, prediction, response_time_ms, 
                      success, error_message))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total predictions
                cursor.execute('SELECT COUNT(*) FROM predictions')
                total_predictions = cursor.fetchone()[0]
                
                # Cache hit rate (approximate)
                cursor.execute('SELECT SUM(access_count) FROM predictions')
                total_accesses = cursor.fetchone()[0] or 0
                
                # Recent predictions (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) FROM predictions 
                    WHERE created_at > datetime('now', '-1 day')
                ''')
                recent_predictions = cursor.fetchone()[0]
                
                # Average confidence score
                cursor.execute('''
                    SELECT AVG(confidence_score) FROM predictions 
                    WHERE confidence_score IS NOT NULL
                ''')
                avg_confidence = cursor.fetchone()[0] or 0
                
                return {
                    'total_predictions': total_predictions,
                    'total_accesses': total_accesses,
                    'recent_predictions_24h': recent_predictions,
                    'average_confidence': round(avg_confidence, 2),
                    'cache_size_mb': self._get_database_size()
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def cleanup_old_predictions(self, days: int = 30) -> int:
        """Remove predictions older than specified days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM predictions 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old predictions")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old predictions: {e}")
            return 0
    
    def _get_database_size(self) -> float:
        """Get database file size in MB."""
        try:
            import os
            size_bytes = os.path.getsize(self.db_path)
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0.0

# Global cache instance
prediction_cache = PredictionCache() 