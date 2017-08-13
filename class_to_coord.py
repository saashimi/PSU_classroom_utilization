#Import required packages
import pandas as pd
import numpy as np
import datetime
import os

def format_date(df_date):
    """
    Splits Meeting Times and Dates into datetime objects where applicable using 
    regex. Adds separate columns for days of the weeks to facilitate separate 
    csv file generation. 
    """
    df_date['Days'] = df_date['Meeting_Times'].str.extract('([^\s]+)', expand=True).astype(str)
    df_date['Start_Date'] = df_date['Meeting_Dates'].str.extract('([^\s]+)', expand=True)
    df_date['End_Date'] = df_date['Meeting_Dates'].str.extract('(?<=-)(.*)(?= )', expand=True)
    df_date['Start_Time'] = df_date['Meeting_Times'].str.extract('(?<= )(.*)(?=-)', expand=True)
    df_date['End_Time'] = df_date['Meeting_Times'].str.extract('((?<=-).*$)', expand=True)

    df_date['Building'] =  df_date['ROOM'].str.extract('([^\s]+)', expand=True).astype(str)
    
    date_dict = {'M' : '2016/09/26', 'T': '2016/09/27', 'W': '2016/09/28', 'R': '2016/09/29', 'F': '2016/09/30', 'S': '2016/10/01', 'U':'2016/10/02'}
    days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    for day in days:
        df_date['Day_start_{0}'.format(day)] = 'na'
        df_date['Day_end_{0}'.format(day)] = 'na'

    for index, row in df_date.iterrows():
        for day in row['Days']:
            for match_day in days: # e.g. MWF in the string
                try:
                    if day == match_day:
                        start_time = pd.to_datetime(date_dict[day] + row['Start_Time'], format='%Y/%m/%d%H%M')
                        end_time = pd.to_datetime(date_dict[day] + row['End_Time'], format='%Y/%m/%d%H%M')
                        #df_date.loc[index, 'Day_{0}'.format(day)] = pd.date_range(start_time, end_time)
                        df_date.loc[index, 'Day_start_{0}'.format(day)] = start_time
                        df_date.loc[index, 'Day_end_{0}'.format(day)] = end_time
                    else:
                        continue
                except:
                    continue
    return df_date


def save_to_csv(df_final):
    """
    Save to separate csv files per weekday
    """
    df_final = df_final.loc[
        (df_final['Latitude'] != None) &
        (df_final['Longitude'] != None)]
    columns = ['Building', 'Class', 'Actual_Enrl', 'Latitude', 'Longitude']
    day_cols = [col for col in df_final.columns if 'Day' in col]
    for col in day_cols:
        columns.append(col)   
    df_final.to_csv('full_sched.csv', columns=columns)
    days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    for day in days:
        df_temp = df_final.loc[
            (df_final['Day_start_{0}'.format(day)] != 'na') &
            (df_final['Day_end_{0}'.format(day)] != 'na') &
            (df_final['Actual_Enrl'] > 0) ]
        columns = ['Building', 'Class', 'Actual_Enrl', 'Day_start_{0}'.format(day),
         'Day_end_{0}'.format(day), 'Latitude', 'Longitude']
        df_temp.to_csv('classes_{0}.csv'.format(day), columns=columns)

def join_coords(df_proc):
    filename = 'map_input/bldg_pt.csv'
    df_new = pd.read_csv(os.path.join(os.path.dirname(__file__), filename))
    df_coord = pd.merge(df_proc, df_new, left_on='Building', right_on='BUILDINGID', how='left')
    return df_coord

def main():
    """
    main program control.
    """
    pd.set_option('display.max_rows', None)  
    filename = 'map_input/PSU_master_classroom.csv'
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), filename), dtype={'Schedule': object, 'Schedule Desc': object})   
    df = df.fillna('')

    terms = [201604]
    df = df.loc[df['Term'].isin(terms)]

    df = format_date(df)

    df = join_coords(df)

    # Avoid classes that only occur on a single day
    df = df.loc[df['Start_Date'] != df['End_Date']]
    df = df.loc[df['Online Instruct Method'] != 'Fully Online']
    save_to_csv(df)

if __name__ == '__main__':
    main()

