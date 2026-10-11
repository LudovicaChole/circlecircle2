"""Write shared contact, coupling, set and node-history data as LS-DYNA cards."""
from core.fea.translator import Translator
from core.fea.model.lsdyna.set_node_list import SetNodeList
from .card_fields import card


class InteractionTranslator(Translator):
    def translate(self, version):
        df, lines = self.dataframe, []
        from .contact_sets import prepare_contact_sets
        segment_ids = prepare_contact_sets(df)
        for sid, obj in df.set_segment.items():
            if sid not in segment_ids:
                continue
            lines += ['*SET_SEGMENT_TITLE\n', obj.name+'\n', card((sid,))]
            lines += [card((*face, face[-1])) if len(face)==3 else card(face) for face in obj.segments]
        for key, keyword in (('set_part_list','*SET_PART_LIST'), ('set_shell_list','*SET_SHELL_LIST'), ('set_solid_list','*SET_SOLID_LIST')):
            for sid, obj in df.storge[key].items():
                lines += [keyword+'_TITLE\n', obj.name+'\n', card((sid,))]
                lines += [card(obj.ids[i:i+8]) for i in range(0,len(obj.ids),8)]
        for obj in df.constrained_nodal_rigid_body.values():
            if getattr(obj,'material_rigidized',False):
                continue
            lines += ['*CONSTRAINED_NODAL_RIGID_BODY\n', card((obj.pid,obj.cid,obj.sid,obj.pnode,
                                                          obj.iprt,obj.drflag,obj.rrflag))]
        for obj in df.constrained_extra_nodes_set.values():
            lines += ['*CONSTRAINED_EXTRA_NODES_SET\n', card((obj.pid,obj.nsid,obj.iflag))]
        for store, keyword in ((df.contact_automatic_surface_to_surface_id, '*CONTACT_AUTOMATIC_SURFACE_TO_SURFACE_ID'),
                               (df.contact_automatic_single_surface_id, '*CONTACT_AUTOMATIC_SINGLE_SURFACE_ID')):
            for obj in store.values():
                lines += [keyword+'\n', card((obj.uid,))+ '']
                # ID option permits a free-text heading after the I10 ID.
                lines[-1] = card((obj.uid,)).rstrip('\n') + str(obj.heading) + '\n'
                lines += [card(tuple(getattr(obj,k) for k in ('ssid','msid','sstyp','mstyp','sboxid','mboxid','spr','mpr'))),
                          card(tuple(getattr(obj,k) for k in ('fs','fd','dc','vc','vdc','penchk','bt','dt'))),
                          card(tuple(getattr(obj,k) for k in ('sfs','sfm','sst','mst','sfst','sfmt','fsf','vsf')))]
        for obj in df.storge['surface_ties'].values():
            if obj.master.sid is None:
                raise ValueError(f'TIE {obj.name}: master must be an element surface')
            sid = max(df.set_node_list,default=0)+1
            group = SetNodeList(uid=sid, name=obj.name+'_slave')
            group.ids = obj.slave.nodes
            df.set_node_list[sid] = group
            lines += ['*SET_NODE_LIST_TITLE\n', group.name+'\n',card((sid,))]
            lines += [card(group.ids[i:i+8]) for i in range(0,len(group.ids),8)]
            cid = max(set(df.contact_automatic_surface_to_surface_id)|set(df.contact_automatic_single_surface_id),default=0)+obj.uid
            lines += ['*CONTACT_TIED_NODES_TO_SURFACE_OFFSET_ID\n',card((cid,)).rstrip('\n')+obj.name+'\n',
                      card((sid,obj.master.sid,4,0,0,0,0,0)),card((0,0,0,0,0,0,0,1e20)),
                      card((0,0,-obj.tolerance,-obj.tolerance,0,0,0,0))]
        nodes = sorted({int(n) for group in df.database_history_node.values() for n in group.ids})
        if nodes:
            lines += ['*DATABASE_HISTORY_NODE\n']+[card(nodes[i:i+8]) for i in range(0,len(nodes),8)]
        df.output_storge['*INTERACTIONS'] = lines
