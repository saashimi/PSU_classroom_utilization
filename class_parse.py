import pandas as pd
import re
import numpy as np
import datetime
import matplotlib.pyplot as plt

def format_df_reg(df_reg):
    df_reg = df_reg.loc[df_reg['Xlst'] == '']
    columns = ['ROOM', 'Actual_Enrl', 'Room_Capacity', 'Weekly_Class_Hours']
    df_reg = df_reg[columns]
    df_reg['%_Capacity'] = df_reg['Actual_Enrl'] / df_reg['Room_Capacity'].astype(int)
    return df_reg

def merge_xlist(df_xl):
    """
    Merges courses with a value in Xlist column. Sums Actual_Enrl for totals 
    column but retains Room Number, Room Capacity, and Weekly Class Hours, as 
    these numbers are constant. 
    """
    df_xl = df_xl.loc[df_xl['Xlst'] != '']
    xl_operations = ({'ROOM' : 'max',
                      'Actual_Enrl' : 'sum', 
                      'Room_Capacity' : 'max',
                      'Weekly_Class_Hours' : 'max',})
    df_xl = df_xl.groupby('Xlst', as_index=False).agg(xl_operations)
    df_xl['%_Capacity'] = df_xl['Actual_Enrl'] / df_xl['Room_Capacity'].astype(int)
    return df_xl

def aggregate(df_agg):
    # Aggregate arithmetic operations:
    df_agg['Room_Capacity'] = df_agg['Room_Capacity'].astype(float)
    df_agg['Actual_Enrl'] = df_agg['Actual_Enrl'].astype(float)

    operations = ({'Weekly_Class_Hours' : 'sum', 
                   'Room_Capacity' : 'mean', 
                   'Actual_Enrl' : 'mean',})
    df_agg = df_agg.groupby('ROOM', as_index=False).agg(operations)

    # Calculate hourly utilizations
    df_agg['Class_Hour_Utilization'] = (df_agg['Weekly_Class_Hours']/40.0).astype(float)

    # Round optimal size to the nearest 5
    df_agg['Optimal_Size'] = 5 * round((df_agg['Actual_Enrl'] * 1.25)/5)
    # Optimal size should be a minimum of 10 seats
    df_agg.loc[df_agg['Optimal_Size'] < 10.0, 'Optimal_Size'] = 10.0
    # 'Bin' figures to fixed ranges. From Ernest Tipton's 201604 Spreadsheet.
    df_agg.loc[(df_agg['Optimal_Size'] > 60.0) & (df_agg['Optimal_Size'] < 75.0), 'Optimal_Size'] = 75.0
    df_agg.loc[(df_agg['Optimal_Size'] > 75.0) & (df_agg['Optimal_Size'] < 80.0), 'Optimal_Size'] = 80.0
    df_agg.loc[(df_agg['Optimal_Size'] > 80.0) & (df_agg['Optimal_Size'] < 100.0), 'Optimal_Size'] = 100.0
    df_agg.loc[(df_agg['Optimal_Size'] > 100.0) & (df_agg['Optimal_Size'] < 150.0), 'Optimal_Size'] = 150.0
    df_agg.loc[(df_agg['Optimal_Size'] > 150.0) & (df_agg['Optimal_Size'] < 200.0), 'Optimal_Size'] = 200.0
    df_agg.loc[(df_agg['Optimal_Size'] > 200.0) & (df_agg['Optimal_Size'] < 220.0), 'Optimal_Size'] = 220.0  
    df_agg.loc[(df_agg['Optimal_Size'] > 220.0) & (df_agg['Optimal_Size'] < 380.0), 'Optimal_Size'] = 380.0
    return df_agg

def right_sizing(df_rs):
    growth_factor = 0.01 * 3 # 1% annual growth over three years
    rs_operations = ({'Class_Hour_Utilization' : 'sum'})
    df_rs = df_rs.groupby('Optimal_Size', as_index=False).agg(rs_operations)
    df_rs['Calibrated_Demand'] = df_rs['Class_Hour_Utilization'] + growth_factor
    # Round up to the nearest integer
    df_rs['Qty_Classrooms'] = np.ceil(df_rs['Calibrated_Demand'])
    df_rs['Qty_Seats'] = df_rs['Optimal_Size'] * df_rs['Qty_Classrooms']
    df_rs = df_rs.drop('Class_Hour_Utilization', 1) #Simplify formatting for printing
    return df_rs

