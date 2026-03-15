"""
core/rag.py --- Production RAG Pipeline
Multi-tenant.Async.pgvector cosine search.GPT-4o
"""
import os,asyncio,asyncpg,numpy as np
from openai import AsyncOpenAI
from typing import Optional

_openai:Optional[AsyncOpenAI]=None
_pool:Optional[asyncpg.Pool]=None

def get_openai() -> AsyncOpenAI:
    global _openai
    if not _openai:
        _openai=AsyncOpenAI(API_KEY=os.environ['OPENAI_API_KEY'])
    return _openai


async def get_pool() -> asyncpg.Pool:
    global _pool
    if not _pool:
        _pool= await asyncpg.create_pool(
            dsn=os.environ["DATABASE_URL"],min_size=2,max_size=10,command_timeout=30
        )
    return _pool   


def product_to_chunk(p: dict) -> str:
    stock = float(p.get("stock") or 0)
    status = "IN STOCK" if stock > 0 else "OUT OF STOCK"
    return (
        f"Product: {p['name']}\nSKU: {p['sku']}\nCategory: {p.get('category','General')}\n"
        f"Status: {status} — {stock} {p.get('unit','units')} available\n"
        f"Price: £{float(p.get('price') or 0):.2f} per {p.get('unit','unit')}\n"
        f"Minimum Order: {p.get('moq',1)} {p.get('unit','units')}\n"
        f"Description: {p.get('description','')}"
    )

async def embed_texts(texts: list[str])->list[list[float]]:
    client=get_openai()
    all_emb=[]
    for i in range(0,len(texts),512):
        resp=await client.embeddings.create(model='text-embedding-3-small',input=texts[i:i+512])
        all.emb.extend([d.embeddings for d in resp.data])
    return all_emb

async def ingest_products(tenant_id:str,product:list[dict])->dict:
    if not product:
        return{'embedded':0}
    pool=await get_pool()
    chunks=[product_to_chunk(p) for p in product]   
    embedding=await embed_texts(chunks)
    async with pool.acquire() as conn:
        records=[(tenant_id,p['id'],chunks[i],str(embedding[i])) for i,p in enumerate(product)]
        await conn.executemany(
            """ INSERT INTO product_embeddings(tenant_id,product_id,chunk_text,embedding)
                VALUES($1,$2,$3,$4::vector)
                ON CONFLICT(product_id) DO UPDATE
                SET Chunk_text=EXCLUDED.chunk_text,embedding=EXCLUDED.embedding,updated_at=NOW()
            
""",
             records
        ) 
    return('embedded',len(product))    

SYSTEM_PROMPT = """You are a helpful stock assistant for a wholesale supplier.
Answer ONLY from the STOCK DATA provided. Never invent information.
Mention stock status, price, and MOQ when relevant.
If out of stock, say so clearly and suggest in-stock alternatives from the data.
If you can't find the answer: "I don't have that info — let me connect you with our team."
Be friendly and concise. Use *bold* with asterisks for WhatsApp formatting."""

async def query(tenant_id:str,question:str,history:list|None=None,top_k:int=4)->dict:
    pool,client=await get_pool(),get_openai()
    q_emb=(await embed_texts([question]))[0]
    async with pool.acquire() as conn:
        rows= await conn.fetch(
            """SELECT pe.chuck_text ,p.name AS product_name,
            1-(pe.embedding<=>$2::vecor) AS similarity
            FROM product_embedding pe JOIN product p ON p.id=pe.product_id,
            WHERE pe.tenant_id=$1 AND p.is_active=TRUE,
            ORDER BY pe.embedding <=> $2::vector LIMIT $3
"""
        )
    if not rows:
        return {"answer":"Our stock database hasn't been loaded yet. Please contact us directly.", "confidence":0.0, "sources":[]}
    strong=[r for r in rows if r['similarity']>=0.30]
    if not strong:
        return {"answer":"I couldn't find specific info on that. Let me connect you with our team!", "confidence":0.0, "sources":[]}
    context="\n\n---\n\n".join([r["chunk_text"] for r in strong])
    messages=[{'role':'system','content':SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role":"user","content":f"STOCK DATA:\n{context}\n\nCUSTOMER: {question}"})
    resp = await client.chat.completions.create(model="gpt-4o", messages=messages, max_tokens=350, temperature=0.15)
    return {
        "answer": resp.choices[0].message.content,
        "confidence": round(sum(r["similarity"] for r in strong) / len(strong), 3),
        "sources": [r["product_name"] for r in strong]
    }    




