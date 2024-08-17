import requests
import random
import os

# Configuration & Paths
SECRET_1 = os.environ['TRAKT_SECRET']
SECRET_2 = os.environ['TMDB_SECRET']
SECRET_3 = os.environ['UN_SECRET']

headers = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': SECRET_1
}

cover_base_image_url = 'https://image.tmdb.org/t/p/w500'
collection_url = f'https://api.trakt.tv/users/{SECRET_3}/collection/movies'
recommendations_url = 'https://api.trakt.tv/lists/28498128/items/movies?extended=full'

def fetch_trakt_data(url):
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        return response.json()
    print(f"Error: {response.status_code}, Message: {response.text}")
    return []

def get_collection():
    data = fetch_trakt_data(collection_url)
    return {(item['movie']['title'], item['movie']['year']) for item in data}

def get_recommendations():
    data = fetch_trakt_data(recommendations_url)
    return [
        {
            'title': item['movie']['title'],
            'year': item['movie']['year'],
            'tagline': item['movie']['tagline'],
            'overview': item['movie']['overview'],
            'rating': item['movie']['rating'],
            'slug': item['movie']['ids'].get('slug'),
            'imdb': item['movie']['ids'].get('imdb'),
            'tmdb': item['movie']['ids'].get('tmdb'),
            'trailer': item['movie']['trailer']
        } for item in data
    ]

def get_movie_image_url(tmdb_id):
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={SECRET_2}'
    response = requests.get(url)
    if response.status_code == 200:
        poster_path = response.json().get('poster_path')
        if poster_path:
            return f"{cover_base_image_url}{poster_path}"
    return "Doesnt seem to be any poster for this film ¯\_(ツ)_/¯"

def add_image_urls_to_movies(movies):
    for movie in movies:
        movie['image'] = get_movie_image_url(movie['tmdb'])

def generate_html(movie_data, status_flag, status_color):
    return f"""
    <div class="movie-card">
        <div class="poster-wrapper">
            <div class="poster">
                <img src="{movie_data['image']}" alt="Poster"/>
                <div class="status-flag" style="background-color: {status_color}">
                    <p>{status_flag}</p>
                </div>
            </div>
        </div>
        <div class="movie-info">
            <div class="header-section">
                <h2>{movie_data['title']}</h2>
                <div class="extra">
                    <div class="ratings"><p>&#9733; {round(movie_data['rating'], 1)}</p></div>
                    <p class="tagline"><span>{movie_data['tagline']}</span></p>
                </div>
            </div>
            <div class="link-section">
                <h3>LINKS</h3>
                <div class="links">
                    <a href="{movie_data['trailer']}" target="_blank"><img src="images/youtube.png" alt="YouTube" title="Trailer"></a>
                    {generate_request_or_watch_link(movie_data)}
                </div>
            </div>
            <div class="about-section">
                <h3>ABOUT</h3>
                <p>{movie_data['overview']}</p>
            </div>
        </div>
    </div>
    <br>"""

def generate_request_or_watch_link(movie):
    if movie['in_collection']:
        return '<a href="http://vault:8096/web/index.html" target="_blank"><img src="images/media.png" alt="Media" title="Watch"></a>'
    else:
        link = f"{movie['slug']}"
        return f'<a href="https://trakt.tv/movies/{link}" target="_blank"><img src="images/trakt.png" alt="Request" title="Request Media"></a>'

def main():
    collection_set = get_collection()
    recommendations = get_recommendations()

    for movie in recommendations:
        movie['in_collection'] = (movie['title'], movie['year']) in collection_set

    available_movies = [movie for movie in recommendations if movie['in_collection']]
    non_available_movies = [movie for movie in recommendations if not movie['in_collection']]

    random_available = random.sample(available_movies, min(3, len(available_movies)))
    random_non_available = random.sample(non_available_movies, min(3, len(non_available_movies)))

    add_image_urls_to_movies(random_available)
    add_image_urls_to_movies(random_non_available)

    html = """<html><head><link rel="stylesheet" href="./recomendations.css"></head><body><main>"""
    html += ''.join([generate_html(movie, "AVAILABLE", "#068FFF") for movie in random_available])
    html += ''.join([generate_html(movie, "REQUEST", "#0c101a") for movie in random_non_available])
    html += "</main></body></html>"

    with open("recommendations.html", "w") as file:
        file.write(html)

if __name__ == '__main__':
    main()
