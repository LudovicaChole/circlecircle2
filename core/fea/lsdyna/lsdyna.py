import re
from core.fea.lsdyna.parser.set_solid_list_parser import SetSolidListParser
from core.fea.lsdyna.parser.set_solid_list_title_parser import SetSolidListTitleParser
from core.fea.lsdyna.parser.database_nodfor_parser import DatabaseNodforParser
from core.fea.lsdyna.parser.database_spcforc_parser import DatabaseSpcforcParser
from core.fea.lsdyna.parser.control_hourglass_parser import ControlHourglassParser
from core.fea.lsdyna.parser.database_binary_d3dump_parser import DatabaseBinaryD3DumpParser
from core.fea.lsdyna.parser.database_binary_runrsf_parser import DatabaseBinaryRunrsfParser
from core.fea.lsdyna.parser.database_binary_d3thdt_parser import DatabaseBinaryD3ThdtParser
from core.fea.lsdyna.parser.mat_piecewise_linear_plasticity_parser import MatPiecewiseLinearPlasticityParser
from core.fea.lsdyna.parser.mat_piecewise_linear_plasticity_title_parser import MatPiecewiseLinearPlasticityTitleParser
from core.fea.lsdyna.parser.element_mass_parser import ElementMassParser
from core.fea.lsdyna.parser.mat_add_damage_gissmo_title_parser import MatAddDamageGissmoTitleParser
from core.fea.lsdyna.parser.set_part_list_collect_title_parser import SetPartListCollectTitleParser
from core.fea.lsdyna.parser.contact_single_edge_id_parser import ContactSingleEdgeIDParser
from utilities.logger import logger
from core.fea.lsdyna.parser.set_segment_parser import SetSegmentParser
from core.fea.solver import Solver
from core.fea.lsdyna.parser.keyword_parser import KeyWordParser
from core.fea.lsdyna.parser.parameter_parser import ParameterParser
from core.fea.lsdyna.parser.node_parser import NodeParser
from core.fea.lsdyna.parser.element_shell_parser import ElementShellParser
from core.fea.lsdyna.parser.element_solid_parser import ElementSolidParser
from core.fea.lsdyna.parser.part_parser import PartParser
from core.fea.lsdyna.parser.part_inertia_parser import PartInertiaParser
from core.fea.lsdyna.parser.section_shell_parser import SectionShellParser
from core.fea.lsdyna.parser.section_shell_title_parser import SectionShellTitleParser
from core.fea.lsdyna.parser.section_solid_parser import SectionSolidParser
from core.fea.lsdyna.parser.section_solid_title_parser import SectionSolidTitleParser
from core.fea.lsdyna.parser.hourglass_parser import HourglassParser
from core.fea.lsdyna.parser.hourglass_title_parser import HourglassTitleParser
from core.fea.lsdyna.parser.set_node_list_parser import SetNodeListParser
from core.fea.lsdyna.parser.set_node_list_title_parser import SetNodeListTitleParser
from core.fea.lsdyna.parser.set_shell_list_parser import SetShellListParser
from core.fea.lsdyna.parser.set_shell_list_title_parser import SetShellListTitleParser
from core.fea.lsdyna.parser.set_part_list_parser import SetPartListParser
from core.fea.lsdyna.parser.set_part_list_title_parser import SetPartListTitleParser
from core.fea.lsdyna.parser.set_part_list_generate_parser import SetPartListGenerateParser
from core.fea.lsdyna.parser.database_history_node_parser import DatabaseHistoryNodeParser
from core.fea.lsdyna.parser.database_history_node_title_parser import DatabaseHistoryNodeTitleParser
from core.fea.lsdyna.parser.mat_elastic_parser import MatElasticParser
from core.fea.lsdyna.parser.mat_elastic_title_parser import MatElasticTitleParser
from core.fea.lsdyna.parser.mat_rigid_parser import MatRigidParser
from core.fea.lsdyna.parser.mat_rigid_title_parser import MatRigidTitleParser
from core.fea.lsdyna.parser.mat_piecewise_linear_plasticity_log_interpolation_parser import MatPiecewiseLinearPlasticityLogInterpolationParser
from core.fea.lsdyna.parser.mat_piecewise_linear_plasticity_log_interpolation_title_parser import MatPiecewiseLinearPlasticityLogInterpolationTitleParser
from core.fea.lsdyna.parser.mat_modified_piecewise_linear_plasticity_parser import MatModifiedPiecewiseLinearPlasticityParser
from core.fea.lsdyna.parser.mat_modified_piecewise_linear_plasticity_title_parser import MatModifiedPiecewiseLinearPlasticityTitleParser
from core.fea.lsdyna.parser.mat_barlat_yld2000_parser import MatBarlatYld2000Parser
from core.fea.lsdyna.parser.mat_barlat_yld2000_title_parser import MatBarlatYld2000TitleParser
from core.fea.lsdyna.parser.define_curve_parser import DefineCurveParser
from core.fea.lsdyna.parser.define_curve_title_parser import DefineCurveTitleParser
from core.fea.lsdyna.parser.define_table_parser import DefineTableParser
from core.fea.lsdyna.parser.define_table_title_parser import DefineTableTitleParser
from core.fea.lsdyna.parser.define_table_2d_parser import DefineTable2DParser
from core.fea.lsdyna.parser.define_table_2d_title_parser import DefineTable2DTitleParser
from core.fea.lsdyna.parser.mat_add_erosion_parser import MatAddErosionParser
from core.fea.lsdyna.parser.mat_add_erosion_title_parser import MatAddErosionTitleParser
from core.fea.lsdyna.parser.constrained_extra_nodes_set_parser import ConstrainedExtraNodesSetParser
from core.fea.lsdyna.parser.constrained_extra_nodes_set_title_parser import ConstrainedExtraNodesSetTitleParser
from core.fea.lsdyna.parser.constrained_nodal_rigid_body_parser import ConstrainedNodalRigidBodyParser
from core.fea.lsdyna.parser.constrained_nodal_rigid_body_title_parser import ConstrainedNodalRigidBodyTitleParser
from core.fea.lsdyna.parser.database_cross_section_plane_id_parser import DatabaseCrossSectionPlaneIDParser
from core.fea.lsdyna.parser.contact_automatic_surface_to_surface_id_parser import ContactAutomaticSurfaceToSurfaceIDParser
from core.fea.lsdyna.parser.contact_automatic_surface_to_surface_id_title_parser import ContactAutomaticSurfaceToSurfaceIDTitleParser
from core.fea.lsdyna.parser.contact_automatic_single_surface_id_parser import ContactAutomaticSingleSurfaceIDParser
from core.fea.lsdyna.parser.contact_automatic_single_surface_id_title_parser import ContactAutomaticSingleSurfaceIDTitleParser
from core.fea.lsdyna.parser.initial_velocity_generation_parser import InitialVelocityGenerationParser
from core.fea.lsdyna.parser.initial_velocity_generation_title_parser import InitialVelocityGenerationTitleParser
from core.fea.lsdyna.parser.boundary_prescribed_motion_rigid_parser import BoundaryPrescribedMotionRigidParser
from core.fea.lsdyna.parser.title_parser import TitleParser
from core.fea.lsdyna.parser.database_deforc_parser import DatabaseDeforcParser
from core.fea.lsdyna.parser.database_jntforc_parser import DatabaseJntforcParser
from core.fea.lsdyna.parser.database_format_parser import DatabaseFormatParser
from core.fea.lsdyna.parser.control_shell_parser import ControlShellParser
from core.fea.lsdyna.parser.database_abstat_parser import DatabaseAbstatParser
from core.fea.lsdyna.parser.database_swforc_parser import DatabaseSwforcParser
from core.fea.lsdyna.parser.database_rwforc_parser import DatabaseRwforcParser
from core.fea.lsdyna.parser.database_sleout_parser import DatabaseSleoutParser
from core.fea.lsdyna.parser.database_elout_parser import DatabaseEloutParser
from core.fea.lsdyna.parser.database_matsum_parser import DatabaseMatsumParser
from core.fea.lsdyna.parser.database_nodout_parser import DatabaseNodoutParser
from core.fea.lsdyna.parser.database_binary_intfor_parser import DatabaseBinaryIntforParser
from core.fea.lsdyna.parser.control_dynamic_relaxation_parser import ControlDynamicRelaxationParser
from core.fea.lsdyna.parser.contact_tied_nodes_to_surface_offset_id_parser import ContactTiedNodesToSurfaceOffsetIDParser
from core.fea.lsdyna.parser.control_bulk_viscosity_parser import ControlBulkViscosityParser
from core.fea.lsdyna.parser.control_output_parser import ControlOutputParser
from core.fea.lsdyna.parser.control_parallel_parser import ControlParallelParser
from core.fea.lsdyna.parser.database_disbout_parser import DatabaseDisboutParser
from core.fea.lsdyna.parser.control_rigid_parser import ControlRigidParser
from core.fea.lsdyna.parser.control_solid_parser import ControlSolidParser
from core.fea.lsdyna.parser.database_extent_binary_parser import DatabaseExtentBinaryParser
from core.fea.lsdyna.parser.database_rcforc_parser import DatabaseRcforcParser
from core.fea.lsdyna.parser.control_solution_parser import ControlSolutionParser
from core.fea.lsdyna.parser.control_timestep_parser import ControlTimestepParser
from core.fea.lsdyna.parser.database_sbtout_parser import DatabaseSbtoutParser
from core.fea.lsdyna.parser.control_contact_parser import ControlContactParser
from core.fea.lsdyna.parser.database_binary_d3plot_parser import DatabaseBinaryD3plotParser
from core.fea.lsdyna.parser.control_energy_parser import ControlEnergyParser
from core.fea.lsdyna.parser.database_secforc_parser import DatabaseSecforcParser
from core.fea.lsdyna.parser.database_glstat_parser import DatabaseGlstatParser
from core.fea.lsdyna.parser.database_dcfail_parser import DatabaseDcfailParser
from core.fea.lsdyna.parser.control_accuracy_parser import ControlAccuracyParser
from core.fea.lsdyna.parser.control_termination_parser import ControlTerminationParser
from core.fea.lsdyna.parser.end_parser import EndParser


