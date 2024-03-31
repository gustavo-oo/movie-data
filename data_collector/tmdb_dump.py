import requests
import pandas as pd
import time
import os

from typing import Dict, List, TypedDict

class GenreDict(TypedDict):
    id: int
    name: str
    
class MovieDict(TypedDict):
    genres: List[str]
    
session = requests.Session()

def get_from_api(endpoint: str):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkZmUyZjVjMTI4Y2QxMDBkNDdhYWRkOGNjMTE4OTIzMyIsInN1YiI6IjY2MDA2MGY2NDU5YWQ2MDE2NGY4NzQzNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.z1-zQCjzRYFcMqNghXHpCpuOtqPr6vh1Imj8HAeqdbU"
    }
    api_url = "https://api.themoviedb.org/3/"
    
    response = session.get(api_url + endpoint, headers=headers)
    
    while response.status_code != 200:
        time.sleep(0.5)
        response = session.get(api_url + endpoint, headers=headers)
        print(f'Erro no request do Endpoint {endpoint}. Tentando novamente...')
    return response

genres_cache = None  # Initialize cache
def get_genres() -> Dict[int, str]:
    global genres_cache
    if genres_cache is not None:
        return genres_cache
    
    genres_endpoint = "genre/movie/list?language=en"
    response = get_from_api(genres_endpoint)
    response_json: Dict[str, List[GenreDict]] = response.json()
    genres = response_json["genres"]
    
    genres_map: Dict[int, str] = {}
    
    for genre in genres:
        genres_map[genre["id"]] = genre["name"]
        
    genres_cache = genres_map
    return genres_map

def get_movies(page: int):
    movies_endpoint = f'discover/movie?include_adult=false&include_video=false&language=en-US&page={page}&sort_by=popularity.desc'
    response = get_from_api(movies_endpoint)
    movies = response.json()["results"]
    
    genres = get_genres()
    
    movies_list: List[MovieDict] = []
    
    for movie in movies:
        movie_id = movie["id"]
        
        details = get_movie_details(movie_id)
        credits = get_movie_credits(movie_id)
        
        movie.update(details)
        movie.update(credits)
        
        movie["genres"] = []
        for genre_id in movie["genre_ids"]:
            genre = genres[genre_id]
            movie["genres"].append(genre)
        movies_list.append(movie)
        
    return movies_list
    
def get_movie_details(movie_id: int):
    movie_detail_endpoint = f'movie/{movie_id}?language=en-US'
    response = get_from_api(movie_detail_endpoint)
    return response.json()

def get_movie_credits(movie_id: int):
    movie_credits_endpoint = f'movie/{movie_id}/credits?language=en-US'
    response = get_from_api(movie_credits_endpoint)
    return response.json()

def load_progress():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as f:
            return int(f.read().strip())
    return 1

def save_progress(page: int):
    with open('progress.txt', 'w') as f:
        f.write(str(page))

if __name__ == '__main__':
    file_name = "tmdb_dump.csv"
    start_page = load_progress()
    final_page = 3
    
    batch_size = 10
    movies_accumulator: List[MovieDict] = []

    with open(f'data/{file_name}', 'a') as file:
        for current_page in range (start_page, final_page + 1):
            print(f'Downloading page: {current_page}')
            
            movies = get_movies(current_page)
            movies_accumulator.extend(movies)
            
            print(f'Finished page: {current_page}')
            
            if (current_page % batch_size == 0) or (current_page == final_page):
                movies_df = pd.DataFrame(movies_accumulator)
                
                print(f'Updating file from page {current_page-batch_size+1} to page {current_page}')
                movies_df.to_csv(file, index=False, encoding='utf-8')

                save_progress(current_page)