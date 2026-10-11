# Cross-solver conversion

## Large input decks

Includes are expanded once with original file/line records. LS-DYNA and PAM
dependency passes reuse a per-deck block index and skip data belonging to other
passes while retaining keyword boundaries, comments inside selected blocks and
positional blank cards. Encrypted input retains the original full-stream path.
Material readers receive only relevant material/curve cards plus block boundaries,
with a source map back to the original included files. Abaqus continued headers
are preserved. Indexes live only as long as the loaded deck, so later file edits
are not hidden by a persistent cache.

The solver loader reads bytes once and uses the same lossless BOM/UTF-8/cp1252/
Latin-1 fallback as the editor. Numeric parsing attempts standard floats before
the special D/implicit-exponent path. Mesh-index rebuilding checks just each
element's connectivity rather than rebuilding a set of all nodes per element.
These CPU optimizations benefit machines with and without CUDA.

## Geometry acceleration

Large nearest-contact-face searches and generated rotational velocity fields use
optional PyTorch CUDA. Small jobs use NumPy CPU batches. Missing PyTorch, a
CPU-only installation, unavailable CUDA, or a CUDA runtime/memory error fall back
to CPU. Logs identify the chosen backend for large operations. No solver syntax
or contact semantics change: Explicit automatic shell contacts remain two-sided;
only Standard shell orientation needs nearest-face searching.

Distances use float64 direct coordinate differences, with at most 256 query
points by 4096 reference points in each distance block. Ties choose the first
face in input order, including across blocks. No full all-pairs matrix is kept.
Contact selection results, facet centers and the segment-to-element index are
cached only within a translation and are discarded between models. Parsing,
dictionary-based topology checks and text output remain on CPU.

`CIRCLECIRCLE_FEA_DEVICE=cpu` forces CPU execution for troubleshooting;
the default `auto` selects CUDA for at least one million distance pairs or
32768 generated velocity nodes. `cuda` requests CUDA also for small geometry
jobs, retaining CPU fallback. PyTorch remains optional; install a CUDA-capable
build separately if GPU support is desired. GPU initialization/transfer overhead
and file parsing mean kernel speedups are not whole-conversion speedups.

The converters share the existing `DataFrame` and LS-DYNA keyword record classes.
Source node and element labels are preserved. Abaqus sections become internal
parts; PAM element thickness overrides become separate homogeneous parts and
sections. Unit conversion is not performed: use one consistent unit system.

## Implemented reverse-conversion subset

| Source | Supported input |
| --- | --- |
| PAM-CRASH 2020 | NODE, SHELL (including triangles and element H), SOLID, TETR4, homogeneous SHELL/SOLID PART, numeric PYVAR assignments |
| PAM-CRASH 2020 | Node GROUP selections using NOD, inclusive ranges, GRP/OGRP, and DELNOD/DELGRP; global BOUNC; global INVEL with IRIGB=0; RUNEND TIME |
| PAM-CRASH 2020 | SECFO SECTION with explicit node/element selections and IFRA=0, translated to LS-DYNA cross-section sets |
| Abaqus | Flat global-coordinate NODE; linear S3/S3R/S4/S4R and C3D4/C3D6/C3D8/C3D8R/C3D8I; ELSET/NSET including GENERATE and nested sets; homogeneous SHELL SECTION and 3D SOLID SECTION |
| Abaqus | Zero model-data BOUNDARY constraints and nodal INITIAL CONDITIONS, TYPE=VELOCITY |

LS-DYNA output now includes mesh, parts, sections, node sets, fixed nodal
constraints, nodal initial velocities and termination time, rather than only a
material library. Each keyword parser/writer remains in a separate module.
The existing version-availability restrictions still apply.

Material mapping now uses the configured Material_Library folder and the complete
lowest-strain-rate plastic curve. It does not compare material names, numeric
IDs, density or elastic constants. See [Material library and static conversion](material_library.md).
Johnson-Cook cards without tabulated plastic curves use the elastic fallback.
PAM shell MATYP100/105 templates cannot be used as solid material laws; solid
conversion still uses a warned elastic MATYP1 fallback when no suitable solid
library template exists. Source density must be present when the target requires it.

Abaqus mechanical conversion writes a Standard STATIC step. Prescribed velocity
and acceleration curves are integrated into displacement histories; initial
nodal velocity becomes a displacement of velocity times the source duration.
Source velocity and motion notes can restore those values on reverse conversion.
This is a prescribed static loading conversion, not an equivalent dynamic impact
simulation. Thermal and eigenvalue steps retain their dedicated analysis procedures.

PAM FUNCT and global DIS3D/VEL3D/ACC3D, RAN3D/RVE3D/RAC3D are parsed.
Non-failing RBODY types 0/1/2 use nodal rigid couplings. Global real constant
motion uses the `&` continuation and supports IDNOD=0 node selections. Sensors,
local frames, imaginary harmonic constants, simultaneous function-plus-constant
definitions, failing rivets/spotwelds, and RBODY user mass/inertia variants require
additional mapping and are rejected explicitly.

