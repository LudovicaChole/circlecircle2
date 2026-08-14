def set_display_3():
    code = r"""hm.setoption(fe_display=1)

model.setdisplayattributes(style=3, colortype=0)  

with open(run_hwx_log, "a", encoding="utf-8") as f:
    f.write('set display 3\n$$\n$$\n$$\n')

##
##
##

"""
    return code