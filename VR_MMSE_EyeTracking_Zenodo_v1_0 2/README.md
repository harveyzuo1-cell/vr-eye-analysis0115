# VR-MMSE + Eye-Tracking (Zenodo Release v1.0)

**Generated**: 2026-01-16
**Target**: DADM submission (reproducibility-first)
**DOI**: [To be assigned by Zenodo]

## What is included

- **Participant-level dataset** (N=60; 3 groups × 20 participants)
- **Group-level ADQ_ID files** for data traceability
- **ROI dictionary + mapping rules** (KW/INST/BG classification)
- **Reproducibility code** to regenerate Tables/Figures and cross-validated ROC results
- **Pre-generated results** (ROC metrics, figures, sanity checks)

## Cohort summary

| Group | N | Age (mean±SD) | VR-MMSE (mean±SD) |
|-------|---|---------------|-------------------|
| Control | 20 | 70.8±2.8 | 19.1±1.2 |
| MCI | 20 | 69.4±2.4 | 17.2±1.3 |
| AD | 20 | 70.4±3.4 | 10.8±1.4 |

**Total**: 60 participants
**Exclusions**: None (all participants included in analysis)

## Quick start (reproduce key outputs)

### 1) Create environment

```bash
pip install -r code/requirements.txt
```

### 2) Run cross-validated ROC analysis

```bash
cd code
python 04_roc_cv.py
```

**Expected output**:
- `results/roc_cv/mci_cv_roc_results.csv` (out-of-fold predictions)
- `results/roc_cv/mci_cv_roc_report.txt` (AUC, 95% CI, sensitivity, specificity)

### 3) Generate Figure 3

```bash
python 05_figures.py
```

**Expected output**:
- `results/figures/Figure3_Saccade_Amplitude_Publication.pdf`
- `results/figures/Figure3_Saccade_Amplitude_Publication.png`

### 4) Outputs are written to

- `results/tables/` - Primary analysis tables
- `results/figures/` - Publication-ready figures
- `results/roc_cv/` - Cross-validated ROC metrics
- `results/sanity_checks/` - Data quality checks

## Data files

### Participant-level (primary analysis)

- `data/participant_level/participants_master.csv` - Main dataset (N=60, one row per participant)
  - Demographics, MMSE scores, eye-tracking features for ROC models
- `data/participant_level/participant_task_level_metrics.csv` - Task-level metrics (N=300, 60×5 tasks)
  - Saccade amplitude, fixation metrics per participant per task

### Group-level (with ADQ_ID, for traceability)

- `data/group_level_adq_id/CTRL_All_Folders_ROI_Summary.csv`
- `data/group_level_adq_id/MCI_All_Folders_ROI_Summary.csv`
- `data/group_level_adq_id/AD_All_Folders_ROI_Summary.csv`
- `data/group_level_adq_id/CTRL_All_Folders_Events.csv`
- `data/group_level_adq_id/MCI_All_Folders_Events.csv`
- `data/group_level_adq_id/AD_All_Folders_Events.csv`

**Purpose**: Allow reviewers to trace repeated participant IDs (e.g., m06 appears 25 times = 5 tasks × 5 ROIs) and verify data provenance.

## ROI mapping

See:
- `docs/ROI_Dictionary.txt` - Human-readable ROI descriptions
- `docs/ROI_Mapping.csv` - Machine-readable ROI type classifications

**ROI types**:
- **KW** (Keywords): Target words in each task (e.g., time words, location names)
- **INST** (Instructions): Task instruction regions
- **BG** (Background): Background regions (used to detect off-task attention)

## Key results (from manuscript)

### MCI vs Controls - Cross-Validated ROC

- **Cross-validated AUC**: 0.94 (95% CI: 0.84–1.00)
- **Sensitivity**: 100.0% (at optimal Youden index threshold)
- **Specificity**: 85.0%
- **Method**: 10-fold stratified cross-validation with leakage-safe standardization

**Interpretation**: The VR-MMSE eye-tracking features combined with cognitive scores provide excellent discrimination between MCI and healthy controls.

## Analysis approach

### Pseudoreplication avoidance

- **Primary inference unit**: Participant (N=60)
- **ROI-level data**: Used for feature extraction only (not for statistical inference)
- **Cross-validation**: 10-fold stratified, leakage-safe standardization (StandardScaler fit on training folds only)

### Features used for ROC models

1. VR_MMSE_total (cognitive score)
2. Mean_FixTime (average ROI dwell time across all ROIs)
3. Mean_EnterCount (average ROI entry count)
4. Mean_RegressionCount (average regression count)
5. Mean_Saccade_Amplitude (average saccade amplitude in degrees)

## License and citation

### Data license
- **License**: CC BY 4.0 (see `LICENSE_DATA_CC_BY_4_0.txt`)
- **Attribution**: Required when reusing data

### Code license
- **License**: MIT (see `LICENSE_CODE_MIT.txt`)
- **Usage**: Free for academic and commercial use

### Preferred citation
See `CITATION.cff` for BibTeX and structured citation information.

## Contact

For questions about this dataset or manuscript, please contact:
- [Your Name/Email]
- [Corresponding Author]

## Version history

### v1.0 (2026-01-16)
- Initial Zenodo release
- Includes MCI vs Controls cross-validated ROC analysis
- Publication-ready Figure 3 with corrected terminology (saccade amplitude)
- Complete ROI dictionary and mapping rules

## File integrity

See `MANIFEST.tsv` for complete file inventory with SHA256 checksums.

## Reproducibility checklist

- ✅ N=60 participants (3 groups × 20)
- ✅ No personal identifiers (ParticipantIDs are anonymized codes)
- ✅ Participant-level inference (avoids pseudoreplication)
- ✅ Leakage-safe cross-validation (StandardScaler fit on training only)
- ✅ Fixed random seed (random_state=42)
- ✅ Pre-generated results match code outputs
- ✅ ROI type classifications documented
- ✅ Figure axis labels and units match manuscript

---

**This dataset supports the manuscript**: "VR-based MMSE with Eye-Tracking for Alzheimer's Disease and MCI Detection"
**Submitted to**: Diagnosis, Assessment & Disease Monitoring (DADM)
