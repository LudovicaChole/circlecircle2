# Concentrated nodal mass conversion

LS-DYNA ELEMENT_MASS is converted to a native PAMCRASH MASS card at the same
node. The scalar physical mass is written into each diagonal translational
mass entry, Mx/My/Mz. These three entries describe the inertia for three
directions; they are not three additional masses to sum. No rotary inertia or
offset is introduced.

Native isotropic PAM MASS cards are read into the shared concentrated-mass
model, including when source archive comments are deleted. Anisotropic mass,
rotary inertia, offsets, frames and general entity selections are rejected
explicitly until their conversions are implemented.

HyperMesh 2025 and later represent PAM MASS using the Solver Masses entity,
configuration 401, rather than ordinary elements/groups. Look under Solver
Masses to inspect the node and mass values.

The supplied DYNA CrashBox case contains a 1,500 kg concentrated mass at node
5379. Its PAM output was imported and exported with HyperMesh 2026: zero errors,
zero warnings, one Solver Mass at node 5379, and Mx=My=Mz=1500. The native
exported MASS card was parsed again after deleting comments to confirm the
same node and mass. This is import/export validation, not a PAM solver run.

Reference: https://help.altair.com/hwdesktop/hwd/topics/reference/hm/api_programmers_guide_2025_r.htm
