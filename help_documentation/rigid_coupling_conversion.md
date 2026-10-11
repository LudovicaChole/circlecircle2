# Abaqus rigid couplings to LS-DYNA

A complete component with an elastic material, captured by a full six-DOF
Abaqus rigid coupling, becomes a rigid LS-DYNA part using MAT20. The converter
creates a separate material for that part so other components sharing the
original elastic material keep their behavior.

Captured nodes belonging to plastic components do not make those components
rigid. Their elements and materials remain unchanged. Nodes outside the rigid
part, including an external reference node, are associated with that part using
CONSTRAINED_EXTRA_NODES_SET and SET_NODE_LIST.

Fixed reference-node DOFs become MAT20 CMO/CON1/CON2 constraints. Reference-node
prescribed motion becomes BOUNDARY_PRESCRIBED_MOTION_RIGID, using the rigid part
ID and the original physical motion curve. Initial MAT20 constraints remain
model-data BOUNDARY conditions in Abaqus; step motion modifies them with OP=MOD.
Both the initial constraint mask and the motion are retained on conversion back
to LS-DYNA, even after deleting all comments. Ordinary deformable-node
constraints remain ordinary boundary conditions.

This mapping requires a unique, completely captured elastic or rigid component
and a full six-DOF coupling. Partial couplings, ambiguous multiple component
anchors and couplings with only plastic components retain their nodal
representation; assigning a whole rigid part would change their behavior.

The supplied comment-free CrashBox input was verified on 2026-10-10. It creates
two MAT20 parts and two extra-node sets. Its four plastic shell parts retain
their materials. The rigid reference constraints produce no BOUNDARY_SPC cards.
HyperMesh imports 4,536 nodes and 4,336 elements in six components with zero
errors, zero warnings and no undefined materials. LS-DYNA completes 31,103
cycles and terminates normally at 20 ms. The 1,500 kg concentrated mass remains
included in the upper rigid body.

For the source impactor, CON1=6 constrains global X and Z translation and
leaves Y translation free; CON2=7 constrains all rotations. The corresponding
initial Abaqus reference-node BOUNDARY entries include DOFs 1, 3, 4, 5 and 6.
A prescribed X displacement in a subsequent step modifies the X boundary with
OP=MOD. It must not remove DOF 1 from the stored initial MAT20 constraint mask.
An earlier converter version omitted that initial X entry; such an already
converted file needs regeneration from its source to recover missing data.
