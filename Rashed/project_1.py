#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip3 install requests')
import requests
import json
import pandas as pd
from pandas import json_normalize
import datetime
get_ipython().system('pip install folium')
import folium
from folium.plugins import HeatMap
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
get_ipython().system('pip install plotly')
import plotly.express as px


# In[2]:


#url for Police Department Incident Reports: 2018 to Present (dataset #1)
url = "https://data.sfgov.org/resource/wg3w-h783.json?$limit=1000"
#url for Police Department Incident Reports: Historical 2003 to May 2018 (dataset #2)
url_2 = "https://data.sfgov.org/resource/tmnf-yvry.json?$limit=2000"


# In[3]:


#returns a JSON object of the result (url)
response = requests.get(url).json()


# In[4]:


#returns a JSON object of the result (url_2)
response_2 = requests.get(url_2).json()


# In[5]:


#Normalize semi-structured JSON data into a flat table. (df)
res = json_normalize(response)
df = pd.DataFrame(res)


# In[6]:


##Normalize semi-structured JSON data into a flat table. (df_2)
res_2 = json_normalize(response_2)
df_2 = pd.DataFrame(res_2)


# In[7]:


#extract the months from incident date before dropping it (dataset #1)
df['incident_month'] = pd.DatetimeIndex(df['incident_date']).month


# In[9]:


df["analysis_neighborhood"].unique()


# In[10]:


#dropping columns
df = df.drop(['incident_datetime', 'row_id','report_type_description',
'report_datetime','incident_time','incident_date','incident_day_of_week',':@computed_region_nqbw_i6c3',
 ':@computed_region_h4ep_8xdi','report_type_code',
 ':@computed_region_n4xg_c4py',
 ':@computed_region_jg9y_a9du',
 ':@computed_region_jwn9_ihcz',
 ':@computed_region_26cr_cadq','analysis_neighborhood',
 ':@computed_region_qgnn_b9vv', 'police_district','incident_subcategory',
 'point.type', 'supervisor_district', 'resolution','filed_online','incident_number', 'incident_id', 'cad_number', 'cnn', 'intersection','point.coordinates',], axis = 1)


# In[11]:


#dropping null values
df = df.dropna(how="any")

#dropping 2023 data and reset the index
df = df.drop(df.index[df['incident_year'] == "2023"])
df = df.reset_index(drop = True)


# In[12]:


#extract the months and years from incident date before dropping it (dataset #2)

df_2['incident_month'] = pd.DatetimeIndex(df_2['date']).month
df_2['incident_year'] = pd.DatetimeIndex(df_2['date']).year


# In[13]:


#dropping columns (dataset #2)
df_2= df_2.drop(['time','resolution', 'location.coordinates', 'location.type', ':@computed_region_26cr_cadq',
 ':@computed_region_rxqg_mtj9',
 ':@computed_region_bh8s_q3mv','dayofweek','pdid','pddistrict',
 'incidntnum',':@computed_region_6qbp_sg9q',
 ':@computed_region_qgnn_b9vv','date',
 'address',
 ':@computed_region_ajp5_b2md',
 ':@computed_region_yftq_j783',
 ':@computed_region_p5aj_wyqh',
 ':@computed_region_fyvs_ahh9',
 ':@computed_region_6pnf_4xz7',
 ':@computed_region_jwn9_ihcz',
 ':@computed_region_9dfj_4gjx',
 ':@computed_region_4isq_27mq',
 ':@computed_region_pigm_ib2e',
 ':@computed_region_9jxd_iqea',
 ':@computed_region_6ezc_tdp2',
 ':@computed_region_h4ep_8xdi',
 ':@computed_region_n4xg_c4py',
 ':@computed_region_fcz8_est8',
 ':@computed_region_nqbw_i6c3',
 ':@computed_region_2dwj_jsy4'], axis = 1)


# In[14]:


#rename columns (dataset #2)
df_2.rename(columns = {'category':'incident_category', 'descript':'incident_description', 'y':'latitude', 'x':'longitude'}, inplace = True)


# In[15]:


#dropping null values (dataset #2)
df_2 = df_2.dropna(how="any")
#changing incident_year type to mearge the two Dataframes (dataset #2)
df_2.astype({'incident_year': 'object'},{}).dtypes


# In[16]:


#creating a combined Dataframe 
crime_df = pd.concat([df, df_2], ignore_index=True, sort=False)
crime_df.astype({'incident_category': 'str'},{'incident_description' : 'str'}).dtypes


# In[17]:


# Display the new Dataframe created
crime_df


# In[18]:


list(crime_df.head())


# In[19]:


# Changing letters to lower case in both incident_category & incident_description columns
crime_df["incident_category"] = crime_df["incident_category"].str.lower()
crime_df["incident_description"] = crime_df["incident_description"].str.lower()

#know all type of unique values in column
crime_df["incident_category"].unique()


# In[20]:


crime_df['incident_category']


# In[21]:


# replace values.
rep = {
    "drug violation":"drug offense",
    'drug/narcotic':"drug offense",
    "forgery/counterfeiting" : "forgery and counterfeiting",
    "larceny/theft" : "larceny theft",
    "human trafficking, commercial sex acts" : "human trafficking (a), commercial sex acts",
    "motor vehicle theft?" : "motor vehicle theft",
    "other miscellaneous" : "other",
    "other offenses" : "other",
    "sex offenses, forcible" : "sex offense",
    'sex offenses, non forcible' : 'sex offense',
    'suspicious occ' : 'suspicious',
    'warrants': 'warrant',
    'weapons offence': 'weapons offense',
    'weapons carrying etc' : 'weapon laws'
}

crime_df.replace({"incident_category": rep})
crime_df


# In[22]:


heat_m = folium.Map(location = [37.7749 , -122.4194], zoom_start = 13 , tiles = 'Stamen Terrain')
heat_mat = crime_df[['latitude', 'longitude']].to_numpy()
HeatMap(heat_mat,radius= 0, blur=10).add_to(heat_m)


# In[23]:


heat_m


# In[24]:


plt.figure(figsize=(15,5))
ax = sns.countplot(x = crime_df['incident_category'] ,  orient='v', order = crime_df['incident_category'].value_counts().index)
ax.set_xticklabels(ax.get_xticklabels(),rotation = 90)


# In[26]:


crime_df['latitude'] = crime_df['latitude'].astype(float)
crime_df['longitude'] = crime_df['longitude'].astype(float)


# In[28]:


fig = px.scatter_mapbox(crime_df, 
                        lat="latitude", 
                        lon="longitude", 
                        color_continuous_scale="size",
                        zoom=10, 
                        height=1000,
                        width=800)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()


# In[ ]:




