# app/routers/product.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.database.db import get_connection

router = APIRouter(prefix="/products", tags=["products"])


class Product(BaseModel):
    id: int
    name: str


class ProductCreate(BaseModel):
    name: str


@router.get("", response_model=List[Product])
def list_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM product")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("", response_model=Product)
def create_product(product: ProductCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO product (name) VALUES (?)", (product.name,))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "name": product.name}


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM product WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)


@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE product SET name = ? WHERE id = ?", (product.name, product_id))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    conn.close()
    return {"id": product_id, "name": product.name}


@router.delete("/{product_id}")
def delete_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM product WHERE id = ?", (product_id,))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    conn.close()
    return {"message": "deleted"}