def final_print(df_print, school_print, term_print):
    print('===================================================================')
    print('Report for {0} - {1}'.format(school_print, term_print))
    print(df_print)
    print("Total Number of Classrooms Needed (Projected): ", df_print['Qty_Classrooms'].sum())
    print("Total Number of Seats Needed (Projected): ", df_print['Qty_Seats'].sum())
    print('===================================================================','\n')
    columns = ['Optimal_Size', 'Key', 'Qty_Classrooms']
    df_print['Key'] = term_print
    df_print['Optimal_Size'] = df_print['Optimal_Size'].astype(int)
    df_print = df_print[columns]
    return df_print

def plot_graphs(df_grph_lst):
    df_all = pd.concat(df_grph_lst)
    df_group = df_all.groupby(['Optimal_Size', 'Key'])
    df_group_plot = df_group.sum().unstack('Key').plot(kind='bar')
    df_group_plot.set_xlabel('Classrooms by Size')
    df_group_plot.set_ylabel('Number of Classrooms Needed (Projected)')
    df_group_plot.set_ylim([0, 5])
    plt.show()
    
def main():
    school = input("Enter desired GSE or SPH for evaluation >>> ")

    terms = ['201604', '201504', '201404', '201304']
    graph_dfs = []
    for term in terms:
        df = pd.read_csv('classroom_data/PSU_master_classroom.csv')
        df = df.fillna('')
        df = df[df['Term'] == int(term)]

        
        ### Comment out this block for General PSU Campus Snapshot
        # Filter for desired school
        df_classes = pd.read_csv('enrollment_data/CLE-{0}-{1}.csv'.format(school, term))
        # Filter out PE classes
        df_classes = df_classes.loc[df_classes['Schedule_Type_Desc'] != 'Activity']
        
        df_classes['Class_'] = df_classes['Subj'] + " " + df_classes['Course'] 
        valid_class_list = set(df_classes['Class_'].tolist())
        df = df.loc[df['Class'].isin(valid_class_list)]
        ###
        

        # Split Meeting times into Days of the week, Start time, and End time
        # Regex searches
        df['Days'] = df['Meeting_Times'].str.extract('([^\s]+)', expand=True)
        df['Start_Date'] = df['Meeting_Dates'].str.extract('^(.*?)-', expand=True)
        df['End_Date'] = df['Meeting_Dates'].str.extract('((?<=-).*$)', expand=True)
        df['Start_Time'] = df['Meeting_Times'].str.extract('(?<= )(.*)(?=-)', expand=True)
        df['Start_Time'] = pd.to_datetime(df['Start_Time'], format='%H%M')
        df['End_Time'] = df['Meeting_Times'].str.extract('((?<=-).*$)', expand=True)
        df['End_Time'] = pd.to_datetime(df['End_Time'], format='%H%M')
        df['Duration_Hr'] = ((df['End_Time'] - df['Start_Time']).dt.seconds)/3600

        # Avoid classes that only occur on a single day
        df = df.loc[df['Start_Date'] != df['End_Date']]

        # Calculate number of days per week and treat Sunday condition
        if 'SU' not in df['Days']:
            df['Days_Per_Week'] = df['Days'].str.len()
        else:
            print('Sunday Condition!')
            #ToDO: If sunday does come up, refactor code to address this.

        df['Room_Capacity'] = df['Room_Capacity'].apply(lambda x: x if (x != 'No Data Available') else 0)
        df['%_Capacity'] = df['Actual_Enrl'].astype(int) / df['Room_Capacity'].astype(int) 
        df['Actual_Enrl'] = df['Actual_Enrl'].astype(int)
        df['Weekly_Class_Hours'] = df['Duration_Hr'] * df['Days_Per_Week']

        df_reg = format_df_reg(df)
        df_xlist = merge_xlist(df)
        df_combined = aggregate(pd.concat([df_reg, df_xlist]))
        
        df_final = right_sizing(df_combined)
        df_graph = final_print(df_final, school, term)
        graph_dfs.append(df_graph)

    plot_graphs(graph_dfs)

    
if __name__=='__main__':
    main()
    #print(df_combined.loc[df_combined['ROOM'] == 'NH 209'])
