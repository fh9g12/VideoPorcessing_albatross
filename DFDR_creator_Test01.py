# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 10:50:02 2020
DFDR Creator
@author: PMetcalfe1
"""

import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time


#######################
### READ DATA FILES ###
#######################

# PIXHAWK DATAFLASH CSVs:
PIX_data_AHR2 = pd.read_csv('Dataflash CSV/DataflashAHR2.csv')
PIX_data_ARSP = pd.read_csv('Dataflash CSV/DataflashARSP.csv')
PIX_data_ATT = pd.read_csv('Dataflash CSV/DataflashATT.csv')
PIX_data_IMU2 = pd.read_csv('Dataflash CSV/DataflashIMU2.csv')

# ARDUINO / BLACKBOX FTI:
ARDU_data_SD = pd.read_csv('SD/A1F3.txt',header=None)

# TRANSMITTER LOGS:
TRANS_data_1 = pd.read_csv('Transmitter Log/AlbatrossOne-2020-11-24.csv') # PRIMARY
TRANS_data_2 = pd.read_csv('Transmitter Log/AlbatrossSecond-2020-11-24.csv') # SECONDARY
TRANS_data_1 = TRANS_data_1.iloc[969:] # remove any unwanted rows at the beginning if the transmitter was turned off beforehand
TRANS_time_s = TRANS_data_1['Time'].apply(lambda x: datetime.timedelta(hours=datetime.datetime.strptime(x,'%H:%M:%S.%f').hour,minutes=datetime.datetime.strptime(x,'%H:%M:%S.%f').minute, seconds=datetime.datetime.strptime(x,'%H:%M:%S.%f').second, microseconds=datetime.datetime.strptime(x,'%H:%M:%S.%f').microsecond).total_seconds())
TRANS_data_1.insert(loc=2, column='Time (s)', value=TRANS_time_s) # add seconds column for later merging with other datasets

# SYNC PIXHAWK DATA TO COMMON UNIXTIME (IMU2 dt=0.02s) using nearest neighbour (not interpolating):
PIX_merge = pd.merge_asof(PIX_data_IMU2,PIX_data_AHR2,on='timestamp',suffixes=('_IMU2','_AHR2'))
PIX_merge = pd.merge_asof(PIX_merge,PIX_data_ARSP,on='timestamp',suffixes=('_AHR2','_ARSP'))
PIX_merge = pd.merge_asof(PIX_merge,PIX_data_ATT,on='timestamp',suffixes=('_AHR2','_ATT'))
PIX_merge = PIX_merge.drop(['TimeUS_IMU2','TimeUS_AHR2','TimeUS_ATT','TimeUS_merge','EG','EA','T','GH','AH','GHz','AHz','Alt','Lat','Lng','Q1','Q2','Q3','Q4','U','Health','Primary','RawPress','Offset','DesRoll','DesPitch','DesRoll','DesYaw','ErrRP','ErrYaw'],axis=1)
                          
# ADP SYNCING PLOTS
if (1==0):
    fig,ax = plt.subplots()
    #ax.plot(ARDU_data_SD.index, ARDU_data_SD[17], color="red")
    ax.plot(ARDU_data_SD[0], ARDU_data_SD[17], color="red")
    ax.set_xlabel("Index",fontsize=12)
    ax.set_ylabel("Alpha",color="red",fontsize=12)
    ax2=ax.twinx()
    #ax2.plot(ARDU_data_SD.index, ARDU_data_SD[18],color="blue")
    ax2.plot(ARDU_data_SD[0], ARDU_data_SD[18],color="blue")
    ax2.set_ylabel("Beta",color="blue",fontsize=12)
    #plt.xlim(9500,11000)
    plt.show()

# PIXHAWK YAW SYNCING PLOTS
if (1==0):
    fig,ax = plt.subplots()
    ax.plot(PIX_merge.index, PIX_merge['GyrZ'], color="red")
    ax.set_xlabel("Index",fontsize=12)
    ax.set_ylabel("GyrZ",color="red",fontsize=12)
    ax2=ax.twinx()
    ax2.plot(PIX_merge.index, PIX_merge['Yaw_ATT'],color="blue")
    ax2.set_ylabel("Yaw_ATT",color="blue",fontsize=12)
    plt.xlim(9500,11000)
    plt.show()



#######################
###     INPUTS     ####
#######################

# Master Stopwatch is NOT always started with Arduino BB SD t=0
# Transmitter 2 deemed unnecessary data for DFDR (only controlling secondary surfaces)
# Whole DFDR should be aligned to Master Stopwatch time

# TAILCAM VIDEO STOPWATCH SYNC:
# Vid 1:
tailcamT_stopwatchT = ['03:08.090','09:46.370']; # any pair of timestamps from Tailcam and Master stopwatch MM:SS:MS from first video file
tailcam_stopwatch_dT = datetime.datetime.strptime(tailcamT_stopwatchT[1], '%M:%S.%f') - datetime.datetime.strptime(tailcamT_stopwatchT[0], '%M:%S.%f') # time delta in (M,S,ms) between Tailcam video and Master stopwatch
# Vid 2:
secondVid = True # True if there is a second video file which needs stiching on the end of the VTP timestamp columns, False if not.
tailcamT_stopwatchT_2 = ['03:26.120','27:05.680']; # any pair of timestamps from Tailcam and Master stopwatch MM:SS:MS from second video file
tailcam_stopwatch_dT_2 = datetime.datetime.strptime(tailcamT_stopwatchT_2[1], '%M:%S.%f') - datetime.datetime.strptime(tailcamT_stopwatchT_2[0], '%M:%S.%f') # time delta in (M,S,ms) between Tailcam video and Master stopwatch   
                                                 
# TAILCAM VIDEO ARDUINO ADP SYNC:
tailcamT_ADPSync = ['03:31.650',34497]; # time on Tailcam video at which Alpha vane is moved suddenly during calibration, ARDU row index which corresponds to this                                        
stopwatchT_ADPSync = datetime.datetime.strptime(tailcamT_ADPSync[0], '%M:%S.%f') + tailcam_stopwatch_dT # calculated time on Master Stopwatch when the yaw sync begins, using dT relationship above.                         
ARDU_data_SD['ARDU_t'] = pd.to_datetime(ARDU_data_SD[0], unit='s').dt.strftime('%M:%S.%f') # change time format to MM:SS:MS
ARDUT_ADPSync = ARDU_data_SD['ARDU_t'].iloc[tailcamT_ADPSync[1]] # get ARDU_data_SD timestamp corresponding to ADP sync start
ARDU_stopwatch_dT = datetime.datetime.strptime(ARDUT_ADPSync, '%M:%S.%f') - stopwatchT_ADPSync # time delta in (M,S,ms) between Pixhawk and Master Stopwatch                     
                                               
# TAILCAM VIDEO PIXHAWK YAW SYNC:
tailcamT_PIXi_yawSync = ['03:57.340',39083]; # time on Tailcam video at which first 90 deg yaw sync starts, Pixhawk merged row index which correponds to this yaw
stopwatchT_yawSync = datetime.datetime.strptime(tailcamT_PIXi_yawSync[0], '%M:%S.%f') + tailcam_stopwatch_dT # calculated time on Master Stopwatch when the yaw sync begins, using dT relationship above.
PIX_merge.insert(loc=0, column='Pix_t (s)', value=(PIX_merge['timestamp'] - PIX_merge['timestamp'].iloc[0])) # create new first column for Pixhawk t since start, starting at 0
PIX_merge['Pix_t'] = pd.to_datetime(PIX_merge['Pix_t (s)'], unit='s').dt.strftime('%M:%S.%f') # change time format to MM:SS:MS
PIXT_yawSync = PIX_merge['Pix_t'].iloc[tailcamT_PIXi_yawSync[1]] # get PIX_merge timestamp corresponding to yaw sync start
PIX_stopwatch_dT = datetime.datetime.strptime(PIXT_yawSync, '%M:%S.%f') - stopwatchT_yawSync # time delta in (M,S,ms) between Pixhawk and Master Stopwatch
                                            
# TAILCAM VIDEO TRANSMITTER 1 SYNC:
tailcamT_Trans1SyncT = ['04:47.000','10:13:01.580'] # time on Tailcam video when transmitter sync aileron input is started, Transmitter 1 time which corresponds to this aileron input
Trans1_tailcam_dT = datetime.datetime.strptime(tailcamT_Trans1SyncT[1], '%H:%M:%S.%f') - datetime.datetime.strptime(tailcamT_Trans1SyncT[0], '%M:%S.%f') # time delta in (H,M,S,ms) between Transmitter 1 and Tailcam video
    
# TAILCAM VIDEO SPLIT?
tailcamLength = '16:58.300' # total length of initial tailcam video for test (MM:SS:ms). If shorter than whole test then a second video file will have been created.
tailcamLength = datetime.datetime.strptime(tailcamLength, '%M:%S.%f')
tailcamLengthS = datetime.timedelta(minutes=tailcamLength.minute,seconds=tailcamLength.second,milliseconds=tailcamLength.microsecond/1000)

             

                                                                
#######################
### TIMESERIES SYNC ###
#######################

# CREATE NEW DATAFRAME FOR FINAL DFDR
DFDR = pd.DataFrame()

# TIMES
DFDR['Master Stopwatch (s)'] = ARDU_data_SD[0] - ARDU_stopwatch_dT.total_seconds() # Add primary timing column, in seconds
DFDR['Master Stopwatch'] = pd.to_datetime(DFDR['Master Stopwatch (s)'], unit='s').dt.strftime('%M:%S.%f') # change time format to MM:SS:MS
DFDR['ARDU Time (s)'] = ARDU_data_SD[0] # Add ARDUINO time column, in seconds
DFDR['VTP Cam Time (s)'] = DFDR['Master Stopwatch (s)'] - tailcam_stopwatch_dT.total_seconds() # Add VTP cam time column, in seconds
DFDR['Transmitter 1 Time (s)'] = DFDR['VTP Cam Time (s)'] + Trans1_tailcam_dT.total_seconds() # Add Transmitter 1 time column
DFDR['Transmitter 1 Time'] = pd.to_datetime(DFDR['Transmitter 1 Time (s)'], unit='s').dt.strftime('%H:%M:%S.%f') # change time format to MM:SS:MS
DFDR['VTP Cam Time (s)'][DFDR['VTP Cam Time (s)'] < 0] = 0.0; # remove all negative VTP cam times!
DFDR['VTP Cam Time'] = pd.to_datetime(DFDR['VTP Cam Time (s)'], unit='s').dt.strftime('%M:%S.%f') # change time format to MM:SS:MS
DFDR['VTP Cam Time'][DFDR['VTP Cam Time (s)']>tailcamLengthS.total_seconds()] = None; # Remove VTP times after first video ended
DFDR['VTP Cam Time (s)'][DFDR['VTP Cam Time (s)']>tailcamLengthS.total_seconds()] = None; # Remove VTP times after first video ended
DFDR['Pixhawk Time (s)'] = DFDR['Master Stopwatch (s)'] + PIX_stopwatch_dT.total_seconds() # Add Pixhawk time column, in seconds 
DFDR['Pixhawk Time (s)'][DFDR['Pixhawk Time (s)'] < 0] = 0.0; # remove all negative Pixhawk times!
DFDR['Pixhawk Time'] = pd.to_datetime(DFDR['Pixhawk Time (s)'], unit='s').dt.strftime('%M:%S.%f') # change time format to MM:SS:MS
if (secondVid):
    DFDR['VTP Cam Time (s)'][DFDR['VTP Cam Time'].isnull()] = DFDR['Master Stopwatch (s)'] - tailcam_stopwatch_dT_2.total_seconds() # add second video timing
    DFDR['VTP Cam Time (s)'][DFDR['VTP Cam Time (s)'] < 0] = 0.0; # remove all negative VTP cam times!
    DFDR['VTP Cam Time'] = pd.to_datetime(DFDR['VTP Cam Time (s)'], unit='s').dt.strftime('%M:%S.%f') # change time format to MM:SS:MS
DFDR['Master Stopwatch (s)'][DFDR['Master Stopwatch (s)'] < 0] = 0.0; # remove all negative Master Stopwatch times!
DFDR['Master Stopwatch'] = pd.to_datetime(DFDR['Master Stopwatch (s)'], unit='s').dt.strftime('%M:%S.%f') # change time format to MM:SS:MS
# Re-order timing columns:
DFDR = DFDR[['Master Stopwatch (s)','Master Stopwatch','ARDU Time (s)','VTP Cam Time (s)','VTP Cam Time','Pixhawk Time (s)','Pixhawk Time','Transmitter 1 Time (s)','Transmitter 1 Time']]
    
# ADP DATA (no merging/interpolation needed)
DFDR['Alpha (deg)'] = ARDU_data_SD[17] # Add calibrated angle of attack data, in degrees
DFDR['Beta (deg)'] = ARDU_data_SD[18] # Add calibrated angle of sideslipe data, in degrees

# WINGTIP STATUSES (no merging/interpolation needed)
# note: documentation beleived to be incorrect and sequence in Arduino SD data is Right,Left not Left,Right.
DFDR['Right Wingtip'] = ARDU_data_SD[19] # Add right wingtip switch status (0: unlocked 1: locked)
DFDR['Left Wingtip'] = ARDU_data_SD[20] # Add left wingtip switch status (0: unlocked 1: locked)

# PIXHAWK DATA (merging/interpolation required due to differing timeseries)
DFDR = pd.merge_asof(DFDR,PIX_merge,left_on='Pixhawk Time (s)',right_on='Pix_t (s)')
DFDR = DFDR.drop(['timestamp','Pix_t'],axis=1) # drop unwanted Pixhawk parameters
DFDR['nY (g)'] = -DFDR['AccY']/9.80665 # add post-processed g column for Y acc
DFDR['nZ (g)'] = -DFDR['AccZ']/9.80665 # add post-processed g column for Z acc 

# TRANSMITTER 1 DATA (merging/interpolation required due to differing timeseries)
DFDR = pd.merge_asof(DFDR,TRANS_data_1,left_on='Transmitter 1 Time (s)',right_on='Time (s)')
#DFDR = DFDR.drop(['RB2V(V)','RB2A(A)','RBCS','RBS','RB1C(mAh)','RB2C(mAh)','RB1A(A)','RB1V(V)','RSSI(dB)','RxBt(V)','EX1','EX2','S1','S2','LS','RS','SA','SB','SC','SD','SE','SF','SF','SG','SI','SJ','SH','LSW','TxBat(V)'],axis=1)
DFDR = DFDR.drop(['RSSI(dB)','RxBt(V)','EX1','EX2','S1','S2','LS','RS','SA','SB','SC','SD','SE','SF','SF','SG','SI','SJ','SH','LSW','TxBat(V)'],axis=1) # drop unimportant transmitter parameters

                
                
#######################
### EXPORT TO .XLSX ###
#######################  

if (1==1):
    # PREPARE DFDR FOR EXPORT
    DFDR_export = DFDR.drop(['Pix_t (s)','Time','Time (s)','ARDU Time (s)','VTP Cam Time (s)','Pixhawk Time (s)','Pixhawk Time','Transmitter 1 Time (s)'],axis=1)
    # Add placeholders for future additions
    DFDR_export['Alpha Corrected (deg)'] = ''
    DFDR_export['Beta Corrected (deg)'] = ''
    DFDR_export['FWT Command'] = ''
    # Order columns correctly
    DFDR_export = DFDR_export[['Master Stopwatch (s)','Master Stopwatch','VTP Cam Time','Transmitter 1 Time','Alpha (deg)','Beta (deg)','Alpha Corrected (deg)','Beta Corrected (deg)','Right Wingtip','Left Wingtip','Roll_AHR2','Pitch_AHR2','Yaw_AHR2','Airspeed','Temp', \
    'DiffPress','Roll_ATT','Pitch_ATT','Yaw_ATT','GyrX','GyrY','GyrZ','AccX','AccY','AccZ','nY (g)','nZ (g)','Rudp','Rud','Ele','Thr','Ail','RB1A(A)','RB2A(A)','RB1V(V)','RB2V(V)','RB1C(mAh)','RB2C(mAh)','RBCS','RBS','6P','FWT Command']]
    
    # EXPORT TO .XLSX
    DFDR_export.to_excel('DFDR_Test01_export.xlsx', sheet_name='DFDR', index=False, startrow = 0, startcol = 0)





