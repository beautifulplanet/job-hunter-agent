import re
from typing import Dict, List


class PIIScrubber:
    """
    Privacy Vault: Scrubs PII from text and restores it later.

    Flow:
      1. Register manual scrub terms (names, addresses, etc.)
      2. Call scrub(text) — applies regex patterns + manual terms
      3. Send scrubbed text to LLM
      4. Call restore(text) — swaps placeholders back to real values
    """

    def __init__(self):
        self.mappings: Dict[str, str] = {}
        self.manual_scrubs: List[Dict[str, str]] = []
        self.counter = 0

        # Regex patterns for common PII
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        }

    def register_name(self, full_name: str):
        """Register a person's name for scrubbing (handles full name + first/last)."""
        parts = full_name.strip().split()
        # Full name (both casings)
        self.manual_scrubs.append({
            'term': full_name,
            'placeholder': '<CANDIDATE_NAME>'
        })
        self.manual_scrubs.append({
            'term': full_name.upper(),
            'placeholder': '<CANDIDATE_NAME>'
        })
        self.manual_scrubs.append({
            'term': full_name.lower(),
            'placeholder': '<CANDIDATE_NAME>'
        })
        # Individual parts (first name, last name)
        if len(parts) >= 2:
            self.manual_scrubs.append({
                'term': parts[0],
                'placeholder': '<FIRST_NAME>'
            })
            self.manual_scrubs.append({
                'term': parts[-1],
                'placeholder': '<LAST_NAME>'
            })

    def register_address(self, address: str):
        """Register an address for scrubbing."""
        if address.strip():
            self.manual_scrubs.append({
                'term': address.strip(),
                'placeholder': '<ADDRESS>'
            })

    def register_custom(self, term: str, placeholder_name: str):
        """Register any custom term for scrubbing."""
        if term.strip():
            self.manual_scrubs.append({
                'term': term.strip(),
                'placeholder': f'<{placeholder_name.upper()}>'
            })

    def scrub(self, text: str) -> str:
        """
        Scrubs all registered PII from text.
        Order: Manual terms first (longest first to avoid partial matches),
        then regex patterns.
        """
        scrubbed = text

        # 1. Manual scrubs (sort by length descending to avoid partial matches)
        sorted_scrubs = sorted(self.manual_scrubs, key=lambda x: len(x['term']), reverse=True)
        for item in sorted_scrubs:
            # Case-insensitive matching to catch all variations
            pattern = re.escape(item['term'])
            matches = re.findall(pattern, scrubbed, re.IGNORECASE)
            if matches:
                for match in set(matches):
                    self.mappings[item['placeholder']] = match
                    scrubbed = scrubbed.replace(match, item['placeholder'])

        # 2. Regex: Emails
        emails = re.findall(self.patterns['email'], scrubbed)
        for email in set(emails):
            placeholder = f"<EMAIL_{self._get_next_id()}>"
            self.mappings[placeholder] = email
            scrubbed = scrubbed.replace(email, placeholder)

        # 3. Regex: Phone numbers
        phones = re.findall(self.patterns['phone'], scrubbed)
        for phone in set(phones):
            placeholder = f"<PHONE_{self._get_next_id()}>"
            self.mappings[placeholder] = phone
            scrubbed = scrubbed.replace(phone, placeholder)

        return scrubbed

    def restore(self, text: str) -> str:
        """Swaps all placeholders back to real values."""
        restored = text
        for placeholder, original in self.mappings.items():
            restored = restored.replace(placeholder, original)
        return restored

    def _get_next_id(self) -> int:
        self.counter += 1
        return self.counter

    def get_report(self) -> str:
        """Returns a human-readable report of all PII found and scrubbed."""
        if not self.mappings:
            return "No PII detected."
        lines = ["PII Scrub Report:", "-" * 40]
        for placeholder, original in self.mappings.items():
            lines.append(f"  {placeholder} → {original}")
        lines.append("-" * 40)
        return "\n".join(lines)
