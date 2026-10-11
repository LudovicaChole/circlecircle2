# GUI, Console and Licensing

Start main.py in the project Python environment. Select File > Set Work Directory, then double-click files or drag them into the editor. The tree displays Name, Size and Date. Ctrl/Shift select multiple items; Ctrl+C/Ctrl+V create copies. Delete asks before removing files/folders permanently. New files do not overwrite existing files. Deleted open files keep their editor contents for Save as.

Supported text types: .inp, .geo, .k, .key, .pc, .inc, .txt, .py, .md and .json. Decoding errors are reported; large files load progressively. Switching files prompts for unsaved edits. Ctrl+F searches case-insensitively with an orange current-match highlight. Select an image/GIF and press Space to preview it; resizing scales the content and Space/Esc closes the window.

Console history is read-only but can be selected/copied. Enter commands in the separate input row; Up/Down browse history. Use -help for the list. -nn or -NN opens training/validation with Towing Hook NN and Towing Shape NN selections. Console does not execute arbitrary Python/system commands. Translation runs in the background and reports INFO/WARNING/ERROR without closing the GUI.

Translate is offered for Abaqus INP/GEO, LS-DYNA K/KEY and PAM-CRASH PC/INC, case-insensitively. Enabled target versions are Abaqus 6.14, PAM-CRASH 2020 and LS-DYNA 12.0/13.0 within implemented keyword coverage. Other versions report that they are under development. Reverse LS-DYNA output primarily covers materials. Setting > ABAQUS Translate opens length/template settings together.

Setting > Clear FEA Result has separate preserved-extension and exact-extensionless-name fields. Defaults include .md and binout. Right-click a folder to preview counts and confirm cleanup.

Administrators run gui/license.py, select/type IPv4, enter validity days, generate and copy a code. Activate through Setting > License. Validity starts at generation and binds to the selected local IPv4. Missing, expired or mismatched licenses block conversion; viewing/editing remain available. Activation is saved in config/circlecircle2.lic; work-directory settings use config/profile.setting. Older valid user-directory licenses migrate automatically.

The issuer uses config/private_key.pem; the application verifies with config/public_key.pem. Preserve/back up this pair. The key-generation button creates or reuses the pair directly in config, creating the folder automatically. Never distribute the private key or issuer tools.

Setting > Device or -device queries hardware, PyTorch acceleration, adapter addresses and local time in the background; missing dependencies/features are reported explicitly. Help > Contact displays ludovica.chole@icloud.com. See documentation.md through Help > Documentation for the full guide.

