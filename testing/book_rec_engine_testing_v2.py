import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", 
                   page_title="My Next Book",
                   page_icon=":blue-book:")

book_data = pd.read_pickle("./data/best_books_working_20221229.pkl")
cosine_sim = np.load('./data/cosine_sim_20221229.npy')
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
    
    frame = {'index':book_indices, 
             'title':book_data['title'].iloc[book_indices]}
    
    dataframe = pd.DataFrame(frame)
    
    title_input = dataframe.iloc[0]
    results = dataframe.iloc[1:]
    
    return title_input, results



#desc_sim('Twilight', cosine_sim)
#rec_table(desc_sim('Twilight', cosine_sim))
#reduce_by_genre(desc_sim('Twilight', cosine_sim),2)

#rec_table(reduce_by_genre(desc_sim('Twilight', cosine_sim),2), False)



def genre_overlap(a, b, num):
    """Counts the number of overlap between two lists and returns True if 
    the number of overlap is higher than the minimum set
    Args:
        a and b (list or array): First comparison list
        num (int): the min overlap between a and b to return True   
    Retrns:
        bool: 
    """       
    if len(set(a) & set(b)) > num:
        return True
    else:
        return False


def reduce_by_genre(recs, num):
    """
    """
    reduced_recs = []
    recs_index = []
    
    for i in range(len(recs)):
        if genre_overlap(book_data['genre'][recs.index[0]], 
                         book_data['genre'][recs.index[i]], num) == True:
            reduced_recs.append(book_data['title'][recs.index[i]])
            recs_index.append(recs.index[i])
    recs_df = pd.DataFrame({'index':recs_index, 'title':reduced_recs})
    
    return recs_df









def rec_table(eng_output, split=True):
    """Takes engine output and creates full dataframe
    """
    
    output_index = eng_output.index
    
    frame = {
        'title':[book_data['title'][i] for i in output_index['index']],
        'author':[book_data['author'][i] for i in output_index['index']],
        'desc':[book_data['desc'][i] for i in output_index['index']],
        'genre':[book_data['genre'][i] for i in output_index['index']],
        'rating':[book_data['rating'][i] for i in output_index['index']],
        'cover link':[book_data['cover link'][i] for i in output_index['index']],
        'book link':[book_data['book link'][i] for i in output_index['index']]}

    dataframe = pd.DataFrame(frame)
    
    if split == True:
    
        input_suggestion = dataframe.iloc[0]
        output_recs = dataframe.iloc[1:]
        return input_suggestion, output_recs
    else:
        return dataframe


def include_author(suggestion, table, include):
    
    if include == True:
        val = table
        val.reset_index(inplace=True, drop=True)
    elif include == False:
        val = table.loc[table['author'] != suggestion['author']]
        val.reset_index(inplace=True, drop=True)
    
    return val


def limit_by_genre(table, genre=None):
    table.reset_index(inplace=True, drop=True)
    keep = []
    if genre == None:
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


def check_output_na(table):
    """"This function will take the updated rec table and determine if the 
    values are blank. If blank, will update the table to fill out NA in all 
    columns"""
    
    error_cat_link = "./data/error_cat.jpg"
    error_frame = {'title':'NA','author':'NA','desc':'NA','rating':'NA',
                   'genre':'NA','cover link':error_cat_link,'book link':np.nan}
    if table.empty == True:
        val = pd.DataFrame(error_frame, index=[0])
    else:
        val = table 
    return val



rec_table(dest_output_test)



#dest_output_test = desc_sim("Pride and Prejudice", cosine_sim)


rec_suggestion_test, rec_df_0_test = desc_sim("Pride and Prejudice", cosine_sim)


rec_table(rec_suggestion_test)



limit_output_test = limit_by_genre(rec_df_0_test, None)






reduce_output_test = reduce_by_genre(limit_output_test, 1)
rec_df_2_test = rec_table(reduce_output_test, split=False)





def reduce_by_genre2(suggestion, recs, num):
    """
    """
    reduced_recs = []
    recs_index = []
    
    for i in range(len(recs)):
        if genre_overlap(suggestion['genre'], 
                         recs['genre'], num) == True:
            reduced_recs.append(book_data['title'][recs.index[i]])
            recs_index.append(recs.index[i])
    recs_df = pd.DataFrame({'index':recs_index, 'title':reduced_recs})
    
    return recs_df


rec_suggestion_test['genre']

reduce_by_genre2(rec_suggestion_test, rec_df_0_test, 1)




genre_overlap(rec_suggestion_test['genre'],
              book_data['genre'][recs.index[i]], num) == True



book_data['genre'][recs.index[i]]











st.sidebar.title('My Next Book Is')
col1, col2 = st.columns([3, 1], gap="medium")


selection = st.sidebar.selectbox("I Want Something Like...", 
                                 book_data['title'],
                                 index=2)

by_author_text = book_data['author'][book_data['title'] == selection].iloc[0]
st.sidebar.text("by {}".format(by_author_text))



# desc engine output 
user_suggestion, recs0 = desc_output = desc_sim(selection, cosine_sim)
######rec_suggestion, rec_df_0 = rec_table(desc_output)


# genre reduction section
genre_list = ['Science Fiction', 'Dystopia', 'Fantasy',
              'Romance', 'Adventure', 'Young Adult','Historical',
              'Classics','Horror', 'Mystery']
select_genres = st.sidebar.multiselect('Limit Suggestions by Genre', 
                                       genre_list, 
                                       default=None)
rec_df_1 = limit_by_genre(rec_df_0, select_genres) 

# overlap
num_input_text = 'Amount of Genre Overlap between Input and Recommendations'
num_input = st.sidebar.number_input(num_input_text, 
                                    min_value=1,
                                    max_value=10,
                                    value=3)

reduce_output = reduce_by_genre(rec_df_1, num_input)
rec_df_2 = rec_table(reduce_output, split=False)


# include rec book author section
include_author_text = "Include Author in Suggestions?"
include_author_bool = st.sidebar.checkbox(include_author_text, value=False)
rec_df = include_author(user_suggestion, rec_df_2, include_author_bool)
rec_df.reset_index(inplace=True, drop=True)






# final check on output 
rec_df = check_output_na(rec_df)



st.sidebar.text('below are genres associated \nwith your suggestion')
st.sidebar.text(user_suggestion['genre'])


col1.header("Your top recommendation is:")
col1.subheader("{} by {}".format(rec_df['title'][0], rec_df['author'][0]))
col1.markdown(rec_df["desc"].iloc[0].replace("#","\n"))
col1.subheader("Other Suggestions")
col1.dataframe(rec_df[['title', 'author','genre', 'rating']])

col2.image(rec_df["cover link"].iloc[0])






#streamlit run book_rec_engine_testing_v2.py
#testS, testDF = rec_table(book_engine("To Kill a Mockingbird", cosine_sim, 1))
#limit_by_genre(testDF, 'All') 





#streamlit run book_rec_engine_testing_v3.py
















