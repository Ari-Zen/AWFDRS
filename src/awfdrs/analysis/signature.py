"""
Error signature generation for incident grouping.
"""

import hashlib
import re
from typing import Dict, Any
from src.awfdrs.db.models.events import Event


class ErrorSignatureGenerator:
    """
    Generates unique signatures for error grouping.

    Normalizes error messages and creates stable hashes for similar errors.
    """

    def generate_signature(self, event: Event) -> str:
        """
        Generate unique signature for an event.

        Args:
            event: Event to generate signature for

        Returns:
            Signature hash string
        """
        payload = event.payload
        error_pattern = self.extract_error_pattern(payload)

        # Build signature components
        components = [
            payload.get('error_code', 'unknown'),
            payload.get('vendor', ''),
            error_pattern
        ]

        # Create stable hash
        signature_str = '|'.join(str(c) for c in components)
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]

    def normalize_error_message(self, message: str) -> str:
        """
        Normalize error message by removing variable data.

        Args:
            message: Raw error message

        Returns:
            Normalized error message
        """
        if not message:
            return ""

        # Remove UUIDs
        normalized = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            'UUID',
            message,
            flags=re.IGNORECASE
        )

        # Remove timestamps
        normalized = re.sub(
            r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',
            'TIMESTAMP',
            normalized
        )

        # Remove numeric IDs
        normalized = re.sub(r'\bid[:\s]*\d+\b', 'ID', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\b\d{6,}\b', 'NUMERIC_ID', normalized)

        # Remove IP addresses
        normalized = re.sub(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'IP_ADDRESS',
            normalized
        )

        # Remove amounts/numbers with decimals
        normalized = re.sub(r'\$?\d+\.\d+', 'AMOUNT', normalized)

        # Normalize whitespace
        normalized = ' '.join(normalized.split())

        return normalized.lower()

    def extract_error_pattern(self, payload: Dict[str, Any]) -> str:
        """
        Extract error pattern from payload.

        Args:
            payload: Event payload

        Returns:
            Normalized error pattern
        """
        # Extract error message
        error_message = payload.get('error_message', '') or payload.get('message', '')

        if error_message:
            return self.normalize_error_message(str(error_message))

        # Fallback to error details if no message
        error_details = payload.get('error_details', {})
        if isinstance(error_details, dict):
            detail_msg = error_details.get('message', '')
            if detail_msg:
                return self.normalize_error_message(str(detail_msg))

        return "unknown_pattern"
