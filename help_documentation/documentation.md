# CircleCircle2 User Guide

CircleCircle2 provides finite-element file viewing, text editing, solver keyword and material conversion, and device information. The file tree is on the left, the editor at the upper right, and Console below it.

## Getting started and files

Choose File > Set Work Directory. The application remembers it in config/profile.setting beside the application. Double-click a file or drag it into the editor. Ctrl+S saves; switching files or closing prompts for unsaved changes. A moved or missing work directory produces a message asking you to select it again. Until a directory is selected, logs appear only in Console. After selection, logs go to app.log in that directory. Changing directories redirects future logs and preserves earlier logs. Missing/corrupt settings do not prevent startup.

The tree displays Name, Size and Date; click a heading to sort. Open/Preview items are blue, Modified items yellow, and Loading/Translating items purple. These labels track use inside CircleCircle2, not other applications' file handles. Ctrl-click selects individual items; Shift-click selects a range. Right-click blank space to create items in the work directory, or a folder to create inside it. Supported new text types: .inp, .geo, .k, .key, .pc, .inc, .txt, .py, .md and .json. Creation never overwrites existing files. Right-click a file or directory and choose Open in Explorer or Copy Path.

Delete asks once before permanently deleting selected items and their contents. Parent/child selections process the parent once. Deleted open files keep their editor text for Save as. Ctrl+C/Ctrl+V create copies named name_copy.inp, then name_copy2.inp. Pasting a selected folder in place creates a sibling; selecting another folder copies into it. Existing files are preserved; linked items are rejected.

## Editing, search and previews

The editor detects supported encodings and preserves the source encoding, BOM and newline format when saving. Decoding failures are reported. Existing Chinese text is not rewritten during loading. Typed, pasted and input-method Chinese characters are filtered; full-width letters, digits and punctuation become English equivalents. This input rule does not translate words.

Large files load progressively in the background. Scroll, select and search the loaded portion while loading; editing/saving become available after completion. Dragging the scrollbar pauses additions until release. Changing files cancels the previous load. Setting > Editor controls word wrap and font size. With word wrap disabled, long lines use horizontal scrolling.

Ctrl+F opens case-insensitive search. Enter/Next moves forward; Previous moves backward. Search wraps at document boundaries and reports missing matches. The current keyword is orange; each search replaces the previous highlight. Esc closes search.

Markdown supports heading, list, link and code highlighting. Markdown Preview opens an independent snapshot window; reopen after editing. Automatic highlighting and preview rendering are limited to one million characters with a notice; the editor retains the full source. JSON up to one million characters is indented/highlighted without rounding numeric text. Invalid JSON retains its source and displays a warning. Display formatting is not written until saving.

Select a JPG/JPEG/PNG/GIF in the file tree and press Space, double-click it, or drag it into the editor. A separate preview scales proportionally as you resize it. GIF animation plays automatically. Space/Esc closes it. Multiple preview windows can remain open during editing.

## Translation and towing settings

Open/select a solver file and use Translate, File > Translate or Ctrl+E. Select the target solver/version. Translation runs in the background, one task at a time; Console displays progress and source diagnostics with path and LINE - number where available.

| Extension | Source | Default version |
| --- | --- | --- |
| .inp, .geo | Abaqus | 6.14 |
| .k, .key | LS-DYNA | 12.0 |
| .pc, .inc | PAM-CRASH | 2020 |

LS-DYNA translation currently enables Abaqus 6.14 and PAM-CRASH 2020; translation to LS-DYNA enables 12.0/13.0. Other listed target versions report that they are under development and stop before generating/overwriting output. Keyword coverage remains limited to implemented translators. Reverse LS-DYNA output covers supported mesh, material, constraint and nodal-motion cards; keyword coverage remains limited. See cross_solver_conversion.md for detailed limits.

Material_Library mapping is enabled by default. The default directory is Material_Library beside the application. Setting > Material_Library_Path selects a different library location; Setting > Unit selects the source model units, defaulting to kg/mm/ms/J. Solver templates are discovered recursively and new material filenames are accepted. A unique complete lowest-rate curve match in the source solver library identifies a filename stem; the same-named compatible target solver template is then loaded. Invalid individual templates are skipped; unmatched nonlinear materials use a warned elastic fallback. Elastic and rigid materials do not require template matching. See material_library.md for library units, curve scaling and detailed limits.

