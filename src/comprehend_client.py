import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

comprehend = boto3.client('comprehend')

# Limite de caracteres aceito pelo Comprehend por chamada
MAX_TEXT_LENGTH = 4500


def detect_pii(text: str) -> dict:
    """
    Detecta entidades PII em texto usando o Amazon Comprehend.

    Nota importante: LanguageCode deve ser 'pt' para português.
    'pt-BR' NÃO é aceito pelo Comprehend — causa erro de validação.
    """
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
