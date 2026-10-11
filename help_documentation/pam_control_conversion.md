# LS-DYNA controls to PAMCRASH

Control conversion maps physical/output intent rather than matching keyword
names. The native layouts were checked against the supplied PAM 2020 local
help (TCTRL pages 4-7, ANALYSIS, SOLVER, OCTRL), the `*.pc` examples and
`controlcard_audi_noid.inc`. The Audi example is a formatting reference, not
a default configuration applied to unrelated models.

| Source setting | PAM output | Scope |
| --- | --- | --- |
| Target solver/version and explicit analysis | INPUTVERSION, SOLVER CRASH, ANALYSIS EXPLICIT | Explicit mechanical model header |
| TITLE | TITLE / | Text retained |
| CONTROL_TERMINATION ENDTIM | RUNEND TIME | Other stop criteria are reported separately |
| CONTROL_TIMESTEP DTINIT > 0 | TCTRL INITIAL | Initial imposed step |
| CONTROL_TIMESTEP TSSFAC > 0 | TCTRL SCALE CONSTANT | Stable time-step scale factor |
| Negative DT2MS with MS1ST=1 and no advanced scaling options | TCTRL INIT_MASS_SCALE | Initial-only scaling intent; element algorithms differ |
| Constant DATABASE history DT | OCTRL TIME_HISTORY INTERVAL | One common output time grid |
| Constant DATABASE_BINARY_D3PLOT DT | OCTRL CONTOUR_PLOT INTERVAL | Plot frequency; selection/format options remain separate |
| Constant D3DUMP/RUNRSF interval | OCTRL RSTOUTPUT INTERVAL | Frequency only; restart contents differ |
| GLSTAT/MATSUM/SLEOUT/energy output intent | OCTRL GLBTHP ALL | Superset of global histories; accounting switches are not identical |
| ELOUT history intent | SHLTHP/SOLTHP/BEATHP ALL | History-variable superset, with an explicit selection/layout notice |
| NODOUT | NODPLOT FACM plus existing THNOD selections | Nodal output intent |
| EXTENT_BINARY stress/strain/plastic strain requests | SHLPLOT SIGM/STRA/EPME, SOLPLOT EPLE | Shell tensor and equivalent plastic output; unsupported solid tensor options are reported |

Different constant history intervals use a common divisor, for example 0.3
and 0.4 become 0.1. This preserves source sample times while increasing output
volume. Unreasonably dense common grids are rejected. Curve-driven schedules
are not silently replaced by constant intervals.

LCTM is a mass-scaling control and must not be written as PAM PREFER. An inactive
zero-valued physical curve introduces no scaling. Dynamic/selective mass
scaling, positive DT2MS (which can remove mass), advanced options and mass-limit
semantics remain unconverted until verified. No 0.0005/20.0 Audi-example mass
scaling values are injected into a source model.

Contact penalty algorithms, bulk viscosity, dynamic relaxation, shell/solid
failure and numerical algorithms, processor settings, binary formats and
unsupported termination criteria are not treated as equivalent merely because
similarly named PAM options exist. Every parsed CONTROL/DATABASE card is
audited: mapped fields and remaining nonzero fields are recorded, with log and
NOT CONVERTED comments for partial mappings. Source archive comments retain
the original cards for exact source restoration. Removing these archives loses
solver-only data which cannot be reconstructed from target native cards.

Generated headers are self-contained and use resolved values; they do not
depend on undefined Audi-template variables such as edt or PC_T_TRS. Arbitrary
Python try/except blocks and string-valued template logic are not executed by
the numeric PYVAR reader.

CrashBox validation: native HyperMesh 2026 import/export reports zero errors
and warnings. Export confirms SCALE CONSTANT 0.9, TIME_HISTORY INTERVAL 0.4,
CONTOUR_PLOT INTERVAL 1.0, GLBTHP/element histories and shell stress/strain
variables. The 1500 kg mass at node 5379 and Velocity=2.5 remain present.
Five control-rule tests and sixteen existing regressions pass. This validation
does not constitute a PAM solver calculation.
