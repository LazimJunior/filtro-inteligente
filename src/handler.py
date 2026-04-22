import boto3
import json
import urllib.parse
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

textract = boto3.client('textract')
comprehend = boto3.client('comprehend')
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

NOME_TABELA = 'FiltroInteligenteDados'
TOPICO_ARN = 'arn:aws:sns:us-east-1:020200817308:AlertaFiltroInteligente:9c417b3c-16ff-44e6-ba65-5646cce36a2b'
# ---------------------

tabela = dynamodb.Table(NOME_TABELA)


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    logger.info(f"Processando: {key}")

    try:
        response_textract = textract.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )

        texto_extraido = ""
        for item in response_textract['Blocks']:
            if item['BlockType'] == 'LINE':
                texto_extraido += item['Text'] + " "

        pii_detectado = comprehend.detect_pii_entities(
            Text=texto_extraido[:4500],
            LanguageCode='pt'
        )

        status_risco = "LIMPO"
        tipos_encontrados = []

        if pii_detectado['Entities']:
            status_risco = "CONTEM_DADOS_SENSIVEIS"
            tipos_encontrados = list(set([entidade['Type'] for entidade in pii_detectado['Entities']]))

            mensagem_email = (
                f"⚠️ ALERTA DE SEGURANÇA ⚠️\n\n"
                f"O arquivo '{key}' contém dados sensíveis.\n"
                f"Detectado: {', '.join(tipos_encontrados)}\n"
                f"ID da Execução: {context.aws_request_id}"
            )

            sns.publish(
                TopicArn=TOPICO_ARN,
                Message=mensagem_email,
                Subject="Filtro Inteligente: Dados Detectados"
            )

        tabela.put_item(
            Item={
                'document_id': key,
                'timestamp': int(time.time()),
                'status': status_risco,
                'tipos_dados': tipos_encontrados,
                'bucket': bucket,
                'request_id': context.aws_request_id
            }
        )

        logger.info(f"Sucesso: {key} classificado como {status_risco}")

        return {
            'statusCode': 200,
            'body': json.dumps({'status': status_risco})
        }

    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        raise e
