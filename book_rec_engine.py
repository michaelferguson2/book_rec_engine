import numpy as np
import pandas as pd
import os
import streamlit as st

st.set_page_config(layout="wide", 
                   page_title="My Next Book",
                   page_icon=":blue-book:")

#path = os.getcwd()


book_data = pd.read_pickle("./data/best_books_working.pkl")


#book_data = pd.read_pickle(path+r"\data\best_books_working.pkl")
#book_data.drop_duplicates(subset=['title'], inplace=True)
#book_data.reset_index(inplace=True, drop=True)

#cosine_sim = np.load(path+'\data\cosine_sim.npy')

cosine_sim = np.load('./data/cosine_sim.npy')


indices = pd.Series(book_data.index,index=book_data['title']).drop_duplicates()

def desc_sim(title, sim_matrix):
    """Returns a list of book recs based on a given title based on the 
    similarity matrix
    Args:
        title (str): Title of the book in question
        sim_matrix (array): A matrix of similary scores across all book titles
    Returns:
        array: A list of books similary to the title book based on the 
        similarity score
    Notes:
        The return list includes the title as the first item    
    """
    idx = indices[title]
    
    sim_scores1 = list(enumerate(sim_matrix[idx]))    
    sim_scores2 = sorted(sim_scores1, key=lambda x: x[1], reverse=True)
    sim_scores3 = sim_scores2[0:30]
    
    book_indices = [i[0] for i in sim_scores3]
    
    return book_data['title'].iloc[book_indices]


def grene_overlap(a, b, num):
    """Counts the number of overlap between two lists and returns True if 
    the number of overlap is higher than the minimum set
    Args:
        a (list or array): First comparison list
        b (list or array): Second comparison list
        num (int): the minimum amout of overlap between the lists to return a 
        True value    
    Retrns:
        bool: 
    """    
    
    if len(set(a) & set(b)) > num:
        return True
    else:
        return False


def reduce_by_genre(full_recs, num):
    """
    """
    reduced_recs = []
    recs_index = []
    
    for i in range(len(full_recs)):
        if grene_overlap(book_data['genre'][full_recs.index[0]], 
                         book_data['genre'][full_recs.index[i]], num) == True:
            reduced_recs.append(book_data['title'][full_recs.index[i]])
            recs_index.append(full_recs.index[i])
    recs_df = pd.DataFrame({'index':recs_index, 'title':reduced_recs})
    
    return recs_df


def book_engine(title, sim_matrix, num):
    
    recs = desc_sim(title, sim_matrix)
    final_recs = reduce_by_genre(recs, num)
    
    return final_recs


def rec_table(eng_output):
    """Takes engine output and creates full dataframe
    """
    
    frame = {
        'title':[book_data['title'][i] for i in eng_output['index']],
        'author':[book_data['author'][i] for i in eng_output['index']],
        'desc':[book_data['desc'][i] for i in eng_output['index']],
        'genre':[book_data['genre'][i] for i in eng_output['index']],
        'rating':[book_data['rating'][i] for i in eng_output['index']],
        'cover link':[book_data['cover link'][i] for i in eng_output['index']],
        'book link':[book_data['book link'][i] for i in eng_output['index']]}

    dataframe = pd.DataFrame(frame)

    return dataframe


def include_author(table, include):
    
    if include == True:
        val = table.iloc[1:] 
        val.reset_index(inplace=True, drop=True)
    elif include == False:
        val = table.loc[table['author'] != table['author'][0]]
        val.reset_index(inplace=True, drop=True)
    
    return val



st.sidebar.title('My Next Book Is')
col1, col2 = st.columns([3, 1], gap="medium")


selection = st.sidebar.selectbox("I Want Something Like...", 
                                 book_data['title'],
                                 index=2)

by_author_text = book_data['author'][book_data['title'] == selection].iloc[0]
st.sidebar.text("by {}".format(by_author_text))

num_input = st.sidebar.number_input('Force Genre Overlap', 
                                    min_value=1,
                                    max_value=5,
                                    value=3)

rec_values = book_engine(selection, cosine_sim, num_input)
rec_df_0 = rec_table(rec_values)
#rec_df_0.reset_index(inplace=True, drop=True)



include_author_text = "Include Author in Suggestions?"
include_author_bool = st.sidebar.checkbox(include_author_text, value=False)
rec_df = include_author(rec_df_0, include_author_bool)
rec_df.reset_index(inplace=True, drop=True)

#rec_table(book_engine('Jane Eyre', cosine_sim, 1)).iloc[0:10]



# column1
col1.header("Your top recommendation is:")
col1.subheader("{} by {}".format(rec_df['title'][0], rec_df['author'][0]))
col1.markdown(rec_df["desc"].iloc[0].replace("#","\n"))
col1.subheader("Other Suggestions")
col1.dataframe(rec_df[['title', 'author','genre', 'rating']])

col2.image(rec_df["cover link"].iloc[0])







#streamlit run streamlit_testing.py









