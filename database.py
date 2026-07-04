"""
database.py — SQLite veritabanı katmanı
AI Sınav Hazırlama Sistemi için veri kalıcılığı sağlar.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "exams.db")


def get_connection() -> sqlite3.Connection:
    """Veritabanı bağlantısı oluşturur ve döndürür."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    """Veritabanını ve tabloları oluşturur (yoksa)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                konu            TEXT    NOT NULL,
                tarih           TEXT    NOT NULL,
                soru_sayisi     INTEGER NOT NULL,
                zorluk          TEXT    NOT NULL,
                ai_model        TEXT    NOT NULL DEFAULT 'Gemini',
                olusturulan_sinav TEXT  NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_exam(
    konu: str,
    soru_sayisi: int,
    zorluk: str,
    sinav_icerigi: dict,
    ai_model: str = "Gemini",
) -> int:
    """
    Sınav içeriğini veritabanına kaydeder.

    Returns:
        Yeni kaydın id değeri.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO exams (konu, tarih, soru_sayisi, zorluk, ai_model, olusturulan_sinav)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                konu,
                datetime.now().isoformat(timespec="seconds"),
                soru_sayisi,
                zorluk,
                ai_model,
                json.dumps(sinav_icerigi, ensure_ascii=False),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def list_exams(search_query: Optional[str] = None) -> list[dict]:
    """
    Tüm sınavları tarihe göre azalan sırada listeler.
    search_query verilirse konu üzerinde LIKE araması yapılır.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if search_query and search_query.strip():
            cursor.execute(
                """
                SELECT id, konu, tarih, soru_sayisi, zorluk, ai_model
                FROM exams
                WHERE konu LIKE ?
                ORDER BY tarih DESC
                """,
                (f"%{search_query.strip()}%",),
            )
        else:
            cursor.execute(
                """
                SELECT id, konu, tarih, soru_sayisi, zorluk, ai_model
                FROM exams
                ORDER BY tarih DESC
                """
            )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_exam_by_id(exam_id: int) -> Optional[dict]:
    """Verilen id'ye sahip sınavı döndürür."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        result = dict(row)
        result["olusturulan_sinav"] = json.loads(result["olusturulan_sinav"])
        return result
    finally:
        conn.close()


def delete_exam(exam_id: int) -> bool:
    """Verilen id'ye sahip sınavı siler. Başarılıysa True döner."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_stats() -> dict:
    """Genel istatistikleri döndürür."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM exams")
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT zorluk, COUNT(*) as cnt FROM exams GROUP BY zorluk"
        )
        by_difficulty = {row["zorluk"]: row["cnt"] for row in cursor.fetchall()}

        cursor.execute("SELECT SUM(soru_sayisi) as toplam FROM exams")
        total_questions = cursor.fetchone()["toplam"] or 0

        return {
            "toplam_sinav": total,
            "zorluga_gore": by_difficulty,
            "toplam_soru": total_questions,
        }
    finally:
        conn.close()


# Uygulama başladığında veritabanını hazırla
initialize_database()
