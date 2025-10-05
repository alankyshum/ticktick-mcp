import logging
import sys
from typing import Optional

# TickTick library imports
from ticktick.api import TickTickClient
from ticktick.oauth2 import OAuth2

# Import config variables and paths
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USERNAME, PASSWORD, dotenv_dir_path

# Custom OAuth2 class that provides better error messages for MCP context
class MCPFriendlyOAuth2(OAuth2):
    """
    Custom OAuth2 class that detects MCP server context and provides better error messages.
    """
    
    def _get_user_input(self, prompt: str = ''):
        """
        Override the user input method to detect MCP server context and provide helpful error.
        """
        # Check if we're likely running in an MCP server context (stdio transport)
        if not sys.stdin.isatty():
            # We're likely in MCP server mode where stdin/stdout are used for protocol communication
            error_msg = [
                "",
                "=" * 80,
                "🔧 TICKTICK AUTHENTICATION REQUIRED",
                "=" * 80,
                "The TickTick MCP server needs to authenticate with TickTick's API first.",
                "Since you're running this as an MCP server, interactive authentication cannot",
                "work because stdin/stdout are used for MCP protocol communication.",
                "",
                "SOLUTION: Run the setup command first in a separate terminal:",
                "",
                "  ticktick-mcp-setup",
                "",
                "This will handle the OAuth2 flow interactively and cache the authentication",
                "token. After that, the MCP server will work normally.",
                "",
                "If you don't have the setup command, you can also run:",
                "",
                "  python -c \"from ticktick_mcp.client import setup_auth; setup_auth()\"",
                "",
                "=" * 80,
                ""
            ]
            raise RuntimeError("\n".join(error_msg))
        
        # If we're in an interactive terminal, proceed normally
        return input(prompt)


def setup_auth():
    """
    Standalone function to handle OAuth authentication interactively.
    """
    print("Setting up TickTick MCP Server authentication...")
    print("This will handle the OAuth2 flow interactively.")
    print()
    
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USERNAME, PASSWORD]):
        logging.error("TickTick credentials not found in environment variables. Ensure .env file is correct.")
        return False

    try:
        logging.info(f"Initializing OAuth2 with cache path: {dotenv_dir_path / '.token-oauth'}")
        auth_client = MCPFriendlyOAuth2(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            cache_path=dotenv_dir_path / ".token-oauth"
        )
        # The OAuth2 constructor already calls get_access_token(), so if we get here, it worked
        
        logging.info(f"Initializing TickTickClient with username: {USERNAME}")
        client = TickTickClient(USERNAME, PASSWORD, auth_client)
        logging.info(f"✅ Authentication successful! Token cached for future use.")
        print("✅ Authentication successful!")
        print("You can now run the MCP server.")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error during authentication: {e}")
        print(f"❌ Error during authentication: {e}")
        return False


class TickTickClientSingleton:
    """Singleton class to manage the TickTickClient instance."""
    _instance: Optional[TickTickClient] = None
    _initialized: bool = False

    def __new__(cls):
        # Standard singleton pattern: __new__ controls object creation
        if cls._instance is None:
            # Only create the instance if it doesn't exist
            # But defer actual client initialization to __init__
            # to ensure it happens only once even if __new__ is called multiple times
            # before __init__ completes (though unlikely in typical singleton usage).
            pass # Object creation handled by Python automatically
        return super(TickTickClientSingleton, cls).__new__(cls) # Return the instance (or create if needed)

    def __init__(self):
        """Initializes the TickTick client within the singleton instance, ensuring it runs only once."""
        if self._initialized:
            return # Already initialized

        if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USERNAME, PASSWORD]):
            logging.error("TickTick credentials not found in environment variables (checked in config.py). Ensure .env file is correct.")
            TickTickClientSingleton._instance = None # Ensure instance is None if creds are missing
            TickTickClientSingleton._initialized = True # Mark as initialized (attempted)
            return

        try:
            logging.info(f"Initializing OAuth2 with cache path: {dotenv_dir_path / '.token-oauth'}")
            auth_client = MCPFriendlyOAuth2(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                cache_path=dotenv_dir_path / ".token-oauth" # Use path from config
            )
            # The OAuth2 constructor already calls get_access_token(), so if we get here, it worked

            logging.info(f"Initializing TickTickClient with username: {USERNAME}")
            client = TickTickClient(USERNAME, PASSWORD, auth_client)
            logging.info(f"TickTick client initialized successfully within singleton.")
            TickTickClientSingleton._instance = client
        except Exception as e:
            logging.error(f"Error initializing TickTick client within singleton: {e}", exc_info=True)
            TickTickClientSingleton._instance = None # Ensure instance is None on error
        finally:
            # Mark as initialized regardless of success/failure to prevent re-attempts
            TickTickClientSingleton._initialized = True

    @classmethod
    def get_client(cls) -> Optional[TickTickClient]:
        """Returns the initialized TickTick client instance."""
        if not cls._initialized:
            cls() # Ensure __init__ is called if not already initialized
        if cls._instance is None:
            logging.warning("get_client() called, but TickTick client failed to initialize.")
        return cls._instance

# Removed the old function
# def initialize_ticktick_client():
# ... existing code ... 