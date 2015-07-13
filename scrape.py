__author__ = 'erindooley'
import pickle
import pandas as pd

with open("movie_data.pkl", 'r') as picklefile:
     all_movies = pickle.load(picklefile)

df = pd.DataFrame(all_movies)
print df.head()