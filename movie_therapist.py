import requests
import random
from textblob import TextBlob
from config import Config

class MovieTherapist:
    def __init__(self):
        self.emotion_profiles = {
            'stressed': {
                'name': '😫 Stressed & Overwhelmed',
                'description': 'You need to relax and unwind from daily pressures',
                'genres': [16, 35, 10751, 10402],
                'mood_keywords': ['lighthearted', 'funny', 'uplifting', 'wholesome'],
                'therapeutic_effect': 'stress_relief',
                'color': '#4CAF50',
                'icon': '😌',
                'avoid_genres': [27, 53, 80, 9648]
            },
            'heartbroken': {
                'name': '💔 Heartbroken & Sad',
                'description': 'You need catharsis, hope, and emotional healing',
                'genres': [18, 10749, 36],
                'mood_keywords': ['emotional', 'hopeful', 'redemption', 'growth'],
                'therapeutic_effect': 'emotional_release',
                'color': '#2196F3',
                'icon': '🌟',
                'avoid_genres': [10749, 35]
            },
            'unmotivated': {
                'name': '😴 Unmotivated & Stuck',
                'description': 'You need inspiration, energy, and new perspectives',
                'genres': [12, 14, 28, 99],
                'mood_keywords': ['inspiring', 'epic', 'transformative', 'courage'],
                'therapeutic_effect': 'motivation',
                'color': '#FF9800',
                'icon': '🚀',
                'avoid_genres': [18, 10749]
            },
            'anxious': {
                'name': '😰 Anxious & Worried',
                'description': 'You need calm, perspective, and mindfulness',
                'genres': [16, 10751, 99, 10402],
                'mood_keywords': ['calming', 'educational', 'mindful', 'gentle'],
                'therapeutic_effect': 'anxiety_reduction',
                'color': '#9C27B0',
                'icon': '🧘',
                'avoid_genres': [27, 53, 9648]
            },
            'celebratory': {
                'name': '🎉 Celebratory & Happy',
                'description': 'You want to amplify good vibes and positive energy',
                'genres': [35, 10402, 10751, 14],
                'mood_keywords': ['joyful', 'energetic', 'festive', 'magical'],
                'therapeutic_effect': 'mood_amplification',
                'color': '#FFEB3B',
                'icon': '✨',
                'avoid_genres': [18, 9648, 80]
            },
            'neutral': {
                'name': '😊 Open to Anything',
                'description': 'You\'re feeling balanced and open to new experiences',
                'genres': [28, 12, 16, 35, 18, 10751, 14],
                'mood_keywords': ['engaging', 'well_rated', 'popular', 'classic'],
                'therapeutic_effect': 'entertainment',
                'color': '#607D8B',
                'icon': '🎬',
                'avoid_genres': []
            }
        }

    def get_tmdb_data(self, endpoint, params=None):
        if params is None:
            params = {}
        params['api_key'] = Config.TMDB_API_KEY
        url = f"https://api.themoviedb.org/3/{endpoint}"
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from TMDB: {e}")
            return None

    def detect_emotion_from_text(self, user_input):
        if not user_input or user_input.strip() == "":
            return 'neutral'
            
        input_lower = user_input.lower()
        
        emotion_keywords = {
            'stressed': ['stressed', 'overwhelmed', 'tired', 'exhausted', 'busy', 'pressure', 'work', 'deadline'],
            'heartbroken': ['sad', 'heartbroken', 'broken', 'lonely', 'miss', 'breakup', 'lost', 'grief'],
            'unmotivated': ['bored', 'unmotivated', 'stuck', 'routine', 'blah', 'lazy', 'uninspired'],
            'anxious': ['anxious', 'nervous', 'worried', 'scared', 'panic', 'fear', 'tense'],
            'celebratory': ['happy', 'excited', 'celebrate', 'achieved', 'won', 'success', 'joy', 'proud']
        }
        
        emotion_scores = {emotion: 0 for emotion in emotion_keywords}
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in input_lower:
                    emotion_scores[emotion] += 1
        
        try:
            blob = TextBlob(user_input)
            sentiment = blob.sentiment.polarity
            
            if sentiment > 0.3:
                emotion_scores['celebratory'] += 2
            elif sentiment < -0.3:
                emotion_scores['heartbroken'] += 2
        except:
            pass

        max_score = max(emotion_scores.values())
        if max_score > 0:
            dominant_emotions = [emotion for emotion, score in emotion_scores.items() if score == max_score]
            return random.choice(dominant_emotions)
        
        return 'neutral'

    def get_therapeutic_recommendations(self, emotion, user_input=""):
        if emotion not in self.emotion_profiles:
            emotion = 'neutral'
        
        profile = self.emotion_profiles[emotion]
        
        params = {
            'api_key': Config.TMDB_API_KEY,
            'language': 'en-US',
            'include_adult': False,
            'sort_by': 'popularity.desc',
            'vote_count.gte': 10,
            'with_genres': ','.join(map(str, profile['genres'])),
            'page': 1
        }
        
        data = self.get_tmdb_data('discover/movie', params)
        
        if data and 'results' in data:
            movies = data.get('results', [])
            
            therapeutic_movies = []
            for movie in movies[:12]:
                if movie.get('poster_path'):
                    therapeutic_movies.append(self.enhance_movie_with_therapy(movie, profile, emotion))
            
            return therapeutic_movies, profile
        
        return [], profile

    def enhance_movie_with_therapy(self, movie, profile, emotion):
        base_score = random.randint(75, 95)
        rating = movie.get('vote_average', 0)
        if rating > 7.5:
            base_score += 10
        elif rating > 7.0:
            base_score += 5
        
        therapeutic_reasons = {
            'stressed': [
                "Perfect escape from stress with its lighthearted tone",
                "Great for unwinding and forgetting your worries",
                "The ideal comedy to lift your spirits after a long day"
            ],
            'heartbroken': [
                "Offers beautiful catharsis and emotional healing",
                "Shows that growth often comes from difficult times",
                "A story about resilience that will give you hope"
            ],
            'unmotivated': [
                "Will inspire you to pursue your passions with new energy",
                "Full of transformative moments that spark motivation",
                "The perfect boost to get you out of a rut"
            ],
            'anxious': [
                "Calming and gentle - perfect for anxious moments",
                "Helps put things in perspective with its mindful approach",
                "A peaceful escape from racing thoughts"
            ],
            'celebratory': [
                "Amplifies the good vibes you're feeling right now!",
                "The perfect movie to celebrate and enjoy life",
                "Matches your joyful energy with infectious positivity"
            ],
            'neutral': [
                "A critically acclaimed film that engages and entertains",
                "Popular choice loved by audiences worldwide",
                "Well-crafted storytelling that respects your time"
            ]
        }
        
        movie['therapeutic_reason'] = random.choice(therapeutic_reasons.get(emotion, ["Great choice for your current mood!"]))
        movie['mood_match'] = min(base_score, 100)
        movie['therapy_color'] = profile['color']
        movie['therapy_icon'] = profile['icon']
        
        return movie

    def get_mood_quiz(self):
        return {
            'title': 'Movie Mood Assessment 🎭',
            'description': 'Help us understand what you need right now...',
            'questions': [
                {
                    'id': 1,
                    'question': 'How are you feeling right now?',
                    'type': 'emotion',
                    'options': [
                        {'text': '😫 Stressed and overwhelmed', 'emotion': 'stressed', 'icon': '😫'},
                        {'text': '💔 A bit sad or heartbroken', 'emotion': 'heartbroken', 'icon': '💔'},
                        {'text': '😴 Unmotivated or stuck in a rut', 'emotion': 'unmotivated', 'icon': '😴'},
                        {'text': '😰 Anxious or worried', 'emotion': 'anxious', 'icon': '😰'},
                        {'text': '🎉 Happy and celebratory!', 'emotion': 'celebratory', 'icon': '🎉'},
                        {'text': '😊 Balanced and open to anything', 'emotion': 'neutral', 'icon': '😊'}
                    ]
                }
            ]
        }

    def get_emotion_display_data(self, emotion):
        return self.emotion_profiles.get(emotion, self.emotion_profiles['neutral'])

    def get_quick_mood_picks(self):
        moods = ['stressed', 'celebratory', 'unmotivated', 'anxious']
        quick_picks = {}
        
        for mood in moods:
            movies, profile = self.get_therapeutic_recommendations(mood)
            quick_picks[mood] = {
                'movies': movies[:4],
                'profile': profile
            }
        
        return quick_picks