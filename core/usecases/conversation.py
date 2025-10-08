"""
Conversation use case (alias for conversation_management).

This is a compatibility shim for imports that reference the old module name.
The actual implementation is in conversation_management.py
"""

from core.usecases.conversation_management import ConversationManagementUseCase as ConversationUseCase

__all__ = [
    'ConversationUseCase',
]
