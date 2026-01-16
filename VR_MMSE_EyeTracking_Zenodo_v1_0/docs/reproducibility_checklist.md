# Reproducibility Checklist for VR-MMSE Eye-Tracking Dataset

**Version**: 1.0
**Date**: 2026-01-16
**Target**: DADM submission

## Purpose

This checklist helps reviewers verify that all results in the manuscript can be reproduced from the provided data and code.

## Pre-upload Verification (✅ = Completed)

### 1. Data Quality Checks

- ✅ **Participant counts**: 3 groups × 20 participants = 60 total
- ✅ **ParticipantID unique**: All 60 IDs are unique, no duplicates
- ✅ **No missing Group labels**: All participants have valid group assignment
- ✅ **Age range reasonable**: 65-75 years (expected for AD/MCI studies)
- ✅ **Sex distribution**: Control (10M/10F), MCI (10M/10F), AD (10M/10F)
- ✅ **No personal identifiers**: ParticipantIDs are anonymized codes only

### 2. MMSE Score Validation

- ✅ **VR_MMSE_total ≠ MMSE_paper_total**: Confirmed not identical (different scales)
- ✅ **VR_MMSE range**: 0-21 (correct for VR-MMSE)
- ✅ **MMSE_paper range**: 0-30 (correct for traditional MMSE)
- ✅ **Group differences plausible**:
  - Control: VR_MMSE = 19.1±1.2
  - MCI: VR_MMSE = 17.2±1.3
  - AD: VR_MMSE = 10.8±1.4
- ✅ **Correlation check**: r(VR_MMSE, MMSE_paper) = [stored in results/sanity_checks/]

### 3. Eye-tracking Data Validation

- ✅ **ROI coverage complete**: All ROI strings mapped to KW/INST/BG types
- ✅ **No unclassified ROIs**: 100% coverage in `roi_mapping.csv`
- ✅ **Event types valid**: Only "fixation" and "saccade" in EventType column
- ✅ **Saccade amplitude range**: 0.98-65.28 degrees (plausible for VR eye-tracking)
- ✅ **No negative durations**: All Duration_ms >= 0
- ✅ **Task labels consistent**: Q1, Q2, Q3, Q4, Q5 across all files

### 4. Statistical Inference Level

- ✅ **Primary analysis unit**: Participant (N=60)
- ✅ **Avoided pseudoreplication**: ROI-level data aggregated to participant level before inference
- ✅ **Participant-task metrics**: 300 rows = 60 participants × 5 tasks ✓
- ✅ **Degrees of freedom correct**: df reflects N=60, not N=1,647 ROIs

### 5. Cross-Validation Protocol

- ✅ **Method**: 10-fold stratified cross-validation
- ✅ **Leakage-safe standardization**: StandardScaler fit on training folds only
- ✅ **Fixed random seed**: random_state=42 (reproducible splits)
- ✅ **Out-of-fold predictions saved**: `results/roc_cv/mci_cv_roc_results.csv`
- ✅ **Fold allocation documented**: Can regenerate identical folds with seed=42

### 6. ROC Analysis Results

#### MCI vs Controls

- ✅ **Cross-validated AUC**: 0.94
- ✅ **95% CI (Bootstrap)**: [0.84–1.00]
- ✅ **Sensitivity (Youden index)**: 100.0%
- ✅ **Specificity (Youden index)**: 85.0%
- ✅ **Features used**: VR_MMSE_total + 4 eye-tracking features
- ✅ **Model**: Logistic Regression (max_iter=1000, random_state=42)

### 7. Figures and Tables

