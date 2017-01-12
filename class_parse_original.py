"""
class_parse.py 
A script that calculates csv files generated from DATAMASTER. Utilizes pandas
library for csv file manipulation.
"""

import pandas as pd
import numpy as np
import re

#quarters = ['01', '02', '03', '04']
#years = ['2013', '2014', '2015', '2016']
#days = ['M', 'T', 'W', 'R', 'F', 'S', 'SU']

quarters = ['04']
years = ['2013', '2014', '2015', '2016']
days = ['M', 'T', 'W', 'R', 'F', 'S', 'SU']

master_classes = []
master_enrls = [] 
master_auths = []
master_times = []
master_morning = []
master_afternoon = []
master_evening = []

def dept_control_filter(df_cleaned_enrl, df_class_raw):
    dept_controlled_rooms = df_class_raw.Meeting_Location.tolist()
    sort_dept_controlled_rooms = []
    sort_gen_pool_rooms = []
    rooms = df_cleaned_enrl.Meeting_Location_1.tolist()
    for room in rooms:
        if room in dept_controlled_rooms:
            sort_dept_controlled_rooms.append(room)
        else: 
            sort_gen_pool_rooms.append(room)

    print(' Number of Department controlled classroom used: {0}'.format(len(sort_dept_controlled_rooms)),'\n'
        ' Number of General pool classrooms used: {0}'.format(len(sort_gen_pool_rooms)),'\n'
        ' =============================================================','\n')


def clean_day_time(df_day_time):
    """
    Cleans meeting times by splitting inputs into separate date/time lists for 
    counting.
    """
    split_times = []
    meeting_times = df_day_time.Meeting_Time_1.tolist()
    day_list = []
    start_times = []
    for time in meeting_times:
        split_times.append(re.findall(r"[\w]+", time))
        #Splits a date/time in format MW 0700-1200 to [M, 0700, 1200] 
    for list_ in split_times:
        try:
            day = list_[0]
            start_time = list_[1]
            master_times.append(start_time)
            start_times.append(start_time)
            if 'SU' in day:
                print('Sunday condition!')
            else:
                for char in day:
                    day_list.append(char)
        except:
            print(' -WARNING: A class is missing a date/time and will not be counted!-')
            continue

    morning = []
    afternoon = []
    evening = []
    for time in start_times:
        time = int(time)
        if time > 700 and time < 1200:
            morning.append(time)
            master_morning.append(time)
        if time >= 1200 and time < 1700:
            afternoon.append(time)
            master_afternoon.append(time)
        if time >1700:
            evening.append(time)
            master_evening.append(time)
    for day in days:
        print(" ", day, ": {:.0%}".format(day_list.count(day)/len(day_list)))

    print(" Morning classes: {:.0%}".format(len(morning)/len(start_times)),'\n'
    " Afternoon classes: {:.0%}".format(len(afternoon)/len(start_times)), '\n'
    " Evening classes: {:.0%}".format(len(evening)/len(start_times)))


def compile_reg_classes_and_xlist_classes(df_reg_xlist, df_class_raw, current_term_in):
    """
    Group crosslisted classes and calculate required statistics.
    """
    # Count the crosslisted classes separately.
    xlist = df_reg_xlist.groupby('Crosslist_ID').Actual_Enrl
    xlist_count = len(xlist) - 1
    xlist_actual_enrl = (df_reg_xlist.groupby('Crosslist_ID').Actual_Enrl.sum())[0]
    xlist_auth_size = (df_reg_xlist.groupby('Crosslist_ID').Auth_Size.sum())[0]

    # Count the regular classes and calculate their sums.
    df_reg_xlist = df_reg_xlist[df_reg_xlist['Crosslist_ID'] == ''] 
    # Isolates non-crosslisted classes

    total_count = df_reg_xlist.shape[0] + xlist_count
    reg_actual_enrl = df_reg_xlist.Actual_Enrl.sum()
    reg_auth_size = df_reg_xlist.Auth_Size.sum()

    # Calculate necessary statistics.
    avg_enrl = int(round((xlist_actual_enrl + reg_actual_enrl) / (total_count)))
    avg_auth = int(round((xlist_auth_size + reg_auth_size) /  (total_count)))
    avg_cap =  (xlist_actual_enrl + reg_actual_enrl) / (xlist_auth_size + reg_auth_size)    

    # Append to master counts
    master_classes.append(total_count)
    master_enrls.append(xlist_actual_enrl + reg_actual_enrl)
    master_auths.append(xlist_auth_size + reg_auth_size)

    print('\n','=============================================================','\n'
    " Total classes for {0}: {1}".format(current_term_in, total_count),'\n'
    " Average classroom capacity: {0}".format(avg_auth),'\n',
    "Average enrollment per class: {0}".format(avg_enrl),'\n',
    "Average capacity per classroom: {:.0%}".format(avg_cap)
    )
    clean_day_time(df_reg_xlist)
    dept_control_filter(df_reg_xlist, df_class_raw)


def print_summary():
    print('\n','=============================================================','\n'
        " Average number of classes for ALL TERMS: {0}".format(int(round(np.mean(master_classes)))),'\n'
        " Average classroom capacity for ALL TERMS: {0}".format(int(round(sum(master_auths)/sum(master_classes)))),'\n',
        "Average enrollment per class for ALL TERMS: {0}".format(int(round(sum(master_enrls)/sum(master_classes)))),'\n',
        "Average capacity per classroom for ALL TERMS: {:.0%}".format(sum(master_enrls)/sum(master_auths)),'\n',
        "Morning classes: {:.0%}".format(len(master_morning)/len(master_times)),'\n',
        "Afternoon classes: {:.0%}".format(len(master_afternoon)/len(master_times)), '\n',
        "Evening classes: {:.0%}".format(len(master_evening)/len(master_times)), 
    )
    print('=============================================================','\n')


def main():
    school = input("Enter desired GSE or SPH for evaluation >>> ")

    for year in years:
        for quarter in quarters:
            current_term = year + quarter
            df_enrl = pd.read_csv('enrollment_data/CLE-{0}-{1}.csv'.format(school, current_term))
            df_enrl = df_enrl.fillna('') #fill all null values with empty space
            
            #Give us classes that have actual physical meeting locations, e.g. NOT 
            #Offcampus, TBA, web-based, or have empty fields.
            meeting_location_values = ['OFFCAM', 'TBA', 'WEB', '']
            df_enrl = df_enrl[~df_enrl['Meeting_Location_1'].isin(meeting_location_values)]

            df_class = pd.read_csv('classroom_data/dept_control_list-{0}.csv'.format(current_term))
            df_class = df_class.fillna('')
            df_class["Meeting_Location"] = df_class["Room"] + " " + df_class["Room.1"]
            #Room is Building Name, Room.1 is Room Number
            #df_joined = pd.merge(df_enrl, df_class, left_on=df_enrl.Meeting_Location_1, right_on=df_class.Meeting_Location, how='inner')

            compile_reg_classes_and_xlist_classes(df_enrl, df_class, current_term)

    print_summary()

if __name__=="__main__":
    main()