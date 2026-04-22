import boto3
import logging
import time
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

NOME_TABELA = os.environ.get('TABLE_NAME', 'FiltroInteligenteDados')
tabela = dynamodb.Table(NOME_TABELA)


def salvar_resultado(document_id: str, bucket: str, status: str, tipos_dados: list, request_id: str):
    """Persiste os metadados de análise do documento no DynamoDB."""
    item = {
        'document_id': document_id,
        'timestamp': int(time.time()),
        'status': status,
        'tipos_dados': tipos_dados,
        'bucket': bucket,
        'request_id': request_id
    }

    tabela.put_item(Item=item)
    logger.info(f"Metadados salvos no DynamoDB para: {document_id}")
