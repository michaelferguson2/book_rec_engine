import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.metrics.pairwise import linear_kernel
import os

path = os.getcwd()
book_data = pd.read_pickle(path+r"\data\best_books_20221222.pkl")
book_data.drop_duplicates(subset=['title'], inplace=True)
book_data.reset_index(inplace=True, drop=True)
book_data.to_pickle(path+r"\data\best_books_working.pkl")


tfid_transformer = TfidfVectorizer(stop_words='english')
desc_matrix = tfid_transformer.fit_transform(book_data['desc'].astype(str))
#desc_matrix.shape

#tfid_transformer.get_feature_names_out()[300:310]

cosine_sim = cosine_similarity(desc_matrix, desc_matrix)
cosine_sim.shape

np.save(path+'\data\cosine_sim', cosine_sim)






