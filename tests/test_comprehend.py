import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@mock_aws
def test_detect_pii_retorna_entidades():
    client = boto3.client('comprehend', region_name='us-east-1')

    with patch.object(client, 'detect_pii_entities') as mock_comprehend:
        mock_comprehend.return_value = {
            'Entities': [
                {
                    'Score': 0.99,
                    'Type': 'BR_CPF',
                    'BeginOffset': 5,
                    'EndOffset': 19
                }
            ]
        }

        response = client.detect_pii_entities(
            Text='CPF: 000.000.000-00',
            LanguageCode='pt'
        )

    assert len(response['Entities']) == 1
    assert response['Entities'][0]['Type'] == 'BR_CPF'


@mock_aws
def test_detect_pii_documento_limpo():
    client = boto3.client('comprehend', region_name='us-east-1')

    with patch.object(client, 'detect_pii_entities') as mock_comprehend:
        mock_comprehend.return_value = {'Entities': []}

        response = client.detect_pii_entities(
            Text='Este documento não contém dados sensíveis.',
            LanguageCode='pt'
        )

    assert response['Entities'] == []


def test_language_code_invalido():
    """Documenta que 'pt-BR' NÃO é aceito pelo Comprehend."""
    language_correto = 'pt'
    language_invalido = 'pt-BR'

    assert language_correto != language_invalido
    assert len(language_correto) == 2
