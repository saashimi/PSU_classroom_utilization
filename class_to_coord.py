#Import required packages
import pandas as pd
import numpy as np
import datetime
import os

def format_date(df_date):
    """
    Splits Meeting Times and Dates into datetime objects where applicable using regex.
    """
    df_date['Days'] = df_date['Meeting_Times'].str.extract('([^\s]+)', expand=True).astype(str)
    df_date['Start_Date'] = df_date['Meeting_Dates'].str.extract('([^\s]+)', expand=True)
    df_date['End_Date'] = df_date['Meeting_Dates'].str.extract('(?<=-)(.*)(?= )', expand=True)
    df_date['Start_Time'] = df_date['Meeting_Times'].str.extract('(?<= )(.*)(?=-)', expand=True)
    df_date['End_Time'] = df_date['Meeting_Times'].str.extract('((?<=-).*$)', expand=True)
    
    date_dict = {'M' : '2016/09/26', 'T': '2016/09/27', 'W': '2016/09/28', 'R': '2016/09/29', 'F': '2016/09/30', 'S': '2016/10/01', 'U':'2016/10/02'}
    days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    for day in days:
        df_date['Day_{0}'.format(day)] = ''
    for index, row in df_date.iterrows():
        for day in row['Days']:
            try:
                start_time = pd.to_datetime(date_dict[day] + row['Start_Time'], format='%Y/%m/%d%H%M')
                end_time = pd.to_datetime(date_dict[day] + row['End_Time'], format='%Y/%m/%d%H%M')
                df_date.loc[index, 'Day_{0}'.format(day)] = pd.date_range(start_time, end_time)
            except:
                continue
    #df_date['Start_Time'] = pd.to_datetime(df_date['Start_Time'], format='%H%M')
    #df_date['End_Time'] = pd.to_datetime(df_date['End_Time'], format='%H%M')

    return df_date

pd.set_option('display.max_rows', None)  
filename = 'enrollment_data/PSU_master_classroom.csv'

df = pd.read_csv(os.path.join(os.path.dirname(__file__), filename), dtype={'Schedule': object, 'Schedule Desc': object})   
df = df.fillna('')
terms = [201604]
df = df.loc[df['Term'].isin(terms)]

df = format_date(df)

# Avoid classes that only occur on a single day
df = df.loc[df['Start_Date'] != df['End_Date']]
df = df.loc[df['Online Instruct Method'] != 'Fully Online']

df.to_csv('./test_output.csv')

