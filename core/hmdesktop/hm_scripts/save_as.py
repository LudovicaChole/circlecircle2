def save_as(target_path, runhwxlog_path):
    code = f"""save_as_folder = os.path.dirname(r'{target_path}')

save_as_basename = os.path.basename(r'{target_path}')

save_as_name, save_as_ext = os.path.splitext(save_as_basename)

save_as_file = os.path.join(save_as_folder, save_as_name+"_c2auto.hm")

model.writefile(filename=save_as_file, do_not_write_facets=1)

with open(r'{runhwxlog_path}', 'a', encoding='utf-8', errors='ignore') as f:
    f.write('save as file:')
    f.write(save_as_file)

##
##
##
##

"""

    return code