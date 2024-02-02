from datetime import datetime, timedelta
import os
import csv
import requests
import time
from airflow import DAG
from airflow.operators.python import PythonOperator

# Fonction pour récupérer la correspondance entre les IDs de genres et leurs noms
def get_genre_names(api_key):
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {
        'api_key': api_key,
        'language': 'en-US'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        genre_list = response.json()['genres']
        return {genre['id']: genre['name'] for genre in genre_list}
    return {}

def get_movies(api_key, number_of_movies, genre_names, csv_file_path):
    url = "https://api.themoviedb.org/3/discover/movie"
    page = 1
    total_movies = 0
    today = datetime.now().strftime('%Y-%m-%d')
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['movie_id', 'title', 'genres', 'release_date', 'poster_link'])
        writer.writeheader()
        while total_movies < number_of_movies:
            params = {
                'api_key': api_key,
                'language': 'en-US',
                'sort_by': 'popularity.desc',
                'page': page
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                results = response.json()['results']
                for movie in results:
                    release_date = movie.get('release_date', '')
                    if release_date and release_date < today:
                        movie_genres = [genre_names.get(genre_id) for genre_id in movie.get('genre_ids', [])]
                        poster_link = f"https://image.tmdb.org/t/p/original{movie.get('poster_path')}" if movie.get('poster_path') else None
                        writer.writerow({
                            'movie_id': movie['id'],
                            'title': movie['title'],
                            'genres': '|'.join(filter(None, movie_genres)),
                            'release_date': release_date,
                            'poster_link': poster_link
                        })
                        total_movies += 1
                        if total_movies >= number_of_movies:
                            break
            else:
                break
            page += 1
            time.sleep(0.5)  # to comply with rate limit of the API
            
def fetch_movies_to_csv(**context):
    api_key = context['params'].get('api_key')
    number_of_movies = context['params'].get('number_of_movies')
    
    genre_names = get_genre_names(api_key)
    
    output_folder = context['params'].get('output_folder')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    csv_file_path = os.path.join(output_folder, 'movies_data.csv')
    get_movies(api_key, number_of_movies, genre_names, csv_file_path)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 2, 2),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

dag = DAG(
    'fetch_movies_weekly',
    default_args=default_args,
    description='A DAG to fetch movies from TMDB and store in a CSV file on a weekly basis.',
    # Runs every Thursday at 14:00
    schedule_interval='15 16 * * 5',
    catchup=False
)


fetch_movies_task = PythonOperator(
    task_id='fetch_movies',
    python_callable=fetch_movies_to_csv,
    provide_context=True,
    params={
        'api_key': 'b8218bd4516663ac1ad5be68dd943a7c',
        'number_of_movies': 10, # or any other number you prefer
        'output_folder': 'data',
    },
    dag=dag,
)

fetch_movies_task