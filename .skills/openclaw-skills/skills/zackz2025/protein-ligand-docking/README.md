# Protein-Ligand In Silico Docking Workflow

![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Stage](https://img.shields.io/badge/Stage-Beta-orange)

A complete **in silico protein-ligand molecular docking pipeline** powered by OpenClaw. From sequence retrieval and structure modeling to molecular docking and quantitative analysis — fully automated.

## 🎯 What This Does

Answer questions like:
- **"Can Drug X bind to Protein Y?"**
- **"How selective is this inhibitor between bacterial and human proteins?"**
- **"Does this inhibitor act through direct bactericidal or indirect mechanisms?"**

## 📐 Workflow Overview (7 Steps)

```
Step 1: Sequence Retrieval (UniProt API)
         ↓
Step 2: PDB Structure Search (RCSB PDB API)
         ↓
Step 3: Sequence Alignment (Biopython)
         ↓
Step 4: AlphaFold-Multimer Modeling (Google Colab)
         ↓
Step 5: Model Quality Assessment (pLDDT + PAE)
         ↓
Step 6: AutoDock Vina Molecular Docking
         ↓
Step 7: Quantitative Analysis & Report Generation
```

## 🔧 Installation

### Install the Skill

```bash
# Using OpenClaw's clawhub CLI
clawhub install protein-ligand-docking
```

Or manually clone this repository into your OpenClaw skills directory:

```bash
git clone https://github.com/YOUR_USERNAME/openclaw-protein-ligand-docking.git \
  ~/.openclaw/workspace/skills/protein-ligand-docking
```

### Install Dependencies

```bash
# Python packages
pip install biopython pandas numpy matplotlib
pip install rdkit openbabel-wheel
pip install py3Dmol python-docx

# AutoDock Vina (WSL/Linux)
wget https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.7/vina_1.2.7_linux_x86_64 -O vina
chmod +x vina
```

## 📁 File Structure

```
protein-ligand-docking/
├── SKILL.md                                  # OpenClaw skill definition (this file is the main entry point for the AI)
├── README.md                                 # This file
├── LICENSE                                   # MIT License
├── notebooks/
│   └── alphafold_multimer_colab.ipynb        # AlphaFold-Multimer Colab template
└── scripts/
    ├── step3_alignment.py                    # Sequence alignment
    ├── step5_pae_analysis.py                 # Model quality + Grid Box calculation
    ├── step6_vina_docking.py                 # AutoDock Vina docking
    └── step7_summary_report.py               # Report generation
```

## 🚀 Quick Start

### Typical Command Examples

#### Step 3: Sequence Alignment
```bash
python scripts/step3_alignment.py \
    --query1 human_target_ct.fasta \
    --query2 bacterial_target.fasta \
    --name1 "Human_Target_CT" \
    --name2 "Bacterial_Target" \
    --output_dir ./03_alignment
```

#### Step 5: Model Quality + Grid Box
```bash
python scripts/step5_pae_analysis.py \
    --pdb AF_complex_rank_001.pdb \
    --pae_json predicted_aligned_error_v1.json \
    --chain_a A --chain_b B \
    --chain_a_len 194 --chain_b_len 303 \
    --output_dir ./05_results
```

#### Step 6: Vina Docking
```bash
python scripts/step6_vina_docking.py \
    --receptor_pdb receptor.pdb \
    --ligand_sdf drug_candidate.sdf \
    --center_x -1.5 --center_y 3.3 --center_z -5.0 \
    --size 25 \
    --vina_path ./vina \
    --output_dir ./04_docking
```

#### Step 7: Generate Report
```bash
python scripts/step7_summary_report.py \
    --workspace ./ \
    --protein_name "Bacterial_Protein" \
    --ligand_name "Drug_Candidate" \
    --alignment_json 03_alignment/alignment_results.json \
    --model_quality_json 05_results/model_quality_results.json \
    --docking_summary_json 04_docking/docking_summary.json \
    --output_name Complete_Summary
```

## 📊 Output Interpretation

### Binding Affinity
| Binding Energy | Strength |
|----------------|----------|
| < -9 kcal/mol | Strong binding |
| -7 ~ -9 kcal/mol | Moderate |
| > -7 kcal/mol | Weak / not meaningful |

### Sequence Similarity → Conservation
| Similarity | Inference |
|------------|-----------|
| > 40% | Binding pocket likely conserved, proceed |
| 20-40% | Uncertain, structural analysis needed |
| < 20% | Likely not conserved |

### Model Quality Thresholds
- **pLDDT > 70**: Confident single-chain fold
- **PAE < 15 Å**: Interface position reliable for docking

## ⚠️ Limitations

1. **Static Docking**: Does not account for ligand-induced fit and conformational changes
2. **AlphaFold Limitations**: N/C-terminal disordered regions may be missing; interface PAE has estimation errors
3. **Force Field**: Vina scoring function may be inaccurate for certain compound classes
4. **Gold Standard**: SPR, ITC, and enzyme inhibition assays are required for experimental validation

## 👥 Use Cases

- Antimicrobial drug target discovery and validation
- Selectivity profiling (host vs pathogen)
- Drug-host-microbiome interaction studies
- Mechanism-of-action research for novel compounds

## 📜 License

MIT License — see [LICENSE](LICENSE) file for details.

---

*This is an OpenClaw Skill. For more information about OpenClaw, visit [openclaw.ai](https://openclaw.ai).*
