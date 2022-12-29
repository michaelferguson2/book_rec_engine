import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", 
                   page_title="My Next Book",
                   page_icon=":blue-book:")

book_data = pd.read_pickle("./data/best_books_working.pkl")
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

    input_suggestion = dataframe.iloc[0]
    output_recs = dataframe.iloc[1:]

    return input_suggestion, output_recs


test_suggest, test_table = rec_table(book_engine("The Hunger Games", cosine_sim, 3))


def include_author(suggestion, table, include):
    
    if include == True:
        val = table
        val.reset_index(inplace=True, drop=True)
    elif include == False:
        val = table.loc[table['author'] != suggestion['author']]
        val.reset_index(inplace=True, drop=True)
    
    return val


#include_author(test_suggest, test_table, False)
#test_suggest['author']
#test_table = rec_table(book_engine("The Hunger Games", cosine_sim, 3))
#test_table.loc['Childrens' in test_table['genre'] == True]



def limit_by_genre(table, genre=['All']):
    table.reset_index(inplace=True, drop=True)
    keep = []
    if len(genre) == 1 and genre[0] == 'All':
        val = table 
        val.reset_index(inplace=True, drop=True)
    elif len(genre) == 1 and genre[0] != 'All':
        for i in range(len(table['genre'])):
            if (genre[0] in table['genre'][i]) == True:
                keep.append(i)
        val = table.iloc[keep]
    else:
        for i in range(len(table['genre'])):
            if len(set(genre) & set(table['genre'][i])) == len(set(genre)):
                keep.append(i)
        val = table.iloc[keep]
        val.reset_index(inplace=True, drop=True)
    return val


#genre=['Classics','Adventure']
#(genre[0] in test_table['genre'][6]) == True
#limit_by_genre(test_table, ['Classics','Adventure'])


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
# book engine output 
book_engine_output = book_engine(selection, cosine_sim, num_input)
rec_suggestion, rec_df_0 = rec_table(book_engine_output)


# genre reduction section
genre_list = ['All', 'Science Fiction', 'Dystopia', 'Fantasy',
              'Romance', 'Adventure', 'Young Adult','Historical',
              'Classics','Horror', 'Mystery']
select_genres = st.sidebar.multiselect('multi', genre_list, default='All')
rec_df_1 = limit_by_genre(rec_df_0, select_genres) 





# include rec book author section
include_author_text = "Include Author in Suggestions?"
include_author_bool = st.sidebar.checkbox(include_author_text, value=False)
rec_df = include_author(rec_suggestion, rec_df_1, include_author_bool)
rec_df.reset_index(inplace=True, drop=True)


col1.header("Your top recommendation is:")
col1.subheader("{} by {}".format(rec_df['title'][0], rec_df['author'][0]))
col1.markdown(rec_df["desc"].iloc[0].replace("#","\n"))
col1.subheader("Other Suggestions")
col1.dataframe(rec_df[['title', 'author','genre', 'rating']])

col2.image(rec_df["cover link"].iloc[0])







#streamlit run book_rec_engine_testing.py





#testS, testDF = rec_table(book_engine("To Kill a Mockingbird", cosine_sim, 1))
#limit_by_genre(testDF, 'All') 





















