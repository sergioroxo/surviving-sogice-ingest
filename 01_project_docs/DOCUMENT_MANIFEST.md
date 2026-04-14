# SurvivingSOGICE — Document Manifest for New PRD Chat
**April 2026 · Send these documents to the new chat in this order**

---

## Documents to send — complete list

Send all of these. The new chat needs all of them to build a well-informed PRD.

---

### 00_infrastructure/ — The ontology spine (send all four)

**1. SOGICE_Ontology_v2.1.md**
What it is: The structural spine. Seven cluster definitions, tactic-to-cluster mapping, tag instance structure with ai_metadata and layer field, entity model, asset extraction protocol, multilingual term model, visibility framework, open questions register.
Size: ~312 lines
Send first.

**2. SOGICE_Ontology_v2.2_additions.md**
What it is: Supplement to v2.1. Adds the Practice-Regulatory Layer: LegalDefinition and ExclusionClause entity types, updated tag fields (target_dimensions, goal_verbs, jurisdiction, stance_profile), attestation tiers for multilingual terms, new legal terms (Greek, Maltese, Spanish), new European laws and events, the AffirmativeOrExploratorySupport boundary concept, ILGA-Europe practice taxonomy alignment.
Size: ~600 lines
Send second, after v2.1.

**3. SOGICE_Lexicon_v1.1.md**
What it is: Complete term definitions — all seven clusters, full slurs section (Section 8), reference terms (Section 9), shorthand table (Section 10), multilingual quick reference (Section 11). Every term has: definition, promotional use rule, related terms, source.
Size: ~543 lines
Send third.

**4. Entity_Registry_v1.1.md**
What it is: Seed list of all known Persons (~15), Organizations (~50, both pro- and anti-SOGICE), Laws/Policies (~12), Events (~10). Includes new additions from April 2026: Greece N.4931/2022, Norway §270 (in force 2024), PACE Resolution 2643, European Citizens' Initiative, ILGA-Europe Intersections 2.0.
Size: ~750 lines
Send fourth.

---

### 01_project_docs/ — Project context

**5. PRD_v1.0.md**
What it is: Full product requirements document. Covers: platform architecture (Sanity + Supabase dual-layer), ingestion pipeline step-by-step, algorithmic hybrid model (NER/TF-IDF/BERTopic/NetworkX), storage and backup system (GitHub LFS + 250GB), experience modules (all nine), integration points, non-functional requirements, phase summary, open questions register.
Size: ~600 lines

**6. Vision_Brief.md**
What it is: The creative platform concept. i-Doc shell as retro OS navigation metaphor, all nine experience modules described, three-register platform model (archive/lexicon/experience layer), phase structure.
Note: This file is in your project files — copy it to the folder you are sending.

---

### 02_working_tools/ — Working tools

**7. TAGGING_GUIDE.md**
What it is: The practical tagging guide for researcher and intern. Covers the hardest distinction calls: Organization-Claim vs Propaganda, all the confusable tactic pairs (Rebranding-SOGICE vs Policy-Resistance-Frame, False-Scientific-Authority vs Social-Contagion-Myth, Anti-Gender vs Anti-LGBT Conspiracy, Anti-Trans vs ROGD vs Detrans), country tagging rules, needs_review criteria.
Note: This file is in your project files — copy it to the folder.

**8. SOGICE_LLM_Prompt.md**
What it is: System prompt for using external LLMs (Copilot, GPT-4) when the built-in tagger is not available. Produces tagger-compatible JSON output.
Note: This file is in your project files — copy it to the folder.

**9. NotebookLM_Questionnaire.md**
What it is: The 11-step extraction questionnaire for running against the corpus in NotebookLM. Covers corpus inventory, terminology harvest for each cluster, actor/network mapping, transnational patterns, harm documentation, and cross-collection distinction questions.
Note: This document was written in this conversation — not yet a separate file. If you need it, tell me and I will produce it as a standalone file.

---

### What to tell the new chat

Open the new chat and say something like:

> "I am building a PRD for SurvivingSOGICE, a PhD research platform at the University of Bergen studying SOGICE (conversion therapy) networks in Europe. I am going to send you a set of documents. Please read all of them before we begin. I will tell you when I have sent everything."
>
> Then send the documents one at a time, in order, each in a separate message. After the last one, say: "Those are all the documents. Now let us begin."

---

### What is NOT needed for the new chat

These files exist but the new chat does not need them:
- SOGICE_Ontology_v1.0.md (superseded by v2.1)
- SOGICE_Ontology_v1.1_updates.md (superseded by v2.1)
- SOGICE_Lexicon_v1.0.md (superseded by v1.1)
- Entity_Registry_v1.0.md (superseded by v1.1)
- sogice_log_YYYY-MM-DD.json (data export, not architecture)
- sogice_glossary_YYYY-MM-DD.json / .csv (data export)
- SOGICE_Vocabulary.json (superseded by Lexicon v1.1)

---

### Complete folder structure as of April 2026

```
survivingsogice/
|-- 00_infrastructure/
|   |-- SOGICE_Ontology_v2.1.md          SEND (1)
|   |-- SOGICE_Ontology_v2.2_additions.md SEND (2)
|   |-- SOGICE_Lexicon_v1.1.md            SEND (3)
|   |-- Entity_Registry_v1.1.md           SEND (4)
|   +-- Tagging_Decision_Guide_v1.0.md    TO PRODUCE
|
|-- 01_project_docs/
|   |-- PRD_v1.0.md                       SEND (5)
|   |-- PROJECT_DESCRIPTION.md            (not needed for PRD chat)
|   +-- Vision_Brief.md                   SEND (6) -- copy from project files
|
|-- 02_working_tools/
|   |-- TAGGING_GUIDE.md                  SEND (7) -- copy from project files
|   |-- SOGICE_LLM_Prompt.md              SEND (8) -- copy from project files
|   +-- NotebookLM_Questionnaire.md       SEND (9) -- produce if needed
|
+-- 03_data/
    |-- SOGICE_Vocabulary.json             (not needed for PRD chat)
    |-- sogice_log_YYYY-MM-DD.json         (not needed)
    +-- sogice_glossary_*.json/.csv        (not needed)
```

---

### One document still to produce

**Tagging_Decision_Guide_v1.0.md** — the short intern-facing practical guide (country rules, when to use Term vs Tactic, how to flag promotional vs critical use, how to handle testimony). Not yet produced. If you need this before the new chat, ask me to produce it now.

---

*Document Manifest · April 2026 · SurvivingSOGICE · University of Bergen*
