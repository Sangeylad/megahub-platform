# url_shortener/security.py
import re
import logging
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

class SecurityValidator:
    def __init__(self):
        # Patterns suspects
        self.suspicious_patterns = [
            r'\.\./',  # Path traversal
            r'<script',  # XSS
            r'javascript:',  # JS injection
            r'data:',  # Data URLs
            r'vbscript:',  # VBScript
            r'file://',  # File URLs
            r'ftp://',  # FTP
        ]
        
        # User agents suspects
        self.blocked_user_agents = [
            'bot', 'crawler', 'spider', 'scraper', 'automated',
            'python-requests', 'curl', 'wget', 'postman',
            'scanner', 'exploit', 'sqlmap', 'nikto'
        ]
        
        # Domaines bloqués
        self.blocked_domains = [
            'localhost', '127.0.0.1', '0.0.0.0',
            '10.', '192.168.', '172.16.', '172.17.',
            'malware', 'phishing', 'spam'
        ]
        
        # Rate limiting simple en mémoire
        self.request_counts = {}
        self.blocked_ips = set()
    
    def is_safe_request(self, request, short_id):
        """Validation complète de la requête"""
        try:
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            user_agent = request.headers.get('User-Agent', '').lower()
            
            # 1. IP bloquée
            if client_ip in self.blocked_ips:
                return False
            
            # 2. Rate limiting simple
            if not self._check_rate_limit(client_ip):
                return False
            
            # 3. User agent suspect
            if any(blocked in user_agent for blocked in self.blocked_user_agents):
                logger.warning(f"Blocked user agent: {user_agent[:100]} from {client_ip}")
                return False
            
            # 4. Patterns suspects dans short_id
            if any(re.search(pattern, short_id, re.IGNORECASE) 
                   for pattern in self.suspicious_patterns):
                logger.warning(f"Suspicious pattern in short_id: {short_id} from {client_ip}")
                return False
            
            # 5. Headers suspects
            if self._has_suspicious_headers(request):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Security validation error: {str(e)}")
            return False
    
    def is_safe_destination(self, url):
        """Validation de l'URL de destination"""
        try:
            parsed = urlparse(url)
            
            # Protocole autorisé
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Domaine bloqué
            hostname = parsed.netloc.lower()
            if any(blocked in hostname for blocked in self.blocked_domains):
                return False
            
            # Patterns suspects dans l'URL
            if any(re.search(pattern, url, re.IGNORECASE) 
                   for pattern in self.suspicious_patterns):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation error for {url}: {str(e)}")
            return False
    
    def _check_rate_limit(self, ip):
        """Rate limiting simple : 100 req/minute par IP"""
        current_time = int(time.time() / 60)  # Minute actuelle
        
        if ip not in self.request_counts:
            self.request_counts[ip] = {}
        
        # Nettoie les anciennes minutes
        self.request_counts[ip] = {
            minute: count for minute, count in self.request_counts[ip].items()
            if minute >= current_time - 5  # Garde 5 minutes
        }
        
        # Compte requêtes cette minute
        current_count = self.request_counts[ip].get(current_time, 0)
        
        if current_count >= 100:  # Limite : 100/minute
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            self.blocked_ips.add(ip)  # Blocage temporaire
            return False
        
        # Incrémente compteur
        self.request_counts[ip][current_time] = current_count + 1
        return True
    
    def _has_suspicious_headers(self, request):
        """Détecte headers suspects"""
        suspicious_headers = [
            'X-Forwarded-For',  # Si trop de proxy
            'X-Real-IP',        # Si IP suspecte
        ]
        
        # Check si trop de proxies (indicateur de tunneling)
        forwarded = request.headers.get('X-Forwarded-For', '')
        if forwarded.count(',') > 3:  # Plus de 3 proxies = suspect
            return True
        
        return False