def set_component_cardimage_to_part():
    code = r"""
    components_collection.set_values("cardimage", "Part")

    with open(run_hwx_log, "a", encoding="utf-8") as f:
        f.write('set component cardimage to part\n$$\n$$\n$$\n')

"""
    return code