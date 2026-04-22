import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

comprehend = boto3.client('comprehend')

MAX_TEXT_LENGTH = 4500


def detect_pii(text: str) -> dict:
    truncated = text[:MAX_TEXT_LENGTH]

    response = comprehend.detect_pii_entities(
        Text=truncated,
        LanguageCode='pt'
    )

    entities = response.get('Entities', [])
    logger.info(f"Entidades PII detectadas: {len(entities)}")

    return {
        'entities': entities,
        'types': list(set([e['Type'] for e in entities])),
        'is_sensitive': len(entities) > 0
    }
