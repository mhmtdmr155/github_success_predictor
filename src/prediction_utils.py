"""
Prediction Utilities
Helper functions for making predictions with confidence intervals
"""
import numpy as np
import pandas as pd


def calculate_prediction_interval(prediction, residual_std, confidence=0.95):
    """Calculate prediction interval for a single prediction"""
    # Z-score for confidence level
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_scores.get(confidence, 1.96)
    
    # Calculate interval
    margin = z * residual_std
    lower = max(0, prediction - margin)
    upper = prediction + margin
    
    return lower, upper, margin


def calculate_confidence_score(prediction, feature_dict, model_metadata=None):
    """Calculate confidence score based on input features and model performance"""
    # Get base confidence from model metadata if available
    if model_metadata and 'cv_scores' in model_metadata:
        cv_scores = model_metadata['cv_scores']
        if cv_scores:
            # Use best CV score as base
            best_cv = max([score.get('mean', 0.85) for score in cv_scores.values()])
            base_confidence = min(0.92, max(0.80, best_cv))
        else:
            base_confidence = 0.85
    else:
        base_confidence = 0.85
    
    # Adjust based on feature quality
    title_len = feature_dict.get('title_length', len(feature_dict.get('title', '')))
    duration = feature_dict.get('duration_minutes', 10)
    channel_subs = feature_dict.get('channel_subscribers', 100000)
    publish_hour = feature_dict.get('publish_hour', 18)
    
    confidence = base_confidence
    
    # Title quality
    if 50 <= title_len <= 60:
        confidence += 0.06
    elif 45 <= title_len <= 65:
        confidence += 0.03
    elif 40 <= title_len <= 70:
        confidence += 0.01
    else:
        confidence -= 0.04
    
    # Duration quality
    if 10 <= duration <= 15:
        confidence += 0.05
    elif 8 <= duration <= 20:
        confidence += 0.02
    elif 5 <= duration <= 30:
        confidence += 0.01
    else:
        confidence -= 0.03
    
    # Prime time
    if 18 <= publish_hour <= 21:
        confidence += 0.04
    
    # Channel size (larger channels have more predictable patterns)
    if channel_subs > 1000000:
        confidence += 0.03
    elif channel_subs > 100000:
        confidence += 0.02
    elif channel_subs > 10000:
        confidence += 0.01
    elif channel_subs < 10000:
        confidence -= 0.03
    
    # SEO score boost
    seo_score = feature_dict.get('seo_score', 0)
    if seo_score > 0.7:
        confidence += 0.03
    elif seo_score > 0.5:
        confidence += 0.01
    
    # Engagement potential boost
    engagement_score = feature_dict.get('engagement_potential_score', 0)
    if engagement_score > 0.8:
        confidence += 0.02
    
    # Clip to reasonable range
    confidence = max(0.75, min(0.95, confidence))
    
    return confidence


def estimate_prediction_accuracy(prediction, feature_dict):
    """Estimate prediction accuracy based on feature quality"""
    score = 0.0
    max_score = 0.0
    
    # Title quality (max 25 points)
    title_len = feature_dict.get('title_length', len(feature_dict.get('title', '')))
    if 50 <= title_len <= 60:
        score += 25
    elif 45 <= title_len <= 65:
        score += 18
    elif 40 <= title_len <= 70:
        score += 12
    elif 35 <= title_len <= 75:
        score += 6
    max_score += 25
    
    # Duration quality (max 20 points)
    duration = feature_dict.get('duration_minutes', 10)
    if 10 <= duration <= 15:
        score += 20
    elif 8 <= duration <= 20:
        score += 14
    elif 5 <= duration <= 30:
        score += 8
    max_score += 20
    
    # Prime time (max 18 points)
    publish_hour = feature_dict.get('publish_hour', 18)
    is_prime_time = feature_dict.get('is_prime_time', 0)
    if is_prime_time == 1 or (18 <= publish_hour <= 21):
        score += 18
    elif 17 <= publish_hour <= 22:
        score += 12
    max_score += 18
    
    # Channel size (max 15 points)
    channel_subs = feature_dict.get('channel_subscribers', 100000)
    if channel_subs > 1000000:
        score += 15
    elif channel_subs > 100000:
        score += 12
    elif channel_subs > 10000:
        score += 8
    max_score += 15
    
    # Tag count (max 10 points)
    tag_count = feature_dict.get('tag_count', 5)
    if 8 <= tag_count <= 12:
        score += 10
    elif 5 <= tag_count <= 15:
        score += 7
    elif tag_count > 0:
        score += 3
    max_score += 10
    
    # SEO score (max 12 points)
    seo_score = feature_dict.get('seo_score', 0)
    if seo_score > 0.7:
        score += 12
    elif seo_score > 0.5:
        score += 8
    elif seo_score > 0.3:
        score += 4
    max_score += 12
    
    # Calculate accuracy percentage
    accuracy = (score / max_score) * 100 if max_score > 0 else 75
    
    return min(95, max(75, accuracy))

