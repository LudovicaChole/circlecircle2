# PAMCRASH parameters

PAMCRASH defines variables with PYVAR and supports Python expressions through
PYVAR/PYFUNC. Numeric LS-DYNA PARAMETER definitions are exported as native PYVAR
blocks, preserving variable names, integer/real values and unused definitions.

Example for the supplied CrashBox source:

```
PYVAR /        1
NAME Velocity
Velocity = 2.5
END_PYVAR
```

The converter evaluates supported numeric source references while parsing.
Preserving definitions does not rebind already resolved output fields to these
variables. Changing a PYVAR value therefore affects only fields which explicitly
reference it in the PAM deck. Original expressions/reference bindings remain
available in the source archive for exact source restoration.

The native reader accepts finite numeric assignments and basic arithmetic;
it does not execute arbitrary embedded Python. String parameters and names
which are invalid Python identifiers are rejected by the output converter.

HyperMesh 2026 import/export of the supplied case confirms a real PYVAR
parameter named Velocity with value 2.5, zero import errors and warnings, and
the existing 1500 kg nodal mass retained. Native exported parameter data was
read again without source archive comments. No PAM solver run was performed.

Reference: https://www.help.altair.com/2021/hwdesktop/hm/topics/release_notes/rn_2021_hypermesh_pam_crash_2g_r.htm
