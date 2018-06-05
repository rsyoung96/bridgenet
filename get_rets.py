# By: Gitanjali Bhattacharjee
# last modified: 5 June 2018
# ----------------------------------------------------------------------------------------------------------------------
# This script imports the original master_dict that contains the fragility function parameters of every bridge in the
# Bay Area that is owned by CalTrans. It then copies that dictionary and updates the fragility function parameters of
# bridges that undergo retrofit. That update is simply an increase in the median of each fragility function, which
# results in the curve shifting to the right, in graphical terms.

# user inputs:
# - retrofit improvement factor: reflects percent increase in median of each fragility function (type: float)
# - bridges to retrofit: list of the new IDs of bridges (between 1 and 1743, inclusive) to retrofit (type: list of strings)
# outputs:
# - master_dict_ret: dictionary with the same structure and key-value pairs of master_dict, but with updated fragility
# function parameters (type: dictionary)

import pickle, copy

# placeholder - retrofit improvement factor (user-defined)
ret_factor = 1.15;
assert ret_factor > 1.0

# FIX THIS placeholder - get new IDs of bridges to retrofit from user-defined list
rets = ['300','812','22','55'];

# get master_dict
with open('input/20140114_master_bridge_dict.pkl', 'rb') as f:
    master_dict = pickle.load(f)  # has 1743 keys. One per highway bridge. (NOT BART)

print master_dict.keys()

# GB: create inverse dictionary to map new IDs to original IDs
new_to_oldIDs = {}
for k, v in master_dict.items():
    for v2 in v.keys():
        if v2 == 'new_id':
            n = master_dict[k][v2]
            new_to_oldIDs[str(n)] = k  # key = newID, value = originalID


# duplicate the master_dict to  modify fragility function parameters for retrofit - DO NOT modify anything in master_dict
master_dict_ret = copy.deepcopy(master_dict)
#
rets_oldID = []
for i in range(len(rets)):
    oldID = new_to_oldIDs[rets[i]]
    rets_oldID.append(oldID)

for i in range(len(rets)):
    master_dict_ret[rets_oldID[i]]['mod_lnSa'] = master_dict[rets_oldID[i]]['mod_lnSa']*ret_factor;
    master_dict_ret[rets_oldID[i]]['ext_lnSa'] = master_dict[rets_oldID[i]]['ext_lnSa']*ret_factor;
    master_dict_ret[rets_oldID[i]]['com_lnSa'] = master_dict[rets_oldID[i]]['com_lnSa']*ret_factor;

with open('input/master_bridge_dict_ret.pkl', 'wb') as f:
    pickle.dump(master_dict_ret, f, protocol=pickle.HIGHEST_PROTOCOL)

