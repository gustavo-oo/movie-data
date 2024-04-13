from requests import Session
import pandas as pd
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from typing import Dict, List, TypedDict

class GenreDict(TypedDict):
    id: int
    name: str
    
class MovieDict(TypedDict):
    genres: List[str]
    
session = Session()
def get_from_api(endpoint: str, params: Dict[str, str] = {}):
    params['language'] = 'en-US'
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkZmUyZjVjMTI4Y2QxMDBkNDdhYWRkOGNjMTE4OTIzMyIsInN1YiI6IjY2MDA2MGY2NDU5YWQ2MDE2NGY4NzQzNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.z1-zQCjzRYFcMqNghXHpCpuOtqPr6vh1Imj8HAeqdbU",
        "User-Agent": "python-requests/2.28.2",
    }
    api_url = "https://api.themoviedb.org/3/"
    
    response = session.get(api_url + endpoint, headers=headers, params=params)
    
    sleep_time = 0.5
    sleep_factor = 2
    while response.status_code != 200:
        time.sleep(sleep_time)
        sleep_time *= sleep_factor
        response = session.get(api_url + endpoint, headers=headers)
        print(f'{response.status_code}: Erro no request do Endpoint {endpoint}. Tentando novamente em {sleep_time} segundos...')
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

total_pages = 0
def get_movies(page: int, year: int):
    global total_pages
    params = {
        'include_adult': 'false',
        'include_video': 'false',
        'page': page,
        'sort_by': 'popularity.desc',
        'vote_count.gte': '10',
        'year': year
    }
    
    print(f"Downloading page {page} - Year: {year}")

    movies_endpoint = 'discover/movie'
    response = get_from_api(movies_endpoint, params)
    response_json = response.json()
    movies = response_json["results"]
    total_pages = response_json["total_pages"]
    
    movies_list = []
    
    for movie in movies:
        movie_id = movie["id"]
        
        details = get_movie_details(movie_id)
        credits = get_movie_credits(movie_id)
        keywords = get_movie_keywords(movie_id)
        
        movie.update(details)
        movie.update(credits)
        movie.update(keywords)

        movies_list.append(movie)
        
    return movies_list
    
def get_movie_details(movie_id: int):
    movie_detail_endpoint = f'movie/{movie_id}?'
    response = get_from_api(movie_detail_endpoint)
    return response.json()

def get_movie_credits(movie_id: int):
    movie_credits_endpoint = f'movie/{movie_id}/credits'
    response = get_from_api(movie_credits_endpoint)
    return response.json()

def get_movie_keywords(movie_id: int):
    movie_keywords_endpoint = f'movie/{movie_id}/keywords'
    response = get_from_api(movie_keywords_endpoint)       
    return response.json()

def load_progress():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as f:
            content = f.read().strip()
            page, year = map(int, content.split(','))
            return (page, year)
    return (1, 2013)

def save_progress(page: int, year: int):
    with open('progress.txt', 'w') as f:
        f.write(f"{page},{year}")
    
    
def fetch_movies_in_parallel(start_page: int, end_page: int, year: int, max_workers: int) -> List[MovieDict]:
    movies_accumulator: List[MovieDict] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks to the executor for each page we want to fetch
        future_to_page = {executor.submit(get_movies, page, year): page for page in range(start_page, end_page + 1)}

        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                movies = future.result()
                movies_accumulator.extend(movies)
                print(f"Successfully fetched page {page} - Year: {year}")
            except Exception as exc:
                print(f"Page {page} generated an exception: {exc}")

    return movies_accumulator



if __name__ == '__main__':
    api_max_page = 500
    file_name = "tmdb_dump"
    start_page, start_year = load_progress()
    final_page = api_max_page

    batch_size = 50
    end_year = 2023

    for year in range(start_year, end_year + 1):
        with open(f'data/{file_name}-{year}.csv', 'a') as file:
            for current_page in range (start_page, final_page + 1, batch_size):                
                upper_limit =  final_page if current_page + batch_size > final_page else current_page + batch_size
                
                movies = fetch_movies_in_parallel(current_page, upper_limit, year, batch_size)
                final_page = total_pages
                movies_df = pd.DataFrame(movies)
                    
                print(f'Updating file from page {current_page} to page {upper_limit}')
                show_headers = current_page == 1
                movies_df.to_csv(file, index=False, encoding='utf-8', header=show_headers)

                save_progress(upper_limit, year)
        save_progress(1, year+1)