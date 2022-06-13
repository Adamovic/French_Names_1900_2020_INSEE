import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import json
from geopy.geocoders import Nominatim
# import geopandas as gpd...
import folium
import zipfile

import matplotlib as mpl
mpl.rcParams['figure.figsize'] = [6.4, 4]

query_params = st.experimental_get_query_params()

# PLOT

first_name = 'CAMILLE'
if 'name' in query_params :
    if isinstance(query_params['name'], list): first_name = query_params['name'][0]
    else: first_name = query_params['name']
first_name = first_name.upper()

@st.cache()
def load_data(default_name='CAMILLE', first_name=first_name, remove_rare=True, remove_X=True):
#     file = r"./Data/french_names_1900-2020.csv"
    file = r"dpt2020.csv"
    file_zip = r"./Data/dpt2020_csv.zip"
    zf = zipfile.ZipFile(file_zip)
#     with open(file) as f:
    df = pd.read_csv(zf.open(file),delimiter=';')
#     df = pd.read_csv(file,delimiter=';')
    df.columns = ['sex','name','year','dpt','count']
    if remove_rare: df = df[df.name != '_PRENOMS_RARES']
    if remove_X:
        df = df[df.year != "XXXX"]
        df = df[df.dpt != "XX"]
        df = df.astype({'year':'int32'})
    unique_names = df.name.unique()
    df = df.sort_values(by='year')
    if first_name not in unique_names: first_name = default_name
    first_name_index = int(np.where(unique_names == first_name)[0][0])
    return df, unique_names, first_name_index

name_data, unique_names, first_name_index = load_data()

def get_name_data(name, df=name_data, include_X=False):
    name_df = df[df.name == name]
#     if not include_X:
#         name_df = name_df[name_df.year != 'XXXX']
#         name_df = name_df.astype({'year':'int32'})
#     name_df = name_df.sort_values(by='year')
    # fill missing years with 0:
    new_index = pd.Index(np.arange(1900,2021,1), name='year',dtype=int)
    st.write(new_index)
    st.write(name_df)
    name_df = name_df.reset_index().set_index(['year']).reindex(new_index,fill_value=0).reset_index()
    st.write(name_df)
    return name_df
    
def plot_name(name, data, handle_sex='SEPARATE'):
#     data=get_name_data(name)
    if handle_sex == 'SUM':
        data=data.groupby(by=['year']).sum().reset_index()
        c='tab:blue'
        plt.plot('year','count', data=data, c=c)
        plt.title(name + ' (males + females)')
        
    elif handle_sex == 'SEPARATE':
        data=data.groupby(by=['year','sex']).sum().reset_index()
        for sex in data.sex.unique():
            if sex == 1:
                label='males'
                c='deepskyblue'
            elif sex == 2:
                label='females'
                c='pink'
            data_temp = data[data.sex==sex]
            plt.plot('year','count',data=data_temp, label=label,c=c)
        plt.title(name + ' (males vs females)')
        plt.legend()
        
    elif handle_sex in ['MALE','MALES','FEMALE','FEMALES']:
        data=data.groupby(by=['year','sex']).sum().reset_index()
        if handle_sex in ['MALE','MALES']:
            sex=1
            label='males'
            c='deepskyblue'
            title='males'
        else:
            sex=2
            label='females'
            c='pink'
            title='females'
        data_temp = data[data.sex==sex]
        plt.plot('year','count',data=data_temp, label=label,c=c)
        plt.title(f"{name} ({title})")
        plt.legend()
        
    plt.xticks(np.floor(plt.xticks()[0])) # round xticks
    plt.yticks(np.floor(plt.yticks()[0]))
    fig = plt.gcf()
    st.pyplot(fig)
    
st.header('French Names by Year')
cols = st.columns(2)
with cols[0]:
    separate = st.checkbox('Separate by gender', True)
    name_selected = st.selectbox('Type a name :', unique_names, first_name_index)
    st.experimental_set_query_params(name=name_selected.lower())
    handle_sex = 'SEPARATE' if separate else 'SUM'
    data=get_name_data(name_selected)
    plot_name(name_selected, data, handle_sex)

# MAP

# @st.cache()
def load_map_data():
    geojson_file = r"./Data/france_departments_corse_merged.json"
    with open(geojson_file) as f:
        geojson = json.load(f)
    return geojson
        
geojson = load_map_data()

map_name_data = data.groupby(['dpt']).sum().drop(columns=['sex','year']).reset_index()

# fill absent dpts with 0
new_index = pd.Index(np.arange(1,96,1), name='dpt',dtype=str).append(pd.Index([971,972,973,974], name='dpt',dtype=str))
new_index = new_index.str.zfill(2)
map_name_data = map_name_data.set_index(['dpt']).reindex(new_index,fill_value=0).reset_index()
with cols[1]:
    st.write(map_name_data)


# SOURCE

st.markdown('INSEE 2021, _Fichier des prénoms_  \n\
            <https://www.insee.fr/fr/statistiques/2540004#documentation>')

# GENERATION

st.markdown('#')
st.header('Name Generation (coming soon)')
cols = st.columns(4)
with cols[0]:
    st.selectbox('Gender :', ['Male','Female','Neither'],0)
with cols[1]:
    st.selectbox('Period :', [str(x)+'s' for x in range(1900,2011,10)],11)
with cols[2]:
    st.selectbox('Department :', ['...'],0)
with cols[3]:
    st.checkbox('Only show original names',True)
#     st.markdown('#')
#     st.markdown(' ')
    st.button('Generate Names', disabled=True)
