# Classroom useage estimator

This program is intended for use by the Portland State University Campus Planning Office (CPO).  It summarizes classroom useage by department in order to estimate demand for classrooms based on Fall Quarter schedules. 

### Dependencies

cycler==0.10.0
matplotlib==1.5.3
numpy==1.11.2
pandas==0.19.1
pyparsing==2.1.4
python-dateutil==2.6.0
pytz==2016.10
six==1.10.0

## Methodology

### Data Sources

class_parse.py utilizes two main Datamaster CSV files:
* PSU_master_classroom.csv: This was generated from Datamaster classroom schedule query (Datamaster Table S0017 - ), containing ALL buildings. Provided in .xls format by CPO Space Analyst, Lucius Shields, and converted to CSV.
* CLE-<school>-<term>.csv, which are files generated from Datamaster Table S0025 (Course List with Enrollments) for each individual Fall term of interest. This file is used to generate a list of valid courses to filter against PSU_master_classroom.csv.

### Overall methodology assumptions:

* Program analyzes classroom useage BY SCHOOL. Modifications will have to be made to generate a campus-wide snapshot.
* Classes which have a start date and end date on the same day are not counted.
* Assumes a 1% enrollment growth rate over three years.

### Formulas used:
* Growth Rate = 1% * 3 years
* Classroom Utilization = sum(Weekly Class Hours per Classroom) / 40 Hours
* Calibrated Demand = Classroom Utilization + Growth Rate