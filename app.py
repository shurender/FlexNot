from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.security import generate_password_hash, check_password_hash
import json
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'flexnot_secret_key_2024')

# OMDB API Configuration
OMDB_API_KEY = os.getenv('OMDB_API_KEY', 'demo_key')
OMDB_BASE_URL = 'http://www.omdbapi.com/'

class MovieRecommendationSystem:
    def __init__(self):
        self.init_database()
        if OMDB_API_KEY != 'demo_key':
            self.update_movie_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect('flexnot.db')
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                overview TEXT,
                poster_path TEXT,
                backdrop_path TEXT,
                release_date TEXT,
                vote_average REAL,
                vote_count INTEGER,
                genres TEXT,
                runtime TEXT,
                director TEXT,
                cast TEXT,
                country TEXT,
                language TEXT,
                awards TEXT,
                box_office TEXT,
                is_new BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id TEXT,
                rating REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                UNIQUE(user_id, movie_id)
            )
        ''')
        
        # Watchlist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                UNIQUE(user_id, movie_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Add sample movies if no API key
        if OMDB_API_KEY == 'demo_key':
            self.add_sample_movies()
    
    def add_sample_movies(self):
        """Add sample movies for demo purposes"""
        sample_movies = [
            ("tt0111161", "The Shawshank Redemption", "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.", "https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg", "", "23 Sep 1994", 9.3, 2500000, "Drama", "142 min", "Frank Darabont", "Tim Robbins, Morgan Freeman, Bob Gunton", "USA", "English", "Nominated for 7 Oscars", "$16,000,000", 0),
            ("tt0068646", "The Godfather", "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.", "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg", "", "24 Mar 1972", 9.2, 1800000, "Crime, Drama", "175 min", "Francis Ford Coppola", "Marlon Brando, Al Pacino, James Caan", "USA", "English", "Won 3 Oscars", "$134,966,411", 0),
            ("tt0468569", "The Dark Knight", "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.", "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg", "", "18 Jul 2008", 9.0, 2600000, "Action, Crime, Drama", "152 min", "Christopher Nolan", "Christian Bale, Heath Ledger, Aaron Eckhart", "USA", "English", "Won 2 Oscars", "$534,858,444", 0),
            ("tt0110912", "Pulp Fiction", "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.", "https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg", "", "14 Oct 1994", 8.9, 2000000, "Crime, Drama", "154 min", "Quentin Tarantino", "John Travolta, Uma Thurman, Samuel L. Jackson", "USA", "English", "Won 1 Oscar", "$214,179,088", 0),
            ("tt0109830", "Forrest Gump", "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate and other historical events unfold from the perspective of an Alabama man.", "https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg", "", "06 Jul 1994", 8.8, 2100000, "Drama, Romance", "142 min", "Robert Zemeckis", "Tom Hanks, Robin Wright, Gary Sinise", "USA", "English", "Won 6 Oscars", "$677,387,716", 0),
            ("tt0137523", "Fight Club", "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into an anarchist organization.", "https://m.media-amazon.com/images/M/MV5BMmEzNTkxYjQtZTc0MC00YTVjLTg5ZTEtZWMwOWVlYzY0NWIwXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg", "", "15 Oct 1999", 8.8, 2000000, "Drama", "139 min", "David Fincher", "Brad Pitt, Edward Norton, Meat Loaf", "USA", "English", "Nominated for 1 Oscar", "$100,853,753", 0),
            ("tt0816692", "Interstellar", "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg", "", "07 Nov 2014", 8.6, 1700000, "Adventure, Drama, Sci-Fi", "169 min", "Christopher Nolan", "Matthew McConaughey, Anne Hathaway, Jessica Chastain", "USA", "English", "Won 1 Oscar", "$677,471,339", 1),
            ("tt0120737", "The Lord of the Rings: The Fellowship of the Ring", "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth from the Dark Lord Sauron.", "https://m.media-amazon.com/images/M/MV5BN2EyZjM3NzUtNWUzMi00MTgxLWI0NTctMzY4M2VlOTdjZWRiXkEyXkFqcGdeQXVyNDUzOTQ5MjY@._V1_SX300.jpg", "", "19 Dec 2001", 8.8, 1800000, "Action, Adventure, Drama", "178 min", "Peter Jackson", "Elijah Wood, Ian McKellen, Orlando Bloom", "New Zealand, USA", "English", "Won 4 Oscars", "$871,530,324", 0),
            ("tt0167260", "The Lord of the Rings: The Return of the King", "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring.", "https://m.media-amazon.com/images/M/MV5BNzA5ZDNlZWMtM2NhNS00NDJjLTk4NDItYTRmY2EwMWI5MTktXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg", "", "17 Dec 2003", 8.9, 1750000, "Action, Adventure, Drama", "201 min", "Peter Jackson", "Elijah Wood, Viggo Mortensen, Ian McKellen", "New Zealand, USA", "English", "Won 11 Oscars", "$1,142,456,536", 0),
            ("tt0133093", "The Matrix", "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg", "", "31 Mar 1999", 8.7, 1900000, "Action, Sci-Fi", "136 min", "Lana Wachowski, Lilly Wachowski", "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss", "USA", "English", "Won 4 Oscars", "$463,517,383", 0)
        ]
        
        conn = sqlite3.connect('flexnot.db')
        cursor = conn.cursor()
        
        for movie in sample_movies:
            cursor.execute('SELECT id FROM movies WHERE id = ?', (movie[0],))
            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO movies 
                    (id, title, overview, poster_path, backdrop_path, release_date, 
                     vote_average, vote_count, genres, runtime, director, cast, country, language, awards, box_office, is_new)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', movie)
        
        conn.commit()
        conn.close()
    
    def get_omdb_movie(self, params):
        """Fetch movie from OMDB API"""
        if OMDB_API_KEY == 'demo_key':
            return None
            
        params['apikey'] = OMDB_API_KEY
        
        try:
            response = requests.get(OMDB_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('Response') == 'True':
                return data
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from OMDB: {e}")
            return None
    
    def search_omdb_movies(self, search_term, year=None):
        """Search movies from OMDB API"""
        params = {'s': search_term, 'type': 'movie'}
        if year:
            params['y'] = year
            
        data = self.get_omdb_movie(params)
        if data and 'Search' in data:
            return data['Search']
        return []
    
    def get_movie_details(self, imdb_id):
        """Get detailed movie information from OMDB"""
        params = {'i': imdb_id, 'plot': 'full'}
        return self.get_omdb_movie(params)
    
    def update_movie_database(self):
        """Update local database with movies from OMDB"""
        # Popular movie searches to populate database
        popular_searches = [
            'Batman', 'Superman', 'Spider', 'Avengers', 'Star Wars', 'Lord of the Rings',
            'Harry Potter', 'Godfather', 'Matrix', 'Inception', 'Interstellar', 'Titanic',
            'Avatar', 'Jurassic', 'Fast Furious', 'Mission Impossible', 'James Bond',
            'Marvel', 'Disney', 'Pixar', 'Comedy', 'Horror', 'Action', 'Drama'
        ]
        
        conn = sqlite3.connect('flexnot.db')
        cursor = conn.cursor()
        
        for search_term in popular_searches[:5]:  # Limit to avoid API rate limits
            movies = self.search_omdb_movies(search_term)
            for movie in movies[:10]:  # Limit results per search
                imdb_id = movie.get('imdbID')
                if imdb_id:
                    # Check if movie already exists
                    cursor.execute('SELECT id FROM movies WHERE id = ?', (imdb_id,))
                    if cursor.fetchone() is None:
                        # Get detailed information
                        details = self.get_movie_details(imdb_id)
                        if details:
                            # Convert IMDB rating to 0-10 scale
                            imdb_rating = details.get('imdbRating', 'N/A')
                            try:
                                vote_average = float(imdb_rating) if imdb_rating != 'N/A' else 0
                            except:
                                vote_average = 0
                            
                            # Convert votes
                            imdb_votes = details.get('imdbVotes', '0').replace(',', '')
                            try:
                                vote_count = int(imdb_votes)
                            except:
                                vote_count = 0
                            
                            # Determine if new (released in last 2 years)
                            is_new = False
                            release_year = details.get('Year', '')
                            try:
                                if release_year and int(release_year) >= datetime.now().year - 2:
                                    is_new = True
                            except:
                                pass
                            
                            cursor.execute('''
                                INSERT OR REPLACE INTO movies 
                                (id, title, overview, poster_path, release_date, vote_average, vote_count, 
                                 genres, runtime, director, cast, country, language, awards, box_office, is_new)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                imdb_id,
                                details.get('Title', ''),
                                details.get('Plot', ''),
                                details.get('Poster', ''),
                                details.get('Released', ''),
                                vote_average,
                                vote_count,
                                details.get('Genre', ''),
                                details.get('Runtime', ''),
                                details.get('Director', ''),
                                details.get('Actors', ''),
                                details.get('Country', ''),
                                details.get('Language', ''),
                                details.get('Awards', ''),
                                details.get('BoxOffice', ''),
                                is_new
                            ))
        
        conn.commit()
        conn.close()
    
    def search_and_add_movie(self, title):
        """Search for a specific movie and add it to database"""
        if OMDB_API_KEY == 'demo_key':
            return None
            
        # Search for the movie
        movies = self.search_omdb_movies(title)
        if movies:
            # Get the first result
            movie = movies[0]
            imdb_id = movie.get('imdbID')
            
            if imdb_id:
                # Get detailed information
                details = self.get_movie_details(imdb_id)
                if details:
                    conn = sqlite3.connect('flexnot.db')
                    cursor = conn.cursor()
                    
                    # Convert ratings
                    imdb_rating = details.get('imdbRating', 'N/A')
                    try:
                        vote_average = float(imdb_rating) if imdb_rating != 'N/A' else 0
                    except:
                        vote_average = 0
                    
                    imdb_votes = details.get('imdbVotes', '0').replace(',', '')
                    try:
                        vote_count = int(imdb_votes)
                    except:
                        vote_count = 0
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO movies 
                        (id, title, overview, poster_path, release_date, vote_average, vote_count, 
                         genres, runtime, director, cast, country, language, awards, box_office, is_new)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        imdb_id,
                        details.get('Title', ''),
                        details.get('Plot', ''),
                        details.get('Poster', ''),
                        details.get('Released', ''),
                        vote_average,
                        vote_count,
                        details.get('Genre', ''),
                        details.get('Runtime', ''),
                        details.get('Director', ''),
                        details.get('Actors', ''),
                        details.get('Country', ''),
                        details.get('Language', ''),
                        details.get('Awards', ''),
                        details.get('BoxOffice', ''),
                        False
                    ))
                    
                    conn.commit()
                    conn.close()
                    return details
        return None
    
    def get_recommendations(self, user_id, limit=20):
        """Generate movie recommendations for a user"""
        conn = sqlite3.connect('flexnot.db')
        
        # Get user's rated movies
        try:
            user_ratings = pd.read_sql_query('''
                SELECT movie_id, rating FROM user_ratings WHERE user_id = ?
            ''', conn, params=(user_id,))
        except:
            user_ratings = pd.DataFrame()
        
        # Get all movies
        try:
            movies = pd.read_sql_query('''
                SELECT * FROM movies ORDER BY vote_average DESC, vote_count DESC
            ''', conn)
        except:
            movies = pd.DataFrame()
        
        conn.close()
        
        if user_ratings.empty or movies.empty:
            # Return popular movies for new users
            return movies.head(limit).to_dict('records') if not movies.empty else []
        
        # Content-based recommendation using movie overviews and genres
        rated_movie_ids = user_ratings['movie_id'].tolist()
        liked_movies = user_ratings[user_ratings['rating'] >= 4]['movie_id'].tolist()
        
        if not liked_movies:
            # If no highly rated movies, return popular unrated movies
            unrated_movies = movies[~movies['id'].isin(rated_movie_ids)]
            return unrated_movies.head(limit).to_dict('records')
        
        # Get genres of liked movies
        liked_movie_genres = []
        for movie_id in liked_movies:
            movie_data = movies[movies['id'] == movie_id]
            if not movie_data.empty:
                genres = movie_data.iloc[0]['genres']
                if genres:
                    liked_movie_genres.extend(genres.split(', '))
        
        # Find movies with similar genres
        recommendations = []
        for _, movie in movies.iterrows():
            if movie['id'] not in rated_movie_ids:
                movie_genres = movie['genres'].split(', ') if movie['genres'] else []
                # Check if movie has any genre in common with liked movies
                if any(genre in liked_movie_genres for genre in movie_genres):
                    recommendations.append(movie.to_dict())
        
        # Sort by rating and return top recommendations
        recommendations.sort(key=lambda x: x['vote_average'], reverse=True)
        
        # Fill remaining slots with popular movies if needed
        if len(recommendations) < limit:
            popular_movies = movies[~movies['id'].isin(rated_movie_ids + [r['id'] for r in recommendations])]
            remaining = limit - len(recommendations)
            recommendations.extend(popular_movies.head(remaining).to_dict('records'))
        
        return recommendations[:limit]

