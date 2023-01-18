from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MaxAbsScaler
import numpy as np
import pandas as pd
import re
from html import escape, unescape

def get_index_from_name(name, anime):
    return anime[anime['name'] == name].index.tolist()[0]


def get_id_from_partial_name(partial, anime):
    all_anime_names = anime['name'].values
    results = pd.DataFrame(columns=['name', 'id'])

    for name in all_anime_names:
        if partial in name:
            results = results.append({'name': name, 'id': all_anime_names.index(name)}, ignore_index=True)

    return results

def get_similar_names(partial, anime=None):
    partial = partial.lower()
    if anime is None:
        anime = pd.read_csv('Anime Recommender/app/static/anime.csv')

    anime['name_lower'] = anime['name'].map(lambda name: name.lower())
    anime_names = anime['name_lower'].values
        
    results = pd.DataFrame(columns=['name', 'image_url'])

    for name_lower in anime_names:
        if partial in name_lower:
            name = anime[anime['name_lower'] == name_lower]['name'].values[0]
            image_url = anime[anime['name_lower'] == name_lower]['image_url'].values[0]

            results = results.append({'name': name, 'image_url': image_url}, ignore_index=True)

    return results

def get_random_animes(anime=None):
    if anime is None:
        anime = pd.read_csv('Anime Recommender/app/static/anime.csv')

    anime_type = anime['genre'].str.get_dummies(sep=", ")

    anime = pd.concat([anime, anime_type], axis=1)
    
    anime = anime[(anime['Hentai'] != 1) & (anime['Yaoi'] != 1) & (
        anime['Yuri'] != 1) & (anime['Shounen Ai'] != 1) & (anime['Shoujo Ai'] != 1)]
    
    results = pd.DataFrame(columns=['name', 'image_url'])

    ids = np.random.choice(anime['anime_id'], size=(10))

    for id in ids:
        results = results.append({'name': anime[anime['anime_id'] == id]['name'].values[0],
                                  'image_url': anime[anime['anime_id'] == id]['image_url'].values[0]}, ignore_index=True)

    return results

def get_similar_animes(query=None, id=None):
    anime = pd.read_csv('Anime Recommender/app/static/anime.csv')
    animes = pd.read_csv('Anime Recommender/app/static/similar_animes.csv', header=None, index_col=0)

    results = pd.DataFrame(columns=['name', 'image_url'])
    if id:
        for id in animes.iloc[id]:
            results = results.append({'name': anime.loc[id]['name'], 'image_url': anime.loc[id]['image_url']}, ignore_index=True)
        return results   
    if query:
        found_id = get_index_from_name(query, anime)
        for id in animes.iloc[found_id]:
            results = results.append({'name': anime.loc[id]['name'], 'image_url': anime.loc[id]['image_url']}, ignore_index=True)
        return results

def get_anime_details(name=None):
    anime = pd.read_csv('Anime Recommender/app/static/anime.csv')
    
    result = pd.DataFrame(columns=['name', 'image_url', 'anime_genre', 'anime_type', 'anime_episodes', 'anime_rating'])

    id = get_index_from_name(name, anime)

    result = result.append({'name': anime.loc[id]['name'], 'image_url': anime.loc[id]['image_url'], 'anime_genre': anime.loc[id]['genre'], 'anime_type': anime.loc[id]['type'], 'anime_episodes': anime.loc[id]['episodes'], 'anime_rating': anime.loc[id]['rating'] }, ignore_index=True)

    return result

def nearest_neighbors():
    anime = pd.read_csv('Anime Recommender/app/static/anime.csv')

    anime_features = pd.concat([anime['genre'].str.get_dummies(sep=', '), pd.get_dummies(anime[['type']]), anime[['rating']], anime[['members']], anime['episodes']], axis=1)

    #anime["name"] = anime["name"].map(lambda name: re.sub('[^A-Za-z0-9]+', " ", name))

    max_abs_scaler = MaxAbsScaler()
    anime_features = max_abs_scaler.fit_transform(anime_features)

    nbrs = NearestNeighbors(n_neighbors=11, algorithm='auto').fit(anime_features)
    distances, indices = nbrs.kneighbors(anime_features)

    np.savetxt('C:/Users/81274853/OneDrive - BAT/Data Science/python/Anime Recommender/app/static/similar_animes.csv', indices, delimiter=',', fmt='%s')