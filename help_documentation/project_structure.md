# Project structure

`main.py` is the application entry point. `pack.py` is a distribution build tool.
Administrative license tools and neural-network training utilities are not
alternate application launchers.

```text
circlecircle2/
  main.py
  pack.py
  core/
    fea/
      model/
        lsdyna/       # Shared records used by multiple solver readers/writers
        abaqus/       # Abaqus-specific shared records
      lsdyna/
        parser/       # Read LS-DYNA cards into the shared data frame
        translator/   # Write LS-DYNA cards from the shared data frame
      abaqus/
        parser/
        translator/
      pamcrash/
        parser/
        translator/
      dataframe.py    # Shared conversion state
      parser.py       # Shared parser interface
      translator.py   # Shared translator interface
      solver.py       # Shared solver interface
      tbox.py         # Tensor operations for FEA part features
    hmdesktop/        # HyperMesh integration and scripts
    nn/               # Neural-network inference and training
  gui/                # Windows, dialogs and editor display behavior
  utilities/          # Application paths, logging, settings and other helpers
  help_documentation/
  Material_Library/   # Extensible solver material templates
  net_services/       # Reserved network-service package
  config/             # Application settings and runtime configuration
```

## Ownership and dependencies

Solver parsers own input syntax and source diagnostics. Solver translators own
output syntax, target mapping and target-specific conversion limits. Data model
classes contain records rather than file-reading or file-writing workflows.
Their shared package prevents translators from depending on parser classes.
Several PAM and Abaqus readers intentionally construct common LS-DYNA-shaped
records: these records are consumed by all three output solvers. Keep such
records in `core/fea/model`, not in one solver's parser package.

Solver orchestration modules remain beside their parser/translator directories.
`lsdyna/em_cards.py` is a shared schema used by parsing, validation and editor
formatting. Shared FEA services, including material parsing, library matching,
unit conversion, include expansion, mesh operations and reversible archives,
stay directly under `core/fea`.

HyperMesh code belongs to `core/hmdesktop`, learning code to `core/nn`, and
presentation code to `gui`. Runtime caches, licenses, IDE settings and Git
metadata are not application modules; they are not removed during code cleanup.
The network package is retained because it is an explicitly reserved subsystem.

## Extending and maintaining the project

Add a solver input feature to its parser and an output feature to its translator.
Add a shared record only when the reader and writer need that record contract.
Keep material templates outside Python code. The material scanner recursively
loads solver folders, accepts new filenames, and validates each template
individually. Do not enumerate the supplied example material names in code.

The build module discovers Python packages recursively, including shared models.
After moving a module, update every import and verify conversion, GUI imports and
build discovery. Removed legacy modules and pre-migration copies for the
2026-10-10 cleanup are retained outside the project under
`E:/CircleCircle2_Test_Environment/GPT_Debug`.
