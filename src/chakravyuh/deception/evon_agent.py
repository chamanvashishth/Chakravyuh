"""
Evon v3.3: Tactical Hinglish Deception Engine & State Machine.

Core Deception Strategy:
Instead of hanging up or sounding robotic, Evon v3.3 acts like an anxious, law-abiding
Indian citizen who wants to comply immediately, but encounters realistic NPCI / banking
technical friction:
- Stage 1 -> Stage 2: Feigns panic and agrees to transfer money immediately; asks where to pay.
- Stage 3 (Primary UPI Stall): As soon as the scammer reveals their primary UPI ID, Evon
  pretends Google Pay / PhonePe is throwing "NPCI Bank Server Busy (Error U16)" and asks
  for a secondary/backup UPI handle.
- Stage 4 (Secondary Mule Bait): Once the secondary UPI handle is extracted, Evon claims
  "₹1,00,000 UPI Daily Limit Reached" and begs for a direct IMPS/RTGS Bank Account Number
  and IFSC Code so they can transfer from netbanking before the arrest warrant executes.
- Stage 5 (Phishing & Supervisor Bait): Once Bank Account + IFSC are captured, Evon claims
  netbanking requires a "Verification Case Portal URL or Senior Officer WhatsApp Number"
  to bypass the 30-minute beneficiary cooling period.
- Stage 6 (Infinite Hold Loop): Keeps the scammer stalled on a "92% RBI OTP Sync" loop
  while the I4C FIR Dossier is finalized.
"""

from typing import Dict, List, Tuple

from chakravyuh.models.schemas import (
    DeceptionStage,
    ExtractedIOC,
    IOCType,
    ScamCategory,
)


# Multi-turn Hinglish fraud vectors across primary Indian telephonic scam categories
SCAM_SCENARIOS: Dict[ScamCategory, List[Dict[str, str]]] = {
    ScamCategory.DIGITAL_ARREST: [
        {
            "scammer_text": (
                "Hello! Main Inspector Vikram Rathore, CBI Cyber Crime HQ Mumbai se bol raha hoon. "
                "Warrant ID CBI-8841 aapke Aadhaar card pe issue hua hai Naresh Goyal Money Laundering "
                "case mein! Aap abhi Digital Arrest mein hain - call disconnect mat karna warna 10 minute "
                "mein local police ghar aake arrest karegi!"
            ),
            "note": "Initial Digital Arrest Coercion & Warrant Threat",
        },
        {
            "scammer_text": (
                "Agar aapko arrest warrant cancel karwana hai toh abhi RBI Secret Supervision Account "
                "mein ₹95,000 verification bond transfer karna hoga. Turant Google Pay ya PhonePe kholo "
                "aur humare primary settlement handle rbi.verification.cell@okaxis pe ₹95,000 bhejo!"
            ),
            "note": "Scammer drops Primary Mule UPI ID (rbi.verification.cell@okaxis)",
        },
        {
            "scammer_text": (
                "Kya bol rahe ho axis server busy hai?! Time waste mat karo court line pe hai! "
                "Achha ruko, humare doosre treasury officer ka backup PhonePe UPI ID note karo: "
                "mumbaicrime.deposit99@ybl: ispe abhi turant transfer maaro aur screenshot bhejo!"
            ),
            "note": "Scammer baited into revealing Secondary Backup Mule UPI ID (mumbaicrime.deposit99@ybl)",
        },
        {
            "scammer_text": (
                "Uff! Tumhara UPI daily limit block ho gaya?! Suno, IMPS/RTGS turant karo! "
                "Account Number likho: 50100482917364 aur IFSC Code hai HDFC0001842. "
                "Saath mein senior officer ke WhatsApp +91-9820471829 ya portal "
                "https://cbi-rbi-verify-court.in/clearance.apk pe receipt upload karo!"
            ),
            "note": "Scammer reveals Mule Bank Account + IFSC + WhatsApp C2 + Phishing APK Link",
        },
    ],
    ScamCategory.FEDEX_PARCEL: [
        {
            "scammer_text": (
                "Main FedEx International Customs Mumbai aur NCB Narcotics Cell se Officer Deshmukh "
                "bol raha hoon. Case ID CUSTOMS-4419: Aapke naam se Taiwan jaane wale parcel mein "
                "450 gram MDMA drugs aur 5 fake passports mile hain! Aapke khilaaf non-bailable NDPS "
                "warrant nikla hai!"
            ),
            "note": "Fake FedEx Customs & Narcotics Seizure Threat",
        },
        {
            "scammer_text": (
                "Agar aap chahte hain ki NCB raid ruk jaye, toh Customs Security Bond ₹88,500 "
                "abhi जमा karna padega. Humara official customs UPI ID fedex.customs.bond@oksbi "
                "hai, abhi 2 minute mein transfer karke UTR number batao!"
            ),
            "note": "Scammer reveals Primary Mule UPI ID (fedex.customs.bond@oksbi)",
        },
        {
            "scammer_text": (
                "SBI server U16 error aa raha hai?! Jaldi doosra UPI handle try karo warna NCB team "
                "nikal jayegi! Yeh lo alternate handle: ncb.clearance.desk@paytm: ispe ₹88,500 "
                "turanat bhejo!"
            ),
            "note": "Scammer reveals Secondary Mule UPI ID (ncb.clearance.desk@paytm)",
        },
        {
            "scammer_text": (
                "UPI limit cross ho gaya toh seedha NEFT/IMPS maro! Customs Escrow Account Number "
                "389201746512 aur IFSC Code SBIN0004821 note karo. Aur apna statement "
                "https://ncb-fedex-clearance-india.com pe upload karke +91-9167283910 pe confirm karo!"
            ),
            "note": "Scammer reveals SBI Mule Account + IFSC + Phishing Domain + C2 Phone",
        },
    ],
    ScamCategory.KYC_BANK_FRAUD: [
        {
            "scammer_text": (
                "Hello sir, main SBI Head Office KYC & Electricity Billing Verification Department "
                "se bol raha hoon. Aapka PAN card aur SBI YONO KYC aaj raat 8 baje block ho jayega "
                "aur ghar ki bijli line kat jayegi! Case FIR-2026-9910 lag chuka hai."
            ),
            "note": "Urgent KYC & Utility Disconnection Threat",
        },
        {
            "scammer_text": (
                "Apna account active rakhne ke liye abhi ₹49,999 refundable KYC re-verification charge "
                "humare NPCI nodal UPI handle sbi.kyc.update24@okicici pe transfer karo,5 minute mein "
                "wapas aa jayega!"
            ),
            "note": "Scammer reveals Primary Mule UPI ID (sbi.kyc.update24@okicici)",
        },
        {
            "scammer_text": (
                "ICICI handle pe technical error aa raha hai? Ruko, humara backup verification UPI ID "
                "lo: pan.verify.nodal@axl: ispe jaldi transfer karo warna account freeze ho jayega!"
            ),
            "note": "Scammer reveals Secondary Backup UPI ID (pan.verify.nodal@axl)",
        },
        {
            "scammer_text": (
                "Agar UPI fail ho raha hai toh IMPS karo: Account No 918273645019, IFSC Code "
                "UTIB0000912. Aur humara KYC support app http://bit.ly/sbi-kyc-fast-update.apk "
                "install karke +91-8879123409 pe screen share karo!"
            ),
            "note": "Scammer reveals Axis Bank Mule Account + IFSC + Malicious APK + Phone",
        },
    ],
}

