# Feature Spec 04  -  Evon v3.3 Tactical Deception State Machine & IOC Extractor

## 1. Objective
Implement the `IOCExtractor` (extracting mule UPI IDs, bank account numbers, IFSC codes, phone numbers, phishing links, and fake officer badges) and the `Evon v3.3` Tactical Deception Engine that plays along in anxious Hinglish - feigning UPI app lag and bank limit errors to bait scammers into revealing secondary UPI handles and full bank account details.

## 2. Context & Dependencies
- Depends on: `re`, `uuid`, `src/chakravyuh/models/schemas.py`.

## 3. Exact Implementation Scope
- `src/chakravyuh/intelligence/__init__.py`
- `src/chakravyuh/intelligence/ioc_extractor.py`
- `src/chakravyuh/deception/__init__.py`
- `src/chakravyuh/deception/evon_agent.py`

## 4. Required Behavior
1. **Multi-Modal IOC Extractor (`IOCExtractor`)**:
   - **UPI IDs**: Extracts handles matching `[a-zA-Z0-9.\-_]{2,64}@[a-zA-Z0-9]{2,32}` and resolves the PSP/Bank name (`@ybl` -> PhonePe / Yes Bank, `@okaxis` -> Google Pay / Axis Bank, `@oksbi` -> Google Pay / SBI, `@okhdfcbank` -> Google Pay / HDFC, `@okicici` -> Google Pay / ICICI, `@paytm` -> Paytm Payments Bank, `@ibl` -> PhonePe / ICICI, `@axl` -> PhonePe / Axis). Ignores standard email providers (`gmail.com`, `yahoo.com`, `outlook.com`, `hotmail.com`, `gov.in`).
   - **IFSC Codes**: Extracts `^[A-Z]{4}0[A-Z0-9]{6}$` (case-insensitive input normalized to uppercase) and maps the 4-letter bank prefix to the official Indian bank name.
   - **Bank Account Numbers**: Extracts 9-18 digit numbers when banking context keywords appear (`account`, `a/c`, `ac`, `khata`, `imps`, `neft`, `rtgs`, `beneficiary`, `transfer`, `bank`, `ifsc`) while excluding 10-digit numbers preceded by `call`, `whatsapp`, `mobile`, `phone`, `+91`.
   - **Phone Numbers**: Extracts Indian mobile numbers (`+91-98...`, `9876543210`, etc.) when phone/contact context or standalone 10-digit mobile patterns (`[6-9]\d{9}`) are detected.
   - **Phishing URLs & Fake Officer IDs**: Extracts `https?://...`, shortlinks, `.apk` filenames, and fake badge/warrant numbers (e.g., `CBI-9921`, `FIR-2026-8841`).
2. **`Evon v3.3` Deception State Machine (`EvonDeceptionEngine`)**:
   - Tracks session state across 6 tactical stages:
     - `STAGE_1_INITIAL_PANIC`: Responds to initial arrest/parcel/KYC threat with anxious compliance in natural Hinglish.
     - `STAGE_2_COMPLIANCE_HOOK`: Asks for the verification UPI ID or payment details so the victim can "clear their name immediately".
     - `STAGE_3_PRIMARY_UPI_STALL`: Triggered as soon as the scammer provides the **first UPI ID**. Simulates `"GPay Server Busy / NPCI Error U16"` and asks the scammer for a **secondary/backup UPI ID** ("Sir yeh والا UPI ID pe 'Bank Server Busy Error U16' aa raha hai, mera paisa katne se pehle ruk gaya - kya aapke paas koi doosra backup UPI ID ya PhonePe handle hai?").
     - `STAGE_4_SECONDARY_MULE_BAIT`: Triggered once a **second UPI ID** is extracted (or if the scammer insists). Simulates `"₹1,00,000 UPI Daily Limit Reached"` and baits the scammer into giving a **direct Bank Account Number and IFSC code** for immediate IMPS/RTGS transfer.
     - `STAGE_5_PHISHING_AND_SUPERVISOR_BAIT`: Triggered after Bank Account + IFSC are captured. Pretends the beneficiary cooling period requires a "Verification Link / Senior Officer WhatsApp Number" to extract phishing domains and supervisor numbers.
     - `STAGE_6_INFINITE_HOLD_LOOP`: Keeps the scammer waiting on a simulated `"SBI High-Value OTP Verification (89% complete...)"` while Law Enforcement / I4C dossier is dispatched.
   - Also provides pre-scripted, realistic multi-turn **Hackathon Demo Scenarios** (`DIGITAL_ARREST`, `FEDEX_PARCEL`, `KYC_BANK_FRAUD`) so a 60-second live demo or automated simulation can step through turn-by-turn effortlessly.

## 5. Acceptance Criteria & Definition of Done
- Primary UPI extraction transitions state to `STAGE_3_PRIMARY_UPI_STALL`.
- Secondary UPI extraction transitions state to `STAGE_4_SECONDARY_MULE_BAIT`.
- Bank account + IFSC extraction transitions state to `STAGE_5_PHISHING_AND_SUPERVISOR_BAIT`.
- All extracted IOCs are deduplicated per session while preserving `first_seen_turn`.
