import logging
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as Obj

logging.getLogger('user_logger').addHandler(logging.NullHandler())
from core.fea.dataframe import dataframe as df
from core.fea.lsdyna.lsdyna import LsDyna
from core.fea.lsdyna.parser.element_mass_parser import ElementMassParser
from core.fea.lsdyna.parser.mat_piecewise_linear_plasticity_parser import MatPiecewiseLinearPlasticityParser
from core.fea.lsdyna.parser.set_part_list_collect_title_parser import SetPartListCollectTitleParser
from core.fea.lsdyna.parser.boundary_prescribed_motion_rigid_parser import BoundaryPrescribedMotionRigidParser
from core.fea.lsdyna.keywords.initial_velocity_generation import InitialVelocityGeneration
from core.fea.abaqus.translator.analysis_data import velocity_field, rigid_dofs, curve_points
from core.fea.abaqus.translator.step_translator import StepTranslator
from core.fea.abaqus.translator.initial_state_translator import InitialStateTranslator
from core.fea.pamcrash.translator.mtoco_translator import MtocoTranslator
from core.fea.pamcrash.translator.cntac33_translator import Cntac33Translator
from core.fea.pamcrash.translator.cntac36_translator import Cntac36Translator
from core.fea.pamcrash.translator.cntac43_translator import Cntac43Translator
from core.fea.pamcrash.translator.group_translator import GroupTranslator
from services.fea_material_generator import MaterialGenerator


def card(*values):
    return ''.join(str(v).rjust(10) for v in values) + '\n'


