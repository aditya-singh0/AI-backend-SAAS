# src/proxy_manager.py
import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.proxy_host = os.getenv('PROXY_HOST')
        self.proxy_port = os.getenv('PROXY_PORT')
        self.proxy_username = os.getenv('PROXY_USERNAME')
        self.proxy_password = os.getenv('PROXY_PASSWORD')
        self.session_duration = int(os.getenv('SESSION_DURATION', 10))
        self.rotating_session = os.getenv('ROTATING_SESSION', 'true').lower() == 'true'
        
        # Validate proxy configuration
        if not all([self.proxy_host, self.proxy_port, self.proxy_username, self.proxy_password]):
            logger.warning("Proxy configuration incomplete. Some proxy settings are missing.")
            self.proxy_configured = False
        else:
            self.proxy_configured = True
            logger.info(f"Proxy configured: {self.proxy_host}:{self.proxy_port}")
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration for requests
        Returns None if proxy is not configured (direct connection)
        """
        if not self.proxy_configured:
            logger.info("No proxy configured, using direct connection")
            return None
        
        # Format proxy URL with authentication
        proxy_url = f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"
        
        proxy_config = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        logger.debug(f"Using ThorData proxy: {self.proxy_host}:{self.proxy_port}")
        return proxy_config
    
    def get_proxy_info(self) -> Dict[str, str]:
        """Get proxy information for logging/debugging"""
        return {
            "host": self.proxy_host or "Not configured",
            "port": self.proxy_port or "Not configured",
            "username": self.proxy_username or "Not configured",
            "configured": str(self.proxy_configured),
            "rotating_session": str(self.rotating_session),
            "session_duration": str(self.session_duration)
        }
    
    def test_proxy_connection(self) -> bool:
        """Test if proxy is working"""
        if not self.proxy_configured:
            return False
            
        try:
            import requests
            proxy_config = self.get_proxy()
            
            # Test with a simple request
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxy_config,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Proxy connection test successful")
                return True
            else:
                logger.error(f"Proxy test failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Proxy connection test failed: {str(e)}")
            return False