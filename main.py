from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <-- Ferramenta para destravar o bloqueio do navegador
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega as variáveis de segurança do arquivo .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave GEMINI_API_KEY não foi encontrada no arquivo .env")

genai.configure(api_key=api_key)

def get_best_model():
    modelos_disponiveis = list(genai.list_models())
    for m in modelos_disponiveis:
        if 'generateContent' in m.supported_generation_methods and 'flash' in m.name.lower():
            return m.name
    for m in modelos_disponiveis:
        if 'generateContent' in m.supported_generation_methods:
            return m.name
    return 'models/gemini-1.5-flash' 

nome_do_modelo = get_best_model()
model = genai.GenerativeModel(nome_do_modelo)

app = FastAPI(
    title="API Girassol da Fé",
    description="Backend para adaptação de textos bíblicos utilizando IA"
)

# ---------------------------------------------------------
# LIBERANDO O ACESSO (CORS): Permite que o Flutter Web conecte
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # O asterisco permite requisições de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextoRequest(BaseModel):
    texto_original: str

@app.get("/")
def read_root():
    return {"mensagem": "O backend do Girassol da Fé está online e pronto!"}

@app.post("/adaptar")
async def adaptar_texto(request: TextoRequest):
    try:
        prompt_sistema = """
        Você é um especialista em psicopedagogia e educação especial inclusiva.
        Sua missão é adaptar o seguinte texto ou história bíblica para crianças atípicas (como autistas).
        
        Regras inquebráveis para a adaptação:
        1. Use linguagem extremamente simples, direta e literal.
        2. Elimine qualquer metáfora, ironia ou linguagem figurada (ex: em vez de "o Senhor é meu pastor", use "Deus cuida de mim como um pastor cuida das ovelhas").
        3. Frases curtas: Estrutura lógica de Sujeito + Verbo + Predicado.
        4. Destaque emoções de forma clara (ex: "Jesus ficou feliz").
        5. Divida a história em no máximo 3 ou 4 parágrafos curtos.
        6. IMPORTANTE: Retorne APENAS a história adaptada. Não inclua NENHUMA saudação, introdução, explicação ou texto adicional (ex: evite dizer "Excelente missão" ou "Aqui está o texto").
        
        Texto original para adaptar:
        """
        
        prompt_final = f"{prompt_sistema}\n\n{request.texto_original}"
        resposta = model.generate_content(prompt_final)
        
        return {
            "texto_adaptado": resposta.text,
            "status": "sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))