import json
import os

from core.fea.dataframe import dataframe
from utilities.logger import logger


class MaterialMapping:
    """Load solver templates and match exact material tags or names."""

    def __init__(self, file_path, solver):
        if not file_path:
            raise ValueError("material_mapping=True requires material_mapping_file_path")
        file_path = os.fspath(file_path)
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "material_mapping.json")
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            all_material = json.load(f)
        if not isinstance(all_material, dict) or not isinstance(all_material.get(solver), dict):
            raise ValueError(f"Material mapping file must contain a '{solver}' object: {file_path}")

        self.solver = solver
        self.templates = {}
        self.used_curve_ids = set(dataframe.define_curve)
        self.next_curve_id = 1
        for name, template in all_material[solver].items():
            key = name.strip().casefold()
            if not key or not isinstance(template, str) or not template.strip():
                raise ValueError(f"Invalid material template: {solver}.{name}")
            if key in self.templates:
                raise ValueError(f"Duplicate material mapping name: {name}")
            self.templates[key] = template

    def render(self, material, mid):
        # Keep curve-based recognition first; explicit material names also work.
        for name in (getattr(material, "map_tag", None), getattr(material, "name", None)):
            key = str(name).strip().casefold() if name is not None else ""
            if key in self.templates:
                template = self.templates[key]
                material_id = f"{mid: >9}" if self.solver == "pamcrash" else str(mid)
                template = template.replace("{material_id}", material_id)
                template = template.replace("{material_name}", str(material.name))
                if self.solver == "pamcrash":
                    template = self._prepare_pam_curves(template)
                logger.info(f"Material mapping: {mid} ({material.name}) -> {self.solver}.{key}")
                return template.rstrip("\r\n") + "\n"
        logger.warning(f"Material mapping: no {self.solver} template for {mid} "
                       f"({material.name}); using standard translation")
        return None

    def _prepare_pam_curves(self, template):
        """Allocate per-material FUNCT IDs and update the fixed-width LC fields."""
        lines = template.splitlines(keepends=True)
        curve_ids = {}
        for line in lines:
            if line.startswith("FUNCT /"):
                old_id = int(line[7:16])
                if old_id in curve_ids:
                    raise ValueError(f"Duplicate FUNCT ID in material template: {old_id}")
                while self.next_curve_id in self.used_curve_ids:
                    self.next_curve_id += 1
                if self.next_curve_id > 99999999:
                    raise ValueError("No available PAM-CRASH function ID")
                curve_ids[old_id] = self.next_curve_id
                self.used_curve_ids.add(self.next_curve_id)
                self.next_curve_id += 1

        curve_reference_line = False
        for index, line in enumerate(lines):
            if line.startswith("FUNCT /"):
                lines[index] = f"FUNCT /{curve_ids[int(line[7:16])]: >9}" + line[16:]
            elif curve_reference_line and not line.startswith("$"):
                ending = "\n" if line.endswith("\n") else ""
                fields = line.rstrip("\r\n")
                updated = []
                for offset in range(0, len(fields), 10):
                    field = fields[offset:offset + 10]
                    if field.strip() and int(field) in curve_ids:
                        field = f"{curve_ids[int(field)]: >10}"
                    updated.append(field)
                lines[index] = "".join(updated) + ending
                curve_reference_line = False
            if line.startswith("$") and "LC1" in line.split():
                curve_reference_line = True
        return "".join(lines)
