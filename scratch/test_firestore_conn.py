import os
import asyncio
from dotenv import load_dotenv
from google.cloud import firestore

# Carrega as variáveis do .env
load_dotenv()

async def test_connection():
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    print(f"--- Iniciando teste de conexão ---")
    print(f"Projeto: {project_id}")
    print(f"Credenciais: {credentials_path}")
    
    try:
        # Se as credenciais estiverem no .env como GOOGLE_APPLICATION_CREDENTIALS,
        # a biblioteca o detecta automaticamente.
        db = firestore.AsyncClient(project=project_id)
        
        # Tenta escrever um documento de teste
        print("Tentando escrever documento de teste...")
        test_ref = db.collection("test_connection").document("status")
        await test_ref.set({
            "message": "Conexão realizada com sucesso!",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        # Tenta ler de volta
        print("Tentando ler documento de teste...")
        doc = await test_ref.get()
        if doc.exists:
            print(f"SUCESSO! Dados do Firestore: {doc.to_dict()}")
        
        # Limpa o teste
        await test_ref.delete()
        print("Teste concluído e dados de limpeza removidos.")
        
    except Exception as e:
        print(f"ERRO de conexão: {e}")
        print("\nDICA: Verifique se o arquivo JSON de credenciais está correto e se o FIREBASE_PROJECT_ID no .env bate com o do console.")

if __name__ == "__main__":
    asyncio.run(test_connection())
