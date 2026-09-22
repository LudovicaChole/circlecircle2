from .analysis_data import is_explicit
import math

from core.fea.translator import Translator
from core.fea.abaqus.translator.contact_surface import ContactSurface
from utilities.logger import logger


class ContactPairTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.version = {"6.14": self._6p14}

    def translate(self, version):
        if version in self.version:
            self.version[version]()

    def _6p14(self):
        surface = ContactSurface(self.dataframe)
        output = []
        # Other contact families, including single-surface contact, are omitted.
        for cid, contact in self.dataframe.contact_automatic_surface_to_surface_id.items():
            try:
                if contact.sboxid or contact.mboxid:
                    raise ValueError("Contact box filtering is not supported")
                fs, fd = float(contact.fs), float(contact.fd)
                if not all(math.isfinite(value) and value >= 0 for value in (fs, fd)):
                    raise ValueError("FS/FD must be nonnegative constant friction coefficients")
                slave = surface.resolve(contact.ssid, contact.sstyp)
                master = surface.resolve(contact.msid, contact.mstyp)
                if {uid for uid, _, _ in slave} & {uid for uid, _, _ in master}:
                    raise ValueError("Overlapping contact selections would create self-contact")
                slave_faces = surface.orient_shells(slave, master)
                master_faces = surface.orient_shells(master, slave)
                prefix = f"dyna_contact_{int(cid)}"
                # Abaqus explicit face lists cannot mix shells with solids.
                # Split mixed part sets and retain all cross-group interactions.
                slave_groups = self._surface_groups(f"{prefix}_slave", slave_faces)
                master_groups = self._surface_groups(f"{prefix}_master", master_faces)
                lines = []
                for name, faces in slave_groups + master_groups:
                    lines.extend(surface.write_surface(name, faces))
                lines.extend([
                    f"*SURFACE INTERACTION, NAME={prefix}_fric\n",
                    "*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD\n",
                    "*FRICTION\n", f"{max(fs, fd):.12g}\n",
                ])
                for slave_name, _ in slave_groups:
                    for master_name, _ in master_groups:
                        if is_explicit(self.dataframe):
                            self.dataframe.output_storge.setdefault('*STEP_CONTACT', []).extend([
                                f'*CONTACT PAIR, INTERACTION={prefix}_fric, MECHANICAL CONSTRAINT=PENALTY\n',
                                f'{slave_name}, {master_name}\n'])
                        else:
                            lines.extend([
                                f"*CONTACT PAIR, INTERACTION={prefix}_fric, ADJUST=0.1, TYPE=SURFACE TO SURFACE\n",
                                f"{slave_name}, {master_name}\n",
                            ])
                output.extend(lines)
                logger.info(f"ABAQUS contact {cid}: {len(slave_faces)} slave / {len(master_faces)} master faces")
            except (KeyError, ValueError, TypeError) as e:
                # Never silently write a partial or dangling contact definition.
                raise ValueError(f"ABAQUS ContactPairTranslator ERROR: contact {cid}: {e}") from e
        if output:
            self.dataframe.output_storge.setdefault("*CONTACT PAIR", []).extend(output)

    @staticmethod
    def _surface_groups(name, faces):
        shells = [face for face in faces if face[1] in ("SPOS", "SNEG")]
        solids = [face for face in faces if face[1] not in ("SPOS", "SNEG")]
        if shells and solids:
            return [(f"{name}_shell", shells), (f"{name}_solid", solids)]
        return [(name, faces)]
