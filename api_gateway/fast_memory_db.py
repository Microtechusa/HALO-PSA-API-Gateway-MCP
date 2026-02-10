#!/usr/bin/env python3
"""
Fast Memory Database Module

Stores and retrieves frequently used API queries for quick reuse.
"""

import os
import sqlite3
import json
import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger("halo_api_gateway.fast_memory")


class FastMemoryDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        self.connect()
        self.initialize_db()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_db(self):
        if not self.conn:
            self.connect()
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS saved_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            path TEXT NOT NULL,
            method TEXT NOT NULL,
            params TEXT,
            data TEXT,
            timestamp INTEGER NOT NULL,
            usage_count INTEGER DEFAULT 0
        )''')
        self.conn.commit()

    def _parse_json_fields(self, row: dict) -> dict:
        q = dict(row)
        for field in ('params', 'data'):
            if q.get(field):
                try:
                    q[field] = json.loads(q[field])
                except json.JSONDecodeError:
                    q[field] = None
        return q

    def save_query(self, description: str, path: str, method: str,
                   params: Optional[Dict] = None, data: Optional[Any] = None) -> int:
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM saved_queries WHERE path = ? AND method = ?', (path, method))
        existing = cursor.fetchone()
        now = int(time.time())
        if existing:
            cursor.execute('''UPDATE saved_queries SET usage_count = usage_count + 1,
                timestamp = ?, params = ?, data = ?, description = ? WHERE id = ?''',
                (now, json.dumps(params) if params else None,
                 json.dumps(data) if data else None, description, existing['id']))
            self.conn.commit()
            return existing['id']

        cursor.execute('''INSERT INTO saved_queries (description, path, method, params, data, timestamp, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, 1)''',
            (description, path, method,
             json.dumps(params) if params else None,
             json.dumps(data) if data else None, now))
        self.conn.commit()
        return cursor.lastrowid

    def find_query(self, path: str, method: str) -> Optional[Dict]:
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM saved_queries WHERE path = ? AND method = ?', (path, method))
        result = cursor.fetchone()
        return self._parse_json_fields(result) if result else None

    def search_queries(self, search_term: str) -> List[Dict]:
        if not self.conn:
            self.connect()
        pattern = f"%{search_term}%"
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM saved_queries WHERE description LIKE ? OR path LIKE ?
            ORDER BY usage_count DESC, timestamp DESC''', (pattern, pattern))
        return [self._parse_json_fields(row) for row in cursor.fetchall()]

    def get_all_queries(self) -> List[Dict]:
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM saved_queries ORDER BY usage_count DESC, timestamp DESC')
        return [self._parse_json_fields(row) for row in cursor.fetchall()]

    def increment_usage(self, query_id: int):
        if not self.conn:
            self.connect()
        self.conn.execute('UPDATE saved_queries SET usage_count = usage_count + 1, timestamp = ? WHERE id = ?',
            (int(time.time()), query_id))
        self.conn.commit()

    def delete_query(self, query_id: int) -> bool:
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM saved_queries WHERE id = ?', (query_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def clear_all(self) -> int:
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM saved_queries')
        self.conn.commit()
        return cursor.rowcount
