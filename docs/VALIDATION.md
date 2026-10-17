# Validation scope

## Mechanical release

The 18 STL files are copied without geometry changes from the reviewed final export package. `tools/validate_release.py` verifies SHA-256, byte sizes, quantities, binary STL triangle lengths, native FreeCAD archive integrity, presence of STEP exchange files and the manual PDF. Publication was separately scanned for credential-looking content and private workstation paths.

Previously completed geometric and fastening review is recorded in `assembly/Micro_Dog_fastener_dimensional_audit.txt`, `assembly/assembly_access_review.txt` and the assembly PDF. Those records are nominal CAD assessments. They do not establish physical manufacturability, safe torque, strength, payload or full-motion clearance. STL topology checks are re-run when trimesh is installed; otherwise the checker reports that stage as skipped.

The assembly diagrams simplify fasteners. Their color-coded screws are specification/sequence aids, not full certified fastener CAD. Hardware counts exclude horn center screws and spare parts. Bearing width must be checked: MR137ZZ 7×13×4 and small 6×10×2.5.

## Native editing documents

The selected FreeCAD documents preserve editable work and may contain hidden intermediate/reference objects. STEP/STL files and print-manifest hashes are the manufacturing baseline. A FreeCAD archive integrity check is not a full recompute or feature-tree equivalence test.

## Robot description

Read the description package's own validation report and README for tests performed, coordinate conventions, closed-chain approximation and mass/inertia assumptions. The central box remains a parametric stand-in. No powered hardware, real gait, controller tuning, ROS launch or simulator stability is implied unless explicitly reported there.

## CI

The original destination repository had no workflows or required automated test suite. No GitHub Actions permissions or CI installation are added by this publication.