- ✅ **Figure 3 terminology**: "Saccade Amplitude (deg)" ✓ (not "speed")
- ✅ **Figure axis labels**: Match manuscript units (degrees)
- ✅ **Figure colors**: Exact color codes documented (#496698, #F6A934, #EE3233)
- ✅ **Figure source data**: `results/figures/Fig3_source_data.csv` provided
- ✅ **Tables match code output**: Re-generated tables identical to manuscript

### 8. Code Reproducibility

- ✅ **Dependencies pinned**: `requirements.txt` includes version numbers
- ✅ **No absolute paths**: All scripts use relative paths from package root
- ✅ **Single entry point**: `04_roc_cv.py` and `05_figures.py` runnable independently
- ✅ **Random seed policy**: All random operations use seed=42
- ✅ **Software versions documented**: `results/sanity_checks/software_versions.txt`

### 9. Documentation Completeness

- ✅ **README.md**: Includes quick start, data description, key results
- ✅ **CITATION.cff**: Citation information provided
- ✅ **LICENSE files**: Data (CC BY 4.0) and Code (MIT) licenses included
- ✅ **Data dictionary**: All columns in all CSV files documented
- ✅ **ROI mapping rules**: Clear classification algorithm documented
- ✅ **MANIFEST.tsv**: Complete file inventory with SHA256 checksums

### 10. Privacy and Ethics

- ✅ **No names**: ParticipantIDs are anonymized codes only
- ✅ **No contact information**: Phone, address, email removed
- ✅ **No hospital IDs**: Original medical record numbers removed
- ✅ **No audio/video**: Raw VR recordings not included (only eye-tracking metrics)
- ✅ **No precise birthdates**: Only age in years provided
- ✅ **Aggregated data**: Small cell suppression not needed (all groups N=20)

## Post-upload Verification (for reviewers)

### Quick Reproduction Test

1. **Download and extract** the Zenodo package
2. **Install dependencies**:
   ```bash
   pip install -r code/requirements.txt
   ```
3. **Run MCI ROC analysis**:
   ```bash
   cd code
   python 04_roc_cv.py
   ```
4. **Expected output** (in `results/roc_cv/`):
   - `mci_cv_roc_results.csv`: 40 rows (20 Control + 20 MCI)
   - `mci_cv_roc_report.txt`: Contains AUC=0.94, CI=[0.84–1.00]
5. **Generate Figure 3**:
   ```bash
   python 05_figures.py
   ```
6. **Expected output** (in `results/figures/`):
   - `Figure3_Saccade_Amplitude_Publication.pdf`
   - `Figure3_Saccade_Amplitude_Publication.png`

### Verification Questions for Reviewers

1. ✅ **Can I locate the exact data used for Tables/Figures?**
   → Yes: `data/participant_level/participants_master.csv` and `participant_task_level_metrics.csv`

2. ✅ **Can I understand how ROI types are defined?**
   → Yes: `docs/roi_mapping_rules.md` provides clear classification algorithm

3. ✅ **Can I reproduce the ROC analysis?**
   → Yes: Run `code/04_roc_cv.py` with provided data and random seed

4. ✅ **Can I verify the manuscript numbers?**
   → Yes: Compare `results/roc_cv/mci_cv_roc_report.txt` with manuscript

5. ✅ **Can I trace repeated participant IDs?**
   → Yes: `data/group_level_adq_id/` files show ADQ_ID encoding (participant+task)

6. ✅ **Is the analysis statistically sound?**
   → Yes: Participant-level inference (N=60), leakage-safe CV, stratified folds

## Known Limitations and Decisions

1. **AD group participant IDs**: Start from ad03 (not ad01) due to original data collection
2. **ROI count variation**: Number of ROIs per task varies slightly by participant (6-8 per task)
3. **Missing ROI assignments**: Some saccade events don't have ROI assignment (expected)
4. **Short participant IDs**: Group-level files use "n1" instead of "n01" (historical naming)

## Changelog

### v1.0 (2026-01-16)
- Initial Zenodo release
- Passed all reproducibility checks
- Ready for DADM submission

---

**Questions?** If any checks fail or you cannot reproduce a result, please contact the authors via Zenodo comments or the corresponding author email in `CITATION.cff`.
