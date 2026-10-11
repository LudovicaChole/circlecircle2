# Contact conversion without source comments

Abaqus self-contact is expressed through a contact domain, not an independent
`SELF CONTACT` keyword. The converter writes native `CONTACT`, `CONTACT
INCLUSIONS` and `CONTACT PROPERTY ASSIGNMENT` data. Pairing a surface with itself
defines self-contact. The assigned `SURFACE INTERACTION` and constant `FRICTION`
remain normal solver data when all comment lines are removed.

LS-DYNA automatic shell contact is represented by double-sided surfaces in
Abaqus general contact. The selected source parts and friction property are
used directly. The converter does not infer a model-wide self-contact from the
presence of parts, and it does not infer friction from unrelated contact pairs.
A native Abaqus model without self-contact receives no invented self-contact.
Explicit `ALL EXTERIOR` domains remain all-exterior domains.

On conversion to LS-DYNA, a complete shell-part selection uses part IDs or a
`SET_PART_LIST`. A partial shell selection uses a `SET_SHELL_LIST`. Solid faces,
ambiguous coincident faces and tied-contact master surfaces retain explicit
segment sets. This preserves selection scope rather than expanding a partial
surface to an entire component. Unused native segment sets are retained.

HyperMesh may create `^compForSegments_*` display components for explicit
segment sets. Those components are not necessarily `PART` keywords in the input
deck. Their display facets coincide with the structural surfaces they describe.
Using existing part/shell selections avoids these extra display facets for
ordinary automatic shell contacts. Genuine tied or solid segment surfaces may
still require them; removing their geometry would change contact semantics.

Supported general contact input includes one new domain, explicit surface-pair
inclusions or `ALL EXTERIOR`, and uniform/default surface property assignments.
Unsupported exclusions, material-based assignments and domain changes fail
explicitly. Unsupported dependent friction is not replaced with zero friction.
General contact initialization and solver-specific penalty parameters still
require review; the contact algorithms of the solvers are not identical.

The supplied CrashBox case was verified after removing every Abaqus comment:
two surface-to-surface contacts and one self-contact, all with friction 0.2.
Self-contact contains only the four CrashBox shell parts. The upper impactor
and lower support are separate contact partners. HyperMesh import reports zero
errors and warnings and no `^compForSegments_*` component. LS-DYNA calculation
terminates normally at 20 ms. Abaqus data check completes with one standard
warning about initial adjustment of double-sided general contact facets.

Removing comments also removes source-only controls and parameter metadata.
Native mesh, materials, mass, loading, duration and contact can be converted;
solver-specific cards with no Abaqus equivalent cannot be reconstructed exactly
from missing data. Preserve source archives for exact control/database-card
restoration. Case-specific settings are not silently copied into other models.

References:
- https://docs.software.vt.edu/abaqusv2025/English/SIMACAEKEYRefMap/simakey-r-contactinclusions.htm
- https://docs.software.vt.edu/abaqusv2025/English/SIMACAEKEYRefMap/simakey-r-contactpropertyassignment.htm
- https://lsdyna.ansys.com/wp-content/uploads/2025/02/LS-DYNA_Manual_Volume_I_R13.pdf
