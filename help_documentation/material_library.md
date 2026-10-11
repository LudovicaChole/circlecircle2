# Material library and static conversion

## Library layout

The default library is `Material_Library` beside `main.py` or the executable.
Use Setting > Material_Library_Path to choose another parent directory or the
Material_Library directory itself.

```text
Material_Library/
  library_units.json
  Ls_Dyna/<any-material-name>.k
  ABAQUS/<any-material-name>.inp
  PamCrash/2D/<any-material-name>.pc
  PamCrash/3D/<any-material-name>.pc
```

Templates are discovered recursively. The supplied materials are examples;
neither names nor the number of files are fixed. Each file contains one material
and its referenced curves/tables. Solver folder matching ignores case, spaces,
underscores and hyphens. Corresponding materials must use the same filename stem across solvers. Subdirectories may differ.

Matching first compares every point of the complete lowest-rate plastic curve
against the source solver library, applying native curve scales and offsets.
Source-library curves are indexed both in their native units and in the selected
model units. A native-only match warns when the selected model units differ.
A unique match identifies the material by the source file's stem, not by the
material NAME or ID. The target solver folder is then searched recursively for a
compatible template with that same stem. Target curves need not equal source
curves: target templates may deliberately use different point counts, rate laws
or failure models. A target curve alone cannot identify a source material.

Source-curve ambiguity, missing source matches, absent target templates and
ambiguous target filenames are reported separately. Source density, Young's
modulus and Poisson's ratio are preserved when rendering a matched template.
Curve and table IDs are allocated once per conversion without colliding with
source IDs or dependencies already allocated to another material. Target material
IDs are replaced by the converted model material IDs. Invalid neighboring files
are skipped without disabling valid templates.

Setting > Unit selects the model unit system; its default is kg/mm/ms/J. The two model choices are kg/mm/ms/J and T/mm/s/mJ (T = metric tonne; mJ = millijoule).
`library_units.json` declares each solver library's units. Initial library
settings are LS-DYNA KG/mm/ms/J, Abaqus tonne/mm/s/N-mm and PAM g/mm/ms/N-mm.
Keep new templates consistent with their declared library units. The selected
unit describes the source model; it does not rescale its mesh or every loading
quantity. LS-DYNA curve coordinates use `(value + offset) * scale`; PAM function
coordinates use `value * scale + shift`.

Elastic and rigid materials bypass plastic-template matching. A malformed
individual template is skipped without disabling other templates. Missing or
unmatched templates generate an explicit warning and elastic fallback; nonlinear
source behavior remains archived for restoration. Density is never guessed.

The former Export_Material menu and embedded JSON library have been removed.
Edit solver files directly. Packaging copies the complete Material_Library folder
beside the executable, including future material files and subdirectories.

## PAM material parsing

The active material reader is `core/fea/material_cards.py:read_pamcrash`, called
by `PamCrash.parse` after the numeric PYVAR pass. PAM `<name>` references are
resolved consistently for material fields, function scales and curve points,
including values defined in another included file. Fixed-column blank cards
remain positional. Truncated material/function cards, missing function references
and invalid isotropic elastic properties produce source-located errors.

MATYP105 reads density, Young's modulus, Poisson's ratio, LC1-LC8 and ERATE1-ERATE8.
All referenced functions are retained and the lowest-rate curve is used for
library matching. Original material rows, including damage/failure cards, are
retained in the fingerprint for inspection. This is not a complete constitutive
damage-law translation: target templates supply nonlinear and failure behavior,
and an unmatched material uses the documented elastic fallback.

MATYP1 CURVE reads its references after the separate G and K cards and computes
isotropic E and Poisson's ratio from those moduli. Inline point laws and MATYP103
are identified as plastic; unsupported curve reconstruction uses the warned
elastic fallback instead of treating them as equivalent target plastic laws.

## Static Abaqus analysis

Mechanical output uses STATIC with NLGEOM=YES. Nodal history requests are retained
as U and RF. Field requests include U, RF, S, LE, PE, PEEQ and ENER; whole-model
history requests include ALLIE, ALLSE, ALLPD and ALLWK. Variables unavailable for
particular material/element types are subject to Abaqus output rules.

LS-DYNA prescribed rigid or nodal displacement is retained. Prescribed velocity
is integrated once; acceleration is integrated twice. Integration uses the
source piecewise-linear curve, model duration and motion scale. Total displacement
and values at source knots are exact. The exported tabular amplitude samples
intermediate integrated-polynomial values at 16 subdivisions per interval.
Initial nodal velocity produces displacement = velocity * duration. This creates
prescribed static motion; it does not reproduce the source dynamic response.

PAM global DIS3D/VEL3D/ACC3D and RAN3D/RVE3D/RAC3D use the same conversion.
RBODY types 0/1/2 without failure or sensors retain their reference-node coupling.
Global real constant motion is supported on the optional `&` continuation card,
including IDNOD=0 with node-selection cards. Zero constants leave the corresponding
DOFs free. Local frames, sensors, imaginary harmonic constants, simultaneous
function-plus-constant definitions and custom rigid mass/inertia variants are
rejected until their full semantics are implemented.

