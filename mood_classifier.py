from flask import Flask, render_template, request, jsonify
from movie_therapist import MovieTherapist
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

therapist = MovieTherapist()

@app.route('/')
def index():
    """Main homepage with mood-based quick picks"""
    quick_picks = therapist.get_quick_mood_picks()
    emotion = request.args.get('emotion', '')
    return render_template('index.html', quick_picks=quick_picks, initial_emotion=emotion)

@app.route('/mood-quiz')
def mood_quiz():
    """Interactive mood assessment quiz"""
    quiz_data = therapist.get_mood_quiz()
    return render_template('mood_quiz.html', quiz=quiz_data)

@app.route('/recommend/therapeutic', methods=['POST'])
def therapeutic_recommend():
    """Get therapeutic movie recommendations based on mood"""
    try:
        data = request.get_json()
        user_input = data.get('query', '').strip()
        emotion = data.get('emotion', '')
        
        if not emotion and user_input:
            emotion = therapist.detect_emotion_from_text(user_input)
        elif not emotion:
            emotion = 'neutral'
        
        movies, profile = therapist.get_therapeutic_recommendations(emotion, user_input)
        
        recommendations = []
        for movie in movies[:10]:
            recommendations.append({
                'id': movie.get('id'),
                'title': movie.get('title', 'Unknown Title'),
                'year': movie.get('release_date', '')[:4] if movie.get('release_date') else 'TBA',
                'rating': round(movie.get('vote_average', 0), 1),
                'vote_count': movie.get('vote_count', 0),
                'overview': movie.get('overview', 'No description available.'),
                'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None,
                'explanation': movie.get('therapeutic_reason', 'Great for your current mood!'),
                'mood_match': movie.get('mood_match', 85),
                'emotion': emotion,
                'therapy_color': movie.get('therapy_color', '#607D8B'),
                'therapy_icon': movie.get('therapy_icon', '🎬'),
                'therapeutic_effect': profile['therapeutic_effect']
            })
        
        recommendations.sort(key=lambda x: x['mood_match'], reverse=True)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'emotion_detected': emotion,
            'emotion_profile': therapist.get_emotion_display_data(emotion),
            'message': f"We detected you're feeling {emotion}. Here are movies to help:",
            'total_results': len(recommendations)
        })
        
    except Exception as e:
        print(f"Error in therapeutic_recommend: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to get recommendations. Please try again.'
        })

@app.route('/recommend/quick-mood/<mood>')
def quick_mood_recommend(mood):
    """Quick recommendations for specific moods"""
    try:
        if mood not in therapist.emotion_profiles:
            mood = 'neutral'
            
        movies, profile = therapist.get_therapeutic_recommendations(mood)
        
        recommendations = []
        for movie in movies[:8]:
            recommendations.append({
                'title': movie.get('title', 'Unknown Title'),
                'year': movie.get('release_date', '')[:4] if movie.get('release_date') else 'TBA',
                'rating': round(movie.get('vote_average', 0), 1),
                'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None,
                'explanation': movie.get('therapeutic_reason', 'Great choice!'),
                'therapy_color': profile['color'],
                'therapy_icon': profile['icon']
            })
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'mood': mood,
            'profile': profile
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/trending')
def get_trending():
    """Get currently trending movies"""
    try:
        data = therapist.get_tmdb_data('trending/movie/week')
        
        if data and 'results' in data:
            trending_movies = []
            for movie in data['results'][:12]:
                if movie.get('poster_path'):
                    trending_movies.append({
                        'id': movie.get('id'),
                        'title': movie.get('title', 'Unknown Title'),
                        'year': movie.get('release_date', '')[:4] if movie.get('release_date') else 'TBA',
                        'rating': round(movie.get('vote_average', 0), 1),
                        'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
                        'overview': (movie.get('overview', '')[:100] + '...') if movie.get('overview') else 'No description available.'
                    })
            
            return jsonify({'success': True, 'trending_movies': trending_movies})
        
        return jsonify({'success': False, 'error': 'Could not fetch trending movies'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)