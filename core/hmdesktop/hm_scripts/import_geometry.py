def import_geometry():
    code = r"""
    model.start_batch_import(mode=3, isInRepLoading=0)

    model.geomimport(translator_type="step_ct", 
                     input_file_name=target,
                     options=["BodyIDAsMetadata=off", "CleanupTol=-0.01", "ColorsAsMetadata=off", "CreationType=Parts",
                              "DegSurfTol=0.0", "DensityAsMetadata=off", "DisplayRepresentation=off",
                              "DoNotMergeEdges=on", "FullNameAsMetadata=off", "ImportBlanked=off",
                              "ImportCoordinateSystems=on", "ImportFreeCurves=on", "ImportFreePoints=on",
                              "LayerAsMetadata=off", "LegacyHierarchyAsMetadata=off", "MID=MaterialId",
                              "MaterialName=Material", "MeshFlag=MeshFlag", "OriginalIdAsMetadata=on", "PID=PID",
                              "PartName=PartName", "PartNumber=PartNumber", "Revision=Revision", "ScaleFactor=1.0",
                              "SkipCreationOfSolid=off", "SplitComponents=Body", "StitchingAcrossBodies=on",
                              "TagsAsMetadata=on", "TargetUnits=CAD", "units", "ThicknessName=Thickness", "UID=UID",
                              "UpdateSketchingUnits=on", "VariantCondition=VariantCondition",
                              "VariantScope=VariantScope"])

    model.end_batch_import()

    with open(run_hwx_log, "a", encoding="utf-8") as f:
        f.write(f'import geometry: {target}\n$$\n$$\n$$\n')

##
##
##
##

"""
    return code
