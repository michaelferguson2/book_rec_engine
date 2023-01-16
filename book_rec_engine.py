import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", 
                   page_title="My Next Book Is",
                   page_icon="./data/blue-book.png") 

book_data = pd.read_pickle("./data/best_books_working_20221229.pkl")
cosine_sim = np.load('./data/cosine_sim_20221229.npy')
indices = pd.Series(book_data.index, index=book_data['title'])

book_data['desc'] = book_data['desc'].str.replace("#", "\n", regex=False)

def desc_sim(title, sim_matrix):
    """Returns a list of book recs based on a given title based on the 
    similarity matrix
    Args:
        title (str): Title of the book in question
        sim_matrix (array): A matrix of similarly scores across all book titles
    Returns:
        array: A list of books similar to the title book based on the
        similarity score
    Notes:
        The return list includes the title as the first item    
    """
    idx = indices[title]
    
    sim_scores1 = list(enumerate(sim_matrix[idx]))    
    sim_scores2 = sorted(sim_scores1, key=lambda x: x[1], reverse=True)
    sim_scores3 = sim_scores2[0:15]
    
    book_indices = [i[0] for i in sim_scores3]
    frame = {'recs index': book_indices,
             'title': book_data['title'].iloc[book_indices],
             'unique_id':book_data['unique_id'].iloc[book_indices]}
    
    dataframe = pd.DataFrame(frame)
    return dataframe


def rec_table(eng_output, split=True):
    """Takes engine output and creates full dataframe
    """
    output_index = eng_output['recs index']
    frame = {
        'title': [book_data['title'][i] for i in output_index],
        'author': [book_data['author'][i] for i in output_index],
        'desc': [book_data['desc'][i] for i in output_index],
        'genre': [book_data['genre'][i] for i in output_index],
        'rating': [book_data['rating'][i] for i in output_index],
        'cover link': [book_data['cover link'][i] for i in output_index],
        'book link': [book_data['book link'][i] for i in output_index],
        'recs index': output_index}
    dataframe = pd.DataFrame(frame)
    
    if split is not True:
    
        return dataframe
    else:
        input_suggestion = dataframe.iloc[0]
        output_recs = dataframe.iloc[1:]
        return input_suggestion, output_recs


def list_overlap(a, b, num):      
    if len(set(a) & set(b)) > num:
        return True
    else:
        return False


def overlap_by_genre(user_select, table, num):
    indexes = []
    titles = []
    for i in range(len(table['recs index'])):
        if list_overlap(user_select['genre'],
                        table['genre'].iloc[i], num) is True:
            indexes.append(table['recs index'].iloc[i])
            titles.append(table['title'].iloc[i])
    
    dataframe = pd.DataFrame({'recs index': indexes,
                              'title': titles})
    return dataframe   


def limit_by_genre(table, genre=None):
    table.reset_index(inplace=True, drop=True)
    
    if type(genre) == str:
        genre = [genre]  # this is because of how streamlit works
        
    keep = []
    if genre is None:
        val = table
    elif len(genre) == 1 and genre[0] != 'All':
        for i in range(len(table['genre'])):
            if genre[0] in table['genre'][i]:
                keep.append(i)
        val = table.iloc[keep]
    else:
        for i in range(len(table['title'])):
            if len(set(genre) & set(table['genre'][i])) == len(set(genre)):
                keep.append(i)
        val = table.iloc[keep]
        
    return val


def include_author(suggestion, table, include=True):
    val = table
    if include is False:
        val = table.loc[table['author'] != suggestion['author']]
    return val


def book_rec_engine(title_input, genre_select=None,
                    num_overlap=0, title_author=False):

    full_recs = desc_sim(title_input, cosine_sim)
    user_select, rec_output0 = rec_table(full_recs, split=True)

    limit_output = limit_by_genre(rec_output0, genre=genre_select)
    rec_output1 = rec_table(limit_output, split=False)

    overlap_output = overlap_by_genre(user_select, rec_output1, num_overlap)
    rec_output2 = rec_table(overlap_output, split=False)

    rec_output = include_author(user_select, rec_output2, title_author)
    
    return user_select, rec_output 


