class DataFrame:
    """
    base data storge for fea
    typically used for fea keywords files
    """

    def __init__(self):
        self.solver = None

        self.storge = {
            "element_mass": {},
            "set_solid_list": {},
            "database_nodfor": {},
            "database_spcforc": {},
            "database_binary_d3dump": {},
            "database_binary_runrsf": {},
            "database_binary_d3thdt": {},
            "control_hourglass": {},
            "mat_add_damage_gissmo": {},
            "contact_single_edge_id": {},

            "keyword": {},
            "parameter": {},
            "node": {},
            "element_shell": {},
            "element_solid": {},
            "part": {},
            "material": {},
            "section_shell": {},
            "section_solid": {},
            "section_beam": {},
            "hourglass": {},
            "set_node_list": {},
            "set_shell_list": {},
            "set_segment": {},
            "set_part_list": {},
            "database_history_node": {},
            "define_curve": {},
            "define_table": {},
            "mat_add_erosion": {},
            "constrained_extra_nodes_set": {},
            "constrained_nodal_rigid_body": {},
            "database_cross_section_plane_id": {},
            "contact_automatic_surface_to_surface_id": {},
            "contact_automatic_single_surface_id": {},
            "initial_velocity_generation": {},
            "boundary_prescribed_motion_rigid": {},
            "title": {},
            "database_deforc": {},
            "database_jntforc": {},
            "database_format": {},
            "control_shell": {},
            "control_termination": {},
            "control_rigid": {},
            "database_swforc": {},
            "control_solid": {},
            "database_extent_binary": {},
            "control_timestep": {},
            "database_dcfail": {},
            "database_nodout": {},
            "database_abstat": {},
            "database_binary_d3plot": {},
            "database_elout": {},
            "control_output": {},
            "control_accuracy": {},
            "database_binary_intfor": {},
            "database_matsum": {},
            "control_parallel": {},
            "control_contact": {},
            "database_disbout": {},
            "database_glstat": {},
            "database_sleout": {},
            "database_rcforc": {},
            "control_bulk_viscosity": {},
            "control_solution": {},
            "database_secforc": {},
            "control_energy": {},
            "control_dynamic_relaxation": {},
            "database_sbtout": {},
            "database_rwforc": {},
            "contact_tied_nodes_to_surface_id": {},
            "end": {},
        }

        self.storge_node_id = []

        self.storge_part_element = {}

        self.storge_part_node_xyz = {}

        self.storge_part_node_id = {}

        self.storge_rigid_part_goc_xyz = {}    # only used in translator
        self.storge_rigid_part_goc_con = {}    # only used in translator

        self.storge_rigid_part_reference_node = {}

        self.storge_material_id = []

        self.storge_pam_elastic_solid_material = {}    # only used in pamcrash translator

        self.storge_tensor = {
            "node": [],
            "element_shell": [],
            "element_solid": [],
            "element_solid_surface": [],
            "part": [],
        }

        self.output_storge = {}
        self.output_history_node = []

    def reset(self):
        self.solver = None

        for sub_dict in self.storge.values():
            sub_dict.clear()

        self.storge_node_id.clear()

        self.storge_part_element.clear()

        self.storge_part_node_xyz.clear()

        self.storge_part_node_id.clear()

        self.storge_rigid_part_goc_xyz.clear()

        self.storge_rigid_part_goc_con.clear()

        self.storge_rigid_part_reference_node.clear()

        self.storge_material_id.clear()

        self.storge_pam_elastic_solid_material.clear()

        for sub_list in self.storge_tensor.values():
            sub_list.clear()

        self.output_storge.clear()
        self.output_history_node.clear()

    @property
    def set_segment(self):
        return self.storge["set_segment"]

    @property
    def element_mass(self):
        return self.storge["element_mass"]

    @property
    def set_solid_list(self):
        return self.storge["set_solid_list"]

    @property
    def database_nodfor(self):
        return self.storge["database_nodfor"]

    @property
    def database_spcforc(self):
        return self.storge["database_spcforc"]

    @property
    def database_binary_d3dump(self):
        return self.storge["database_binary_d3dump"]

    @property
    def database_binary_runrsf(self):
        return self.storge["database_binary_runrsf"]

    @property
    def database_binary_d3thdt(self):
        return self.storge["database_binary_d3thdt"]

    @property
    def control_hourglass(self):
        return self.storge["control_hourglass"]

    @property
    def mat_add_damage_gissmo(self):
        return self.storge["mat_add_damage_gissmo"]

    @property
    def contact_single_edge_id(self):
        return self.storge["contact_single_edge_id"]

    # for fea parser
    @property
    def keyword(self):
        return self.storge["keyword"]

    @property
    def parameter(self):
        return self.storge["parameter"]

    @property
    def node(self):
        return self.storge["node"]

    @property
    def element_shell(self):
        return self.storge["element_shell"]

    @property
    def element_solid(self):
        return self.storge["element_solid"]

    @property
    def part(self):
        return self.storge["part"]

    @property
    def material(self):
        return self.storge["material"]

    @property
    def section_shell(self):
        return self.storge["section_shell"]

    @property
    def section_solid(self):
        return self.storge["section_solid"]

    @property
    def section_beam(self):
        return self.storge["section_beam"]

    @property
    def hourglass(self):
        return self.storge["hourglass"]

    @property
    def set_node_list(self):
        return self.storge["set_node_list"]

    @property
    def set_shell_list(self):
        return self.storge["set_shell_list"]

    @property
    def set_part_list(self):
        return self.storge["set_part_list"]

    @property
    def database_history_node(self):
        return self.storge["database_history_node"]

    @property
    def define_curve(self):
        return self.storge["define_curve"]

    @property
    def define_table(self):
        return self.storge["define_table"]

    @property
    def mat_add_erosion(self):
        return self.storge["mat_add_erosion"]

    @property
    def constrained_extra_nodes_set(self):
        return self.storge["constrained_extra_nodes_set"]

    @property
    def constrained_nodal_rigid_body(self):
        return self.storge["constrained_nodal_rigid_body"]

    @property
    def database_cross_section_plane_id(self):
        return self.storge["database_cross_section_plane_id"]

    @property
    def contact_automatic_surface_to_surface_id(self):
        return self.storge["contact_automatic_surface_to_surface_id"]

    @property
    def contact_automatic_single_surface_id(self):
        return self.storge["contact_automatic_single_surface_id"]

    @property
    def initial_velocity_generation(self):
        return self.storge["initial_velocity_generation"]

    @property
    def boundary_prescribed_motion_rigid(self):
        return self.storge["boundary_prescribed_motion_rigid"]

    @property
    def title(self):
        return self.storge["title"]

    @property
    def database_deforc(self):
        return self.storge["database_deforc"]

    @property
    def database_jntforc(self):
        return self.storge["database_jntforc"]

    @property
    def database_format(self):
        return self.storge["database_format"]

    @property
    def control_shell(self):
        return self.storge["control_shell"]

    @property
    def control_termination(self):
        return self.storge["control_termination"]

    @property
    def control_rigid(self):
        return self.storge["control_rigid"]

    @property
    def database_swforc(self):
        return self.storge["database_swforc"]

    @property
    def control_solid(self):
        return self.storge["control_solid"]

    @property
    def database_extent_binary(self):
        return self.storge["database_extent_binary"]

    @property
    def control_timestep(self):
        return self.storge["control_timestep"]

    @property
    def database_dcfail(self):
        return self.storge["database_dcfail"]

    @property
    def database_nodout(self):
        return self.storge["database_nodout"]

    @property
    def database_abstat(self):
        return self.storge["database_abstat"]

    @property
    def database_binary_d3plot(self):
        return self.storge["database_binary_d3plot"]

    @property
    def database_elout(self):
        return self.storge["database_elout"]

    @property
    def control_output(self):
        return self.storge["control_output"]

    @property
    def control_accuracy(self):
        return self.storge["control_accuracy"]

    @property
    def database_binary_intfor(self):
        return self.storge["database_binary_intfor"]

    @property
    def database_matsum(self):
        return self.storge["database_matsum"]

    @property
    def control_parallel(self):
        return self.storge["control_parallel"]

    @property
    def control_contact(self):
        return self.storge["control_contact"]

    @property
    def database_disbout(self):
        return self.storge["database_disbout"]

    @property
    def database_glstat(self):
        return self.storge["database_glstat"]

    @property
    def database_sleout(self):
        return self.storge["database_sleout"]

    @property
    def database_rcforc(self):
        return self.storge["database_rcforc"]

    @property
    def control_bulk_viscosity(self):
        return self.storge["control_bulk_viscosity"]

    @property
    def control_solution(self):
        return self.storge["control_solution"]

    @property
    def database_secforc(self):
        return self.storge["database_secforc"]

    @property
    def control_energy(self):
        return self.storge["control_energy"]

    @property
    def control_dynamic_relaxation(self):
        return self.storge["control_dynamic_relaxation"]

    @property
    def database_sbtout(self):
        return self.storge["database_sbtout"]

    @property
    def database_rwforc(self):
        return self.storge["database_rwforc"]

    @property
    def contact_tied_nodes_to_surface_id(self):
        return self.storge["contact_tied_nodes_to_surface_id"]

    @property
    def end(self):
        return self.storge["end"]

    # for nn model data
    # tensor
    @property
    def node_tensor(self):
        return self.storge_tensor["node"]

    @property
    def element_shell_tensor(self):
        return self.storge_tensor["element_shell"]

    @property
    def element_solid_tensor(self):
        return self.storge_tensor["element_solid"]

    @property
    def element_solid_surface_tensor(self):
        """
        format: [[-1, pid, n1, n2, n3, n4], [-1, pid, n1, n2, n3, n4], [-1, pid, n1, n2, n3, n4], ...]
        """
        return self.storge_tensor["element_solid_surface"]

    @property
    def part_tensor(self):
        return self.storge_tensor["part"]

    @property
    def part_name_mapping(self):
        m_dict = {}

        for pid, part in self.storge["part"].items():
            m_dict[pid] = part.name.lower()

        return m_dict


dataframe = DataFrame()
