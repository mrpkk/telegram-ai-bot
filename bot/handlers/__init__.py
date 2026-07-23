from .ai import setup_ai_handlers
from .payments import setup_payments_handlers
from .wallet import setup_wallet_handlers
from .defi import setup_defi_handlers
from .voice import setup_voice_handlers
from .analytics import setup_analytics_handlers
from .agents import setup_agents_handlers
from .blockchains import setup_blockchains_handlers

__all__ = ["setup_ai_handlers", "setup_payments_handlers", "setup_wallet_handlers", "setup_defi_handlers", "setup_voice_handlers", "setup_analytics_handlers", "setup_agents_handlers", "setup_blockchains_handlers"]