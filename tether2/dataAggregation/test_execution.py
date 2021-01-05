import pytest
from correct_time_cols import correct_time
from add_fwt_angels import add_fwt_angles

# --------------------------  DFDR Time Correction ----------------------------------
@pytest.mark.parametrize("test_num",[1,2,3,4,5,6,7,8,9,10,11,12,13,14])
def test_all_fix_times(test_num):
    excel_file = f"/Volumes/Windows Dat/TETHER2/TETHER2_DFDRs/DFDR_Test{test_num:02d}_v1.xlsx"
    worksheet = "DFDR"
    output_file = f"/Volumes/Windows Dat/TETHER2/TETHER2_DFDRs/DFDR_Test{test_num:02d}_v2.xlsx"
    correct_time(excel_file,worksheet,output_file)
    assert True


# --------------------------  DFDR Add FWT angles ----------------------------------
def test_load_test_3_angles():
    test_num = 3
    excel_file = f"/Volumes/Windows Dat/TETHER2/TETHER2_DFDRs/DFDR_Test{test_num:02d}_v2.xlsx"
    worksheet = "DFDR"
    output_file = f"/Volumes/Windows Dat/TETHER2/TETHER2_DFDRs/DFDR_Test{test_num:02d}_v3.xlsx"
    left_angle_data = "/Volumes/Windows Dat/TETHER2/TETHER2_2A.1/VID/tail/first_part/RC_VID_0000_left_data.csv"
    right_angle_data = "/Volumes/Windows Dat/TETHER2/TETHER2_2A.1/VID/tail/first_part/RC_VID_0000_right_data.csv"
    left_angle_calib = "/Volumes/Windows Dat/TETHER2/TETHER2_2A.1/VID/tail/first_part/RC_VID_0000_left_calib.pkl"
    right_angle_calib = "/Volumes/Windows Dat/TETHER2/TETHER2_2A.1/VID/tail/first_part/RC_VID_0000_right_calib.pkl"
    add_fwt_angles(excel_file,worksheet,left_angle_data,left_angle_calib,-19.28,False,output_file)
    add_fwt_angles(excel_file,worksheet,right_angle_data,right_angle_calib,-19.28,True,output_file)
    assert True