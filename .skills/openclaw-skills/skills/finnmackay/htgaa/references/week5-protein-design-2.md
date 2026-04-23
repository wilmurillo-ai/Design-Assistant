# Week 5: Protein Design Part 2 — Advanced Tools & Applications

**Date:** Mar 3, 2026
**Lecturers:**
- Gabriele Corso (CEO/Co-Founder, Boltz) — Protein structure, molecular docking
- Pranam Chatterjee (Professor, UPenn Bioengineering) — Peptide design, programmable biology

## Topics

### Gabriele Corso (Boltz)
- Protein structure prediction advances
- Molecular docking and drug discovery
- Boltz platform for biomolecular structure

### Pranam Chatterjee (UPenn)
- Peptide design for therapeutic applications
- Language model approaches to protein/peptide generation
- Multi-objective optimization in peptide design
- SOD1 and ALS applications

### Recitation: Phage Therapy
- Instructors: Suvin Sundararajan, Dominika Wawrzyniak
- Bacteriophage biology and therapeutic applications

## Homework

### Part A: SOD1 Binder Peptide Design
Target: mutant SOD1 (A4V mutation — aggressive ALS)

1. Retrieve human SOD1 (UniProt P00441), introduce A4V mutation
2. Generate four 12-amino-acid peptides via **PepMLM** (include known binder FLYRWLPSRRGG)
3. Evaluate with **AlphaFold Server** (alphafoldserver.com)
4. Assess properties via **PeptiVerse** (binding affinity, solubility, hemolysis, charge, MW)
5. Generate optimized peptides using **moPPIt** with multi-objective guidance

### Part B: BRD4 Drug Discovery (Gabriele, optional)
- Boltz platform tutorial for drug discovery

### Part C: Final Project — L-Protein Mutants
- Improve stability and auto-folding of MS2-phage lysis protein
- Target: antibiotic resistance applications

## Key Tools
- **PepMLM** — Target sequence-conditioned peptide generation via masked language modeling
- **PeptiVerse** — Therapeutic peptide property prediction (HuggingFace)
- **moPPIt** — Motif-specific multi-objective peptide design
- **AlphaFold Server** — alphafoldserver.com
- **Boltz** — Biomolecular structure prediction (boltz.bio)
- **UniProt** — P00441 for human SOD1

## Key Concept: Peptide Design Pipeline
1. Identify target protein and binding site
2. Generate candidate peptides (PepMLM)
3. Predict 3D complex structure (AlphaFold)
4. Evaluate therapeutic properties (PeptiVerse)
5. Optimize with multi-objective constraints (moPPIt)
