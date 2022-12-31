import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", 
                   page_title="My Next Book",
                   page_icon=":blue-book:")

book_data = pd.read_pickle("./data/best_books_working_20221229.pkl")
cosine_sim = np.load('./data/cosine_sim_20221229.npy')
indices = pd.Series(book_data.index,index=book_data['title']).drop_duplicates()

book_data['desc'] = book_data['desc'].str.replace("#","\n",regex=False)

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
    sim_scores3 = sim_scores2[0:15]
    
    book_indices = [i[0] for i in sim_scores3]
    frame = {'recs index':book_indices, 
             'title':book_data['title'].iloc[book_indices]}
    
    dataframe = pd.DataFrame(frame)
    #title_input = dataframe.iloc[0]
    #results = dataframe.iloc[1:]
    return dataframe


def rec_table(eng_output, split=True):
    """Takes engine output and creates full dataframe
    """
    output_index = eng_output['recs index']
    frame = {
        'title':[book_data['title'][i] for i in output_index],
        'author':[book_data['author'][i] for i in output_index],
        'desc':[book_data['desc'][i] for i in output_index],
        'genre':[book_data['genre'][i] for i in output_index],
        'rating':[book_data['rating'][i] for i in output_index],
        'cover link':[book_data['cover link'][i] for i in output_index],
        'book link':[book_data['book link'][i] for i in output_index],
        'recs index':output_index}
    dataframe = pd.DataFrame(frame)
    
    if split == True:
    
        input_suggestion = dataframe.iloc[0]
        output_recs = dataframe.iloc[1:]
        return input_suggestion, output_recs
    else:
        return dataframe


def genre_overlap(a, b, num):      
    if len(set(a) & set(b)) > num:
        return True
    else:
        return False


def overlap_by_genre(user_input, recs, num):
    indexes = []
    titles = []
    for i in range(len(recs['recs index'])):
        if genre_overlap(user_input['genre'], 
                         recs['genre'].iloc[i], num) == True:
            idx = recs['recs index'].iloc[i]
            title = recs['title'].iloc[i] 
            indexes.append(idx)
            titles.append(title)
    
    dataframe = pd.DataFrame({'recs index':indexes, 'title':titles}) 
    return dataframe   


def limit_by_genre(table, genre=None):
    table.reset_index(inplace=True, drop=True)
    
    if type(genre) == str:
        genre = [genre] # this is because of how streamlit works 
        
    keep = []
    val = 0
    if genre == None:
        val = table     
    elif len(genre) == 1 and genre[0] != 'All':
        for i in range(len(table['genre'])):
            if (genre[0] in table['genre'][i]) == True:
                keep.append(i)
        val = table.iloc[keep]
    else:
        for i in range(len(table['title'])):
            if len(set(genre) & set(table['genre'][i])) == len(set(genre)):
                keep.append(i)
        val = table.iloc[keep]
        
    return val


def include_author(suggestion, table, include):
    if include == True:
        val = table
    elif include == False:
        val = table.loc[table['author'] != suggestion['author']]
    return val


def book_rec_engine(user_input, limit_genre=None, 
                    num_overlap=0, author_bool=False):

    full_recs = desc_sim(user_input, cosine_sim)
    user_select, rec_output0 = rec_table(full_recs, split=True)

    limit_output = limit_by_genre(rec_output0, genre=limit_genre)
    rec_output1 = rec_table(limit_output, split=False)

    overlap_output = overlap_by_genre(user_select, rec_output1, num_overlap)
    rec_output2 = rec_table(overlap_output, split=False)

    rec_output = include_author(user_select, rec_output2, author_bool)
    
    return user_select, rec_output 


def get_index_title(output):
    indexes = []
    for i in output['title']:
        indexes.append(book_data.index[book_data['title'] == i])


def check_output_na(table):
    """"This function will take the updated rec table and determine if the 
    values are blank. If blank, will update the table to fill out NA in all 
    columns"""
    
    error_cat_link = "./data/error_cat.jpg"
    error_frame = {'title':'NA','author':'NA','desc':'NA','rating':'NA',
                   'genre':['NA'],'cover link':error_cat_link,
                   'book link':np.nan}
    if table.empty == True:
        val = pd.DataFrame(error_frame, index=[0])
    else:
        val = table 
    return val

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def list_to_text(genre_list, sep=' ', keep_dup=False):
    if keep_dup==True:
        return sep.join(genre_list)
    else:
       genre_list = unique(genre_list)
       return sep.join(genre_list)
   

##############################################################################
#creating the layout
##############################################################################

#sidebar######################################################################
st.sidebar.title('My Next Book Is')

# user title input 
user_input = st.sidebar.selectbox("Something Like...", 
                                 book_data['title'],
                                 index=2)

by_author_text = book_data['author'][book_data['title'] == user_input].iloc[0]
st.sidebar.markdown("by {}".format(by_author_text))


# limit by specific genres
genre_list = ['Adventure','Childrens','Classics','Dystopia','Fantasy',
              'Historical','Horror','Mystery','Paranormal','Romance',
              'Science Fiction','Thriller','Young Adult']
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
st.sidebar.caption('''Warning: genre overlap below 3 or above 7 may result
result in major inaccuracies''')

# include author in recs
author_text = '''Include other books by *{}* in Possible Recommendations?
'''.format(by_author_text)
author_bool = st.sidebar.checkbox(author_text, value=False)

# book engine call
user_input, rec_df = book_rec_engine(user_input, limit_genre, 
                                     num_input, author_bool)
rec_df.reset_index(inplace=True, drop=True) # needed for author/title display

# checking if final results are NA
rec_df = check_output_na(rec_df)

# side bar genre for user input 
st.sidebar.markdown('''#### {} is Listed Under the Following Genres: 
'''.format(user_input['title']))
genre_list_text_user = list_to_text(user_input["genre"], 
                               sep=', ', keep_dup=False)
st.sidebar.markdown(genre_list_text_user)


#columns#####################################################################
col1, col2 = st.columns([3, 1], gap="medium")

# rec display info
col1.header("Your Top Recommendation:")
col1.subheader("{} by {}".format(rec_df['title'][0], rec_df['author'][0]))
#col1.markdown(rec_df["desc"].iloc[0].replace("#","\n"))
col1.markdown(rec_df["desc"].iloc[0])

# display top rec genres 
genre_list_text = list_to_text(rec_df["genre"].iloc[0], 
                               sep=', ', keep_dup=False)
col1.markdown('##### Your Top Recommendation is Under the Following Genres:')
col1.markdown(genre_list_text)

# dataframe
col1.subheader("Other Recommendations:")
col1.dataframe(rec_df[['title', 'author','genre', 'desc']].iloc[1:],
               width=15)

# image display
col2.image(rec_df["cover link"].iloc[0])




# streamlit run book_rec_engine.py 