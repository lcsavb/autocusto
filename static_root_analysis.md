# Static Root PDF File Analysis

**Analysis Date**: 2025-07-18  
**Total Files Analyzed**: 134 PDF files  
**Total Space Used**: 31.82 MB

## 1. Overall Directory Structure & File Count

- **Total PDF files**: 134 files
- **Total space used**: 31.82 MB
- **Main directories**:
  - `/static_root/protocolos/` - 113 files (25.61 MB) - Disease protocol templates
  - `/static_root/processos/` - 11 files - Application base templates
  - `/static_root/` (root) - 10 files - Legacy base templates

## 2. File Categories & Usage

### A. Active Application Templates (USED)
These files are referenced in `settings.py` and `paths.py`:
- `processos/lme_base_modelo.pdf` (1.1M) - **USED**
- `processos/relatorio_modelo.pdf` (39K) - **USED** 
- `processos/sadt.pdf` (165K) - **USED**
- `processos/exames_base_modelo.pdf` (44K) - **USED**
- `processos/rce_modelo.pdf` (198K) - **USED**

### B. Disease-Specific Templates (POTENTIALLY USED)
Located in `protocolos/` subdirectories:
- `protocolos/artrite_reumatoide/` - 3 files (765K)
- `protocolos/doenca_de_alzheimer/` - 7 files (1.1M)
- `protocolos/esclerose_multipla/` - 6 files (365K)
- `protocolos/epilepsia/` - 2 files (224K)
- `protocolos/dislipidemia/` - 2 files (313K)
- `protocolos/esquizofrenia/` - 1 file (75K)
- `protocolos/doenca_de_parkinson/` - 2 files (148K)
- `protocolos/dor_crônica/` - 3 files (2.6M)

### C. Numbered Protocol Templates (LIKELY UNUSED)
113 numbered files like `1_acnegrave_v8_2.pdf`, `12_artritereumatoide_v21.pdf`, etc.
- These appear to be legacy protocol templates
- **Space used**: ~20 MB
- **Status**: Likely outdated/unused

## 3. Identified Duplicates & Issues

### A. Exact Duplicates (SAFE TO REMOVE)
10 files that are identical copies between root and `/processos/`:
- `exames_base_modelo.pdf` - 2 copies (44K each)
- `lme_base_modelo.pdf` - 2 copies (1.1M each) 
- `rce_modelo.pdf` - 2 copies (198K each)
- `sadt.pdf` - 2 copies (165K each)
- `relatorio_modelo.pdf` - 2 copies (39K each)
- Plus backup versions of above
- **Total space savings**: 2.61 MB (8.2% reduction)

### B. Broken Path References
Code references paths that don't exist:
- `static_root/processos/artrite_reumatoide/` - **MISSING** (code expects this)
- `static_root/processos/alzheimer/` - **MISSING** (code expects this)
- `static_root/processos/esclerose_multipla/` - **MISSING** (code expects this)

**Actual locations are in** `static_root/protocolos/` instead.

### C. Backup Files (REVIEW NEEDED)
21 backup files with `*backup*` pattern:
- Some are identical to main files
- Others are different versions
- **Decision needed**: Keep recent backups, remove old ones

## 4. Recommended Cleanup Actions

### Immediate Actions (Safe)
1. **Remove duplicate files** (2.61 MB savings):
   ```bash
   # Remove these 10 duplicate files from static_root/ (keep processos/ versions)
   rm static_root/exames_base_modelo.pdf
   rm static_root/lme_base_modelo.pdf  
   rm static_root/rce_modelo.pdf
   rm static_root/sadt.pdf
   rm static_root/relatorio_modelo.pdf
   # Plus their backup versions
   ```

2. **Fix path inconsistencies**:
   - Update code to use correct paths in `protocolos/` not `processos/`
   - Or create symlinks to maintain compatibility

### Review Needed
1. **Numbered protocol files** (~20 MB):
   - Verify if any are still needed
   - Consider archiving vs deletion
   - Most appear to be legacy templates

2. **Backup file retention policy**:
   - Keep only necessary backups
   - Remove old/duplicate backup versions

### Potential Total Savings
- **Conservative cleanup**: 2.6 MB (duplicates only)
- **Aggressive cleanup**: 20-25 MB (if numbered protocols are unused)
- **Final optimized size**: 7-12 MB (from current 31.82 MB)

## 5. Critical Files to Preserve
These are actively used by the application:
- `/processos/lme_base_modelo.pdf`
- `/processos/relatorio_modelo.pdf` 
- `/processos/sadt.pdf`
- `/processos/exames_base_modelo.pdf`
- `/processos/rce_modelo.pdf`
- Disease-specific directories in `/protocolos/`

## 6. tmpfs Optimization Impact
After cleanup, the static_root would be optimized from **31.82 MB** to **7-12 MB**, making it much more suitable for tmpfs deployment and improving PDF generation performance.

## Status
The static_root directory contains significant redundancy and unused files. A cleanup could reduce size by 60-75% while maintaining all functionality.