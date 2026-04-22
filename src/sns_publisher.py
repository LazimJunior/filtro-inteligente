import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')

TOPICO_ARN = os.environ.get('SNS_TOPIC_ARN', '')


def publicar_alerta(key: str, tipos_encontrados: list, request_id: str):
    if not TOPICO_ARN:
        logger.warning("SNS_TOPIC_ARN não configurado. Alerta não enviado.")
        return

    mensagem = (
        f"⚠️ ALERTA DE SEGURANÇA ⚠️\n\n"
        f"O arquivo '{key}' contém dados sensíveis.\n"
        f"Detectado: {', '.join(tipos_encontrados)}\n"
        f"ID da Execução: {request_id}"
    )

    sns.publish(
        TopicArn=TOPICO_ARN,
        Message=mensagem,
        Subject="Filtro Inteligente: Dados Detectados"
    )

    logger.info(f"Alerta SNS publicado para: {key}")
