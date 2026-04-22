import boto3
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

textract = boto3.client('textract')


def start_document_text_detection(bucket: str, key: str) -> str:
    """Inicia job assíncrono de detecção de texto no Textract."""
    response = textract.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        }
    )
    job_id = response['JobId']
    logger.info(f"Textract job iniciado: {job_id}")
    return job_id


def poll_job(job_id: str, max_attempts: int = 20, delay: int = 5) -> list:
    """Faz polling do job até conclusão e retorna os blocos de texto."""
    for attempt in range(max_attempts):
        response = textract.get_document_text_detection(JobId=job_id)
        status = response['JobStatus']

        logger.info(f"Tentativa {attempt + 1}: status = {status}")

        if status == 'SUCCEEDED':
            return response.get('Blocks', [])
        elif status == 'FAILED':
            raise RuntimeError(f"Textract job falhou: {job_id}")

        time.sleep(delay)

    raise TimeoutError(f"Textract job não concluiu após {max_attempts} tentativas: {job_id}")


def extract_text(blocks: list) -> str:
    """Extrai o texto de blocos do tipo LINE retornados pelo Textract."""
    lines = [block['Text'] for block in blocks if block['BlockType'] == 'LINE']
    return " ".join(lines)
