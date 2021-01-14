import pytest
from correct_time_cols import correct_time
from add_fwt_angels import add_fwt_angles





# --------------------------  DFDR Time Correction ----------------------------------
# @pytest.mark.parametrize("test_num",[1,2,3,4,5,6,7,8,9,10,11,12,13,14])
# def test_all_fix_times(test_num):
#     excel_file = f"/Volumes/Windows Dat/TETHER2/TETHER2_DFDRs/DFDR_Test{test_num:02d}_v1.xlsx"
#     worksheet = "DFDR"
#     output_file = f"/Volumes/Windows Dat/TETHER2/TETHER2_DFDRs/DFDR_Test{test_num:02d}_v2.xlsx"
#     correct_time(excel_file,worksheet,output_file)
#     assert True


# --------------------------  DFDR Add FWT angles ----------------------------------
def c_file_gen(test,vid_num,is_right,folder):
    return f"{folder}/Test {test}/RC_VID_{vid_num:04d}_{'right' if is_right else 'left'}_calib.pkl"

def d_file_gen(test,vid_num,is_right,folder):
    return f"{folder}/Test {test}/RC_VID_{vid_num:04d}_{'right' if is_right else 'left'}_data.csv"

def e_file_gen(test,folder):
    return f"{folder}/TETHER2_DFDRs/With Fold Angles/DFDR_Test{test:02d}_v2.xlsx"

def add_both_angles(e_file,d_test,d_vid,c_test,c_vid,folder,time_delta):
    for lr in [False,True]:
        add_fwt_angles(e_file,
                    d_file_gen(d_test,d_vid,lr,folder),
                    c_file_gen(c_test,c_vid,lr,folder),
                    'DFDR',time_delta,lr,e_file)

def test_1_vid_2():
    time_delta = 1419.56
    folder = "/Users/fintan/OneDrive - University of Bristol/Tether2"
    e_file = e_file_gen(1,folder)
    add_both_angles(e_file,
                d_test=1,d_vid=6,
                c_test=1,c_vid=5,folder=folder,time_delta=time_delta)
    assert True

def test_3_vid_2():
    time_delta = 1002.26
    folder = "/Users/fintan/OneDrive - University of Bristol/Tether2"
    e_file = e_file_gen(3,folder)
    add_both_angles(e_file,
                d_test=3,d_vid=1,
                c_test=3,c_vid=0,folder=folder,time_delta=time_delta)
    assert True

def test_10_vid_2():
    time_delta = 944.44
    folder = "/Users/fintan/OneDrive - University of Bristol/Tether2"
    e_file = e_file_gen(10,folder)
    add_both_angles(e_file,
                d_test=10,d_vid=15,
                c_test=10,c_vid=14,folder=folder,time_delta=time_delta)
    assert True

def test_13_vid_2():
    time_delta = 1001.23
    folder = "/Users/fintan/OneDrive - University of Bristol/Tether2"
    e_file = e_file_gen(13,folder)
    add_both_angles(e_file,
                d_test=13,d_vid=20,
                c_test=13,c_vid=19,folder=folder,time_delta=time_delta)
    assert True