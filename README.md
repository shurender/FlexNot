# FlexNot - Movie Recommendation System with OMDB API

A comprehensive Python Flask web application for movie recommendations using the OMDB (Open Movie Database) API with global movie database and real-time updates.

## Features

- **Global Movie Database**: Access movies from around the world via OMDB API
- **Real-time Movie Search**: Search and add new movies instantly from OMDB
- **Personalized Recommendations**: AI-powered content-based filtering using genres and ratings
- **User Authentication**: Secure login and registration system
- **Movie Rating System**: Rate movies and get better recommendations
- **Advanced Search**: Search movies by title, plot, cast, or director
- **Watchlist Management**: Save movies to watch later
- **Responsive Design**: Beautiful UI that works on all devices
- **Rich Movie Data**: Detailed information including awards, box office, runtime, and more

## OMDB API Advantages

- **Comprehensive Data**: Detailed movie information including awards, box office, ratings
- **Global Coverage**: Movies from all countries and languages
- **Real-time Access**: Search and add movies instantly
- **Rich Metadata**: Director, cast, plot, runtime, country, language information
- **Free Tier Available**: 1000 requests per day for free

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get OMDB API Key

1. Visit [OMDB API website](http://www.omdbapi.com/apikey.aspx)
2. Choose a plan (free tier available with 1000 requests/day)
3. Register and get your API key
4. Copy your API key

### 3. Environment Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` file and add your OMDB API key:
```
OMDB_API_KEY=your_actual_omdb_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Register**: Create a new account to get personalized recommendations
2. **Browse Movies**: Explore featured movies and new releases
3. **Search**: Find specific movies using the search functionality
4. **Rate Movies**: Rate movies you've watched to improve recommendations
5. **Add to Watchlist**: Save movies to watch later
6. **Get Recommendations**: Visit your dashboard for personalized suggestions
7. **Add New Movies**: Search for any movie and it will be added from OMDB

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with rich movie schema
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **API**: OMDB (Open Movie Database)
- **ML**: scikit-learn for recommendation algorithms

## API Integration Features

This application integrates with OMDB API to provide:
- **Real-time Movie Search**: Search any movie and add it instantly
- **Detailed Movie Information**: Plot, cast, director, awards, box office
- **Global Movie Coverage**: Movies from all countries and languages
- **Rich Metadata**: Runtime, country, language, awards information
- **High-quality Posters**: Movie poster images

## Recommendation Algorithm

The system uses advanced content-based filtering:
1. **Genre Analysis**: Analyzes user's preferred movie genres
2. **Rating-based Filtering**: Considers user's highly-rated movies (4+ stars)
3. **Similarity Matching**: Finds movies with similar genres and themes
4. **Popularity Fallback**: Shows popular movies for new users
5. **Continuous Learning**: Improves recommendations as users rate more movies

## Database Schema

- **users**: User authentication and profile data
- **movies**: Comprehensive movie information from OMDB
  - IMDB ID, title, plot, poster, release date
  - Ratings, votes, genres, runtime
  - Director, cast, country, language
  - Awards, box office information
- **user_ratings**: User ratings for movies (1-5 stars)
- **watchlist**: User's saved movies to watch later

## Key Features

### Movie Search and Discovery
- Search movies by title, plot, cast, or director
- Instant addition of new movies from OMDB
- Browse by genres, ratings, and release dates

### Personalized Experience
- User registration and authentication
- Personal movie ratings and watchlist
- Customized recommendations based on preferences

### Rich Movie Information
- Detailed plots and cast information
- Awards and box office data
- High-quality movie posters
- Runtime, country, and language details

## API Rate Limits

- **Free Tier**: 1000 requests per day
- **Paid Tiers**: Higher limits available
- The app includes intelligent caching to minimize API calls

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the documentation
2. Review the code comments
3. Create an issue on the repository