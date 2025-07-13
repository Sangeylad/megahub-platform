# url_shortener/db.py
import psycopg2
import psycopg2.pool
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'host': os.environ.get('DB_HOST', 'postgres-shortener'),
            'database': os.environ.get('DB_NAME', 'shortener_db'),
            'user': os.environ.get('DB_USER', 'shortener_user'),
            'password': os.environ.get('DB_PASSWORD', 'ShortUrl2025!'),
            'port': 5432
        }
        
        # Connection pool pour performance
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,  # min/max connections
                **self.db_config
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DB pool: {str(e)}")
            self.pool = None
    
    def get_connection(self):
        """Récupère une connexion du pool"""
        if self.pool:
            return self.pool.getconn()
        return None
    
    def put_connection(self, conn):
        """Remet une connexion dans le pool"""
        if self.pool and conn:
            self.pool.putconn(conn)
    
    def test_connection(self):
        """Test de connexion pour health check"""
        conn = None
        try:
            conn = self.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
            return False
        except Exception as e:
            logger.error(f"DB connection test failed: {str(e)}")
            return False
        finally:
            if conn:
                self.put_connection(conn)
    
    def get_original_url(self, short_id):
        """Récupère l'URL originale (READ ONLY)"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return None
                
            cursor = conn.cursor()
            
            # Query simple et sécurisée
            cursor.execute("""
                SELECT original_url 
                FROM url_shortener_shorturl 
                WHERE short_id = %s 
                AND is_active = true 
                AND (expires_at IS NULL OR expires_at > NOW())
            """, (short_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error fetching URL for {short_id}: {str(e)}")
            return None
        finally:
            if conn:
                self.put_connection(conn)
    
    def track_click(self, short_id, ip_address, user_agent):
        """Track un clic (WRITE)"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Update compteur atomique
            cursor.execute("""
                UPDATE url_shortener_shorturl 
                SET click_count = click_count + 1,
                    last_clicked = NOW()
                WHERE short_id = %s
            """, (short_id,))
            
            # Log détaillé (optionnel, pour analytics futures)
            cursor.execute("""
                INSERT INTO url_shortener_clicklog 
                (short_id, ip_address, user_agent, clicked_at) 
                VALUES (%s, %s, %s, NOW())
            """, (short_id, ip_address[:45], user_agent[:200]))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error tracking click for {short_id}: {str(e)}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.put_connection(conn)