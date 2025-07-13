from flask import Flask, redirect, abort, request, jsonify
import re
import psycopg2
import psycopg2.pool
import os
import logging
import time
from collections import defaultdict, deque
from datetime import datetime
from urllib.parse import urlparse

# Configuration Flask
app = Flask(__name__)
app.config.update(
    JSON_SORT_KEYS=False,
    DEBUG=False,
    TESTING=False
)

# Logging sécurisé
logging.basicConfig(
    level=logging.INFO,
    format='[FLASK-SHORTENER] %(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/flask_shortener.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration DB
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'postgres'),           # <-- Nouveau défaut
    'database': os.environ.get('DB_NAME', 'mhdb24'),         # <-- Nouveau défaut  
    'user': os.environ.get('DB_USER', 'SuperAdminduTurfu'),  # <-- Nouveau défaut
    'password': os.environ.get('DB_PASSWORD', 'MHub2401!'),  # <-- Nouveau défaut
    'port': 5432,
    'sslmode': 'prefer',
    'connect_timeout': 5,
    'application_name': 'flask_shortener'
}

# Pattern ultra-strict
SHORT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9]{6,10}$')

# Rate limiting en mémoire
class RateLimiter:
    def __init__(self, max_requests=60, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(deque)
        self.blocked_ips = set()
    
    def is_allowed(self, ip):
        if ip in self.blocked_ips:
            return False
            
        now = time.time()
        # Nettoyer les anciennes requêtes
        while self.requests[ip] and self.requests[ip][0] < now - self.window:
            self.requests[ip].popleft()
        
        if len(self.requests[ip]) >= self.max_requests:
            # Bloquer temporairement les IPs abusives
            if len(self.requests[ip]) > self.max_requests * 2:
                self.blocked_ips.add(ip)
                logger.warning(f"IP blocked for abuse: {ip}")
            return False
        
        self.requests[ip].append(now)
        return True

rate_limiter = RateLimiter()

# Connection pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)
    logger.info("Database connection pool initialized")
except Exception as e:
    logger.error(f"Failed to initialize DB pool: {str(e)}")
    db_pool = None

def get_client_ip():
    """IP réelle avec protection proxy"""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    return request.environ.get('REMOTE_ADDR', 'unknown')

def is_safe_destination(url):
    """Validation URL destination"""
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in ['http', 'https']:
            return False
        
        hostname = parsed.netloc.lower()
        blocked_domains = [
            'localhost', '127.0.0.1', '0.0.0.0',
            '10.', '192.168.', '172.16.', '172.17.',
            '169.254.', 'malware.com', 'phishing.com'
        ]
        
        for blocked in blocked_domains:
            if blocked in hostname:
                return False
        
        return True
    except:
        return False

def lookup_and_track(short_id, client_ip, user_agent):
    """Lookup + tracking atomique"""
    if not db_pool:
        return None
    
    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        
        # 1. Lookup dans les deux tables
        cursor.execute("""
            (SELECT original_url, false as is_public FROM url_shortener_shorturl 
             WHERE short_id = %s AND is_active = true 
             AND (expires_at IS NULL OR expires_at > NOW()))
            UNION ALL
            (SELECT original_url, true as is_public FROM url_shortener_public_shorturl 
             WHERE short_id = %s AND is_active = true 
             AND expires_at > NOW())
            LIMIT 1
        """, (short_id, short_id))
        
        result = cursor.fetchone()
        if not result:
            return None
        
        original_url, is_public = result
        
        # 2. Validation URL destination
        if not is_safe_destination(original_url):
            logger.error(f"Unsafe destination blocked: {original_url}")
            return None
        
        # 3. Tracking atomique
        if is_public:
            cursor.execute("""
                UPDATE url_shortener_public_shorturl 
                SET click_count = click_count + 1, last_clicked = NOW()
                WHERE short_id = %s
            """, (short_id,))
        else:
            cursor.execute("""
                UPDATE url_shortener_shorturl 
                SET click_count = click_count + 1, last_clicked = NOW()
                WHERE short_id = %s
            """, (short_id,))
        
        # 4. Log détaillé pour analytics
        cursor.execute("""
            INSERT INTO url_shortener_click_log 
            (short_id, is_public, ip_address, user_agent, clicked_at, referer, country, city) 
            VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s)
        """, (
            short_id, 
            is_public, 
            client_ip[:45], 
            user_agent[:500],
            request.headers.get('Referer', '')[:500],
            '',  # country vide au lieu de NULL
            ''   # city vide au lieu de NULL
        ))
        
        conn.commit()
        return original_url
        
    except Exception as e:
        logger.error(f"DB error for {short_id}: {str(e)}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            db_pool.putconn(conn)

@app.route('/<short_id>')
def redirect_url(short_id):
    """SEULE fonction métier : redirection sécurisée"""
    start_time = time.time()
    client_ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')
    
    # 1. Validation pattern ultra-strict
    if not SHORT_ID_PATTERN.match(short_id):
        logger.warning(f"Invalid pattern: {short_id} from {client_ip}")
        return redirect('https://humari.fr', code=301)
    
    # 2. Rate limiting
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limited: {client_ip}")
        return redirect('https://humari.fr', code=301)
    
    # 3. Patterns suspects
    suspicious_patterns = ['../', '<script', 'javascript:', 'eval(', 'exec(']
    if any(pattern in short_id.lower() for pattern in suspicious_patterns):
        logger.warning(f"Suspicious pattern in {short_id} from {client_ip}")
        return redirect('https://humari.fr', code=301)
    
    # 4. Lookup + tracking atomique
    original_url = lookup_and_track(short_id, client_ip, user_agent)
    
    if not original_url:
        logger.info(f"URL not found: {short_id} from {client_ip}")
        return redirect('https://humari.fr', code=301)
    
    # 5. Redirection avec logging
    response_time = (time.time() - start_time) * 1000
    logger.info(f"Redirect: {short_id} -> {original_url[:50]}... "
               f"IP: {client_ip} Time: {response_time:.2f}ms")
    
    return redirect(original_url, code=301)

@app.route('/health')
def health_check():
    """Health check pour Docker"""
    try:
        if db_pool:
            conn = db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            db_pool.putconn(conn)
            
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'service': 'url-shortener-flask',
                'version': '1.0.0'
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'error': 'database_pool_unavailable'
            }), 503
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@app.route('/')
def root():
    """Root -> humari.fr"""
    return redirect('https://humari.fr', code=301)

@app.errorhandler(404)
def not_found(error):
    """404 -> humari.fr"""
    return redirect('https://humari.fr', code=301)

@app.errorhandler(403)
def forbidden(error):
    """403 -> humari.fr"""
    return redirect('https://humari.fr', code=301)

@app.errorhandler(500)
def server_error(error):
    """500 -> humari.fr"""
    logger.error(f"Server error: {str(error)}")
    return redirect('https://humari.fr', code=301)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)