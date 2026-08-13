def success_signal(temp_folder):
    code = f"""temp_folder = r'{temp_folder}'
file_path = os.path.join(temp_folder, 'success.success')

with open(file_path, "w", encoding="utf-8") as f:
    f.write("success")

##
##
##
##

"""
    return code
