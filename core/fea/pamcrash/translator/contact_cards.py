from core.fea.translator import Translator
from .selection import field, resolve


class ContactCards(Translator):
    contact_type = 36

    def translate(self, version):
        df = self.dataframe
        source = df.contact_automatic_surface_to_surface_id if self.contact_type == 33 else df.contact_automatic_single_surface_id
        # Allocate type-43 IDs above every existing source contact ID.
        used = set(df.contact_automatic_surface_to_surface_id) | set(df.contact_automatic_single_surface_id) | set(df.storge.get('contact_single_edge_id',{}))
        next_id = max(used, default=0) + 1
        lines = []
        for index,(cid,obj) in enumerate(source.items()):
            if obj.sboxid or obj.mboxid:
                raise ValueError(f'Contact {cid}: box filtering is not implemented')
            coefficient = max(float(obj.fs),float(obj.fd))
            if min(float(obj.fs),float(obj.fd)) < 0:
                raise ValueError(f'Contact {cid}: friction curve requires nonconstant conversion')
            target = next_id+index if self.contact_type == 43 else cid
            lines += [f'$ Source contact {cid}; PAM layout based on supplied examples, 2023 manual not verified.\n',
                      'CNTAC / '+field(target)+field(self.contact_type)+'\n',f'NAME {obj.heading}\n',
                      '$#    T1SL      T2SL     ISENS     HcontITPRT\n',
                      ''.join(field(v,10) for v in (obj.bt,obj.dt,0,0.1))+field(2,5)+'\n',
                      '$#IPC    SLFACM     FSVNL\n',field(0,5)+field(0.0,10)+field(0.0,10)+'\n',
                      '$#FRITYP       VALUE     XDMP1\n','CONST     '+field(coefficient,10)+field(0.0,10)+'\n']
            if self.contact_type == 43:
                lines += ['$#         IRMVIAC32               IFRED\n','          '+field(2,5)+field(0,5)+'\n',
                          '\n','$#                                                                         IPRES\n',' '*79+'0\n']
            else:
                lines += ['$#IRMIERODILEAKIAC32               IFRED   DTHKPLK\n',field(2,5)+' '*5+field(0,5)+field(0,5)+'\n']
                if self.contact_type == 33:
                    lines += ['$#            SEPSTR    SEPTHK IUPA\n',' '*35+'\n']
                else:
                    lines.append('\n')
                lines += ['$#                                                TSCAL                    IPRES\n',' '*80+'\n']
            lines.extend(resolve(df,obj.ssid,obj.sstyp))
            if self.contact_type == 33:
                lines.extend(resolve(df,obj.msid,obj.mstyp))
            elif self.contact_type == 43:
                lines.extend(resolve(df,obj.ssid,obj.sstyp))
        df.output_storge[f'CNTAC{self.contact_type}'] = lines
