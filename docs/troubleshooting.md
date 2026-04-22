# Troubleshooting — filtro-inteligente

Bugs encontrados durante o desenvolvimento no console AWS e suas soluções.

---

## Bug 1: Timeout ao chamar Textract via Lambda na VPC

**Sintoma**: Lambda timeout após 300s sem retorno do Textract.

**Causa raiz**: Interface Endpoint criado com `PrivateDnsEnabled=false`.
A Lambda resolvia o DNS público do Textract (IPs fora da VPC).
Subnet privada sem IGW bloqueava o tráfego → timeout silencioso.

**Solução**: Recriar o endpoint com `PrivateDnsEnabled=true`.

**Diagnóstico usado**:
```python
import socket
print(socket.getaddrinfo('textract.us-east-1.amazonaws.com', 443))
```
Quando `PrivateDnsEnabled=false`, o IP retornado era público (fora do range `10.x.x.x`) — confirmando que o tráfego tentava sair da VPC.

---

## Bug 2: Comprehend não detectando CPF

**Sintoma**: `DetectPiiEntities` retorna lista `Entities` vazia para documento com CPF no formato `000.000.000-00`.

**Causa raiz**: `LanguageCode='en'` passado incorretamente.

**Solução**: Alterar para `LanguageCode='pt'`.

> **Nota importante**: `'pt-BR'` **não é aceito** pelo Comprehend — o parâmetro correto é `'pt'` (causa erro de validação se usar `pt-BR`).

---

## Bug 3: DynamoDB PutItem AccessDenied

**Sintoma**: `ClientError: AccessDenied ao chamar dynamodb:PutItem`.

**Causa raiz**: IAM Policy com ARN da tabela incorreto (nome da tabela errado no ARN).

**Solução**: Corrigir o ARN na policy inline da Lambda Role.

ARN correto:
```
arn:aws:dynamodb:REGION:ACCOUNT_ID:table/NOME-EXATO-DA-TABELA
```

> **Dica**: O nome da tabela no ARN é case-sensitive e deve ser idêntico ao nome criado no DynamoDB, incluindo maiúsculas e hífens.