def get_index_title(table):
    indexes = []
    for i in table['title']:
        indexes.append(book_data.index[book_data['title'] == i])


def check_output_na(table):
    """This function will take the updated rec table and determine if the
    values are blank. If blank, will update the table to fill out NA in all 
    columns"""
    
    error_cat_link = "./data/error_cat.jpg"
    error_frame = {'title': 'NA', 'author': 'NA', 'desc': 'NA', 'rating': 'NA',
                   'genre': ['NA'], 'cover link': error_cat_link,
                   'book link': np.nan}
    if table.empty is True:
        val = pd.DataFrame(error_frame, index=[0])
    else:
        val = table
    return val


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def list_to_text(items, sep=' ', keep_dup=False):
    if keep_dup is True:
        return sep.join(items)
    else:
        items = unique(items)
        return sep.join(items)
   

def other_recs(table):
    separator = ' \n\n '
    string = []
    for i in table.index[1:]:
        string.append(''.join(['#### ',
                               table['title'][i],
                               ' by ',
                               table['author'][i],
                               '\n ',
                               table['desc'][i],
                               separator
                               ]))

    string_join = ''.join(string)
    return string_join


##############################################################################
# creating the layout
##############################################################################

# sidebar######################################################################
st.sidebar.title('My Next Book Is')

# user title input 
user_input = st.sidebar.selectbox("Something Like...",
                                  book_data['title'],
                                  index=2)

by_author_text = book_data['author'][book_data['title'] == user_input].iloc[0]
st.sidebar.markdown("by {}".format(by_author_text))


# include author
container = st.sidebar.container()
author_text = '''Include other books by **{}** in Possible Recommendations?
'''.format(by_author_text)
author_bool = container.checkbox(author_text, value=False)


st.sidebar.markdown('---')


# limit by specific genres
genre_list = ['Adventure', 'Childrens', 'Classics', 'Dystopia', 'Fantasy',
              'Historical', 'Horror', 'Mystery', 'Paranormal', 'Romance',
              'Science Fiction', 'Thriller', 'Young Adult']
limit_genre = st.sidebar.multiselect('Only Include the Below Genres?',
                                     genre_list,
                                     default=None)


# number of overlap
num_input_text = '''How Much Required Genre Overlap Between Your Input and 
Our Recommendations?'''
num_input = st.sidebar.slider(num_input_text, 
                              min_value=0, 
                              max_value=10, 
                              value=5)

# caption on genre overlap
st.sidebar.caption('''Warning: Genre Overlap of less than 3 or more than 7 
may result in major inaccuracies''')


# book engine call
user_input, rec_df = book_rec_engine(user_input, limit_genre, 
                                     num_input, author_bool)
rec_df.reset_index(inplace=True, drop=True)  # needed for author/title display

# checking if final results are NA
rec_df = check_output_na(rec_df)

# side bar genre for user input 
st.sidebar.markdown('''#### *{}* is Listed Under the Following Genres: 
'''.format(user_input['title']))
genre_list_text_user = list_to_text(user_input["genre"],
                                    sep=', ', keep_dup=False)
st.sidebar.markdown(genre_list_text_user)


# columns#####################################################################
col1, col2 = st.columns([3, 1], gap="medium")

# rec display info
col1.header("Your Top Recommendation:")
col1.subheader("*{}* by {}".format(rec_df['title'][0], rec_df['author'][0]))
col1.markdown(rec_df["desc"].iloc[0])

# display top rec genres 
genre_list_text = list_to_text(rec_df["genre"].iloc[0], 
                               sep=', ', keep_dup=False)
col1.markdown('##### *{}* is Listed Under the Following Genres:'.format(
    rec_df['title'][0]))
col1.markdown(genre_list_text)

# other recs
col1.markdown("---")
col1.markdown("##### Other Recommendations:")


other_recs_string = other_recs(rec_df)
expander = col1.expander('**Click to Expand List**')
expander.markdown(other_recs_string)


# image display
col2.image(rec_df["cover link"].iloc[0])

# streamlit run book_rec_engine.py
