# Cornealia — Troubleshooting
Keywords: error, crash, fail, NaN, zero, reliable, segmentation, fix, debug, cultured, phase contrast, pixel size, force field, invert

## Common Errors

### "0 interior cells" or very few interior cells
- Cause: Image is too small or `exclusion_ratio` is too large
- Fix: Reduce `exclusion_ratio` from 0.15 to 0.10 or 0.08
- Check: `results['n_interior']` should be > 50 for reliable analysis

### Analysis returns reliable=False
- Cause: Low cell count, poor image quality, or non-standard tissue
- Check: `results['R2_damped']`, `results['has_peak']`, `results['has_crossing']`
- Fix: Ensure image has clear cell boundaries. Try different `fcm_method` ('local' vs 'global')

### K = 0, NaN, or very large
- Cause: Morse/LJ fit failed or converged to degenerate parameters
- Fix: Adjust `fitting_half_width` (try 8, 10, 12, 15). Check V(r) shape with `plotter.fitting()`
- Check: `plotter.comprehensive()` shows all diagnostic info

### OCR extraction fails (machine_metrics = None)
- Cause: Non-standard machine output format, low resolution, or non-machine image
- Fix: Set `is_input_image_machine_output=False` if using raw images
- Note: EasyOCR needs ~500MB RAM per worker. Low memory causes silent failures.

### Segmentation misses cells or over-segments
- Cause: Poor contrast, non-standard staining, or wrong FCM method
- Fix: Try `fcm_method='global'` instead of 'local' (or vice versa)
- Fix: Adjust CellADE parameters: `min_expansion_shells`, thresholds

### Batch processing: some images fail
- Normal behavior: `_collective_order_safe()` catches per-image errors
- Check: Look for `'error'` key in results: `[r for r in results if 'error' in r]`
- Common: Very dark images, non-endothelial tissue, corrupted files

### Batch plotter: "index out of bounds" or grid errors
- Cause: Some CSV columns missing (old format or failed computations)
- Fix: Dynamic grid handles this now — update to latest `cornealia_batch_plotter.py`

### AS/BS groups not detected (AS: 0, BS: 0)
- Cause: Image filenames don't contain 'AS' or 'BS' suffix
- Fix: Rename files to include ' AS' or ' BS' before extension
- Example: `"001-3731L AS.jpg"`, `"001-3731L_BS.png"`
- Note: Extension is stripped before parsing

### Memory issues with large batches
- Cause: Each worker loads EasyOCR model (~500MB)
- Fix: Reduce `n_workers`. 10 workers ≈ 5GB RAM.
- Fix: For 100+ images, use 4-6 workers to stay under 4GB

### matplotlib backend errors
- Cause: Importing cornealia triggers GUI backend on servers
- Fix: `import matplotlib; matplotlib.use('Agg')` BEFORE importing cornealia
- CelLAB handles this automatically in app.py

### Cultured cell images don't segment properly
- Cause: Phase-contrast images have inverted contrast (dark cells on light background)
- Fix: Set `invert_image=True` and `is_input_image_machine_output=False`
- Example: `cornealia(pixel_size=0.34, invert_image=True, is_input_image_machine_output=False)`
- Note: pixel_size varies by microscope — check your 20× or 10× calibration

### K values in µm⁻² seem wrong but px⁻² looks fine
- Cause: Wrong `pixel_size` — all µm conversions use K_um = K_px / pixel_size²
- Fix: Verify pixel_size matches your microscope. Common values: 0.58 (CellChek D), 0.45 (Topcon SP-1P), 0.34 (Heidelberg)
- Note: px-based K values and reliability flag are unaffected by pixel_size

### K_ds = 0 or NaN (but K_morse_guided is valid)
- Cause: Quality gate fit succeeded (reliable=True) but V''(r₀) on the fitted curve is near zero or negative
- Check: `results['popt_qc']` — if ξ is very large, the oscillation is too weak for meaningful K_ds
- This is rare; if it occurs, K_morse_guided is the fallback

### Force field returns NaN or missing keys
- Cause: Fewer than 4 interior cells — Delaunay triangulation requires ≥ 4 points
- Fix: Reduce `exclusion_ratio` or use a larger image
- Check: `results.get('mean_F', None)` — None means force field was skipped

### Dark-on-light images produce no cells
- Cause: CellADE expects light-on-dark (bright cell boundaries)
- Fix: Set `invert_image=True` in the constructor

## Diagnostic Workflow
1. Run single image with `verbose=True`
2. Check console output: cell counts, timing, quality gate results
3. Run `plotter.comprehensive()` to visualize all steps
4. If segmentation looks wrong → adjust CellADE params
5. If g(r) is flat → image may lack cellular structure
6. If V(r) fit is poor → adjust `fitting_half_width`
7. If K seems wrong → compare with `K_ds` (damped sine method)
