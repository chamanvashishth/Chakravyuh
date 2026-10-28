"""
Multi-Modal Threat Intelligence & Mule Account IOC Extractor.

Extracts, validates, and resolves:
1. UPI IDs / Virtual Payment Addresses (VPAs) across NPCI PSP handles
2. Indian Bank Account Numbers (9 to 18 digits) with contextual disambiguation
3. RBI IFSC Codes (11-char `^[A-Z]{4}0[A-Z0-9]{6}$`) with automatic bank name lookup
4. Scammer Mobile / WhatsApp Numbers (`+91` / 10-digit Indian mobile numbers)
5. Phishing URLs, `.apk` sideload links, and remote-access tool domains
6. Spoofed CBI / Customs / Court Warrant & Officer Badge IDs
"""

import hashlib
import re
from typing import Dict, List, Set

from chakravyuh.models.schemas import ExtractedIOC, IOCType


UPI_PSP_REGISTRY: Dict[str, str] = {
    "ybl": "PhonePe / Yes Bank NPCI Switch",
    "ibl": "PhonePe / ICICI Bank NPCI Switch",
    "axl": "PhonePe / Axis Bank NPCI Switch",
    "okaxis": "Google Pay / Axis Bank",
    "oksbi": "Google Pay / State Bank of India",
    "okhdfcbank": "Google Pay / HDFC Bank",
    "okicici": "Google Pay / ICICI Bank",
    "paytm": "Paytm Payments Bank / Yes Bank",
    "ptyes": "Paytm / Yes Bank",
    "ptaxis": "Paytm / Axis Bank",
    "pthdfc": "Paytm / HDFC Bank",
    "ptsbi": "Paytm / State Bank of India",
    "apl": "Amazon Pay / Axis Bank",
    "rapl": "Amazon Pay / RBL Bank",
    "upi": "BHIM / NPCI Unified Handle",
    "sbi": "YONO / State Bank of India",
    "hdfcbank": "HDFC Bank UPI",
    "icici": "iMobile / ICICI Bank",
    "axisbank": "Axis Bank UPI",
    "kotak": "Kotak Mahindra Bank UPI",
    "barodampay": "Bank of Baroda M-Connect",
    "fbl": "Federal Bank UPI",
    "indus": "IndusInd Bank UPI",
    "pnb": "Punjab National Bank UPI",
    "cnrb": "Canara Bank UPI",
    "idfcfirst": "IDFC First Bank UPI",
    "aubank": "AU Small Finance Bank UPI",
    "waicici": "WhatsApp Pay / ICICI Bank",
    "wasbi": "WhatsApp Pay / State Bank of India",
    "wahdfcbank": "WhatsApp Pay / HDFC Bank",
    "waaxis": "WhatsApp Pay / Axis Bank",
}

EXCLUDED_EMAIL_DOMAINS: Set[str] = {
    "gmail.com",
    "yahoo.com",
    "yahoo.co.in",
    "outlook.com",
    "hotmail.com",
    "icloud.com",
    "protonmail.com",
    "rediffmail.com",
    "gov.in",
    "nic.in",
    "org.in",
    "ac.in",
}

IFSC_BANK_PREFIX_MAP: Dict[str, str] = {
    "SBIN": "State Bank of India (SBI)",
    "HDFC": "HDFC Bank Ltd.",
    "ICIC": "ICICI Bank Ltd.",
    "UTIB": "Axis Bank Ltd.",
    "PUNB": "Punjab National Bank (PNB)",
    "BARB": "Bank of Baroda (BoB)",
    "KKBK": "Kotak Mahindra Bank",
    "CNRB": "Canara Bank",
    "UBIN": "Union Bank of India",
    "IDIB": "Indian Bank",
    "BKID": "Bank of India (BoI)",
    "YESB": "Yes Bank Ltd.",
    "IDFB": "IDFC First Bank",
    "INDB": "IndusInd Bank",
    "FDRL": "Federal Bank",
    "AUBL": "AU Small Finance Bank",
    "PYTM": "Paytm Payments Bank",
    "AIRP": "Airtel Payments Bank",
    "FINO": "Fino Payments Bank",
    "RATN": "RBL Bank",
    "MAHB": "Bank of Maharashtra",
    "UCBA": "UCO Bank",
}


