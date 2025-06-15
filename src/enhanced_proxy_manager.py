import os
import logging
import random
import string
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedProxyManager:
    def __init__(self, proxy_config: Optional[Dict[str, str]] = None):
        """
        Initialize proxy manager with custom configuration
        
        Args:
            proxy_config: Dict with keys: host, port, username, password
        """
        if proxy_config:
            self.proxy_host = proxy_config.get('host', '42q6t9rp.pr.thordata.net')
            self.proxy_port = proxy_config.get('port', '9999')
            self.proxy_username = proxy_config.get('username', 'td-customer-hdXMhtuot8ni')
            self.proxy_password = proxy_config.get('password', '')
        else:
            # Load from environment variables
            self.proxy_host = os.getenv('PROXY_HOST', '42q6t9rp.pr.thordata.net')
            self.proxy_port = os.getenv('PROXY_PORT', '9999')
            self.proxy_username = os.getenv('PROXY_USERNAME', 'td-customer-hdXMhtuot8ni')
            self.proxy_password = os.getenv('PROXY_PASSWORD', '')
        
        self.session_counter = 0
        self.rotating_session = True
        self.proxy_configured = bool(self.proxy_host and self.proxy_port and self.proxy_username)
        
        if self.proxy_configured:
            logger.info(f"Proxy configured: {self.proxy_host}:{self.proxy_port}")
        else:
            logger.warning("Proxy configuration incomplete")
    
    def generate_session_id(self) -> str:
        """Generate a random session ID for IP rotation"""
        # Generate random session ID
        session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{session_id}-{timestamp}"
    
    def get_proxy(self, rotate_ip: bool = True) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration with optional session rotation
        
        Args:
            rotate_ip: If True, generates new session ID for new IP
        """
        if not self.proxy_configured:
            logger.info("No proxy configured, using direct connection")
            return None
        
        # Build username with session ID for IP rotation
        if rotate_ip and self.rotating_session:
            session_id = self.generate_session_id()
            full_username = f"{self.proxy_username}-sessid-{session_id}"
            logger.info(f"Using rotating session ID: {session_id}")
        else:
            full_username = self.proxy_username
        
        # Format proxy URL with authentication
        if self.proxy_password:
            proxy_url = f"http://{full_username}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"
        else:
            proxy_url = f"http://{full_username}@{self.proxy_host}:{self.proxy_port}"
        
        proxy_config = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        self.session_counter += 1
        logger.debug(f"Proxy request #{self.session_counter}: {self.proxy_host}:{self.proxy_port}")
        
        return proxy_config
    
    def get_sticky_proxy(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        Get proxy with a specific session ID (sticky session)
        
        Args:
            session_id: Specific session ID to use
        """
        if not self.proxy_configured:
            return None
        
        # Build username with specific session ID
        full_username = f"{self.proxy_username}-sessid-{session_id}"
        
        if self.proxy_password:
            proxy_url = f"http://{full_username}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"
        else:
            proxy_url = f"http://{full_username}@{self.proxy_host}:{self.proxy_port}"
        
        proxy_config = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        logger.debug(f"Using sticky session: {session_id}")
        return proxy_config
    
    def test_proxy_connection(self, rotate_ip: bool = True) -> Dict[str, any]:
        """Test proxy connection and get IP info"""
        if not self.proxy_configured:
            return {"success": False, "error": "Proxy not configured"}
            
        try:
            import requests
            proxy_config = self.get_proxy(rotate_ip=rotate_ip)
            
            # Test with IP info service
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxy_config,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Proxy test successful. IP: {data.get('origin', 'Unknown')}")
                return {
                    "success": True,
                    "ip": data.get('origin', 'Unknown'),
                    "status_code": response.status_code
                }
            else:
                logger.error(f"Proxy test failed with status: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Status code: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Proxy connection test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_proxy_stats(self) -> Dict[str, any]:
        """Get proxy usage statistics"""
        return {
            "host": self.proxy_host,
            "port": self.proxy_port,
            "username": self.proxy_username,
            "configured": self.proxy_configured,
            "rotating_session": self.rotating_session,
            "total_requests": self.session_counter
        } 