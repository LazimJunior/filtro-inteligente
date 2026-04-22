import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@mock_aws
def test_detect_document_text_retorna_texto():
    """Testa que o Textract retorna blocos de texto corretamente."""
    client = boto3.client('textract', region_name='us-east-1')

    # Simula resposta do Textract com moto
    with patch.object(client, 'detect_document_text') as mock_textract:
        mock_textract.return_value = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'CPF: 000.000.000-00'},
                {'BlockType': 'LINE', 'Text': 'Nome: João da Silva'},
                {'BlockType': 'WORD', 'Text': 'CPF:'},  # Deve ser ignorado
            ]
        }

        response = client.detect_document_text(
            Document={'S3Object': {'Bucket': 'test-bucket', 'Name': 'test.pdf'}}
        )

    linhas = [b['Text'] for b in response['Blocks'] if b['BlockType'] == 'LINE']
    assert len(linhas) == 2
    assert 'CPF: 000.000.000-00' in linhas


@mock_aws
def test_texto_extraido_concatena_linhas():
    """Testa que o texto extraído une as linhas com espaço."""
    blocos = [
        {'BlockType': 'LINE', 'Text': 'Linha um'},
        {'BlockType': 'LINE', 'Text': 'Linha dois'},
        {'BlockType': 'PAGE', 'Text': 'ignorado'},
    ]

    texto = ""
    for item in blocos:
        if item['BlockType'] == 'LINE':
            texto += item['Text'] + " "

    assert texto.strip() == "Linha um Linha dois"
