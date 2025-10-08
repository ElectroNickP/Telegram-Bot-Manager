"""
System use case (alias for system_management).

This is a compatibility shim for imports that reference the old module name.
The actual implementation is in system_management.py
"""

from core.usecases.system_management import SystemManagementUseCase as SystemUseCase

__all__ = [
    'SystemUseCase',
]