Machine-readable CIRCLECIRCLE2_INITIAL_VELOCITY, CIRCLECIRCLE2_MOTION and
CIRCLECIRCLE2_DURATION comments retain source velocity, motion type, scale,
curve and duration. Reverse conversion reads these notes. When absent, direct
global tabular Abaqus boundary loading is converted from its actual data instead.
Delete or update the source notes when deliberately replacing generated loading;
retained notes are the intended source data for reverse conversion.
Point MASS elements are read directly, whether or not notes exist.

Initial and maximum STATIC increments scale with the source duration. Without
a termination card, a prescribed-motion curve supplies its ending time.

## Erosion and segment sets

MAT_ADD_EROSION and its TITLE variant preserve the optional LCFLD card, including
LCFLD=0, with or without the legacy GISSMO continuation. Blank positional cards remain meaningful. Fixed/free formats and
parameter references use the shared numeric parser.

SET_SEGMENT repeated-node edge definitions such as (n1,n2,n2,n2) become two-node
edges. PAM export writes exact EDG selections; triangles/quadrilaterals use SEG.
Abaqus named surfaces preserve edge labels E1/E2/E3/E4 or element faces.
CONTACT_SINGLE_EDGE_ID cannot directly become a Standard contact pair on a 3D
shell edge-based surface. The converter retains the surfaces and emits a clear
NOT CONVERTED warning; a reviewed general-contact interaction remains necessary.

## References

- LS-DYNA R13 Volume I, SET_SEGMENT, pages 41-61 through 41-68.
- LS-DYNA R13 Volume II, MAT_ADD_EROSION and prescribed-motion source cards.
- Local PAM-CRASH 2020 RBODY documentation and Altair HyperMesh PAM templates
  loads_2016, elements_rbody_2006, sets_format and ges_write.
- [SIMULIA surface definitions](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEGSARefMap/simagsa-c-cntsurfaces.htm).


## Hourglass controls for Abaqus conversion

Deformable components exported to LS-DYNA receive an explicit `*HOURGLASS`
reference through PART.HGID. ELFORM 16/-16 shells use IHQ=8, QM=0.1 (warping
stiffness); solids use IHQ=6, QM=0.1. Other shell formulations use IHQ=4,
QM=0.05 because IHQ=8 is specific to ELFORM 16/-16. Formulations without
hourglass modes may ignore this setting. Compatible profiles share one allocated
ID. Existing LS-DYNA hourglass definitions and references are written unchanged.

PAM-CRASH uses component NUMPAR references (PART.IDNUMPAR), with separate
SHELL_LINEAR/SOLID_LINEAR EXPLICIT_MECHA blocks and HOURGLASS_FORMULATION=1.
Coefficients retain PAM defaults. This does not overwrite the material library's
constitutive data. Rigid materials and complete rigid node selections receive
no automatic control; partial couplings remain deformable.

These are converter defaults, not a claim of dynamic equivalence to Abaqus.
[Ansys shell formulations](https://lsdyna.ansys.com/shell-formulations-2/) and
[hourglass guidance](https://lsdyna.ansys.com/hourglass-2/) describe formulation
compatibility. PAM field layouts follow the installed Altair PAM 2020 NUMPAR
and PART export templates.


LS-DYNA/PAM-CRASH to Abaqus also writes versioned
`CIRCLECIRCLE2_HOURGLASS` comments containing the original controls and element-ID
bindings. Conversion back to the same solver restores these settings even when
the full source archive is removed. LS-DYNA local and global controls, and PAM
NUMPAR blocks plus material ISHG/QVM values, are retained. New Abaqus components
without a matching note receive new target defaults. Notes apply only where all
current component elements belong to the original saved component; conflicting
or malformed notes stop conversion. Update or remove these notes when changing
the intended numerical controls. Labels/part IDs may change without losing the
association, but changing element IDs requires updating the notes.


When a source MAT20 constraint overlaps a nonzero prescribed rigid motion,
Abaqus conversion gives the explicit prescribed motion precedence on that DOF,
retains all other MAT20 constraints, and records the source conflict in the log
and step comments. It does not silently edit the source LS-DYNA material. This
is the converter's conflict-resolution policy, not a general claim that source
solver versions treat every contradictory input in the same way.


## Point mass organization

Abaqus point masses use a single-node `*ELEMENT, TYPE=MASS` and a separate
`*MASS` property assigned through its ELSET. Source LS-DYNA ELEMENT_MASS.PID
is retained as the HyperMesh component owner when that part exists. Otherwise
an independent point-mass component is created. Explicit property metadata
keeps the MASS property visible; property IDs and element IDs are allocated
separately, avoiding collisions with structural entities. The original node
and mass value remain unchanged. HyperMesh's Direct Property indicator denotes
valid element-level assignment in its Abaqus interface; it does not mean the
point mass lacks a separate property.