class IOCExtractor:
    """Deterministic + contextual Threat Intelligence IOC Extractor."""

    _UPI_REGEX = re.compile(
        r"\b([a-zA-Z0-9.\-_]{2,64})@([a-zA-Z0-9.\-]{2,32})\b"
    )
    _IFSC_REGEX = re.compile(r"\b([A-Za-z]{4}0[A-Za-z0-9]{6})\b")
    _URL_REGEX = re.compile(
        r"(https?://[^\s<>\"')]+|(?:bit\.ly|tinyurl\.com|t\.me)/[^\s<>\"')]+|\b[a-zA-Z0-9\-_]+\.apk\b)",
        re.IGNORECASE,
    )
    _PHONE_REGEX = re.compile(
        r"(?:\+91[\-\s]?|91[\-\s]?|\b0?)([6-9]\d{4}[\-\s]?\d{5})\b"
    )
    _DIGIT_SEQ_REGEX = re.compile(r"\b(\d{9,18})\b")
    # Require at least one digit in the badge/warrant suffix so URL hostnames like cbi-rbi-verify are never matched
    _BADGE_REGEX = re.compile(
        r"\b((?:CBI|NCB|FIR|RBI|WARRANT|CASE|CUSTOMS)[\-/][A-Z0-9\-/]*\d[A-Z0-9\-/]*)\b",
        re.IGNORECASE,
    )

    _BANK_CONTEXT_WORDS = {
        "account",
        "a/c",
        "ac",
        "acc",
        "khata",
        "imps",
        "neft",
        "rtgs",
        "beneficiary",
        "ifsc",
        "bank",
        "branch",
        "savings",
        "current",
        "deposit",
        "transfer",
    }
    _PHONE_CONTEXT_WORDS = {
        "whatsapp",
        "call",
        "mobile",
        "phone",
        "number",
        "contact",
        "helpline",
        "senior",
        "supervisor",
        "inspector",
    }

    def _make_ioc_id(self, ioc_type: IOCType, value: str) -> str:
        digest = hashlib.sha256(f"{ioc_type.value}:{value.lower()}".encode("utf-8")).hexdigest()
        return f"IOC-{digest[:10].upper()}"

    def extract_from_text(
        self,
        text: str,
        turn_id: int = 1,
        existing_iocs: List[ExtractedIOC] = None,
    ) -> List[ExtractedIOC]:
        """
        Extract all new IOCs from a scammer transcript turn, tagging primary vs. backup mule
        instruments based on previously captured IOCs in the session.
        """
        if existing_iocs is None:
            existing_iocs = []

        existing_keys = {(i.ioc_type, i.value.lower()) for i in existing_iocs}
        prior_upi_count = sum(1 for i in existing_iocs if i.ioc_type == IOCType.UPI_ID)
        prior_bank_count = sum(1 for i in existing_iocs if i.ioc_type == IOCType.BANK_ACCOUNT)

        extracted: List[ExtractedIOC] = []
        seen_in_turn: Set[tuple] = set()
        lower_text = text.lower()

        # 1. Extract UPI IDs (VPAs)
        for match in self._UPI_REGEX.finditer(text):
            user_part, domain_part = match.group(1), match.group(2).lower().rstrip(".")
            full_vpa = f"{user_part}@{domain_part}".lower()
            if domain_part in EXCLUDED_EMAIL_DOMAINS or "." in domain_part:
                continue
            key = (IOCType.UPI_ID, full_vpa)
            if key in existing_keys or key in seen_in_turn:
                continue
            seen_in_turn.add(key)

            provider = UPI_PSP_REGISTRY.get(
                domain_part, f"NPCI UPI PSP Handle (@{domain_part})"
            )
            confidence = 0.99 if domain_part in UPI_PSP_REGISTRY else 0.89
            role = (
                "PRIMARY_MULE_UPI_HANDLE"
                if (prior_upi_count == 0 and len([x for x in extracted if x.ioc_type == IOCType.UPI_ID]) == 0)
                else "SECONDARY_BACKUP_MULE_UPI_HANDLE"
            )
            extracted.append(
                ExtractedIOC(
                    ioc_id=self._make_ioc_id(IOCType.UPI_ID, full_vpa),
                    ioc_type=IOCType.UPI_ID,
                    value=full_vpa,
                    confidence=confidence,
                    bank_or_provider=provider,
                    role_classification=role,
                    context_snippet=text[:180],
                    first_seen_turn=turn_id,
                    flagged_for_npci_freeze=True,
                )
            )

        # 2. Extract IFSC Codes
        for match in self._IFSC_REGEX.finditer(text):
            ifsc_val = match.group(1).upper()
            key = (IOCType.IFSC_CODE, ifsc_val.lower())
            if key in existing_keys or key in seen_in_turn:
                continue
            seen_in_turn.add(key)
            prefix = ifsc_val[:4]
            bank_name = IFSC_BANK_PREFIX_MAP.get(prefix, f"Indian Scheduled Bank ({prefix})")
            extracted.append(
                ExtractedIOC(
                    ioc_id=self._make_ioc_id(IOCType.IFSC_CODE, ifsc_val),
                    ioc_type=IOCType.IFSC_CODE,
                    value=ifsc_val,
                    confidence=0.98,
                    bank_or_provider=bank_name,
                    role_classification="MULE_BRANCH_ROUTING_IFSC",
                    context_snippet=text[:180],
                    first_seen_turn=turn_id,
                    flagged_for_npci_freeze=True,
                )
            )

        upi_digit_prefixes = {
            m.group(1) for m in self._UPI_REGEX.finditer(text) if m.group(1).isdigit()
        }

        # 3. Extract Phone Numbers & Bank Account Numbers with Contextual Disambiguation
        has_bank_context = any(w in lower_text for w in self._BANK_CONTEXT_WORDS)
        has_phone_context = any(w in lower_text for w in self._PHONE_CONTEXT_WORDS)

        detected_phones: Set[str] = set()
        for match in self._PHONE_REGEX.finditer(text):
            raw_phone = re.sub(r"[\-\s]", "", match.group(1))
            full_match_str = match.group(0)
            if raw_phone in upi_digit_prefixes:
                continue
            start_pos = max(0, match.start() - 35)
            end_pos = min(len(lower_text), match.end() + 25)
            window = lower_text[start_pos:end_pos]
            explicit_plus91 = "+91" in full_match_str
            local_bank_kw = any(
                w in window for w in ["account", "a/c", "ac no", "khata", "imps", "rtgs", "neft"]
            )
            local_phone_kw = any(
                w in window for w in ["whatsapp", "call", "mobile", "phone", "number", "helpline", "senior"]
            )

            if explicit_plus91 or local_phone_kw or (has_phone_context and not local_bank_kw):
                normalized_phone = f"+91-{raw_phone}"
                detected_phones.add(raw_phone)
                key = (IOCType.PHONE_NUMBER, normalized_phone.lower())
                if key not in existing_keys and key not in seen_in_turn:
                    seen_in_turn.add(key)
                    extracted.append(
                        ExtractedIOC(
                            ioc_id=self._make_ioc_id(IOCType.PHONE_NUMBER, normalized_phone),
                            ioc_type=IOCType.PHONE_NUMBER,
                            value=normalized_phone,
                            confidence=0.95,
                            bank_or_provider="Indian Telecom MSISDN / WhatsApp C2",
                            role_classification="SCAMMER_COMMAND_NUMBER",
                            context_snippet=text[:180],
                            first_seen_turn=turn_id,
                            flagged_for_npci_freeze=True,
                        )
                    )

        for match in self._DIGIT_SEQ_REGEX.finditer(text):
            digits = match.group(1)
            if digits in detected_phones or digits in upi_digit_prefixes:
                continue
            if len(digits) == 10 and digits[0] in "6789" and not has_bank_context:
                normalized_phone = f"+91-{digits}"
                key = (IOCType.PHONE_NUMBER, normalized_phone.lower())
                if key not in existing_keys and key not in seen_in_turn:
                    seen_in_turn.add(key)
                    extracted.append(
                        ExtractedIOC(
                            ioc_id=self._make_ioc_id(IOCType.PHONE_NUMBER, normalized_phone),
                            ioc_type=IOCType.PHONE_NUMBER,
                            value=normalized_phone,
                            confidence=0.88,
                            bank_or_provider="Indian Telecom MSISDN",
                            role_classification="SCAMMER_CONTACT_NUMBER",
                            context_snippet=text[:180],
                            first_seen_turn=turn_id,
                            flagged_for_npci_freeze=True,
                        )
                    )
                continue

            if has_bank_context or len(digits) >= 11:
                key = (IOCType.BANK_ACCOUNT, digits)
                if key in existing_keys or key in seen_in_turn:
                    continue
                seen_in_turn.add(key)

                resolved_bank = "Indian Scheduled Commercial Bank (Mule Account)"
                for item in extracted + existing_iocs:
                    if item.ioc_type == IOCType.IFSC_CODE:
                        resolved_bank = item.bank_or_provider
                        break

                role = (
                    "PRIMARY_MULE_BANK_ACCOUNT"
                    if prior_bank_count == 0
                    else "SECONDARY_LAYER_MULE_BANK_ACCOUNT"
                )
                extracted.append(
                    ExtractedIOC(
                        ioc_id=self._make_ioc_id(IOCType.BANK_ACCOUNT, digits),
                        ioc_type=IOCType.BANK_ACCOUNT,
                        value=digits,
                        confidence=0.97 if has_bank_context else 0.90,
                        bank_or_provider=resolved_bank,
                        role_classification=role,
                        context_snippet=text[:180],
                        first_seen_turn=turn_id,
                        flagged_for_npci_freeze=True,
                    )
                )

        # 4. Extract Phishing URLs & Malicious APK Links
        url_spans = []
        for match in self._URL_REGEX.finditer(text):
            url_val = match.group(1).rstrip(".,;)")
            url_spans.append((match.start(), match.end()))
            key = (IOCType.PHISHING_URL, url_val.lower())
            if key in existing_keys or key in seen_in_turn:
                continue
            seen_in_turn.add(key)
            provider = (
                "Android RAT / Malicious APK Payload"
                if url_val.lower().endswith(".apk")
                else "Spoofed Phishing / C2 Portal"
            )
            extracted.append(
                ExtractedIOC(
                    ioc_id=self._make_ioc_id(IOCType.PHISHING_URL, url_val),
                    ioc_type=IOCType.PHISHING_URL,
                    value=url_val,
                    confidence=0.96,
                    bank_or_provider=provider,
                    role_classification="PHISHING_INFRASTRUCTURE",
                    context_snippet=text[:180],
                    first_seen_turn=turn_id,
                    flagged_for_npci_freeze=True,
                )
            )

        # 5. Extract Spoofed Officer / Warrant / Case IDs (excluding substrings inside URLs)
        for match in self._BADGE_REGEX.finditer(text):
            if any(s <= match.start() < e for s, e in url_spans):
                continue
            badge_val = match.group(1).upper()
            key = (IOCType.FAKE_OFFICER_ID, badge_val.lower())
            if key in existing_keys or key in seen_in_turn:
                continue
            seen_in_turn.add(key)
            extracted.append(
                ExtractedIOC(
                    ioc_id=self._make_ioc_id(IOCType.FAKE_OFFICER_ID, badge_val),
                    ioc_type=IOCType.FAKE_OFFICER_ID,
                    value=badge_val,
                    confidence=0.93,
                    bank_or_provider="Spoofed Law Enforcement / Warrant Identifier",
                    role_classification="IMPERSONATION_ARTIFACT",
                    context_snippet=text[:180],
                    first_seen_turn=turn_id,
                    flagged_for_npci_freeze=False,
                )
            )

        return extracted
