def save_as():
    code = r"""
    model.writefile(filename=save_as_file, do_not_write_facets=1)

    with open(script_data_file, 'w', encoding='utf-8', errors='ignore') as f:
        json.dump(script_data, f, ensure_ascii=False, indent=4)

    with open(run_hwx_log, 'a', encoding='utf-8', errors='ignore') as f:
        f.write(f'save as file: {save_as_file}\n$$\n$$\n$$\n')

##
##
##
##

"""

    return code
