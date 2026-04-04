from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any, Dict
from app.core.use_cases.auth_service import AuthService
from app.core.domain.models.api_mock import User, UserCreate, UserLogin, Token
from app.adapters.outbound.database.mongodb import MongoDB
from app.adapters.outbound.repositories.mongo_api_repository import MongoApiRepository

router = APIRouter()

def get_repository():
    db = MongoDB.db
    return MongoApiRepository(db)

@router.post("/register", summary="Criar um novo usuário (Administrador)", tags=["Autenticação"])
async def register(user_data: UserCreate, repo: MongoApiRepository = Depends(get_repository)):
    """
    Cadastra um novo usuário no sistema. 
    A senha é criptografada antes de ir para o banco.
    """
    existing_user = await repo.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já cadastrado.")
    
    hashed_password = AuthService.get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    user_id = await repo.create_user(new_user)
    return {"id": user_id, "message": "Usuário criado com sucesso."}

@router.post("/login", summary="Fazer Login (JSON)", response_model=Token, tags=["Autenticação"])
async def login(credentials: UserLogin, repo: MongoApiRepository = Depends(get_repository)):
    """
    **Para Front-end (Angular/React/Vue)**:
    Recebe um JSON: `{ "username": "...", "password": "..." }`
    """
    user = await repo.get_user_by_username(credentials.username)
    if not user or not AuthService.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
    
    access_token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-swagger", include_in_schema=False)
async def login_swagger(
    credentials: OAuth2PasswordRequestForm = Depends(), 
    repo: MongoApiRepository = Depends(get_repository)
):
    """
    **Apenas para o Swagger**: 
    Recebe os dados do formulário nativo do botão 'Authorize'.
    """
    user = await repo.get_user_by_username(credentials.username)
    if not user or not AuthService.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
    
    access_token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reset-password", summary="Trocar Senha", tags=["Autenticação"])
async def reset_password(
    username: str = Body(..., example="admin"), 
    new_password: str = Body(..., example="nova_senha_123"),
    repo: MongoApiRepository = Depends(get_repository)
):
    """
    Altera a senha de um usuário existente.
    """
    hashed_password = AuthService.get_password_hash(new_password)
    updated = await repo.update_user_password(username, hashed_password)
    if not updated:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {"message": "Senha alterada com sucesso."}