Setting > ABAQUS Translate opens one settings window. Towing L is the signed generated-hook length in model units; zero is invalid. Towing Model Select chooses an existing Abaqus INP/GEO solid mesh. Empty selection generates a cylinder. Templates retain their shape, material and length; the sign of L selects direction. See towing_nn.md for details.

## Console and shortcuts

The transcript is read-only and can be selected/copied. Blue separators distinguish operations, warnings use orange, and errors use bold red. New logs do not change unfinished commands. The vertical scrollbar remains visible with a contrasting wide handle. The latest 10,000 message blocks are retained in the visible transcript; file logs are unaffected.

Enter commands in the input row; Up/Down browse history. Console runs application commands only.

| Command | Action |
| --- | --- |
| -help | List commands |
| -new, -open | Create/open text |
| -save, -save as | Save/save as |
| -set work directory | Select/remember work directory |
| -translate | Translate current file |
| -license | Inspect/activate license |
| -device | Query hardware/network information |
| -documentation | Open this guide |
| -NN or -nn | Open training and validation; select Towing Hook NN or Towing Shape NN |
| -close | Close application |

Ctrl+S saves, Ctrl+N creates, Ctrl+O opens, Ctrl+E translates, Ctrl+F searches, and Esc closes search. Space opens a selected image preview.

## Licensing

Setting > License shows availability, bound IPv4 and expiration. Paste a code and select Activate. Activation is saved beside the application in config/circlecircle2.lic and read automatically at startup. Valid older user-directory licenses are migrated while preserving the old file. Licenses bind to the selected local IPv4 and expire relative to issuance time. Expired/mismatched licenses block translation while file viewing/editing remain available. Startup reports status once; each translation checks again. Settings and activation require a writable application directory.

Administrators run gui/license.py separately, select an IPv4 and validity period, generate a code, and paste it into the application. The issuer key is config/private_key.pem; verification uses config/public_key.pem. Back up the private key; distributions exclude it and issuer tools. Restore lost keys from backup: replacing the public key invalidates previous licenses.

Generate Public / Private Keys creates or reuses config/private_key.pem and config/public_key.pem. The config folder is created automatically. Existing key pairs are preserved; older keys are copied to these locations when absent. Verification reads config/public_key.pem and activation uses config/circlecircle2.lic.

## Device, help, cleanup and materials

Setting > Device queries CPU, GPU, PyTorch acceleration, active adapters' IPv4/IPv6/MAC and local time in the background. Unavailable dependencies/features are reported explicitly. Help > Documentation opens this guide independently. Help > Contact displays ludovica.chole@icloud.com.

Setting > Clear FEA Result separates preserved extensions from exact extensionless filenames, one entry per line, in config/clear_fea_result.json. Default extensions: .inp, .geo, .k, .key, .pc, .inc, .jpg, .png, .gif, .mp4, .avi, .md. The default exact filename is binout. Existing customized extension preferences remain in effect; add .md if absent. Right-click a folder to preview recursive deletion counts and preserved rules before confirming. Folder structure remains and links are not traversed. binout matches that exact name, not every extensionless file or numbered variant.

Material > GISSMO and Optimization > Structure / Thickness Refine report that they are under development. Material library files are maintained directly in the Material_Library folder; the former Export_Material action has been removed.

## Project and portable distribution

Run main.py using the project Python environment. See project_structure.md for module ownership and extension rules. core/fea contains parsers/translators, core/nn neural networks, core/hmdesktop HyperMesh integration, gui windows, utilities helpers, help_documentation guides, and config settings. net_services is reserved for network services.

Run pack.py to build dist/<build timestamp>/CircleCircle2/, installing PyInstaller if needed. Copy the entire directory including EXE and _internal. The build includes application modules, Qt, PyTorch and help; it excludes samples, developer work-directory preferences, existing licenses, logs and private keys. Select a directory and activate after deployment. HyperMesh integration requires an installed HyperMesh. pack.py --check checks dependencies/build inputs without installing/building. Initial tool installation requires network access; PyTorch increases build size. Use a writable deployment directory.

Windows Server display/runtime compatibility must be checked on the target OS with its installed Qt, GPU driver and HyperMesh versions. Automated offscreen tests do not establish complete server compatibility.

