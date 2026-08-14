def import_hm():
    code = r"""
    model.setdisplayattributes(style=2, colortype=0)

    model.start_batch_import(mode=1, isInRepLoading=0)

    model.mergefile2(filename=target, 
                         connectors_checkattribute=False, 
                         connectors_layercheck=True, 
                         connectors_thicknesscheck=True, 
                         connectors_tolerance=0.10, 
                         connectors_idcheck=False, 
                         connectors_type=True, 
                         mergemode_comps="keepboth", 
                         mergemode_mats="keepboth", 
                         mergemode_props="keepboth", 
                         mergemode_sensors="keepboth", 
                         mergemode_sections="keepboth", 
                         mergemode_attachments="keepincoming", 
                         mergemode_connectors="keepincoming", 
                         mergemode_geometryandmesh="keepboth", 
                         connectors_tolerancecheck=True, 
                         attachments_tolerancecheck=True, 
                         attachments_tolerance=0.10, 
                         attachments_idcheck=False, 
                         attachments_linkcheck=False, 
                         attachments_configcheck=True, 
                         mergemode_attachmentcontrols="keepincoming", 
                         attachmentcontrols_namecheck=True, 
                         attachmentcontrols_idcheck=False, 
                         attachmentcontrols_configcheck=False, 
                         mergemode_modules="keepexisting", 
                         mergemode_engentities="keepincoming", 
                         engentities_namecheck=True, 
                         engentities_idcheck=False, 
                         engentities_configcheck=False)

    model.end_batch_import()

    with open(run_hwx_log, "a", encoding="utf-8") as f:
        f.write(f'import HM: {target}\n$$\n$$\n$$\n')

"""
    return code
