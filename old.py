# Na limpeza dos dados transformar o genre_id em genre
        
    # movie["genres"] = []
    # for genre_id in movie["genre_ids"]:
    #     genre = genres[genre_id]
    #     movie["genres"].append(genre)

# Remover essas colunas de filmes
# def clean_movie_columns(movie):
#     columns_to_delete = ['adult', 'backdrop_path', 'genre_ids', 'poster_path', 'video', 'homepage', 'imdb_id', 'popularity']
    
#     for column in columns_to_delete:
#         del movie[column]
        
#     return movie

# Remover essas colunas de cast e crew
#  cast = response_json["cast"]
#     crew = response_json["crew"]
#     props_to_delete = ['adult', 'id', 'original_name', 'popularity', 'profile_path', 'cast_id', 'credit_id']
    
#     for props in props_to_delete:
#         del cast[props]
#         del crew[props]
    
#     response_json["cast"] = cast
#     response_json["crew"] = crew

# Transformar as keywords

    # keywords = []
    
    # for keyword in response_json["keywords"]:
    #     keywords.append(keyword["name"])    

import pandas as pd
import ast
from pandas import DataFrame

def map_genre_ids_to_names(genres_ids_col, genres_dict):
    return genres_ids_col.map(lambda genre_ids: [genres_dict[id] for id in ast.literal_eval(genre_ids)])

def map_keywords(keywords_col):
    return keywords_col.map(lambda keywords_dict_list: [keyword['name'] for keyword in ast.literal_eval(keywords_dict_list)])

def map_spoken_languages(spoken_languages_col):
    return spoken_languages_col.map(lambda spoken_languages_dict_list: [spoken_language['english_name'] for spoken_language in ast.literal_eval(spoken_languages_dict_list)])

def get_country(country_iso, countries_dict):
    if country_iso == '': 
        return None
    return countries_dict[country_iso]

def map_production_companies(production_companies_col, countries_dict):
    return production_companies_col.map(lambda production_companies_dict_list: (
            [
                {'name': production_companies_dict['name'], 'origin_country': get_country(production_companies_dict['origin_country'], countries_dict)}
                for production_companies_dict in ast.literal_eval(production_companies_dict_list) 
            ]
        )
    )

def map_production_countries(production_countries_col):
    return production_countries_col.map(lambda production_countries: [pd_dict['name'] for pd_dict in ast.literal_eval(production_countries)])

def remove_dict_props(dict, props_list):
    for prop in props_list:
        dict.pop(prop, None)

    return dict

def map_cast(cast_col):
    def map_cast_gender(actor):
        gender_dict = {
            0: "Not set/not specified",
            1: "Female",
            2: "Male",
            3: "Non-binary"
        }
        gender_id = actor['gender']
        actor['gender'] = gender_dict[gender_id]
        return actor
        
    props_to_remove = ['adult', 'id', 'original_name', 'popularity', 'profile_path', 'cast_id', 'credit_id']
    
    return cast_col.map(lambda cast: [map_cast_gender(remove_dict_props(cast_dict, props_to_remove)) for cast_dict in ast.literal_eval(cast)])

if __name__ == '__main__':
    start_year = 2013
    end_year = 2023
    
    raw_data_common_name = 'raw_data/tmdb_dump'
    prepared_data_common_name = 'prepared_data/tmdb_dump'
    
    genres_df = pd.read_csv(f'{raw_data_common_name}-genres.csv')
    genres = genres_df.set_index('id')['name'].to_dict()
    
    countries_df = pd.read_csv(f'{raw_data_common_name}-countries.csv')
    countries = countries_df.set_index('iso_3166_1')['english_name'].to_dict()
    
    year = 2013

    file_path = f'{raw_data_common_name}-{year}.csv'
    movies_df = pd.read_csv(file_path, encoding='utf-8', lineterminator='\n')

    movies_df['genres'] = map_genre_ids_to_names(movies_df['genre_ids'], genres)
    movies_df['keywords'] = map_keywords(movies_df['keywords'])
    movies_df['spoken_languages'] = map_spoken_languages(movies_df['spoken_languages'])
    movies_df['production_companies'] = map_production_companies(movies_df['production_companies'], countries)
    movies_df['production_countries'] = map_production_countries(movies_df['production_countries'])
    movies_df['cast'] = map_cast(movies_df['cast'])
    movies_df['crew'] = map_cast(movies_df['crew'])
    
    columns_to_remove = ['adult', 'backdrop_path', 'genre_ids', 'poster_path', 'video', 'homepage', 'popularity', 'tagline']

    movies_df.drop(columns_to_remove, axis=1, inplace=True)

    movies_df.to_csv(f'{prepared_data_common_name}-{year}.csv', index=False, encoding='utf-8', header=True)