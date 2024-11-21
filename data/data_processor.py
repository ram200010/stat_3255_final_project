import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import holidays

# Read Data
el_data = pd.read_csv("data/Energy_EL_20180101_20241115_(0238) Austin, Phillip E (Clas).tsv",sep='\t')
st_data = pd.read_csv("data/Energy_ST_20180101_20241115_(0238) Austin, Phillip E (Clas).tsv",sep='\t')
cw_data = pd.read_csv("data/Energy_CW_20180101_20241115_(0238) Austin, Phillip E (Clas).tsv",sep='\t')

# Rename reading column and drop uneccesary columns.
st_data = st_data.rename(columns={'Reading':'steam_reading'}).drop(columns=['Facility_Name','Facility_Code','ScadaTag','TempUnits','HumidityUnits','Sqft_Gross'])
el_data = el_data.rename(columns={'Reading':'electricity_reading'}).drop(columns=['Facility_Name','Facility_Code','ScadaTag','TempUnits','HumidityUnits','Sqft_Gross'])
cw_data = cw_data.rename(columns={'Reading':'chilled_water_reading'}).drop(columns=['Facility_Name','Facility_Code','ScadaTag','TempUnits','HumidityUnits','Sqft_Gross'])

data = pd.merge(el_data,st_data,on='TimeStampUTC')
data = data.merge(cw_data,on='TimeStampUTC').dropna()

data = data.T.drop_duplicates().T


data = data.rename(columns={'TimeStampUTC':'time', 'UOM_x':'el_uom','UOM_y':'st_uom','TempRead_x':'temperature','UOM':'cw_uom',
                    'HumidityRead_x':'humidity'})


print(data)

# Create more variables


data['time'] = pd.to_datetime(data['time'],format='%Y/%m/%d %H:%M:%S')

data['day_of_week'] = data['time'].dt.dayofweek #0-Monday 6-Sunday
data['month'] = data['time'].dt.month
data['year'] = data['time'].dt.year
data['day'] = data['time'].dt.day
data['hour'] = data['time'].dt.hour
data['minute'] = data['time'].dt.minute


us_holidays = holidays.UnitedStates()

def classify_date(date):
    if date in us_holidays:
        return 2 #'holiday'
    elif date.weekday() >= 5:
        return 1 #'weekend'
    else:
        return 0 #'weekday'

data['day_type'] = data['time'].apply(classify_date)

semester_data = pd.read_excel("semester_data.csv.xlsx")

semester_group = semester_data.groupby('semester')
fall_group = semester_group.get_group('Fall')
spring_group = semester_group.get_group('Spring')


def semester(row):

    month = row['month']
    year = row['year']
    day = row['day']

    date = datetime(year, month,day)
    
    if month in range(1,7):
        info = spring_group.groupby('year').get_group(year)

        semester_start = datetime(info['year'].iloc[0],info['semester_start_month'].iloc[0],info['semester_start_day'].iloc[0])
        semester_end = datetime(info['year'].iloc[0],info['semester_end_month'].iloc[0],info['semester_end_day'].iloc[0])

        if date < semester_start:
            row['session'] = 'Winter'
            row['session_coded'] = 1
            row['stors_enrollement'] = 0
            row['clas_enrollement'] = 0
            row['stat_enrollement'] = 0
            row['english_enrollement'] = 0
            
        
        elif date > semester_end:
            row['session'] = 'Summer'
            row['session_coded'] = 3
            row['stors_enrollement'] = 0
            row['clas_enrollement'] = 0
            row['stat_enrollement'] = 0
            row['english_enrollement'] = 0

        else:
            row['session'] = 'Spring'
            row['session_coded'] = 2
            row['stors_enrollement'] = info['storrs_total_enrollement'].iloc[0]
            row['clas_enrollement'] = info['clas_enrollement'].iloc[0]
            row['stat_enrollement'] = info['stat_and_data_science'].iloc[0]
            row['english_enrollement'] = info['english'].iloc[0]

    elif month in list(range(7,13)):
        info = fall_group.groupby('year').get_group(row['year'])

        semester_start = datetime(info['year'].iloc[0],info['semester_start_month'].iloc[0],info['semester_start_day'].iloc[0])
        semester_end = datetime(info['year'].iloc[0],info['semester_end_month'].iloc[0],info['semester_end_day'].iloc[0])


        if date < semester_start:
            row['session'] = 'Summer'
            row['session_coded'] = 3
            row['stors_enrollement'] = 0
            row['clas_enrollement'] = 0
            row['stat_enrollement'] = 0
            row['english_enrollement'] = 0
        
        elif date > semester_end:
            row['session'] = 'Winter'
            row['session_coded'] = 1
            row['stors_enrollement'] = 0
            row['clas_enrollement'] = 0
            row['stat_enrollement'] = 0
            row['english_enrollement'] = 0

        
        else:
            row['session'] = 'Fall'
            row['session_coded'] = 0
            row['stors_enrollement'] = info['storrs_total_enrollement'].iloc[0]
            row['clas_enrollement'] = info['clas_enrollement'].iloc[0]
            row['stat_enrollement'] = info['stat_and_data_science'].iloc[0]
            row['english_enrollement'] = info['english'].iloc[0]
        
    return row

        


print(data)

train_data = data[data['time']>=datetime(2020,8,31)]
train_data = train_data[train_data['time']<datetime(2024,8,26)]
print(train_data)
train_data = train_data.apply(semester, axis=1)


print(train_data)

train_data.to_feather('train_data.feather')   


test_data = data[data['time']>=datetime(2024,8,26)]
test_data = test_data[test_data['time']<=datetime(2024,11,15)]
test_data = test_data.apply(semester, axis=1)

print(test_data)

test_data.to_feather('test_data.feather')



