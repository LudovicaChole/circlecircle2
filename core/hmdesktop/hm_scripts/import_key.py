def import_key():
    solver = r"#ls-dyna\\dynakey"

    h1 = r"import Keywords: {target}\n$$\n$$\n$$\n"

    code = f"""
    model.feinputpreserveincludefiles()

    model.start_batch_import(mode=2, isInRepLoading=0)

    model.feinputwithdata2(import_reader='{solver}', 
                           filename=target, 
                           overwrite_flag=0, 
                           reserved1=0, 
                           cleanup_tolerance=0, 
                           blanked_component=0, 
                           offset_flag=0, 
                           string_array=["LsDyna ", "Keyword971_R16.0 ", "CREATE_ONE_COMP_ACROSS_INCLUDES ", 
                                         "ASSIGNPROP_BYHMCOMMENTS ", "CREATE_PART_HIERARCHY", "IMPORT_MATERIAL_METADATA", 
                                         "IMPORT_PARTS_APP_METADATA", "SKIP_INCLUDE_STAMP ", "ANSA ", 
                                         "ENGINEERINGENTITIES ", "SKIP_HYPERBEAM_MESSAGES ", 
                                         "ACCELEROMETERS_DISPLAY_SKIP ", "ALES_DISPLAY_SKIP ", 
                                         "BLOCKS_DISPLAY_SKIP ", "EXTRANODES_DISPLAY_SKIP ", 
                                         "CONSTRAINEDRIGIDBODY_DISPLAY_SKIP ", "CONTACTSURF_DISPLAY_SKIP ", 
                                         "CROSSSECTION_DISPLAY_SKIP ", "LOADCOLS_DISPLAY_SKIP ", 
                                         "RIGIDWALLS_DISPLAY_SKIP ", "RETRACTORS_DISPLAY_SKIP ", 
                                         "SLIPRINGS_DISPLAY_SKIP ", "SOLVERMASSES_DISPLAY_SKIP ", 
                                         "SYSTCOLS_DISPLAY_SKIP ", "VECTORCOLS_DISPLAY_SKIP ", 
                                         "INITIALGEOMETRIES_DISPLAY_SKIP "], 
                           scale_factor=1, 
                           name_comps_by_layer=0)

    model.end_batch_import()

    with open(run_hwx_log, "a", encoding="utf-8") as f:
        f.write(f'{h1}')

##
##
##

"""

    return code
