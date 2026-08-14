def get_solid_info():
    code = r"""
    script_data.setdefault("solid", {})

    solid_collection = hm.Collection(model, ent.Solid)

    for solid in solid_collection:
        solid_id = solid.id

        uid = len(script_data["solid"]) + 1

        script_data["solid"][uid] = {
        "id": solid_id,
        }

    with open(run_hwx_log, "a", encoding="utf-8") as f:
        f.write('get solid info\n$$\n$$\n$$\n')

##
##
##

"""

    return code