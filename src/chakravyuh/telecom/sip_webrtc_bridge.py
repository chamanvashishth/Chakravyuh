"""
Phase 2 : SIP / WebRTC Call Forwarding & 3GPP IMS Conference Merge Bridge.

Implements:
1. ITU-T G.711 mu-law (`PCMU/8000`) 8-bit logarithmic audio compression & decompression
   for 8 kHz PSTN carrier RTP trunks.
2. RFC 3261 / RFC 3515 `SIP REFER` & `SIP INVITE` dialog generation with SDP (`v=0`)
   negotiating 8000 Hz G.711 mu-law and muting the victim's cellular leg at the IMS bridge.
"""

import hashlib
import uuid
from typing import Any, Dict
import numpy as np

from chakravyuh.models.schemas import CallSession, utc_now_iso


class SIPWebRTCBridgeService:
    """Manages SIP/WebRTC call merging, victim mute gating, and G.711 mu-law RTP framing."""

    MU = 255.0

    @classmethod
    def encode_pcm16_to_ulaw(cls, pcm16: np.ndarray) -> np.ndarray:
        """
        Encode 16-bit linear PCM samples (`[-32768, 32767]`) into 8-bit ITU-T G.711 mu-law
        (`uint8` in `[0, 255]`).
        """
        x = np.asarray(pcm16, dtype=np.float32) / 32768.0
        x = np.clip(x, -1.0, 1.0)
        sign = np.sign(x)
        companded = sign * (np.log1p(cls.MU * np.abs(x)) / np.log1p(cls.MU))
        quantized = np.round(((companded + 1.0) / 2.0) * cls.MU)
        return np.clip(quantized, 0, 255).astype(np.uint8)

    @classmethod
    def decode_ulaw_to_pcm16(cls, ulaw_bytes: np.ndarray) -> np.ndarray:
        """
        Decode 8-bit ITU-T G.711 mu-law (`uint8` in `[0, 255]`) back to 16-bit linear PCM.
        """
        u = np.asarray(ulaw_bytes, dtype=np.float32)
        y = (u / cls.MU) * 2.0 - 1.0
        sign = np.sign(y)
        expanded = sign * (1.0 / cls.MU) * (np.power(1.0 + cls.MU, np.abs(y)) - 1.0)
        pcm = np.clip(expanded * 32767.0, -32768.0, 32767.0)
        return pcm.astype(np.int16)

    def initiate_sip_call_merge(
        self, session: CallSession, victim_msisdn: str = "+91-9811029384"
    ) -> Dict[str, Any]:
        """
        Generate RFC 3261 / RFC 3515 SIP REFER & INVITE signaling to merge the Chakravyuh
        Honeypot SIP Trunk into the user's active cellular call and mute the human victim's
        uplink microphone at the IMS conference focus.
        """
        branch_id = f"z9hG4bK-{uuid.uuid4().hex[:12]}"
        call_id = f"chakravyuh-ims-{session.session_id.lower()}@sip.gnani-defense.in"
        tag_from = hashlib.sha256(session.session_id.encode("utf-8")).hexdigest()[:8]
        ssrc_hex = hashlib.sha256(call_id.encode("utf-8")).hexdigest()[:8].upper()

        sdp_body = (
            "v=0\r\n"
            f"o=chakravyuh-vachana-vc 2890844526 2890842807 IN IP4 10.240.18.92\r\n"
            "s=Chakravyuh Active Voice-Clone Honeypot (vachana-vc-v1 [1,768] bfloat16)\r\n"
            "c=IN IP4 10.240.18.92\r\n"
            "t=0 0\r\n"
            "m=audio 49170 RTP/AVP 0 8 101\r\n"
            "a=rtpmap:0 PCMU/8000/1\r\n"
            "a=rtpmap:8 PCMA/8000/1\r\n"
            "a=rtpmap:101 telephone-event/8000\r\n"
            "a=ptime:20\r\n"
            "a=sendrecv\r\n"
            f"a=x-vachana-embedding-sha256:{session.speaker_embedding.embedding_sha256}\r\n"
        )

        sip_refer_packet = (
            f"REFER sip:{session.caller_number}@ims.mnc045.mcc404.3gppnetwork.org SIP/2.0\r\n"
            f"Via: SIP/2.0/TLS 10.240.18.92:5061;branch={branch_id}\r\n"
            f"From: <sip:{victim_msisdn}@ims.mnc045.mcc404.3gppnetwork.org>;tag={tag_from}\r\n"
            f"To: <sip:{session.caller_number}@ims.mnc045.mcc404.3gppnetwork.org>\r\n"
            f"Call-ID: {call_id}\r\n"
            "CSeq: 102 REFER\r\n"
            f"Refer-To: <sip:honeypot-{session.session_id.lower()}@sip.gnani-defense.in;isfocus>\r\n"
            "Referred-By: <sip:chakravyuh-controller@sip.gnani-defense.in>\r\n"
            "X-Victim-Uplink-Policy: MUTE_HUMAN_MIC_ENABLE_VACHANA_DECOY\r\n"
            f"Content-Length: {len(sdp_body)}\r\n"
            "Content-Type: application/sdp\r\n\r\n"
            f"{sdp_body}"
        )

        return {
            "status": "SIP_IMS_CONFERENCE_MERGED",
            "merged_at": utc_now_iso(),
            "session_id": session.session_id,
            "call_id": call_id,
            "suspect_caller_msisdn": session.caller_number,
            "victim_msisdn": victim_msisdn,
            "victim_uplink_state": "MUTED_AT_IMS_BRIDGE (Human Protected)",
            "honeypot_downlink_state": "ACTIVE_DUPLEX_8KHZ_PCMU (vachana-vc-v1 + Prisma v2.5)",
            "rtp_ssrc": f"0x{ssrc_hex}",
            "codec": "ITU-T G.711 PCMU/8000/1 (64 kbps, 20ms ptime)",
            "sdp_offer": sdp_body,
            "sip_refer_frame": sip_refer_packet,
        }
