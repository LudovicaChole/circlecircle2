"""Consistent component labels without modifying the source base name."""
import re


def material_suffix(name, tags):
    name = re.sub(r'\.\d+$', '', name).lower()
    return next((tag for tag in sorted(tags, key=len, reverse=True)
                 if name == tag.lower() or name.endswith('_'+tag.lower())), None)


def component_name(name, tag, thickness):
    if tag:
        name = re.sub(r'\.\d+$', '', name)
    base = name[:-len(tag)-1] if tag and name.lower().endswith('_'+tag.lower()) else name
    number = f'{thickness:.3f}'.rstrip('0').rstrip('.')
    if '.' not in number:
        number += '.0'
    return f'{base}_{number.replace(".", "p")}mm_{tag or "elastic"}'
