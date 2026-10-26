# Candidate Knowledge Base Setup Guide

All files in this directory are strictly local to each user's machine and are **never synced to the cloud or committed to Git** (enforced by `.gitignore`).

## Quick Setup
1. Copy the example files from `knowledge_base.example/` into a local `knowledge_base/` directory:
   ```bash
   cp -r knowledge_base.example knowledge_base
   ```
2. Populate `candidate_profile.json`, `skills_inventory.md`, and `experience_matrix.md` with your verified career background.
3. Your local studio will automatically detect and ground all resume tailoring, ATS scoring, and cover letters using your local files.