Documented ACFLD, ACTRL, ACTUA and BAGIN cards remain unmapped; they produce
source-located NOT CONVERTED notes. AUTOSLEEP and AIRBAGCHECK free-format cards
are recognized as block boundaries and reported as unmapped controls. Modular
ACTIVATE_GLOBAL input is rejected because flattening active scopes could alter
the model. Added reference pages do not alone establish equivalent target physics.

LS-DYNA SET_SEGMENT accepts two-node edges, triangles and quadrilaterals.
PAM export uses exact EDG or SEG general-entity selections. Abaqus exports named
edge/face surfaces. A Standard contact pair cannot directly use a 3D shell
edge-based surface; CONTACT_SINGLE_EDGE_ID produces a NOT CONVERTED warning
while preserving its selected surfaces. A reviewed general-contact model is still
needed for that interaction.

## Limits

This is not a universal or lossless solver-deck conversion. Reverse conversion
of contacts, arbitrary rigid-body definitions, beams, loads, coordinate systems,
assemblies/instances, transformed/binary includes, nonlinear section options and analysis-step
history is not complete. Unsupported source keywords are reported in the log
and recorded as `NOT CONVERTED` comments in the generated deck. Unsupported
options within handled cards, missing dependencies, duplicate mesh identifiers
and truncated supported cards stop conversion before writing output.

SECFO SECTION cannot be treated as an Abaqus output-frequency request. It needs
an oriented integration surface; until that geometry is explicitly mapped, the
Abaqus output includes a limitation comment instead of an invented section.
PYVAR accepts finite numeric assignments with arithmetic and previously defined
variables; it never executes embedded Python code.

## Include files

Select the main deck. Includes are expanded recursively before the global
parameter, definition and element passes, so child elements can reference nodes,
parts, materials and curves in other included files. Output is flattened into
the existing target deck; the input directory tree is not rewritten.

- LS-DYNA: `*INCLUDE` accepts multiple filenames, quoted paths and the documented
  space-plus filename continuation. `*INCLUDE_PATH` and
  `*INCLUDE_PATH_RELATIVE` supply additional directories for bare filenames.
  Relative includes search the containing file's directory, then the selected
  main deck's directory. Relative search-path directives are anchored to the
  containing file; ordinary search-path directives to the main deck directory.
- Abaqus: `*INCLUDE, INPUT=...` supports parameter continuation and quoted spaces.
  The selected main deck's directory serves as the conversion job directory;
  nested local paths are a fallback. Unquoted filename whitespace is ignored.
- PAM-CRASH: `INCLU / filename` expands an input deck. Relative paths search the
  containing file's directory, then the main deck directory. `IMPFIL/` is a
  mapping-file import and is not interpreted as an input-deck include.

Child `*END` / `ENDDATA` markers end only that child. Missing files, recursive
cycles and nesting beyond 100 levels stop conversion with the include location.
Diagnostics retain the original file and line. LS-DYNA transformed/binary
includes and encrypted Abaqus includes are explicitly unsupported.

## LS-DYNA parameter values

Plain `*PARAMETER` definitions are read before the model passes across the
expanded include deck. Standard-format definitions use four pairs of
10-character PRMR/VAL fields per row; comma-separated definitions are also
accepted. Referenced numeric parameters become numeric model values and target
writers emit literal numbers, not LS-DYNA `&name` references or `*PARAMETER`
declarations. Missing numeric references stop conversion with source context.
A parameter definition does not override a literal field merely because its
name resembles that property (for example, `struc_E`).

Parameter evaluation does not create a target mapping for otherwise unsupported
cards. In particular, evaluated EM properties retain the EM mapping limitations
below. LOCAL/MUTABLE and expression parameter keywords are not implemented by
the plain parameter reader.

## Electromagnetic input and editing

The LS-DYNA parser reads the 16 EM keyword types used by the supplied TEAM
examples: CONTROL, CONTROL_TIMESTEP, CIRCUIT_SOURCE, CIRCUIT_ROGO,
DATABASE_POINTOUT, EOS_PERMEABILITY, EXTERNAL_FIELD, MAT_001, MAT_002, OUTPUT,
POINT_SET, SOLVER_BEM, SOLVER_BEMMAT, SOLVER_FEM, SOLVER_FEMBEM and
SOLVER_FEMBEM_MONOLITHIC (all prefixed `*EM_`). Each has its own parser module.
EM records retain typed fields, original rows and source locations separately
from structural materials. Blank values remain unspecified rather than being
assigned invented defaults. Parameters and comma-separated cards are accepted.

Editor guides share the standard 10-character field definitions, including
reserved columns, first/continuation cards and repeated point rows. Unknown EM
keywords receive no inferred layout. I10 and long-format guides remain disabled.
Legacy EM_OUTPUT and MONOLITHIC continuation fields are retained using the
official example layouts; they are not treated as new R13 solver settings.

This is EM input parsing and editor support, not an electromagnetic physics
translation to Abaqus or PAM. Those target decks contain the supported structural
subset and explicit `NOT CONVERTED` comments for the EM records. Do not treat
the generated structural deck as an equivalent electromagnetic analysis.

