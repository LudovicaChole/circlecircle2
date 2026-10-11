import math

from core.fea.translator import Translator
from core.fea.abaqus.translator.contact_surface import ContactSurface
from utilities.logger import logger


class ContactPairTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.version = {"6.14": self._6p14, "2024": self._6p14}

    def translate(self, version):
        if version in self.version:
            self.version[version]()

    def _6p14(self):
        surface = ContactSurface(self.dataframe)
        output, inclusions, assignments = [], [], []
        for sid in self.dataframe.set_segment:
            faces = surface.resolve(sid, 0)
            output.extend(surface.write_surface(f'dyna_segments_{sid}', [(eid, side or 'SPOS') for eid,side,nodes in faces]))
        for cid, contact in self.dataframe.storge.get('contact_single_edge_id', {}).items():
            from core.fea.conversion_notes import unconverted
            unconverted(f'Single-edge contact {cid}: segment edge selections are exported as dyna_segments surfaces; '
                        'Abaqus/Standard contact cannot directly use 3D shell edge-based surfaces. '
                        'The contact interaction requires a reviewed general-contact model', contact)
        contacts = [(cid, contact, False) for cid, contact in self.dataframe.contact_automatic_surface_to_surface_id.items()]
        contacts += [(cid, contact, True) for cid, contact in self.dataframe.contact_automatic_single_surface_id.items()]
        for cid, contact, self_contact in contacts:
            try:
                if contact.sboxid or contact.mboxid:
                    raise ValueError("Contact box filtering is not supported")
                fs, fd = float(contact.fs), float(contact.fd)
                if not all(math.isfinite(value) and value >= 0 for value in (fs, fd)):
                    raise ValueError("FS/FD must be nonnegative constant friction coefficients")
                if contact.sstyp == 5:
                    slave = surface._exterior(list(self.dataframe.element_shell.values()) + list(self.dataframe.element_solid.values()))
                else:
                    slave = surface.resolve(contact.ssid, contact.sstyp)
                master = slave if self_contact else surface.resolve(contact.msid, contact.mstyp)
                if not self_contact and {uid for uid, _, _ in slave} & {uid for uid, _, _ in master}:
                    raise ValueError("Overlapping contact selections would create self-contact")
                # Native general contact supports both shell sides, matching
                # automatic DYNA contact without guessing normals per facet.
                slave_faces = [(eid, side or 'BOTH') for eid, side, _ in slave]
                master_faces = [(eid, side or 'BOTH') for eid, side, _ in master]
                prefix = f"dyna_contact_{int(cid)}"
                # Abaqus explicit face lists cannot mix shells with solids.
                # Split mixed part sets and retain all cross-group interactions.
                slave_groups = self._surface_groups(f"{prefix}_slave", slave_faces)
                master_groups = [] if self_contact else self._surface_groups(f"{prefix}_master", master_faces)
                lines = []
                for name, faces in slave_groups + master_groups:
                    lines.extend(surface.write_surface(name, faces))
                lines.extend([
                    f"*SURFACE INTERACTION, NAME={prefix}_fric\n",
                    "*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD\n",
                    "*FRICTION\n", f"{max(fs, fd):.12g}\n",
                ])
                for slave_name, _ in slave_groups:
                    targets = slave_groups if self_contact else master_groups
                    for master_name, _ in targets:
                        if self_contact and master_name < slave_name:
                            continue
                        inclusions.append(f'{slave_name}, {master_name}\n')
                        assignments.append(f'{slave_name}, {master_name}, {prefix}_fric\n')
                output.extend(lines)
                logger.info(f"ABAQUS contact {cid}: {len(slave_faces)} slave / {len(master_faces)} master faces")
            except (KeyError, ValueError, TypeError) as e:
                # Never silently write a partial or dangling contact definition.
                raise ValueError(f"ABAQUS ContactPairTranslator ERROR: contact {cid}: {e}") from e
        if output:
            if inclusions:
                output += ['*CONTACT\n', '*CONTACT INCLUSIONS\n', *inclusions,
                           '*CONTACT PROPERTY ASSIGNMENT\n', *assignments]
            self.dataframe.output_storge.setdefault("*CONTACT PAIR", []).extend(output)

    @staticmethod
    def _surface_groups(name, faces):
        shells = [face for face in faces if face[1] in ("SPOS", "SNEG", "BOTH")]
        solids = [face for face in faces if face[1] not in ("SPOS", "SNEG", "BOTH")]
        if shells and solids:
            return [(f"{name}_shell", shells), (f"{name}_solid", solids)]
        return [(name, faces)]
