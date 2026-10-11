# Towing Neural Networks and Abaqus Assembly

## Training and validation

NN training and validation require an active software license. Activation is checked when opening the window and before reading data, training or validating; expired licenses must be activated again through Setting > License.

1. Enter -nn or -NN in Console. The NN menu is hidden. Choose Towing Hook NN for hole-bearing parts or Towing Shape NN for the solid towing-hook template.
2. Choose a training folder. K/KEY shell and solid meshes are read recursively and split into per-file, per-PART point clouds.
3. Automatic labels are enabled by default: 1008.k identifies PART 1008 as target and all other parts as background. Multiple targets use 1008_1009.k. background.k marks all parts as background. Missing target meshes or targets with fewer than 12 nodes produce errors. Disable automatic labels for manual selection. Both target and genuine background examples are required.
4. Set epochs, learning rate and batch size; defaults are 100, 0.001 and 8. Select Train. CUDA is used when available, otherwise CPU. Progress appears in the window and Console. Cancellation preserves the previous saved model.
5. After training, select Validate Model on Separate Folder in the same window. Validation files follow the automatic filename labels above and must contain both classes. The report shows accuracy, target precision/recall, true/false positives and true/false negatives at the model's 0.9 confidence threshold. Set minimum precision and recall in the window (both default to 0.90). PASS/FAIL compares the measured results against those selected criteria; adjust them for your project. Reusing paths recorded in training is rejected. Renamed/copied training data must also be excluded manually.

Repeated IDs may appear in separate subfolders; samples remain scoped to files. Adding examples and training again retrains with the complete selected dataset, rather than incrementally updating weights. Complete assembly meshes are not retained after extraction. Expanded source content, including INCLUDE files, keys a disk point-cloud cache in config/nn_cloud_cache. Repeated loads avoid mesh parsing when content is unchanged. Changes invalidate the entry automatically; old cache files may be removed when no read is running. A read-only installation still trains without writing cache.

Point clouds are centered, scaled by maximum radius, and aligned to PCA principal axes. These operations account for rigid translation and rotation; near-symmetric PCA axes can remain ambiguous. Normalization is computed before epochs, with a bounded pool of up to 4096 points per part; batches sample 512 points and apply PCA sign/noise augmentation. Inference averages four deterministic sign variants. Classification is a lightweight PointNet-style shared point MLP with symmetric max pooling; PCA/cylinder fitting do not assign labels. This is not the complete published PointNet implementation.

Models are config/towing_hook_pointnet.pt and config/towing_towing_pointnet.pt. Settings are config/abaqus_translate.json beside the application. Missing weights generate an English warning and skip automatic towing assembly while conversion continues. Low training loss or correct recognition of training examples does not prove generalization. Include unseen shapes, orientations, mesh densities and realistic background examples in validation. Classification is per PART; multiple holes inside one complex PART are not segmented.

## Generated cylinders and signed length

Setting > ABAQUS Translate opens one settings window containing Towing L and Towing Model Select. L defaults to 300 model units and cannot be zero. Empty model selection generates a cylinder. Right-click a K file and translate through the implemented Abaqus 6.14 path. Abaqus 2024 translation remains under development.

Original hole nodes stay fixed. The cylinder axis is oriented so its largest absolute coordinate component is positive. Positive L aligns low ends and extends in the positive axis direction; negative L aligns high ends and extends in the negative direction. Switching signs aligns opposite end faces.

Generated solids use six-node C3D6 wedges, 32 radial sectors and axial subdivisions based on radius, with layers at overlap boundaries. The hole's material is reused and logged; use a material-bearing template for another material. Solid holes use exposed faces and element interiors to distinguish inner/outer walls. Shell-hole nodes represent midsurfaces; insert radius is the fitted midsurface radius minus half shell thickness.

Tie uses complete cylindrical wall faces in the overlap, excluding end caps. Insufficient overlap skips assembly with a message; increase length or refine the source mesh. Output nodes, elements, sets and surfaces are independently renumbered. IDs avoid source meshes, beams and generated rigid reference nodes. The original hole is the main surface and the inserted solid is secondary for *TIE, TYPE=SURFACE TO SURFACE, ADJUST=NO, avoiding extra secondary constraints on original coupled/constrained nodes. GEO mesh and INP analysis-entry outputs remain separate.

## Existing solid templates

Towing Model Select accepts a meshed Abaqus INP/GEO single solid part. GEO here means an Abaqus keyword mesh, not unmeshed CAD. Use Generated Hook to clear the selection.

Template assembly requires both weights: Towing Hook NN identifies hole parts; Towing Shape NN identifies the template solid. Rigid rotation/translation preserve its shape, length, connectivity and supported material/section. The absolute value of L does not stretch the template; its sign selects alignment direction. Radius mismatch skips assembly without scaling.

Supported elements are C3D6 and C3D8/C3D8R/C3D8I with uniform solid sections and standalone density, isotropic elasticity, plasticity, expansion and damping material blocks. Multi-instance assemblies, tetrahedra, higher-order elements, material orientations and unsupported keywords require a supported standalone mesh export; these are not silently discarded.

## Distribution and engineering checks

pack.py collects runtime modules while excluding license issuers/private keys and the developer's complete config folder. Users can train via -nn or install independently validated weight files in config beside the distributed application. Never copy a developer config folder containing private keys.

Tests are under test/towing_tests. reference_experiment.py runs GPU training, positive/negative-length conversion and template trials on supplied K files, writing reference_artifacts. These experimental weights are evaluated on training examples, are not installed into production config, and do not establish independent accuracy.

Automated checks cover generated mesh volumes, IDs, surface references and conversion workflows. Abaqus solver data-check/solution and graphical checks in HyperMesh 2026 still require the installed engineering applications. Inspect unbound Tie nodes, element quality and overlap before analysis. Generated models do not automatically define towing loads or boundary conditions.

## Official references

- [HyperMesh 2026 Python API](https://help.altair.com/hwdesktop/pythonapi/index.html)
- [LS-DYNA keyword manuals](https://lsdyna.ansys.com/manuals-download/)
- [Abaqus Keywords Guide](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEKEYRefMap/simakey-c-ov.htm)
- [Abaqus mesh tie constraints](https://docs.software.vt.edu/abaqusv2025/English/SIMACAECSTRefMap/simacst-c-tiedconstraint.htm)
- [PointNet paper](https://arxiv.org/abs/1612.00593)
- [Efficient RANSAC for Point-Cloud Shape Detection](https://onlinelibrary.wiley.com/doi/10.1111/j.1467-8659.2007.01016.x): background for robust shape fitting. The application's candidate-axis, projected-circle sampling and weighted least-squares implementation does not reproduce that algorithm fully.


