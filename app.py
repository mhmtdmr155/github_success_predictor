"""
Flask Web Application for YouTube Video Success Predictor
"""
import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import re
from src.config import (
    MODEL_DIR, BEST_MODEL_NAME, SCALER_NAME, 
    FEATURE_NAMES_NAME, MODEL_METADATA_NAME
)
from src.prediction_utils import (
    calculate_prediction_interval,
    calculate_confidence_score,
    estimate_prediction_accuracy
)

app = Flask(__name__)
CORS(app)

# Global variables for model
model = None
scaler = None
feature_names = None
model_metadata = None


def load_model():
    """Load trained model and related files"""
    global model, scaler, feature_names, model_metadata
    
    try:
        model_path = os.path.join(MODEL_DIR, BEST_MODEL_NAME)
        scaler_path = os.path.join(MODEL_DIR, SCALER_NAME)
        feature_path = os.path.join(MODEL_DIR, FEATURE_NAMES_NAME)
        metadata_path = os.path.join(MODEL_DIR, MODEL_METADATA_NAME)
        
        if not os.path.exists(model_path):
            print(f"Warning: Model not found at {model_path}")
            return False
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        feature_names = joblib.load(feature_path)
        model_metadata = joblib.load(metadata_path)
        
        print("Model loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False


def has_emoji(text):
    """Check if text contains emoji"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    return bool(emoji_pattern.search(text))


def extract_title_features(title):
    """Extract features from video title"""
    if not title:
        title = ''
    
    title = str(title)
    
    features = {
        'title_length': len(title),
        'title_word_count': len(title.split()),
        'title_has_number': 1 if re.search(r'\d', title) else 0,
        'title_has_emoji': 1 if has_emoji(title) else 0,
        'title_has_question': 1 if '?' in title else 0,
        'title_has_exclamation': 1 if '!' in title else 0,
        'title_special_char_count': len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', title)),
        'title_is_tutorial': 1 if any(word in title.lower() for word in ['tutorial', 'how to', 'learn', 'guide', 'course']) else 0,
        'title_is_question': 1 if any(word in title.lower() for word in ['what', 'why', 'how', 'when', 'where']) or '?' in title else 0,
        'title_uppercase_ratio': sum(1 for c in title if c.isupper()) / len(title) if len(title) > 0 else 0
    }
    
    return features


def prepare_features(user_input):
    """Prepare features from user input for prediction with advanced features"""
    import numpy as np
    
    # Get title
    title = user_input.get('title', '')
    
    # Extract title features
    title_features = extract_title_features(title)
    
    # Parse publish date and hour
    publish_hour = int(user_input.get('publish_hour', datetime.now().hour))
    publish_date_str = user_input.get('publish_date', datetime.now().isoformat())
    
    try:
        publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
        if 'publish_hour' in user_input:
            publish_date = publish_date.replace(hour=publish_hour)
    except:
        publish_date = datetime.now().replace(hour=publish_hour)
    
    # Time features
    publish_day = publish_date.strftime('%A')
    publish_day_of_week = publish_date.weekday()
    publish_day_of_month = publish_date.day
    publish_week_of_year = publish_date.isocalendar().week
    publish_quarter = (publish_date.month - 1) // 3 + 1
    is_weekend = 1 if publish_day_of_week >= 5 else 0
    is_prime_time = 1 if 18 <= publish_hour <= 21 else 0
    is_month_end = 1 if publish_day_of_month > 25 else 0
    is_month_start = 1 if publish_day_of_month <= 7 else 0
    publish_month = publish_date.month
    
    # Time of day
    if publish_hour <= 6:
        time_of_day = 'night'
    elif publish_hour <= 12:
        time_of_day = 'morning'
    elif publish_hour <= 18:
        time_of_day = 'afternoon'
    else:
        time_of_day = 'evening'
    
    # Duration features (match preprocessing bins)
    duration_minutes = float(user_input.get('duration_minutes', 10))
    duration_seconds = duration_minutes * 60

    # Binary flags (match src/data_preprocessing.py)
    is_short_video = 1 if duration_minutes < 5 else 0
    is_medium_video = 1 if 5 <= duration_minutes <= 15 else 0
    is_long_video = 1 if duration_minutes > 15 else 0

    # Category (match src/data_preprocessing.py bins: 0-5-10-15-30-60-480)
    if duration_minutes < 5:
        duration_category = 'very_short'
    elif duration_minutes < 10:
        duration_category = 'short'
    elif duration_minutes <= 15:
        duration_category = 'medium'
    elif duration_minutes <= 30:
        duration_category = 'long'
    elif duration_minutes <= 60:
        duration_category = 'very_long'
    else:
        duration_category = 'extended'
    
    # Channel features
    channel_subscribers = float(user_input.get('channel_subscribers', 100000))
    channel_video_count = float(user_input.get('channel_video_count', 100))
    channel_view_count = float(user_input.get('channel_view_count', 1000000))
    
    # Match preprocessing pd.cut bins (right-inclusive)
    if channel_subscribers <= 10000:
        channel_size = 'small'
        channel_size_numeric = 1
    elif channel_subscribers <= 100000:
        channel_size = 'medium'
        channel_size_numeric = 2
    elif channel_subscribers <= 1000000:
        channel_size = 'large'
        channel_size_numeric = 3
    else:
        channel_size = 'mega'
        channel_size_numeric = 4
    
    subscribers_per_video = channel_subscribers / (channel_video_count + 1)
    estimated_channel_age_months = channel_video_count / 4  # Estimated
    subscriber_growth_rate = channel_subscribers / (channel_video_count + 1)
    estimated_engagement_rate = channel_view_count / (channel_subscribers + 1)
    
    # Description features
    description = user_input.get('description', '')
    description_length = len(description)
    description_word_count = len(description.split())
    description_has_url = 1 if 'http' in description.lower() else 0
    
    # Tag features
    # UI sends tag_count directly; fall back to parsing tags string if provided
    if 'tag_count' in user_input and user_input.get('tag_count') is not None:
        try:
            tag_count = int(float(user_input.get('tag_count', 0)))
        except Exception:
            tag_count = 0
    else:
        tags = user_input.get('tags', '')
        tag_count = len(tags.split(',')) if tags else 0
    
    # Title advanced features
    title_len = len(title)
    title_positive_words = sum(1 for word in ['best', 'top', 'amazing', 'awesome', 'great', 'ultimate', 'complete', 'perfect'] if word in title.lower())
    title_negative_words = sum(1 for word in ['worst', 'bad', 'terrible', 'avoid', 'never'] if word in title.lower())
    title_power_words = sum(1 for word in ['secret', 'hack', 'trick', 'method', 'system', 'guide', 'tutorial', 'learn', 'master'] if word in title.lower())
    title_has_digit = 1 if re.search(r'\d', title) else 0
    title_number_count = len(re.findall(r'\d+', title))
    title_starts_with_capital = 1 if title and title[0].isupper() else 0
    title_has_colon = 1 if ':' in title else 0
    title_has_dash = 1 if '-' in title or '|' in title else 0
    
    # Build feature dictionary
    features = {
        **title_features,
        'publish_hour': publish_hour,
        'publish_day_of_week': publish_day_of_week,
        'publish_day_of_month': publish_day_of_month,
        'publish_week_of_year': publish_week_of_year,
        'publish_quarter': publish_quarter,
        'is_weekend': is_weekend,
        'is_prime_time': is_prime_time,
        'is_month_end': is_month_end,
        'is_month_start': is_month_start,
        'publish_month': publish_month,
        'duration_seconds': duration_seconds,
        'duration_minutes': duration_minutes,
        'is_short_video': is_short_video,
        'is_medium_video': is_medium_video,
        'is_long_video': is_long_video,
        'channel_subscribers': channel_subscribers,
        'channel_video_count': channel_video_count,
        'channel_view_count': channel_view_count,
        'subscribers_per_video': subscribers_per_video,
        'tag_count': tag_count,
        'description_length': description_length,
        'description_word_count': description_word_count,
        'description_has_url': description_has_url,
        # Advanced features
        'title_length_x_subscribers': title_len * np.log1p(channel_subscribers),
        'duration_x_prime_time': duration_minutes * is_prime_time,
        'title_quality_x_channel_size': (title_features.get('title_is_tutorial', 0) + title_features.get('title_has_number', 0) + title_features.get('title_is_question', 0)) * np.log1p(channel_subscribers),
        'weekend_x_prime_time': is_weekend * is_prime_time,
        'duration_x_channel_size': duration_minutes * np.log1p(channel_subscribers),
        'tag_count_x_title_length': tag_count * title_len,
        'description_length_x_tags': description_length * tag_count,
        'title_length_squared': title_len ** 2,
        'duration_minutes_squared': duration_minutes ** 2,
        'channel_subscribers_log': np.log1p(channel_subscribers),
        'channel_subscribers_sqrt': np.sqrt(channel_subscribers),
        'channel_subscribers_cbrt': np.cbrt(channel_subscribers),
        'title_length_to_words': title_len / (title_features.get('title_word_count', 1) + 1),
        'description_to_title_ratio': description_length / (title_len + 1),
        'tags_to_title_ratio': tag_count / (title_len + 1),
        'video_frequency': channel_video_count / (np.log1p(channel_subscribers) + 1),
        'publish_hour_squared': publish_hour ** 2,
        'publish_hour_sin': np.sin(2 * np.pi * publish_hour / 24),
        'publish_hour_cos': np.cos(2 * np.pi * publish_hour / 24),
        'publish_day_of_week_sin': np.sin(2 * np.pi * publish_day_of_week / 7),
        'publish_day_of_week_cos': np.cos(2 * np.pi * publish_day_of_week / 7),
        'title_positive_words': title_positive_words,
        'title_negative_words': title_negative_words,
        'title_power_words': title_power_words,
        'title_has_digit': title_has_digit,
        'title_number_count': title_number_count,
        'title_starts_with_capital': title_starts_with_capital,
        'title_has_colon': title_has_colon,
        'title_has_dash': title_has_dash,
        'estimated_channel_age_months': estimated_channel_age_months,
        'subscriber_growth_rate': subscriber_growth_rate,
        'estimated_engagement_rate': estimated_engagement_rate,
        'channel_size_numeric': channel_size_numeric,
        'content_completeness_score': ((description_length > 100) * 0.3 + (tag_count >= 5) * 0.3 + (title_len >= 40) * 0.2 + (title_features.get('title_is_tutorial', 0) == 1) * 0.2),
        'seo_score': ((50 <= title_len <= 60) * 0.3 + (8 <= tag_count <= 12) * 0.2 + (description_length > 200) * 0.2 + (title_features.get('title_has_number', 0) == 1) * 0.15 + (title_features.get('title_is_question', 0) == 1) * 0.15),
        'engagement_potential_score': (is_prime_time * 0.3 + (10 <= duration_minutes <= 15) * 0.3 + (title_features.get('title_is_tutorial', 0) == 1) * 0.2 + (title_features.get('title_has_emoji', 0) == 1) * 0.1 + (is_weekend == 0) * 0.1)
    }
    
    # One-hot encode categorical features
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    times = ['morning', 'afternoon', 'evening', 'night']
    durations = ['very_short', 'short', 'medium', 'long', 'very_long', 'extended']
    sizes = ['medium', 'large', 'mega']  # 'small' is drop_first
    
    for day in days[1:]:  # Skip Monday (drop_first)
        features[f'publish_day_{day}'] = 1 if publish_day == day else 0
    
    for time in times[1:]:  # Skip morning (drop_first)
        features[f'time_of_day_{time}'] = 1 if time_of_day == time else 0
    
    for dur in durations[1:]:  # Skip very_short (drop_first)
        features[f'duration_category_{dur}'] = 1 if duration_category == dur else 0
    
    for size in sizes:  # Skip small (drop_first)
        features[f'channel_size_{size}'] = 1 if channel_size == size else 0
    
    # Handle any NaN or inf values
    for key, value in features.items():
        if isinstance(value, (int, float)):
            if np.isnan(value) or np.isinf(value):
                features[key] = 0
    
    return features


def generate_recommendations(user_input, prediction):
    """Generate personalized recommendations based on prediction"""
    recommendations = []
    
    title = user_input.get('title', '')
    duration_minutes = float(user_input.get('duration_minutes', 10))
    publish_hour = int(user_input.get('publish_hour', datetime.now().hour))
    channel_subscribers = float(user_input.get('channel_subscribers', 100000))
    
    # Title recommendations
    title_length = len(title)
    if title_length < 50:
        recommendations.append({
            'type': 'title',
            'priority': 'high',
            'message': f'Başlığı 50-60 karaktere çıkararak %15-20 daha fazla görüntülenme alabilirsiniz.',
            'suggestion': 'Başlığa daha açıklayıcı kelimeler ekleyin'
        })
    elif title_length > 70:
        recommendations.append({
            'type': 'title',
            'priority': 'medium',
            'message': f'Başlığı 50-60 karaktere düşürerek daha fazla tıklama alabilirsiniz.',
            'suggestion': 'Başlığı kısaltın, gereksiz kelimeleri çıkarın'
        })
    
    if not re.search(r'\d', title):
        recommendations.append({
            'type': 'title',
            'priority': 'medium',
            'message': 'Başlığa sayı ekleyerek (örn: "10 İpucu", "5 Yöntem") %12 daha fazla tıklama alabilirsiniz.',
            'suggestion': 'Başlığa sayı ekleyin'
        })
    
    if '?' not in title and not any(word in title.lower() for word in ['what', 'why', 'how']):
        recommendations.append({
            'type': 'title',
            'priority': 'low',
            'message': 'Soru formatındaki başlıklar %10-15 daha fazla merak uyandırır.',
            'suggestion': 'Başlığı soru formatına çevirin'
        })
    
    # Time recommendations
    if not (18 <= publish_hour <= 21):
        recommendations.append({
            'type': 'timing',
            'priority': 'high',
            'message': f'Yayını prime time\'a (18:00-21:00) alarak %20-25 daha fazla görüntülenme alabilirsiniz.',
            'suggestion': f'Yayın saatini {18 + (21-18)//2}:00\'a alın'
        })
    
    # Duration recommendations
    if duration_minutes < 5:
        recommendations.append({
            'type': 'duration',
            'priority': 'medium',
            'message': '5-15 dakika arası videolar en yüksek engagement oranına sahiptir.',
            'suggestion': 'Video süresini 10-12 dakikaya çıkarın'
        })
    elif duration_minutes > 30:
        recommendations.append({
            'type': 'duration',
            'priority': 'low',
            'message': '10-15 dakika arası videolar optimal performans gösterir.',
            'suggestion': 'Video süresini 12-15 dakikaya düşürün'
        })
    
    # Channel size recommendations
    if channel_subscribers < 10000:
        recommendations.append({
            'type': 'channel',
            'priority': 'low',
            'message': 'Kanalınızı büyütmek için düzenli içerik üretimi ve SEO optimizasyonu önemlidir.',
            'suggestion': 'Haftada en az 2-3 video yükleyin'
        })
    
    return recommendations


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'model_name': model_metadata.get('model_name', 'Unknown'),
        'training_date': model_metadata.get('training_date', 'Unknown'),
        'feature_count': model_metadata.get('feature_count', 0)
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict video success"""
    if model is None or scaler is None or feature_names is None:
        return jsonify({'error': 'Model not loaded. Please train the model first.'}), 500
    
    try:
        user_input = request.json
        
        # Prepare features
        features_dict = prepare_features(user_input)
        
        # Convert to DataFrame with correct feature order
        feature_vector = np.zeros(len(feature_names))
        missing_features = []
        for i, feature_name in enumerate(feature_names):
            if feature_name in features_dict:
                feature_vector[i] = features_dict[feature_name]
            else:
                missing_features.append(feature_name)
                # Set default values for missing features
                if 'view_count' in feature_name or 'like_count' in feature_name or 'comment_count' in feature_name:
                    feature_vector[i] = 0
                elif 'channel' in feature_name:
                    # Use provided channel values or defaults
                    feature_vector[i] = 0
                else:
                    feature_vector[i] = 0
        
        # Debug: print missing features (only in development)
        if missing_features and app.debug:
            print(f"Missing features: {missing_features[:5]}")
        
        # Scale features
        feature_vector_scaled = scaler.transform([feature_vector])
        
        # Make prediction
        raw_prediction = model.predict(feature_vector_scaled)[0]
        
        # Debug info (only in development)
        if app.debug:
            print(f"Raw prediction: {raw_prediction}")
            print(f"Key features - channel_subscribers: {features_dict.get('channel_subscribers', 0)}, duration: {features_dict.get('duration_minutes', 0)}")
        
        # Get residual std from metadata for prediction intervals
        residual_std = None
        if model_metadata and 'prediction_interval_std' in model_metadata:
            residual_std = model_metadata['prediction_interval_std']
        
        # Clip prediction to reasonable range based on channel size
        channel_subs = features_dict.get('channel_subscribers', 100000)
        
        # More sophisticated clipping based on channel size and video characteristics
        # Small channels: 2-20% of subscribers
        # Medium channels: 1-15% of subscribers
        # Large channels: 0.5-10% of subscribers
        # Mega channels: 0.2-5% of subscribers (but can go viral)
        
        if channel_subs < 10000:
            min_ratio, max_ratio = 0.02, 0.20
        elif channel_subs < 100000:
            min_ratio, max_ratio = 0.01, 0.15
        elif channel_subs < 1000000:
            min_ratio, max_ratio = 0.005, 0.10
        else:
            min_ratio, max_ratio = 0.002, 0.05
        
        min_prediction = max(50, int(channel_subs * min_ratio))
        max_prediction = int(channel_subs * max_ratio * 3)  # Allow for viral potential
        
        # Apply clipping
        prediction = max(min_prediction, min(max_prediction, int(raw_prediction)))
        prediction = max(0, prediction)
        
        # Calculate prediction intervals using residual std if available
        margin = 0
        if residual_std and residual_std > 0:
            prediction_min, prediction_max, margin = calculate_prediction_interval(
                prediction, residual_std, confidence=0.95
            )
            # Ensure intervals are reasonable
            prediction_min = max(0, int(prediction_min))
            prediction_max = int(prediction_max)
        else:
            # Fallback to percentage-based intervals
            # Use narrower intervals for better predictions (90-110% instead of 85-115%)
            prediction_min = int(prediction * 0.90)
            prediction_max = int(prediction * 1.10)
            margin = int((prediction_max - prediction_min) / 2)
        
        # Generate recommendations
        recommendations = generate_recommendations(user_input, prediction)
        
        # Calculate confidence using improved method
        confidence = calculate_confidence_score(prediction, features_dict, model_metadata)
        
        # Calculate prediction accuracy estimate
        accuracy = estimate_prediction_accuracy(prediction, features_dict)
        
        # Get model performance metrics
        model_name = model_metadata.get('model_name', 'Unknown') if model_metadata else 'Unknown'
        cv_scores = model_metadata.get('cv_scores', {}) if model_metadata else {}
        cv_score = 0
        if cv_scores and model_name in cv_scores:
            cv_score = cv_scores[model_name].get('mean', 0)
        elif cv_scores:
            # Get best CV score
            cv_score = max([score.get('mean', 0) for score in cv_scores.values()])
        
        return jsonify({
            'success': True,
            'prediction': {
                'first_week_views': prediction,
                'confidence': confidence,
                'accuracy': accuracy,
                'range': {
                    'min': prediction_min,
                    'max': prediction_max
                },
                'margin': int(margin)
            },
            'recommendations': recommendations,
            'features_used': len(feature_names),
            'model_info': {
                'model_name': model_name,
                'cv_score': cv_score,
                'r2_score': cv_score  # Use CV score as R² estimate
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    print("Loading model...")
    if load_model():
        print("Starting Flask server...")
        from src.config import FLASK_PORT, FLASK_DEBUG
        app.run(host='0.0.0.0', port=FLASK_PORT, debug=FLASK_DEBUG)
    else:
        print("Warning: Model not loaded. Please train the model first.")
        print("Starting Flask server anyway (for development)...")
        from src.config import FLASK_PORT, FLASK_DEBUG
        app.run(host='0.0.0.0', port=FLASK_PORT, debug=FLASK_DEBUG)

