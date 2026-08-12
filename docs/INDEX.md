# CelLAB Documentation Index
Keywords: cellab, cellular analysis, workbench, platform, pipeline, packages

## Platform
Keywords: project, workspace, pipeline, version control, console, task manager, GUI
Description: CelLAB is a unified workbench for cellular analysis with ANSYS/COMSOL-inspired GUI, parameter version control, and AI assistant.
See: platform/OVERVIEW.md

## Packages

### Cornealia
Keywords: corneal, cornea, endothelium, endothelial, specular microscopy, cell density, hexagonality, morphometry, radial distribution, g(r), V(r), collective order, K value, interaction potential, Morse fit, CD, CV, HEX, Ave, batch, AS, BS
Solves: Corneal endothelial cell morphometric analysis from specular microscopy images. Computes radial distribution function g(r), interaction potential V(r), collective order parameter K, and clinical metrics (CD, CV, HEX, Ave).
See: cornealia/OVERVIEW.md

### FASTIA
Keywords: focal adhesion, FA, timelapse, fluorescence, detection, tracking, classification, kinetics, lifetime, assembly, disassembly, nascent, focal complex, mature, fibrillar, GFP-paxillin, TIRF
Solves: Focal adhesion dynamics analysis from fluorescence timelapse microscopy. Detects, tracks, classifies, and quantifies FA lifecycle.
See: fastia/OVERVIEW.md

### IMMUNIA
Keywords: immune, NK cell, natural killer, tumor, chemotaxis, tracking, migration, Keller-Segel, particle tracking, dead cell, cytotoxicity, timelapse, multi-channel
Solves: Immune cell tracking and chemotaxis analysis from multi-channel timelapse microscopy. Segments, tracks, and models immune-tumor interactions.
See: immunia/OVERVIEW.md

### CellADE
Keywords: cell segmentation, watershed, FCM, fuzzy c-means, LoG, Laplacian of Gaussian, edge detection
Solves: Cell segmentation engine using FCM clustering + watershed. Used internally by Cornealia.
See: cellade/OVERVIEW.md (planned)

### CellFADE
Keywords: focal adhesion detection, deep learning, U-Net, segmentation mask, FA mask
Solves: Deep learning-based focal adhesion detection from fluorescence images.
See: cellfade/OVERVIEW.md (planned)

### MigraFiBA
Keywords: migration, fiber, actin, analysis, cell motility
Solves: Cell migration and fiber orientation analysis.
See: migrafiba/OVERVIEW.md (planned)

### MRheologia
Keywords: microrheology, bead tracking, viscoelastic, MSD, creep compliance
Solves: Microrheology analysis from bead tracking data.
See: mrheologia/OVERVIEW.md (planned)
