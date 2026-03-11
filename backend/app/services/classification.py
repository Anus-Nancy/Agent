from sqlalchemy.orm import Session

from app.models.department import Department
from app.services.nlp.complaint_classifier import ComplaintClassifier, default_department_mapping

classifier = ComplaintClassifier()
classifier.train(default_department_mapping())


def classify_department(db: Session, text: str) -> Department | None:
    result = classifier.classify(text)
    return db.query(Department).filter(Department.name == result.department).first()
