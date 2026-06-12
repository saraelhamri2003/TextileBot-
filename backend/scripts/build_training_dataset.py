"""
Build a supervised fine-tuning JSONL dataset for TextileBot.

Inputs can be chat/compliance CSV exports or plain text regulatory documents.
Output format: {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}
"""

import argparse
import csv
import json
from pathlib import Path

SYSTEM_PROMPT = (
    "Tu es TextileBot Pro, expert en reglementation textile. "
    "Reponds avec justification, references et niveau de confiance."
)


def row_value(row: dict, candidates: list[str]) -> str:
    lowered = {key.lower().strip(): value for key, value in row.items()}
    for candidate in candidates:
        if candidate in lowered and lowered[candidate]:
            return lowered[candidate].strip()
    return ""


def examples_from_csv(path: Path) -> list[dict]:
    examples = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            question = row_value(row, ["question", "query", "user", "prompt", "input"])
            answer = row_value(row, ["answer", "assistant", "response", "completion", "output"])
            if not question or not answer:
                product = row_value(row, ["product_name", "produit", "product"])
                composition = row_value(row, ["fiber_composition", "composition"])
                market = row_value(row, ["intended_market", "market", "marche"])
                label = row_value(row, ["label_text", "etiquette", "label"])
                status = row_value(row, ["status", "statut"])
                analysis = row_value(row, ["analysis_result", "analysis", "justification"])
                if product and composition and analysis:
                    question = (
                        f"Analyse la conformite du produit {product}. "
                        f"Composition: {composition}. Marche: {market}. Etiquette: {label}."
                    )
                    answer = f"Statut: {status or 'a verifier'}.\n{analysis}"
            if question and answer:
                examples.append(to_chat_example(question, answer))
    return examples


def examples_from_text(path: Path, chunk_size: int = 1200) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    words = text.split()
    examples = []
    for index in range(0, len(words), chunk_size):
        chunk = " ".join(words[index : index + chunk_size]).strip()
        if len(chunk) < 300:
            continue
        question = f"Resume les obligations textiles cles du document {path.name}, extrait {index // chunk_size + 1}."
        answer = (
            "Synthese documentaire:\n"
            f"{chunk[:1800]}\n\n"
            f"Source: {path.name}. Confiance: Moyenne, car l'extrait doit etre verifie dans le document complet."
        )
        examples.append(to_chat_example(question, answer))
    return examples


def to_chat_example(question: str, answer: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", required=True, help="CSV/TXT/MD files to convert.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    all_examples = []
    for raw_path in args.input:
        path = Path(raw_path)
        if path.suffix.lower() == ".csv":
            all_examples.extend(examples_from_csv(path))
        elif path.suffix.lower() in {".txt", ".md"}:
            all_examples.extend(examples_from_text(path))

    with output.open("w", encoding="utf-8") as handle:
        for example in all_examples:
            handle.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"Wrote {len(all_examples)} examples to {output}")


if __name__ == "__main__":
    main()