## Format and semantic references

### Added LS-DYNA analysis mappings

Each added keyword has a parser module under `core/fea/lsdyna/parser`.
Parameter substitution and source locations use the same shared machinery as
the existing structural and electromagnetic parsers.

- Abaqus B31: uniform SECTION_BEAM ELFORM 1 rectangular/circular/tubular
  sections and ELFORM 2 symmetric SECTION_01 I profiles. N3 and explicit
  ORIENTATION vectors define the first section axis. Tube diameters are
  converted to outside radius and wall thickness (THICK PIPE in Standard).
- Abaqus T3D2: ELFORM 3 truss area, without initial stress/dynamic relaxation.
- LOAD_NODE_POINT/SET: global forces and moments become CLOAD with scaled
  DEFINE_CURVE amplitudes. NODE/SET SPC ID variants retain repeated ID cards.
- CONTROL_IMPLICIT_EIGENVALUE: positive NEIG without shifts/windows or
  preload becomes a Lanczos FREQUENCY step. Numerical controls are reported
  as target defaults rather than claimed equivalent.
- Pure thermal SOLN=1: isotropic constant conductivity, density and specific
  heat; steady/transient HEAT TRANSFER; solid, planar/axisymmetric and shell
  thermal elements; initial temperature and node/set temperature boundaries;
  uniform segment heat flux and convection. Positive LS-DYNA flux is outward
  and is negated for Abaqus. Independent film and sink amplitudes are retained.
  Thermal material IDs remain separate from structural material IDs.
- Combined SOLN=2 is not generally supported. Only models consisting entirely
  of fully fixed rigid parts, without motion or EM, can be reduced to heat
  transfer with an explicit conversion note (e.g. flux8.k).
- Core ICFD material, time, part, section and fluid mesh cards are parsed into
  separate fluid records. This is input support, **not CFD translation**.
  Current target exporters stop CFD conversion rather than emit empty
  structural jobs. General coupled thermal mechanics, radiation, discrete
  thermal beams, temperature-dependent thermal materials, tapered/offset
  beams and beam end releases remain unmapped and require further work.

Verified online SIMULIA references for these mappings:
[BEAM SECTION](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEKEYRefMap/simakey-r-beamsection.htm),
[beam profiles](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEELMRefMap/simaelm-c-beamcrosssectlib.htm),
[beam orientation](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEELMRefMap/simaelm-c-beamcrosssection.htm),
[HEAT TRANSFER](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEKEYRefMap/simakey-r-heattransfer.htm),
[DFLUX](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEKEYRefMap/simakey-r-dflux.htm),
[FILM](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEKEYRefMap/simakey-r-film.htm),
[FREQUENCY](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEKEYRefMap/simakey-r-frequency.htm).
Checks cover generated decks and source/target field semantics; no licensed
Abaqus or PAM solver execution has been performed.

PAM-CRASH limitations are checked before parsing model dependencies. LS-DYNA
thermal cards, ICFD/MESH cards and beam elements/sections currently have no
verified complete PAM mapping. Their source keyword, included file and line
number are logged individually; conversion stops without creating or replacing
an output file. Missing documentation is described as an unverified converter
mapping, not as proof that PAM-CRASH cannot perform that analysis.

For other conversions that produce a supported subset, any `NOT CONVERTED`
notes cause a final `Partial conversion` warning instead of `All Done`.

- Local PAM-CRASH 2020 photographs and examples: `pamcrash2020/node.jpg`,
  `shell.jpg`, `solid.jpg`, `tetr4.jpg`, `part*.jpg`, `bounc.jpg`, `invel.jpg`,
  `group*.jpg`, and the corresponding `.pc` examples (including `secfo.pc`).
- Local LS-DYNA R13 Volume I: NODE 33-2; ELEMENT_SHELL 19-95;
  ELEMENT_SOLID 19-115; PART 35-4; BOUNDARY_SPC 5-117–118;
  INITIAL_VELOCITY_NODE 27-104; DATABASE_CROSS_SECTION 16-42–46.
- LS-DYNA R13 Volume I, INCLUDE chapter; Volume III, EM chapter.
  Legacy EM layouts: Ansys [TEAM 3](https://lsdyna.ansys.com/team3-d89/)
  and [TEAM 13](https://lsdyna.ansys.com/team13/) examples.
- Abaqus [INCLUDE](https://abaqus.uclouvain.be/English/SIMACAEKEYRefMap/simakey-r-include.htm)
  and [input syntax](https://abaqus-docs.mit.edu/2017/English/SIMACAEMODRefMap/simamod-c-inputsyntax.htm).
- SIMULIA Abaqus keyword documentation:
  [ELEMENT](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-element.htm),
  [SHELL SECTION](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-shellsection.htm),
  [SOLID SECTION](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-solidsection.htm),
  [BOUNDARY](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-boundary.htm),
  [INITIAL CONDITIONS](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-initialconditions.htm).