# Initialize the recommendation system
movie_system = MovieRecommendationSystem()

@app.route('/')
def index():
    """Homepage with featured movies"""
    conn = sqlite3.connect('flexnot.db')
    cursor = conn.cursor()
    
    # Get featured movies (popular and highly rated)
    cursor.execute('''
        SELECT * FROM movies 
        WHERE vote_average >= 7.0 
        ORDER BY vote_average DESC, vote_count DESC 
        LIMIT 20
    ''')
    featured_movies = cursor.fetchall()
    
    # Get new releases
    cursor.execute('''
        SELECT * FROM movies 
        WHERE is_new = 1 
        ORDER BY release_date DESC 
        LIMIT 10
    ''')
    new_releases = cursor.fetchall()
    
    # If no new releases, get recent movies
    if not new_releases:
        cursor.execute('''
            SELECT * FROM movies 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        new_releases = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         featured_movies=featured_movies,
                         new_releases=new_releases)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            flash('All fields are required!')
            return render_template('register.html')
        
        conn = sqlite3.connect('flexnot.db')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            flash('Username or email already exists!')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash) 
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            conn.commit()
            flash('Registration successful! Please login.')
            conn.close()
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed. Please try again.')
            conn.close()
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required!')
            return render_template('login.html')
        
        conn = sqlite3.connect('flexnot.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard with personalized recommendations"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    recommendations = movie_system.get_recommendations(user_id)
    
    return render_template('dashboard.html', 
                         recommendations=recommendations,
                         username=session['username'])

@app.route('/movie/<movie_id>')
def movie_details(movie_id):
    """Movie details page"""
    conn = sqlite3.connect('flexnot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = cursor.fetchone()
    
    if not movie:
        flash('Movie not found!')
        conn.close()
        return redirect(url_for('index'))
    
    # Get user rating if logged in
    user_rating = None
    if 'user_id' in session:
        cursor.execute('SELECT rating FROM user_ratings WHERE user_id = ? AND movie_id = ?', 
                      (session['user_id'], movie_id))
        rating_result = cursor.fetchone()
        if rating_result:
            user_rating = rating_result[0]
    
    conn.close()
    
    return render_template('movie_details.html', 
                         movie=movie, 
                         user_rating=user_rating)

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    """Rate a movie"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    movie_id = data.get('movie_id')
    rating = data.get('rating')
    
    if not movie_id or not rating:
        return jsonify({'error': 'Missing data'}), 400
    
    try:
        rating = float(rating)
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rating'}), 400
    
    conn = sqlite3.connect('flexnot.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO user_ratings (user_id, movie_id, rating)
            VALUES (?, ?, ?)
        ''', (session['user_id'], movie_id, rating))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Database error'}), 500

