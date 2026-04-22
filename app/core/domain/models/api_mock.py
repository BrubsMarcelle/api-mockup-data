from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class SquadTag(str, Enum):
    DM_CARTOES = "Squad DM Cartões"
    SVA = "Squad SVA"
    COBRANCAS = "Squad Cobranças"
    DM_EMPRESTIMO = "Squad DM Emprestimo"
    DM_PAG = "Squad DM Pag"
    DM_CONTA = "DM Conta"
    DM_CRED = "DM Cred"
    DM_ATENDIMENTOS = "Squad DM Atendimentos"

class DatabaseOrigin(str, Enum):
    STAGING_QA = "Staging_qa"
    PRODUTOS_QA = "produtos_qa"
    ATENDIMENTOS = "atendimentos"
    EMPRESTIMO = "emprestimo"
    MONGODB = "base mongodb"
    POSTGRE = "base postgre"
    OUTROS = "outros"

class Method(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class Template(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name_api: Optional[str] = None
    url_base: Optional[str] = None
    endpoint: str
    method: Method
    payload_padrao: Dict[str, Any]
    campos_editaveis: List[str]
    identity_field: Optional[str] = None
    tag_squad: Optional[SquadTag] = None
    base_de_dados: Optional[DatabaseOrigin] = None
    origem_sistema: Optional[str] = None
    data_criacao: datetime = Field(default_factory=datetime.utcnow)

class TemplateCreate(BaseModel):
    name_api: str = Field(..., description="Nome da API")
    url_base: str = Field(..., description="URL original", example="https://api.dmcard.com.br")
    endpoint: str = Field(..., description="Path da API", example="v1/usuarios")
    method: Method = Field(..., description="Método HTTP", example="POST")
    payload_padrao: Dict[str, Any] = Field(..., description="JSON de resposta")
    campos_editaveis: List[str] = Field(..., description="Campos variávies")
    identity_field: Optional[str] = Field(None, description="Campo de identidade")
    tag_squad: Optional[SquadTag] = None
    base_de_dados: Optional[DatabaseOrigin] = None
    origem_sistema: Optional[str] = None

class TemplateBody(BaseModel):
    payload_padrao: Dict[str, Any] = Field(..., description="O JSON completo da resposta padrão da API.", example={"id": 1, "nome": "Exemplo"})
    campos_editaveis: List[str] = Field(..., description="Lista de chaves que poderão ser customizadas.", example=["nome", "status"])

class MockGerado(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    template_id: str
    url_acesso: str
    method: Method
    modified_fields: Dict[str, Any]
    descricao: Optional[str] = None
    payload_final: Dict[str, Any]
    identity_value: Optional[str] = None
    data_criacao: datetime = Field(default_factory=datetime.utcnow)

class MockGeradoCreate(BaseModel):
    endpoint: str = Field(..., description="O path do endpoint exatamente igual ao cadastrado no template", example="v1/cartao/busca-resumo-associado")
    method: Method = Field(..., description="O método HTTP correspondente", example="POST")
    modified_fields: Dict[str, Any] = Field(default={}, description="Os campos que você quer SOBRESCREVER do template original", example={"nome": "Bruna Silva", "status": "Inativo"})
    payload_customizado: Optional[Dict[str, Any]] = Field(None, description="JSON completo customizado para este mock")
    descricao: Optional[str] = Field(None, description="Descrição do mock", example="Descrever o cenario daquele mock, de uma forma curta")
    identity_value: Optional[str] = Field(None, description="O valor do campo de identidade que será usado para a busca (Ex: o CPF real)", example="12345678900")

class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    data_criacao: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str = Field(..., example="admin")
    email: str = Field(..., example="admin@empresa.com.br")
    password: str = Field(..., example="senha_segura_123")

class UserLogin(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="senha_segura_123")

class Token(BaseModel):
    access_token: str
    token_type: str
