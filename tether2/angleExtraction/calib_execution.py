
# %%
import subprocess
import os
# %%
def vid_file(test,num):
    return f"\"C:\\Users\\qe19391\\OneDrive - University of Bristol\\Tether2\\Test {test}\\RC_VID_{num:04d}.MOV\""
def calib_file(test,num,is_right):
    side = 'right' if is_right else 'left'
    return f"\"C:\\Users\\qe19391\\OneDrive - University of Bristol\\Tether2\\Test {test}\\RC_VID_{num:04d}_{side}_calib.pkl\""
# %%
args = dict()
all_args=[]

# vid 1 right
args["-v"] = vid_file(1,5)
args["-f"] = [7796,8232,8620,9040,9460,9820]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(1,5,True)
args["-o"] = calib_file(1,5,True)
all_args.append(args.copy())

# vid 1 left
args["-v"] = vid_file(1,5)
args["-f"] = [3477,3966,4374,4980,5676,6162]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(1,5,False)
args["-o"] = calib_file(6,5,False)
all_args.append(args.copy())

# vid 3 right
args["-v"] = vid_file(3,0)
args["-f"] = [10977,11379,11860,12408,12852,13424]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(3,0,True)
args["-o"] = calib_file(3,0,True)
all_args.append(args.copy())

# vid 3 left
args["-v"] = vid_file(3,0)
args["-f"] = [4921,5461,6907,7508,8075,8686]
args["-c"] = calib_file(3,0,False)
args["-o"] = calib_file(3,0,False)
all_args.append(args.copy())

# vid 6 right
args["-v"] = vid_file(6,5)
args["-f"] = [57300,57709,58261,58699,59161,59558]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(1,5,True)
args["-o"] = calib_file(6,5,True)
all_args.append(args.copy())

# vid 6 left
args["-v"] = vid_file(6,5)
args["-f"] = [54139,54525,54930,55350,55806,56466]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(1,5,False)
args["-o"] = calib_file(6,5,False)
all_args.append(args.copy())

# vid 10 right
args["-v"] = vid_file(10,14)
args["-f"] = [1840,2475,2769,3411,3849,4443]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(3,0,True)
args["-o"] = calib_file(10,14,True)
all_args.append(args.copy())

# vid 10 left
args["-v"] = vid_file(10,14)
args["-f"] = [5319,5727,6201,6705,7167,7683]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(3,0,False)
args["-o"] = calib_file(10,14,False)
all_args.append(args.copy())

# vid 13 right
args["-v"] = vid_file(13,19)
args["-f"] = [5160,5476,5820,6168,6504,6872]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(1,5,True)
args["-o"] = calib_file(13,19,True)
all_args.append(args.copy())

# vid 13 left
args["-v"] = vid_file(13,19)
args["-f"] = [2715,2992,3400,3716,4084,4540]
args["-a"] = [0,15,30,45,60,75]
args["-c"] = calib_file(1,5,False)
args["-o"] = calib_file(13,19,False)
all_args.append(args.copy())


# %%
arg_list = []
for key,val in all_args[1].items():
    arg_list.append(key)
    if isinstance(val,str):
        arg_list.append(val)
    elif hasattr(val,'__iter__'):
        arg_list += [str(i) for i in val]
    else:
        arg_list.append(str(val))
# %%
import os
os.system(' '.join(['conda','activate','albatross','&','python','\"C:\\Git\\VideoPorcessing_albatross\\tether2\\angleExtraction\\calib_angles.py\"',*arg_list]))
# %%
import pickle
d = pickle.load(open(all_args[-3]["-o"].replace('"',''),'rb'))
# %%
for r in all_args:
    arg_list = []
    for key,val in r.items():
        arg_list.append(key)
        if isinstance(val,str):
            arg_list.append(val)
        elif hasattr(val,'__iter__'):
            arg_list += [str(i) for i in val]
        else:
            arg_list.append(str(val))
    os.system(' '.join(['conda','activate','albatross','&','python','\"C:\\Git\\VideoPorcessing_albatross\\tether2\\angleExtraction\\calib_angles.py\"',*arg_list]))

# %%