class DebugRequirementsTests(unittest.TestCase):
    def setUp(self):
        df.reset()
        self.addCleanup(df.reset)

    def test_all_requested_keywords_registered_and_real_material_30(self):
        source = Path(__file__).resolve().parents[1] / 'Test_Items/data3.k'
        parser = LsDyna()
        parser.parse(file_path=str(source),version='12.0')
        self.assertFalse(parser.not_support_keywords)
        self.assertIn(30, df.material)
        self.assertEqual(df.material[30].lcss,28)
        self.assertEqual(df.material[30].name,'HC340-590DP')
        self.assertIn(1820050,df.storge['mat_add_damage_gissmo'])
        self.assertTrue(df.storge['contact_single_edge_id'])

    def test_mass_fixed_width_and_free_format(self):
        parser=ElementMassParser()
        parser.parse(f'{2:8d}{18001461:8d}{100.0:16g}{1800018:8d}\n','12.0')
        mass=df.storge['element_mass'][2]
        self.assertEqual((mass.nid,mass.mass,mass.pid),(18001461,100,1800018))
        parser.parse('3, 42, 1.2D+2, 7\n','12.0')
        self.assertEqual(df.storge['element_mass'][3].mass,120)

    def test_mat24_lcsr_and_optional_blank_cards(self):
        parser=MatPiecewiseLinearPlasticityParser()
        parser.parse('30, 7.8e-9, 210000, .3, 200\n','12.0')
        parser.parse('1, 2, 28, 29, 0, 30\n','12.0')
        self.assertEqual(df.material[30].lcsr,29)
        self.assertEqual(df.material[30].lcss,28)

    def test_collect_appends_and_deduplicates(self):
        parser=SetPartListCollectTitleParser()
        for values in ((1,2),(2,3)):
            parser.reset()
            for line in ('assembly\n',card(5),card(*values)):
                parser.parse(line,'12.0')
        self.assertEqual(df.set_part_list[5].ids,[1,2,3])

    def prepare_velocity(self):
        df.node.update({1:Obj(xyz=(0,0,0)),2:Obj(xyz=(1,0,0))})
        df.set_node_list[10]=Obj(ids=[1,2])
        df.initial_velocity_generation[1]=InitialVelocityGeneration(uid=1,pid=10,styp=3,vx=4)
        df.storge.setdefault('element_mass',{})[7]=Obj(uid=7,nid=1,mass=3,pid=0)
        df.control_termination[1]=Obj(endtim=100)

    def test_energy_is_half_mv_squared_not_velocity_times_duration(self):
        self.prepare_velocity()
        lines=''.join(StepTranslator().translate('6.14'))
        self.assertIn('*DYNAMIC, EXPLICIT\n, 100\n',lines)
        self.assertIn('ELEMENT_MASS only) = 24',lines)
        self.assertIn('excludes shell/solid',lines)
        InitialStateTranslator().translate('6.14')
        model=''.join(df.output_storge['*INITIAL_STATE'])
        self.assertIn('*MASS, ELSET=dyna_mass_7\n3\n',model)
        self.assertIn('1, 1, 4\n',model)

    def test_mass_collision_and_velocity_replacement(self):
        self.prepare_velocity()
        df.element_shell[7]=Obj()
        df.initial_velocity_generation[2]=InitialVelocityGeneration(uid=2,pid=10,styp=3,vx=6)
        self.assertEqual(velocity_field(df)[1][0],6)
        InitialStateTranslator().translate('6.14')
        self.assertIn('ELSET=dyna_mass_8',''.join(df.output_storge['*INITIAL_STATE']))

    def test_rotating_velocity(self):
        self.prepare_velocity()
        v=df.initial_velocity_generation[1]
        v.vx=0
        v.omega=2
        v.nz=1
        self.assertEqual(velocity_field(df)[2][:3],(0,2,0))

    def test_missing_velocity_selection_is_explicit_error(self):
        df.initial_velocity_generation[1]=InitialVelocityGeneration(uid=1,pid=99,styp=1,vx=4)
        with self.assertRaisesRegex(ValueError,'missing SET_PART 99'):
            velocity_field(df)

    def test_rigid_motion_rotation_sf_and_curve(self):
        parser=BoundaryPrescribedMotionRigidParser()
        parser.parse(card(15,5,2,20,2),'12.0')
        df.part[15]=Obj(mid=7)
        df.material[7]=Obj(uid=7,tag='rigid',cmo=1,con1=7,con2=0)
        df.storge_rigid_part_reference_node[15]=100
        df.define_curve[20]=Obj(uid=20,sfa=1,sfo=2,offa=0,offo=0,a1=[0,10],o1=[0,3])
        df.control_termination[1]=Obj(endtim=10)
        text=''.join(StepTranslator().translate('6.14'))
        self.assertIn('100, 4, 4, 2',text)
        self.assertIn('10, 6',text)
        self.assertIn('TYPE=DISPLACEMENT',text)
        self.assertLess(text.index('*AMPLITUDE'),text.index('*STEP,'))

    def test_local_mask_global_system(self):
        self.assertEqual(rigid_dofs(Obj(uid=1,cmo=-1,con1=0,con2=101111)),{1,3,4,5,6})
        self.assertFalse(rigid_dofs(Obj(uid=1,cmo=0,con1=7,con2=7)))

    def test_curve_offsets_precede_scaling(self):
        curve=Obj(uid=1,sfa=2,sfo=3,offa=1,offo=4,a1=[0,1],o1=[2,3],dattyp=1)
        self.assertEqual(curve_points(curve),[(2,18),(4,21)])

    def test_hypermesh_set_name_is_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'names.k'
            path.write_text('*KEYWORD\n*SET_PART_LIST\n$HMNAME SETS      13Crash_Box\n'+card(13)+card(1,2)+'*END\n')
            LsDyna().parse(file_path=str(path),version='12.0')
            self.assertEqual(df.set_part_list[13].name,'Crash_Box')

    def test_all_imported_material_templates_parse(self):
        templates=MaterialGenerator().lsdyna_material
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'material.k'
            for name,text in templates.items():
                if not name.startswith('data'):
                    continue
                with self.subTest(name=name):
                    df.reset()
                    path.write_text('*KEYWORD\n'+text.replace('{material_id}',f'{999:10d}').replace('{material_name}','sample')+'*END\n',encoding='utf-8')
                    parser=LsDyna()
                    parser.parse(file_path=str(path),version='12.0')
                    self.assertIn(999,df.material)
                    self.assertFalse(parser.not_support_keywords)

    def test_mtoco_expands_set_and_preserves_pid(self):
        df.node.update({n:Obj() for n in (10,11,12)})
        df.set_node_list[5]=Obj(ids=[10,11,12])
        df.constrained_nodal_rigid_body[1]=Obj(uid=1,pid=26817,cid=0,sid=5,pnode=10,drflag=0,rrflag=0,name='rigid')
        MtocoTranslator().translate('2023')
        text=''.join(df.output_storge['MTOCO'])
        self.assertIn('MTOCO /    26817      10  111111',text)
        self.assertIn('NOD           11      12',text)
        self.assertNotIn('NOD            5',text)

    def test_contact_types_groups_and_unique_ids(self):
        df.part.update({1:Obj(),2:Obj()})
        df.set_part_list[1]=Obj(ids=[1,2],name='all_part')
        df.set_node_list[1]=Obj(ids=[10],name='all_part')
        df.contact_automatic_single_surface_id[5]=Obj(uid=5,heading='self',ssid=1,sstyp=2,sboxid=0,mboxid=0,bt=0,dt=0,fs=.2,fd=.3)
        df.contact_automatic_surface_to_surface_id[6]=Obj(uid=6,heading='pair',ssid=1,sstyp=2,msid=2,mstyp=3,sboxid=0,mboxid=0,bt=0,dt=0,fs=.2,fd=.3)
        for translator in (GroupTranslator(),Cntac33Translator(),Cntac36Translator(),Cntac43Translator()):
            translator.translate('2023')
        headers=[line for key in ('CNTAC33','CNTAC36','CNTAC43') for line in df.output_storge[key] if line.startswith('CNTAC /')]
        self.assertEqual({int(line[8:16]) for line in headers},{5,6,7})
        self.assertEqual({int(line[16:24]) for line in headers},{33,36,43})
        self.assertIn("GRP 'all_part_part_1'",''.join(df.output_storge['CNTAC43']))
        self.assertIn('CONST            0.3',''.join(df.output_storge['CNTAC36']))
        self.assertIn('all_part_node_1',''.join(df.output_storge['GROUP']))

    def test_source_material_templates_have_dependencies(self):
        templates=MaterialGenerator().lsdyna_material
        self.assertIn('data3_mat_30',templates)
        text=templates['data3_mat_30']
        self.assertIn('{material_id}',text)
        self.assertIn('*DEFINE_CURVE',text)
        self.assertIn('{material_name}',text)


if __name__ == '__main__':
    unittest.main()
