# PAM prescribed motion conversion

LS-DYNA rigid prescribed motion is applied to the independent MTOCO reference
node generated for the rigid part. MTOCO is translated before motion. Dependent
mesh nodes are not independently driven. Nodal prescribed motion keeps its
explicit target nodes.

VAD 2, 0 and 1 become DIS3D, VEL3D and ACC3D respectively. Rotational motions
become RAN3D, RVE3D and RAC3D; LS rigid DOFs 5/6/7 map to rotations 1/2/3.
The loading multiplier SF is written as the selected axis SFAC. FUNCT retains
curve scales and offsets separately. SFO scales the curve ordinate; for a
displacement curve this means displacement, not stress or strain rate.

A single target uses IDNOD directly (HyperMesh DIS3D (NODES)). Multiple targets
with identical direction, loading type, curve and multiplier use IDNOD=0,
a generated GROUP with NOD selections, and a GRP reference followed by END.
Only independent target nodes enter such a motion group.

A prescribed rigid DOF is removed from the generated PAM BOUNC fixed mask;
the other MAT20 constraints remain. Original MAT20 constraints are retained in
the source archive. This does not alter the LS-DYNA/Abaqus constraint mapping.

RUNEND retains the source termination time; motion curves are not truncated
or renormalized. In the CrashBox fixture, curve 1051 has SFO=-1 and raw points
(0,0), (100,100). SF=1 therefore gives X displacement -20 mm at TIME=20 ms.

Missing rigid references, duplicate target DOFs, vector/offset motions and
nondefault BIRTH/DEATH windows fail explicitly. Sensor activation is not yet
mapped. Native syntax follows the local Altair PAM loads_2016/loadcols_2016
templates and the supplied PAM constraint documentation.
