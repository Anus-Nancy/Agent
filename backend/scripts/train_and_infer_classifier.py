"""Training + inference pipeline for complaint classification.

Usage:
  python scripts/train_and_infer_classifier.py --artifact-dir ./artifacts/nlp \
    --text "My fee voucher has not been paid"
"""

import argparse

from app.services.nlp.complaint_classifier import ComplaintClassifier, default_department_mapping


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", default="./artifacts/nlp")
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--text", default="My fee submission deadline is tomorrow and payment is delayed.")
    args = parser.parse_args()

    classifier = ComplaintClassifier(model_name=args.model_name)

    # Training pipeline
    department_mapping = default_department_mapping()
    classifier.train(department_mapping)
    classifier.save_artifacts(args.artifact_dir)

    # Inference pipeline
    reloaded = ComplaintClassifier(model_name=args.model_name)
    reloaded.load_artifacts(args.artifact_dir)
    result = reloaded.classify(args.text)

    print("Preprocessed:", result.preprocessed_text)
    print("Predicted department:", result.department)
    print("Confidence:", round(result.confidence, 4))
    print("Scores:")
    for dept, score in sorted(result.scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {dept}: {score:.4f}")


if __name__ == "__main__":
    main()
