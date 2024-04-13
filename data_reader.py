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

def read_csv_to_dataframe(filepath):
    return pd.read_csv(filepath)

file_path = 'data/tmdb_dump-2013.csv'  # Replace 'your_file.csv' with your actual file path
dataframe = read_csv_to_dataframe(file_path)
if dataframe is not None:
    # print(dataframe.iloc[0]["production_companies"])
    # print()
    # print(dataframe.iloc[0]["production_countries"])
    # print()

    # print(dataframe.iloc[0]["spoken_languages"])
    # print()

    # print(dataframe.iloc[0]["cast"])
    # print()

    print(dataframe.iloc[0])
    # print()
