from mpc_wise_functions import comparer, generate_source_ids_dict
from ds9_interface_functions import make_region
import os
import sys


def load_files(load_file, mpc_code):
    file_stubs = []
    with open(f"loader_data/{load_file}", 'r') as file:
        for line in file:
            file_stubs.append(line.rstrip())

    wise_files = os.listdir(f"wise_images/{mpc_code}")
    run_files = []
    for stub in file_stubs:
        for file in wise_files:
            if file[:9] == stub:
                run_files.append(file)

    idx = list(range(len(run_files)))[::2]
    w_sorted = []
    for i in idx:
        pair = (run_files[i], run_files[i + 1])
        if pair[0][10:12] == "w1":
            w_sorted.extend([pair[0], pair[1]])
        else:
            w_sorted.extend([pair[1], pair[0]])


    mpc_file = "input_data/" + mpc_code + ".txt"
    wise_file = "input_data/" + mpc_code + ".tbl"
    new_epochs = comparer(mpc_file, wise_file, False)
    good_epochs = {}
    for epoch in new_epochs:
        sid = new_epochs[epoch][0][:9]
        for stub in file_stubs:
            if stub == sid:
                good_epochs[sid] = new_epochs[epoch]
                good_epochs[sid][0] = epoch    
    
    print('-' * 65)
    print("| Frame | Source Id | W1 Flux  | W1 Sigma | W2 Flux  | W2 Sigma |")
    print('-' * 65)
    for idx, epoch in enumerate(good_epochs):
        print('|' + f"{idx + 1}".rjust(6) + f" | {epoch}" 
              + ' | ' + f"{good_epochs[epoch][4]}".rjust(8) 
              + ' | ' + f"{good_epochs[epoch][5]}".rjust(8) 
              + ' | ' + f"{good_epochs[epoch][6]}".rjust(8)
              + ' | ' + f"{good_epochs[epoch][7]}".rjust(8) + ' | ')
    print('-' * 65)

    region_list = []
    for file in w_sorted:
        region_list.append(f"wise_images/{mpc_code}/" + file)

    region_files = os.listdir("regions")
    for file in region_files:
        os.remove("regions/" + file)
    lookup_table = generate_source_ids_dict(mpc_file, wise_file)
    for file in region_list:
        make_region(file, lookup_table, mpc_code)

    ds9_script = "ds9 -tile "
    for file in w_sorted:
        sid, w_band = file[:9], file[10:12]
        ds9_script += f"wise_images/{mpc_code}/" + file + ' -regions '
        ds9_script += f"regions/{sid}_{w_band}.reg "
    os.popen(ds9_script)


load_files(sys.argv[1], sys.argv[2])