class LsDyna(Solver):
    def __init__(self):
        self.logger = logger

        # must parse first, and only one keyword: *PARAMETER
        self.parse_keywords_initial = {
            "*PARAMETER": ParameterParser(),
        }

        self.parse_keywords_1 = {
            "*SET_SOLID_LIST": SetSolidListParser(),
            "*SET_SOLID_LIST_TITLE": SetSolidListTitleParser(),
            "*KEYWORD": KeyWordParser(),
            "*NODE": NodeParser(),
            "*SECTION_SHELL": SectionShellParser(),
            "*SECTION_SHELL_TITLE": SectionShellTitleParser(),
            "*SECTION_SOLID": SectionSolidParser(),
            "*SECTION_SOLID_TITLE": SectionSolidTitleParser(),
            "*HOURGLASS": HourglassParser(),
            "*HOURGLASS_TITLE": HourglassTitleParser(),
            "*SET_NODE_LIST": SetNodeListParser(),
            "*SET_NODE_LIST_TITLE": SetNodeListTitleParser(),
            "*SET_SEGMENT": SetSegmentParser(),
            "*SET_SEGMENT_TITLE": SetSegmentParser(title=True),
            "*SET_SHELL_LIST": SetShellListParser(),
            "*SET_SHELL_LIST_TITLE": SetShellListTitleParser(),
            "*SET_PART_LIST": SetPartListParser(),
            "*SET_PART_LIST_TITLE": SetPartListTitleParser(),
            "*SET_PART_LIST_GENERATE": SetPartListGenerateParser(),
            "*DATABASE_HISTORY_NODE": DatabaseHistoryNodeParser(),
            "*DATABASE_HISTORY_NODE_TITLE": DatabaseHistoryNodeTitleParser(),
            "*DEFINE_CURVE": DefineCurveParser(),
            "*DEFINE_CURVE_TITLE": DefineCurveTitleParser(),
            "*DEFINE_TABLE": DefineTableParser(),
            "*DEFINE_TABLE_TITLE": DefineTableTitleParser(),
            "*DEFINE_TABLE_2D": DefineTable2DParser(),
            "*DEFINE_TABLE_2D_TITLE": DefineTable2DTitleParser(),
            "*INITIAL_VELOCITY_GENERATION": InitialVelocityGenerationParser(),
            "*INITIAL_VELOCITY_GENERATION_TITLE": InitialVelocityGenerationTitleParser(),
            "*BOUNDARY_PRESCRIBED_MOTION_RIGID": BoundaryPrescribedMotionRigidParser(),
            "*TITLE": TitleParser(),
            "*DATABASE_DEFORC": DatabaseDeforcParser(),
            "*DATABASE_JNTFORC": DatabaseJntforcParser(),
            "*DATABASE_FORMAT": DatabaseFormatParser(),
            "*CONTROL_SHELL": ControlShellParser(),
            "*DATABASE_ABSTAT": DatabaseAbstatParser(),
            "*DATABASE_SWFORC": DatabaseSwforcParser(),
            "*DATABASE_RWFORC": DatabaseRwforcParser(),
            "*DATABASE_SLEOUT": DatabaseSleoutParser(),
            "*DATABASE_ELOUT": DatabaseEloutParser(),
            "*DATABASE_MATSUM": DatabaseMatsumParser(),
            "*DATABASE_NODOUT": DatabaseNodoutParser(),
            "*DATABASE_BINARY_INTFOR": DatabaseBinaryIntforParser(),
            "*CONTROL_DYNAMIC_RELAXATION": ControlDynamicRelaxationParser(),
            "*CONTROL_BULK_VISCOSITY": ControlBulkViscosityParser(),
            "*CONTROL_OUTPUT": ControlOutputParser(),
            "*CONTROL_PARALLEL": ControlParallelParser(),
            "*DATABASE_DISBOUT": DatabaseDisboutParser(),
            "*CONTROL_RIGID": ControlRigidParser(),
            "*CONTROL_SOLID": ControlSolidParser(),
            "*DATABASE_EXTENT_BINARY": DatabaseExtentBinaryParser(),
            "*DATABASE_RCFORC": DatabaseRcforcParser(),
            "*CONTROL_SOLUTION": ControlSolutionParser(),
            "*CONTROL_TIMESTEP": ControlTimestepParser(),
            "*DATABASE_SBTOUT": DatabaseSbtoutParser(),
            "*CONTROL_CONTACT": ControlContactParser(),
            "*DATABASE_BINARY_D3PLOT": DatabaseBinaryD3plotParser(),
            "*CONTROL_ENERGY": ControlEnergyParser(),
            "*DATABASE_SECFORC": DatabaseSecforcParser(),
            "*DATABASE_GLSTAT": DatabaseGlstatParser(),
            "*DATABASE_DCFAIL": DatabaseDcfailParser(),
            "*CONTROL_ACCURACY": ControlAccuracyParser(),
            "*CONTROL_TERMINATION": ControlTerminationParser(),
            "*END": EndParser(),
        }

        self.parse_keywords_2 = {
            "*ELEMENT_SHELL": ElementShellParser(),
            "*ELEMENT_SOLID": ElementSolidParser(),
            "*PART": PartParser(),
            "*PART_INERTIA": PartInertiaParser(),
            "*MAT_ELASTIC": MatElasticParser(),
            "*MAT_ELASTIC_TITLE": MatElasticTitleParser(),
            "*MAT_RIGID": MatRigidParser(),
            "*MAT_RIGID_TITLE": MatRigidTitleParser(),
            "*MAT_PIECEWISE_LINEAR_PLASTICITY_LOG_INTERPOLATION": MatPiecewiseLinearPlasticityLogInterpolationParser(),
            "*MAT_PIECEWISE_LINEAR_PLASTICITY_LOG_INTERPOLATION_TITLE": MatPiecewiseLinearPlasticityLogInterpolationTitleParser(),
            "*MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY": MatModifiedPiecewiseLinearPlasticityParser(),
            "*MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY_TITLE": MatModifiedPiecewiseLinearPlasticityTitleParser(),
            "*MAT_BARLAT_YLD2000": MatBarlatYld2000Parser(),
            "*MAT_BARLAT_YLD2000_TITLE": MatBarlatYld2000TitleParser(),
            "*MAT_ADD_EROSION": MatAddErosionParser(),
            "*MAT_ADD_EROSION_TITLE": MatAddErosionTitleParser(),
            "*CONSTRAINED_EXTRA_NODES_SET": ConstrainedExtraNodesSetParser(),
            "*CONSTRAINED_EXTRA_NODES_SET_TITLE": ConstrainedExtraNodesSetTitleParser(),
            "*CONSTRAINED_NODAL_RIGID_BODY": ConstrainedNodalRigidBodyParser(),
            "*CONSTRAINED_NODAL_RIGID_BODY_TITLE": ConstrainedNodalRigidBodyTitleParser(),
            "*DATABASE_CROSS_SECTION_PLANE_ID": DatabaseCrossSectionPlaneIDParser(),
            "*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_ID": ContactAutomaticSurfaceToSurfaceIDParser(),
            "*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_ID_TITLE": ContactAutomaticSurfaceToSurfaceIDTitleParser(),
            "*CONTACT_AUTOMATIC_SINGLE_SURFACE_ID": ContactAutomaticSingleSurfaceIDParser(),
            "*CONTACT_AUTOMATIC_SINGLE_SURFACE_ID_TITLE": ContactAutomaticSingleSurfaceIDTitleParser(),
            "*CONTACT_TIED_NODES_TO_SURFACE_OFFSET_ID": ContactTiedNodesToSurfaceOffsetIDParser(),
        }
        self.parse_keywords_2.update({
            "*DATABASE_NODFOR": DatabaseNodforParser(),
            "*DATABASE_SPCFORC": DatabaseSpcforcParser(),
            "*CONTROL_HOURGLASS": ControlHourglassParser(),
            "*DATABASE_BINARY_D3DUMP": DatabaseBinaryD3DumpParser(),
            "*DATABASE_BINARY_RUNRSF": DatabaseBinaryRunrsfParser(),
            "*DATABASE_BINARY_D3THDT": DatabaseBinaryD3ThdtParser(),
            "*MAT_PIECEWISE_LINEAR_PLASTICITY": MatPiecewiseLinearPlasticityParser(),
            "*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE": MatPiecewiseLinearPlasticityTitleParser(),
            "*ELEMENT_MASS": ElementMassParser(),
            "*MAT_ADD_DAMAGE_GISSMO_TITLE": MatAddDamageGissmoTitleParser(),
            "*SET_PART_LIST_COLLECT_TITLE": SetPartListCollectTitleParser(),
            "*CONTACT_SINGLE_EDGE_ID": ContactSingleEdgeIDParser(),
            "*MAT_ADD_DAMAGE_GISSMO": MatAddDamageGissmoTitleParser(title=False),
        })
        self.parse_keywords_1["*SET_PART_LIST_COLLECT_TITLE"] = self.parse_keywords_2.pop("*SET_PART_LIST_COLLECT_TITLE")
        self.translate_keywords = {}
        self.not_support_keywords = set()

        self.current_parser = None

    def reset(self):
        self.current_parser = None
        self.not_support_keywords.clear()

    def parse_data(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)
        parse_keywords = kwargs.get("parse_keywords", args[2] if len(args) > 2 else None)

        if file_path:
            with open(file=file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                try:
                    set_label = None
                    for line in f:

                        if line.startswith('$'):
                            match = re.match(r'^\$HMNAME\s+SETS\s+(\d+)(.*)', line)
                            if match:
                                set_label = (int(match[1]),match[2].strip())
                            continue
                        if not line:
                            continue

                        if line.startswith("*"):
                            set_label = None
                            dyna_keyword = line.split()[0].strip().upper()

                            if dyna_keyword in parse_keywords:
                                self.current_parser = parse_keywords[dyna_keyword]
                                self.current_parser.reset()
                                continue
                            else:
                                if dyna_keyword in self.parse_keywords_initial:
                                    self.current_parser = None
                                    continue

                                elif dyna_keyword in self.parse_keywords_1:
                                    self.current_parser = None
                                    continue

                                elif dyna_keyword in self.parse_keywords_2:
                                    self.current_parser = None
                                    continue

                                else:
                                    self.not_support_keywords.add(dyna_keyword)
                                    self.current_parser = None
                                    continue

                        elif line.strip().strip("-") == "BEGIN PGP MESSAGE":
                            dyna_keyword = "BEGIN PGP MESSAGE"

                            if dyna_keyword in parse_keywords:
                                self.current_parser = parse_keywords[dyna_keyword]
                                continue
                            else:
                                self.current_parser = None
                                continue

                        elif line.strip().strip("-") == "END PGP MESSAGE":
                            self.current_parser = None
                            continue

                        else:
                            if self.current_parser is not None:
                                self.current_parser.parse(line_raw=line, version=version)
                                if set_label and dyna_keyword.startswith('*SET_'):
                                    family = dyna_keyword.split('_')[1].lower()
                                    store = self.current_parser.dataframe.storge.get(f'set_{family}_list',{})
                                    if set_label[0] in store and set_label[1]:
                                        store[set_label[0]].name = set_label[1]

                except Exception as e:
                    raise e

        else:
            self.logger.error(f"LS-DYNA PARSER ERROR: file_path cannot be empty\n")

    def parse(self, *args, **kwargs):
        file_path = kwargs.get("file_path", args[0] if len(args) > 0 else None)
        version = kwargs.get("version", args[1] if len(args) > 1 else None)

        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_initial)
        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_1)
        self.parse_data(file_path=file_path, version=version, parse_keywords=self.parse_keywords_2)

        for not_support_keyword in self.not_support_keywords:
            self.logger.warning(f"Ls-Dyna not support keywords: {not_support_keyword}")

    def translate(self, file_path):
        print(f"lsdyna translate")
