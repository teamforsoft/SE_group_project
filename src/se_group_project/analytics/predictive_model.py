import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.cross_validation import cross_val_score
from sklearn.tree import export_graphviz
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import os
import sqlalchemy

engine = sqlalchemy.create_engine('mysql+pymysql://teamforsoft:whocares1@teamforsoft.ci76dskzcb0m.us-west-2.rds.amazonaws.com:3306/SE_group_project')
conn = engine.connect()#creating local sqlite connection/database for quicker response to marker click queries

analytics_df = pd.read_sql_query('SELECT * FROM dynamic d, weather w WHERE d.latest_weather = w.date;',con=conn)

analytics_df.to_csv('analytics.csv')

df = pd.read_csv('analytics.csv')

df['date_time']=pd.to_datetime(df['last_update']/1000, unit='s')
df['date_time'].head()
df['hours']= df['date_time'].dt.hour
df['day']=df['date_time'].dt.dayofweek

df['rain']=0
df.loc[df['description'] == "moderate rain", 'rain'] = 1
df[df['rain']==0]

#https://stackoverflow.com/questions/19790790/splitting-dataframe-into-multiple-dataframes

#create unique list of names
UniqueNumbers = df.number.unique()

#create a data frame dictionary to store your data frames
DataFrameDictHourDayStation = {}

for key in UniqueNumbers:
    for i in range(7):
        for j in range (24):
            DataFrameDictHourDayStation[str(key)+'/'+str(i)+'/'+str(j)] = df[:][(df.number == key)&(df.hours==j)&(df.day==i)]

with open('dict.pkl','wb') as output:
    pickle.dump(DataFrameDictHourDayStation, output, pickle.HIGHEST_PROTOCOL)

def mkdir(path):
    try:
        os.makedirs("./"+str(path)+"/")
    except FileExistsError:
        pass

for key in DataFrameDictHourDayStation.keys():
    if DataFrameDictHourDayStation[key][['wind','temperature']].shape[0]==0 or DataFrameDictHourDayStation[key]['available_bikes'].shape[0]==0:
        mkdir(key)
        with open("./"+str(key)+"/model.pkl",'wb') as output:
            model = None
            pickle.dump(model, output, pickle.HIGHEST_PROTOCOL)
            continue
    linear = LinearRegression()
    model=linear.fit(DataFrameDictHourDayStation[key][['wind','temperature','rain']],DataFrameDictHourDayStation[key]['available_bikes'])
    mkdir(key)
    with open("./"+str(key)+"/model.pkl",'wb') as output:
        pickle.dump(model, output, pickle.HIGHEST_PROTOCOL)