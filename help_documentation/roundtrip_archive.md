# Reversible source archives

Generated solver decks carry compressed source text in solver comments. All
expanded source keywords are included, including control, database, contact,
material and analysis cards without an equivalent target conversion.

The V2 format groups comment chunks by archive identifier. Abaqus `.geo` files
carry a model fingerprint; the companion `.inp` also carries a fingerprint of
the expanded model and complete analysis step. This allows both files to carry
archives without merging unrelated compressed streams. V1 archives remain
readable. Regenerate older split Abaqus files to obtain full analysis coverage.

Returning an unchanged generated file to an archived solver restores its full
source deck, with original IDs and parameters. Includes are already expanded.
Changing the model or analysis step invalidates the full fingerprint; conversion
then uses the current model rather than silently discarding edits. Retain the
archive comments and the companion `.geo` file when transferring `.inp` files.

An unchanged restoration preserves source behavior, including source warnings.
It does not make unsupported features execute in the intermediate solver. A
successful Abaqus data check does not establish dynamic equivalence to DYNA.

# Segment display components

HyperMesh can create `^compForSegments_*` components when importing explicit
segment contact sets. Their display facets may coincide with structural shells.
Do not delete contact segments merely to hide these facets. Compare physical
`*ELEMENT_SHELL` connectivity in the exported deck and retain valid contact
definitions. Restoring the original part-set contacts avoids newly generated
segment display components in an unchanged DYNA/Abaqus/DYNA round trip.
For native contact conversion after removing comments, see
`contact_conversion.md`. Complete automatic shell selections now use existing
part or shell element sets even when no source archive is present.

# Abaqus labels

Material and section labels are normalized before generating ELSET references.
Periods in source thickness names are replaced with underscores, and collisions
receive unique suffixes. This changes labels only, not thickness or properties.
