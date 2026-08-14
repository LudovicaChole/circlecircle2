def get_component_info():
    code = r"""
    components_collection = hm.Collection(model, ent.Component)

    script_data.setdefault("component", {})

    filter_solid = hm.FilterByCollection(ent.Solid, ent.Component)
    filter_surface = hm.FilterByCollection(ent.Surface, ent.Component)
    filter_line = hm.FilterByCollection(ent.Line, ent.Solid)
    filter_point = hm.FilterByCollection(ent.Point, ent.Solid)

    for component in components_collection:
        component_id = component.id
        component_cardimage = component.cardimage
        component_material_id = component.materialid
        component_propertyid = component.propertyid
        component_name = component.name
        component_isempty = component.isempty

        current_component_collection = hm.Collection(model, hm.FilterByEnumeration(ent.Component, ids=[component_id]))

        current_solid_collection = hm.Collection(model, filter_solid, current_component_collection)
        current_surface_collection = hm.Collection(model, filter_surface, current_component_collection)
        current_line_collection = hm.Collection(model, filter_line, current_solid_collection)
        current_point_collection = hm.Collection(model, filter_point, current_solid_collection)

        current_component_solid = {}
        current_component_surface = {}
        current_component_line = {}
        current_component_point = {}

        for solid in current_solid_collection:
            solid_id = solid.id
            solid_volume = solid.volume

            current_component_solid_uid = len(current_component_solid) + 1

            current_component_solid[current_component_solid_uid] = {
            "id": solid.id,
            "volume": solid.volume,
            }

        for surface in current_surface_collection:
            surface_id = surface.id
            surface_area = surface.area
            surface_geometry_type = surface.geometrytype

            current_component_surface_uid = len(current_component_surface) + 1

            current_component_surface[current_component_surface_uid] = {
            "id": surface.id,
            "area": surface_area,
            "geometry_type": surface_geometry_type,
            }

        for line in current_line_collection:
            line_id = line.id
            line_topologytype = line.topologytype
            line_length = line.length
            line_startcoords = line.startcoords
            line_endcoords = line.endcoords
            line_starttangentangle = line.starttangentangle
            line_endtangentangle = line.endtangentangle
            line_starttangentvector = line.starttangentvector
            line_endtangentvector = line.endtangentvector

            current_component_line_uid = len(current_component_line) + 1

            current_component_line[current_component_line_uid] = {
            "id": line_id,
            "topology_type": line_topologytype,
            "length": line_length,
            "startcoords": list(line_startcoords),
            "endcoords": list(line_endcoords),
            "starttangentangle": line_starttangentangle,
            "endtangentangle": line_endtangentangle,
            "starttangentvector": list(line_starttangentvector),
            "endtangentvector": list(line_endtangentvector),
            }

        for point in current_point_collection:
            point_id = point.id
            point_coordinates = point.coordinates
            point_x = point.x
            point_y = point.y
            point_z = point.z
            point_topology_type = point.topologytype

            current_component_point_uid = len(current_component_point) + 1

            current_component_point[current_component_point_uid] = {
            "id": point.id,
            "coordinates": list(point_coordinates),
            "x": point.x,
            "y": point.y,
            "z": point.z,
            "topology_type": point_topology_type,
            }

        uid = len(script_data["component"]) + 1

        script_data["component"][uid] = {
        "id": component_id,
        "cardimage": component_cardimage,
        "materialid": component_material_id,
        "propertyid": component_propertyid,
        "name": component_name,
        "isempty": component_isempty,
        "solid_collection": current_component_solid,
        "surface_collection": current_component_surface,
        "line_collection": current_component_line,
        "point_collection": current_component_point,
        }

    with open(run_hwx_log, "a", encoding="utf-8") as f:
        f.write('get component info\n$$\n$$\n$$\n')

##
##
##

"""
    return code