# Backward compatibility alias
HACKATHON_SCENARIOS = SCAM_SCENARIOS


class EvonDeceptionEngine:
    """
    Evon v3.3 Tactical Hinglish Deception State Machine.

    Evaluates existing + newly extracted IOCs and current deception stage to craft
    context-aware, anxious Hinglish responses that stall the scammer and bait out
    additional mule financial instruments.
    """

    def __init__(self) -> None:
        self.model_name = "Evon-v3.3-Hinglish-Deception"

    def generate_deception_turn(
        self,
        scammer_text: str,
        scam_category: ScamCategory,
        current_stage: DeceptionStage,
        all_session_iocs: List[ExtractedIOC],
        new_turn_iocs: List[ExtractedIOC],
    ) -> Tuple[DeceptionStage, str, str]:
        """
        Determine the next `DeceptionStage`, the `tactical_stall_reason` badge, and the
        synthesized Hinglish response text.
        """
        upi_iocs = [i for i in all_session_iocs if i.ioc_type == IOCType.UPI_ID]
        bank_iocs = [i for i in all_session_iocs if i.ioc_type == IOCType.BANK_ACCOUNT]
        ifsc_iocs = [i for i in all_session_iocs if i.ioc_type == IOCType.IFSC_CODE]
        url_iocs = [i for i in all_session_iocs if i.ioc_type == IOCType.PHISHING_URL]

        # Determine state progression based on extracted intelligence inventory
        if len(bank_iocs) >= 1 and len(ifsc_iocs) >= 1 and len(url_iocs) >= 1:
            next_stage = DeceptionStage.STAGE_6_INFINITE_HOLD_LOOP
        elif len(bank_iocs) >= 1 and len(ifsc_iocs) >= 1:
            next_stage = DeceptionStage.STAGE_5_PHISHING_AND_SUPERVISOR_BAIT
        elif len(upi_iocs) >= 2:
            next_stage = DeceptionStage.STAGE_4_SECONDARY_MULE_BAIT
        elif len(upi_iocs) == 1:
            next_stage = DeceptionStage.STAGE_3_PRIMARY_UPI_STALL
        elif current_stage == DeceptionStage.STAGE_1_INITIAL_PANIC:
            next_stage = DeceptionStage.STAGE_2_COMPLIANCE_HOOK
        else:
            next_stage = DeceptionStage.STAGE_2_COMPLIANCE_HOOK

        # Craft Hinglish response tailored to the stage and extracted IOCs
        if next_stage == DeceptionStage.STAGE_2_COMPLIANCE_HOOK:
            stall_reason = "ANXIOUS_COMPLIANCE_BAIT_FOR_PRIMARY_UPI"
            if scam_category == ScamCategory.FEDEX_PARCEL:
                reply = (
                    "Sir please meri baat suniye, maine kabhi Taiwan koi parcel nahi bheja! "
                    "Meri mummy heart patient hain, please NCB police ko ghar mat bhejiye. "
                    "Main abhi Customs Security Bond bharne ko taiyaar hoon. Batayiye kis UPI ID "
                    "pe paise bhejne hain? Mera GPay aur PhonePe dono khula hai!"
                )
            elif scam_category == ScamCategory.KYC_BANK_FRAUD:
                reply = (
                    "Arre sir please mera SBI account aur bijli connection block mat kijiye! "
                    "Meri saari savings usi mein hai. Main abhi turant KYC verification charge "
                    "transfer kar deta hoon. Please mujhe apna official UPI ID bata dijiye!"
                )
            else:
                reply = (
                    "Sir please mujhe Digital Arrest mat kijiye! Main ek seedha-saadha tax "
                    "bhara citizen hoon, mera Naresh Goyal se koi lena-dena nahi hai! "
                    "Main abhi RBI verification ke liye paise transfer karne ko ready hoon. Please "
                    "batayiye kis UPI handle pe transfer karoon?"
                )

        elif next_stage == DeceptionStage.STAGE_3_PRIMARY_UPI_STALL:
            primary_upi = upi_iocs[0].value
            stall_reason = f"SIMULATED_NPCI_ERROR_U16_ON_{primary_upi.upper()}"
            reply = (
                f"Sir maine abhi `{primary_upi}` daal ke PIN enter kiya, par screen pe gol-gol "
                f"ghoom ke लाल (red) अक्षरों mein 'NPCI Bank Server Busy: Error U16' aa raha hai! "
                f"Mere hath kaanp rahe hain sir, please mujhe arrest mat kijiye. Kya aapke paas "
                f"koi doosra backup UPI ID ya alternate PhonePe/Paytm handle hai jispe main "
                f"turant try karoon?"
            )

        elif next_stage == DeceptionStage.STAGE_4_SECONDARY_MULE_BAIT:
            secondary_upi = upi_iocs[-1].value
            stall_reason = f"SIMULATED_UPI_DAILY_LIMIT_EXCEEDED_ON_{secondary_upi.upper()}"
            reply = (
                f"Sir maine aapke doosre handle `{secondary_upi}` pe bhi try kiya, abhi bol raha "
                f"hai 'UPI 24-Hour Cooling Limit Exceeded (Error Z9)'! Sir mera NetBanking "
                f"IMPS/RTGS bilkul chalu hai. Aap please mujhe seedha Bank Account Number aur "
                f"IFSC Code de dijiye, main abhi 30 second mein IMPS se poora amount bhej deta hoon!"
            )

        elif next_stage == DeceptionStage.STAGE_5_PHISHING_AND_SUPERVISOR_BAIT:
            acct_val = bank_iocs[-1].value
            ifsc_val = ifsc_iocs[-1].value
            stall_reason = f"BAITING_SUPERVISOR_WHATSAPP_AND_PHISHING_LINK ({ifsc_val})"
            reply = (
                f"Sir maine Account `{acct_val}` aur IFSC `{ifsc_val}` IMPS mein add kar diya hai, "
                f"bas bank screen pe maang raha hai 'Enter Official Verification Portal Link or "
                f"Senior Officer WhatsApp Number for Instant High-Value Approval'. Please apna "
                f"WhatsApp number aur verification link bata dijiye taaki OTP turant clear ho jaye!"
            )

        else:  # STAGE_6_INFINITE_HOLD_LOOP
            stall_reason = "INFINITE_OTP_HOLD_LOOP_DOSSIER_LOCKED"
            reply = (
                "Haanji sir, bas line pe rahiye... IMPS High-Value OTP processing 89% pe अटका "
                "hua hai, bank server bol raha hai 'Do not close window for 120 seconds'. "
                "Main screen ke saamne hi baitha hoon sir, jaise hi UTR number aata hai main "
                "aapko turant padh ke sunata hoon, please call mat kaatna!"
            )

        return next_stage, stall_reason, reply