@app.route('/search')
def search():
    """Search movies"""
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('search.html', movies=[], query='')
    
    conn = sqlite3.connect('flexnot.db')
    cursor = conn.cursor()
    
    # Search in local database first
    cursor.execute('''
        SELECT * FROM movies 
        WHERE title LIKE ? OR overview LIKE ? OR cast LIKE ? OR director LIKE ?
        ORDER BY vote_average DESC, vote_count DESC
        LIMIT 50
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    
    movies = cursor.fetchall()
    
    # If no results and API key available, search OMDB
    if not movies and OMDB_API_KEY != 'demo_key':
        new_movie = movie_system.search_and_add_movie(query)
        if new_movie:
            # Refresh search after adding new movie
            cursor.execute('''
                SELECT * FROM movies 
                WHERE title LIKE ? OR overview LIKE ?
                ORDER BY vote_average DESC, vote_count DESC
                LIMIT 50
            ''', (f'%{query}%', f'%{query}%'))
            movies = cursor.fetchall()
    
    conn.close()
    
    return render_template('search.html', movies=movies, query=query)

@app.route('/add_movie', methods=['POST'])
def add_movie():
    """Add a new movie from OMDB"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    title = data.get('title', '').strip()
    
    if not title:
        return jsonify({'error': 'Movie title required'}), 400
    
    movie = movie_system.search_and_add_movie(title)
    if movie:
        return jsonify({'success': True, 'movie': movie})
    else:
        return jsonify({'error': 'Movie not found'}), 404

@app.route('/update_movies')
def update_movies():
    """Manually update movie database"""
    if OMDB_API_KEY != 'demo_key':
        movie_system.update_movie_database()
        flash('Movie database updated successfully!')
    else:
        flash('Please set OMDB_API_KEY to update movies from API')
    return redirect(url_for('index'))

@app.route('/watchlist')
def watchlist():
    """User's watchlist"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('flexnot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.* FROM movies m
        JOIN watchlist w ON m.id = w.movie_id
        WHERE w.user_id = ?
        ORDER BY w.created_at DESC
    ''', (session['user_id'],))
    
    watchlist_movies = cursor.fetchall()
    conn.close()
    
    return render_template('watchlist.html', movies=watchlist_movies)

@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
    """Add movie to watchlist"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    movie_id = data.get('movie_id')
    
    if not movie_id:
        return jsonify({'error': 'Movie ID required'}), 400
    
    conn = sqlite3.connect('flexnot.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO watchlist (user_id, movie_id)
            VALUES (?, ?)
        ''', (session['user_id'], movie_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Database error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)