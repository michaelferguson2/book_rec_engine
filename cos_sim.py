import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.metrics.pairwise import linear_kernel
import os

path = os.getcwd()
book_data0 = pd.read_pickle("./data/best_books_20221222.pkl")
book_data0.drop_duplicates(subset=['title'], inplace=True)
book_data0.reset_index(inplace=True, drop=True)

book_data1 = pd.read_pickle("./data/best_books_20221229.pkl")
book_data1.drop_duplicates(subset=['title'], inplace=True)
book_data1.reset_index(inplace=True, drop=True)

merged_book_data = pd.concat([book_data0, book_data1], ignore_index=True)
merged_book_data.drop_duplicates(subset=['title'], inplace=True)
merged_book_data.reset_index(inplace=True, drop=True)
merged_book_data.to_pickle("./data/best_books_working_20221229.pkl")


tfid_transformer = TfidfVectorizer(stop_words='english')
desc_matrix = tfid_transformer.fit_transform(merged_book_data['desc'].astype(str))
#desc_matrix.shape

#tfid_transformer.get_feature_names_out()[300:310]

cosine_sim = cosine_similarity(desc_matrix, desc_matrix)
cosine_sim.shape

np.save('./data/cosine_sim_20221229', cosine_sim)






