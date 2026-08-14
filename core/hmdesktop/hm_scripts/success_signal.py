def success_signal():
    code = r"""
    success_signal_file = os.path.join(work_dictionary, 'success.success')
    
    with open(success_signal_file, "a", encoding="utf-8") as f:
        f.write("generate success_signal_file\n$$\n$$\n$$\n")

##
##
##

"""
    return code
