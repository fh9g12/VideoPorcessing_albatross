import pandas as pd
import numpy as np
import argparse
import time
from openpyxl import load_workbook
from datetime import datetime
from openpyxl import load_workbook
from scipy.interpolate import griddata,interp1d
import pickle

def add_fwt_angles(excel_filename,worksheet,angle_data_filename,angle_calib_filename,time_offset=0,is_right=True,output_file = None):
    print('Loading Excel File')
    excel_file = open(excel_filename,'rb')
    data = pd.read_excel(excel_file,sheet_name = 'DFDR',
                  header=None,skiprows=3)
    df = get_angle_data(angle_data_filename,is_right)

    print('Loading calibration')
    calib = pickle.load(open(angle_calib_filename,'rb'))
    calib_func = interp1d(calib['angle_act'],calib['angle_calib'],fill_value='extrapolate')

    print('Interpolate data onto dfdr times')
    df['angle_calib'] = calib_func(df['angle'])
    f_angle = interp1d(df['t']+ time_offset,df['angle_calib'],bounds_error=False)


    # ----------------------- Save to an excel file --------------------------------
    col_index = 45 if is_right else 44
    ind = np.logical_and((data[2] + time_offset) >= min(df['t'] + time_offset),(data[2] + time_offset) <= max(df['t'] + time_offset))
    wb = load_workbook(excel_file)
    ws = wb[worksheet]
    for i,val in enumerate(data.loc[ind,2].to_list()):
        ws.cell(row = 4 + i,column = col_index).value = f_angle([val])[0]

    output_file = excel_file if output_file is None else output_file
    print(f'Saving to File: {output_file}')
    wb.save(output_file)
    excel_file.close()
    print('Complete')


def get_angle_data(filename,flip=False):
    df2 = pd.read_csv(filename)
    df2['t'] = df2['Frame']/df2['fps']
    df2['x_delta'] = df2['x1'] - df2['x0']
    df2['y_delta'] = df2['y1'] - df2['y0']
    df2['x_delta'] = df2['x_delta'].where((df2['x0']>df2['x1']).to_list(),df2['x1']-df2['x0'])
    df2['y_delta'] = df2['y_delta'].where((df2['x0']>df2['x1']).to_list(),df2['y1']-df2['y0'])
    df2['angle'] = np.rad2deg(np.arctan2(df2['y_delta'],df2['x_delta']))
    df2['angle'] = df2['angle'] if not flip else -df2['angle']
    return df2