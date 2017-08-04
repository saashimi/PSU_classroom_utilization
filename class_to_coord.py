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


    date_dict = {'M' : '2016/09/26', 'T': '2016/09/27', 'W': '2016/09/28', 'R': '2016/09/29', 'F': '2016/09/30', 'S': '2016/10/01', 'U':'2016/10/02'}

    df_date['Start_Time'] = df_date['Meeting_Times'].str.extract('(?<= )(.*)(?=-)', expand=True)
    df_date['Start_Time'] = pd.to_datetime(df_date['Start_Time'], format='%H%M')
    df_date['End_Time'] = df_date['Meeting_Times'].str.extract('((?<=-).*$)', expand=True)
    df_date['End_Time'] = pd.to_datetime(df_date['End_Time'], format='%H%M')
    df_date['Day'] = ''

    for index, row in df_date.iterrows():
        for day in row['Days']:
            try:
                row['Day'] = date_dict[day]
                print(row['Day'])
            except:
                continue

    return df_date

def format_xlist(df_xl):
    """
    revises % capacity calculations by using Max Enrollment instead of room capacity.  
    """
    df_xl['Cap_Diff'] = np.where(df_xl['Xlst'] != '', 
                                   df_xl['Max_Enrl'].astype(int) - df_xl['Actual_Enrl'].astype(int), 
                                   df_xl['Room_Capacity'].astype(int) - df_xl['Actual_Enrl'].astype(int)) 
    df_xl = df_xl.loc[df_xl['Room_Capacity'].astype(int) < 999]

    return df_xl 


pd.set_option('display.max_rows', None)  
filename = 'enrollment_data/PSU_master_classroom.csv'

df = pd.read_csv(os.path.join(os.path.dirname(__file__), filename), dtype={'Schedule': object, 'Schedule Desc': object})   
df = df.fillna('')

df = format_date(df)
# Avoid classes that only occur on a single day
df = df.loc[df['Start_Date'] != df['End_Date']]
terms = [201604]
df = df.loc[df['Term'].isin(terms)]
df = df.loc[df['Online Instruct Method'] != 'Fully Online']

# Calculate number of days per week and treat Sunday condition
df['Days_Per_Week'] = df['Days'].str.len()
df['Room_Capacity'] = df['Room_Capacity'].apply(lambda x: x if (x != 'No Data Available') else 0)
df['Building'] = df['ROOM'].str.extract('([^\s]+)', expand=True)

df_cl = format_xlist(df)

# Normalize the results
df_cl = df_cl.replace([np.inf, -np.inf], np.nan).dropna()

#days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
#for day in days:
#    if day in days:


#df_cl.to_csv('./test_output.csv')

