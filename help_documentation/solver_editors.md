# Abaqus and PAM-CRASH editing

The editor selects Abaqus for `.inp` and `.geo`, PAM-CRASH for `.pc`, and
LS-DYNA for `.k` and `.key`. For `.inc`, the opening keyword lines distinguish
Abaqus from PAM-CRASH; files without a recognizable signature use PAM-CRASH.
Data-only include files have no parent keyword context, so field names cannot
be reconstructed from the include file alone.

All solver views use a fixed-width font, line numbers and alternating field
backgrounds. The top panel follows the cursor and shows the keyword, field name,
line and column. These are visual aids: no spaces, separators, commas or values
are inserted into the saved file.

## Abaqus

Abaqus fields are comma-separated. The top panel therefore shows readable field
tiles, including field numbers and actual character ranges, instead of fixed
8- or 10-column guides. Empty fields remain visible in the field panel. Quoted
commas stay inside their original field. Keyword continuations and element
connectivity continuations preserve context across comments.

Named fields cover NODE (rectangular, cylindrical and spherical coordinates),
ELEMENT, NSET/ELSET lists and GENERATE, DENSITY, selected ELASTIC and PLASTIC
variants, ordinary BOUNDARY and CLOAD, and tabular/smooth-step/equally-spaced
AMPLITUDE. Material field-variable continuation lines are supported for the
named variants. Unknown keywords, abbreviations and unsupported options retain
generic numbered fields; they are not assigned guessed semantic labels.
HEADING and PARAMETER content is treated as text. The status tooltip notes
overlength or non-ASCII keyword/data lines. This is not full solver validation.

Sources: SIMULIA Abaqus documentation, publicly hosted by MIT:

- [Input Syntax Rules](https://abaqus-docs.mit.edu/2017/English/SIMACAEMODRefMap/simamod-c-inputsyntax.htm)
- [NODE](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-node.htm)
- [ELEMENT](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-element.htm)
- [NSET](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-nset.htm)
- [ELSET (SIMULIA documentation hosted by UCLouvain)](https://abaqus.uclouvain.be/English/SIMACAEKEYRefMap/simakey-r-elset.htm)
- [ELASTIC](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-elastic.htm)
- [PLASTIC](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-plastic.htm)
- [DENSITY](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-density.htm)
- [BOUNDARY](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-boundary.htm)
- [CLOAD](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-cload.htm)
- [AMPLITUDE](https://abaqus-docs.mit.edu/2017/English/SIMACAEKEYRefMap/simakey-r-amplitude.htm)

## PAM-CRASH 2020

Fixed-column cards show dotted boundaries at the documented column positions,
including reserved blank fields. For example, NODE uses an 8-character keyword,
an 8-character node ID and three 16-character coordinates. BOUNC and MTOCO
freedom codes occupy six characters after their reserved blanks. Contact types
33 and 36 have separate mixed-width layouts.

The photo-based catalog covers NODE, SHELL, SOLID, TETR4, SPRGBM, BEAM, BOUNC,
MTOCO, PLINK, TIED, the regular RBODY header, FRAME variants 0/1/3/4/5, INVEL,
CONLO, general PART cards, contact 33/36 data and material 100 elastic data.
Source photographs are the correspondingly named `.jpg` files in
`pamcrash2020`, including `frame9.jpg` for vector frames, `part3.jpg` and
`part7.jpg` for general part cards, and `cntac33.jpg` / `cntac36.jpg`.

Additional headers and selected FUNCT, MASS, SENSOR, shell PART and material
1/105 rows follow the supplied standard `.pc` examples. Their tooltips identify
the example source. Material 1/105 CURVE rows are supported through curve IDs
and strain rates; subsequent failure-law branches are not guessed. The samples
and photographs are retained unchanged. In particular, the supplied
`inputversion.pc` declares 2024; the photo-based guide catalog remains 2020
and does not claim full 2024 coverage.

Control blocks and entity selections use free-format field tiles. Quoted names
and parameter expressions remain grouped. NAME/RMAT titles, paths and metadata
are displayed as text. Comments do not consume data cards; required blank cards
do. SECURE content is displayed without interpretation. Unknown card variants
receive no fixed-column guides. Tab-containing fixed-format rows also suppress
guides because tab expansion would give misleading column positions.

Some examples contain fields beyond the photographed 2020 layout (such as the
PLINK extension after column 64); those additional fields are left unlabelled.
Consult the corresponding solver manual before changing unlabelled fields.

The LS-DYNA mode is described in [LS-DYNA editing](lsdyna_editor.md).
