import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "database"),
        database=os.getenv("DB_NAME", "app_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres123"),
        port=os.getenv("DB_PORT", 5432)
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS docs (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

class DocItem(BaseModel):
    title: str
    content: str

@app.get("/api/docs")
def list_docs():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM docs ORDER BY id DESC;")
    items = cur.fetchall()
    cur.close()
    conn.close()
    return items

@app.post("/api/docs", status_code=201)
def create_doc(item: DocItem):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO docs (title, content) VALUES (%s, %s) RETURNING *;",
        (item.title, item.content)
    )
    new_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_item
