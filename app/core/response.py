from typing import Any, Optional


class StandardResponse:
    """Standard response wrapper for all API endpoints."""

    @staticmethod
    def success(data: Any) -> dict:
        """Wrap successful response."""
        return {
            "success": True,
            "data": data
        }

    @staticmethod
    def error(error: str) -> dict:
        """Wrap error response."""
        print(f"DEBUG: StandardResponse.error called with: {error}")
        return {
            "success": False,
            "error": error
        }
