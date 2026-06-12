# TextileBot Pro

Plateforme IA textile pour la conformité, la recherche documentaire RAG et la génération de rapports PDF.

## Fonctionnalités

- Chat RAG textile avec filtrage hors domaine, citations de sources et score de confiance.
- Intégration Ollama avec `llama3.2:3b` par défaut, plus fallback local textile quand Ollama est indisponible.
- Recherche hybride vectorielle + lexicale avec re-ranking léger.
- Analyse de conformité déterministe avec trois statuts: `compliant`, `non_compliant`, `conditional`.
- Rapports PDF professionnels avec statut, confiance, composition, étiquette et références.
- Scripts de préparation dataset JSONL et squelette QLoRA pour fine-tuning.
- Interface React: dashboard, documents, chat, conformité et historique.

## Démarrage backend

```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

API: `http://localhost:8000`

## Démarrage frontend

```bash
cd frontend
npm install
npm run dev
```

Interface: `http://localhost:5173`

## Ollama

```bash
ollama pull llama3.2:3b
```

La variable `LLM_MODEL_ID` peut être changée dans `.env`.

## Dataset et fine-tuning

Créer un dataset JSONL:

```bash
python backend/scripts/build_training_dataset.py --input textilbot_chat_dataset.csv textilbot_compliance_dataset.csv --output data/training/textilebot_sft.jsonl
```

Lancer un entraînement QLoRA dans un environnement GPU configuré:

```bash
python backend/scripts/train_qlora.py --dataset data/training/textilebot_sft.jsonl --output-dir models/textilebot-qlora
```

Le script QLoRA nécessite des dépendances GPU optionnelles: `torch`, `transformers`, `datasets`, `peft`, `trl`, `bitsandbytes`.
