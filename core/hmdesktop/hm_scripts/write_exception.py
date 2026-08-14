def write_exception():
    code = r"""
except Exception as e:

    with open(run_hwx_log, "a", encoding="utf-8") as f:
        f.write(f'{time_string}\n')
        f.write(traceback.format_exc())    
"""
    return code