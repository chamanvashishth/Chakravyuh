"""
Chakravyuh Orchestrator & FastAPI REST + WebSocket Endpoints.

Provides:
- `HoneypotOrchestrator`: Coordinates `vachana-vc-v1`, `Prisma v2.5`, `IOCExtractor`,
  `Evon v3.3`, `I4CDossierCompiler`, `SIPWebRTCBridgeService`, `NPCIFraudEngineService`,
  and `ChakravyuhDatabase`.
- REST Endpoints (`/api/v1/*`)
- Full-Duplex WebSocket Endpoint (`/ws/call/{session_id}`)
"""

import base64
import json
import secrets
import uuid
from typing import Any, Dict, List, Optional
import numpy as np
from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from chakravyuh.asr.prisma_asr import PrismaTelephonicASREngine
from chakravyuh.config import CONFIG
from chakravyuh.deception.evon_agent import (
    EvonDeceptionEngine,
    SCAM_SCENARIOS,
    HACKATHON_SCENARIOS,
)
from chakravyuh.dossier.i4c_compiler import I4CDossierCompiler
from chakravyuh.intelligence.ioc_extractor import IOCExtractor
from chakravyuh.models.schemas import (
    CallSession,
    CallStatus,
    CreateSessionRequest,
    DeceptionStage,
    I4CDossier,
    ScamCategory,
    ThreatFeedEntry,
    TranscriptTurn,
    TurnInputRequest,
    TurnProcessingResponse,
    utc_now_iso,
)
from chakravyuh.storage.database import ChakravyuhDatabase
from chakravyuh.telecom.sip_webrtc_bridge import SIPWebRTCBridgeService
from chakravyuh.threat_intel.npci_fraud_engine import NPCIFraudEngineService
from chakravyuh.voice.vachana_vc import BFloat16Tensor, VachanaVoiceCloneEngine


class TransactionCheckRequest(BaseModel):
    """Request payload for Phase 3 Fintech / NPCI pre-transaction mule screening."""

    recipient_vpa: Optional[str] = Field(default=None)
    account_number: Optional[str] = Field(default=None)
    ifsc_code: Optional[str] = Field(default=None)
    amount_inr: float = Field(default=50000.0, gt=0.0)


class SIPMergeRequest(BaseModel):
    """Request payload for Phase 2 SIP/WebRTC IMS conference call merge."""

    victim_msisdn: str = Field(default="+91-9811029384")


class HoneypotOrchestrator:
    """Central coordinator binding all Chakravyuh AI/ML, Telecom, and Threat Intel services."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db = ChakravyuhDatabase(db_path=db_path)
        self.vachana = VachanaVoiceCloneEngine()
        self.prisma = PrismaTelephonicASREngine()
        self.evon = EvonDeceptionEngine()
        self.ioc_extractor = IOCExtractor()
        self.dossier_compiler = I4CDossierCompiler()
        self.sip_bridge = SIPWebRTCBridgeService()
        self.fraud_engine = NPCIFraudEngineService(db=self.db)
        self._embedding_cache: Dict[str, BFloat16Tensor] = {}

    def create_session(self, req: CreateSessionRequest) -> CallSession:
        """
        Hand over a suspicious scam call to the Chakravyuh Honeypot:
        1. Extract `[1, 768]` `torch.bfloat16` speaker embedding from 10s user reference clip.
        2. Initialize session state and persist to SQLite.
        """
        session_id = f"CHK-{uuid.uuid4().hex[:10].upper()}"

        ref_samples: Optional[np.ndarray] = None
        if req.reference_audio_base64:
            try:
                raw_bytes = base64.b64decode(req.reference_audio_base64)
                if len(raw_bytes) >= 4:
                    int16_arr = np.frombuffer(
                        raw_bytes[: len(raw_bytes) - (len(raw_bytes) % 2)], dtype=np.int16
                    )
                    ref_samples = int16_arr.astype(np.float32) / 32768.0
            except Exception:
                ref_samples = None

        bf16_tensor, emb_meta = self.vachana.extract_speaker_embedding(
            reference_audio=ref_samples,
            sample_rate=16000,
            speaker_seed=req.speaker_profile_seed,
        )
        self._embedding_cache[session_id] = bf16_tensor

        session = CallSession(
            session_id=session_id,
            caller_number=req.caller_number,
            victim_alias=req.victim_alias,
            status=CallStatus.ACTIVE_ENGAGEMENT,
            scam_category=req.initial_scam_hint,
            claimed_authority="Incoming Suspected Scam Call (Handover Active)",
            threat_score=65.0,
            current_stage=DeceptionStage.STAGE_1_INITIAL_PANIC,
            time_wasted_sec=12,
            speaker_embedding=emb_meta,
            turns=[],
            extracted_iocs=[],
        )
        self.db.save_session(session)
        initial_dossier = self.dossier_compiler.compile_dossier(session)
        self.db.save_dossier(initial_dossier)
        return session

    def _get_or_restore_embedding(self, session: CallSession) -> BFloat16Tensor:
        if session.session_id in self._embedding_cache:
            return self._embedding_cache[session.session_id]
        bf16_tensor, _ = self.vachana.extract_speaker_embedding(speaker_seed=42)
        self._embedding_cache[session.session_id] = bf16_tensor
        return bf16_tensor

    def process_scammer_turn(
        self, session_id: str, turn_req: TurnInputRequest
    ) -> TurnProcessingResponse:
        """
        Execute one full-duplex honeypot interception cycle:
        1. `Prisma v2.5` processes 8 kHz telephonic scammer audio & classifies scam intent.
        2. `IOCExtractor` captures any new Mule UPI IDs, Bank Accounts, IFSCs, Phones, or URLs.
        3. `Evon v3.3` advances the tactical Hinglish deception state machine.
        4. `vachana-vc-v1` synthesizes anxious user voice decoy conditioned on `[1, 768] bfloat16`.
        5. `I4CDossierCompiler` updates the live Cybercrime FIR Dossier & Phase-3 Threat Feed.
        """
        session = self.db.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found")

        prev_stage = session.current_stage
        scammer_turn_id = len(session.turns) + 1

        _, audio_telemetry = self.prisma.process_telephonic_audio(
            input_sr=turn_req.input_sample_rate_hz,
            fallback_text=turn_req.scammer_text,
            audio_pcm_base64=turn_req.audio_pcm_base64,
        )
        scam_analysis = self.prisma.classify_scammer_utterance(
            turn_req.scammer_text, prior_category=session.scam_category
        )

        new_iocs = self.ioc_extractor.extract_from_text(
            text=turn_req.scammer_text,
            turn_id=scammer_turn_id,
            existing_iocs=session.extracted_iocs,
        )
        session.extracted_iocs.extend(new_iocs)

        scammer_turn = TranscriptTurn(
            turn_id=scammer_turn_id,
            session_id=session.session_id,
            speaker="SCAMMER",
            text=turn_req.scammer_text,
            deception_stage=prev_stage,
            audio_telemetry=audio_telemetry,
            extracted_iocs=new_iocs,
        )
        session.turns.append(scammer_turn)

        next_stage, stall_reason, reply_text = self.evon.generate_deception_turn(
            scammer_text=turn_req.scammer_text,
            scam_category=scam_analysis.scam_category,
            current_stage=prev_stage,
            all_session_iocs=session.extracted_iocs,
            new_turn_iocs=new_iocs,
        )

        speaker_tensor = self._get_or_restore_embedding(session)
        voice_payload = self.vachana.synthesize_decoy_reply(
            reply_text=reply_text,
            speaker_embedding=speaker_tensor,
            stage=next_stage,
        )

        honeypot_turn_id = len(session.turns) + 1
        honeypot_turn = TranscriptTurn(
            turn_id=honeypot_turn_id,
            session_id=session.session_id,
            speaker="HONEYPOT_DECOY",
            text=reply_text,
            deception_stage=next_stage,
            tactical_stall_reason=stall_reason,
            voice_synthesis=voice_payload,
            extracted_iocs=[],
        )
        session.turns.append(honeypot_turn)

        session.scam_category = scam_analysis.scam_category
        session.claimed_authority = scam_analysis.claimed_authority
        session.threat_score = max(session.threat_score, scam_analysis.threat_score)
        session.current_stage = next_stage
        session.time_wasted_sec += 48 + (len(new_iocs) * 25)
        session.updated_at = utc_now_iso()
        if next_stage == DeceptionStage.STAGE_6_INFINITE_HOLD_LOOP:
            session.status = CallStatus.DOSSIER_FINALIZED

        self.db.save_session(session)
        updated_dossier = self.dossier_compiler.compile_dossier(session)
        self.db.save_dossier(updated_dossier)

        return TurnProcessingResponse(
            session_id=session.session_id,
            scammer_turn=scammer_turn,
            honeypot_turn=honeypot_turn,
            newly_extracted_iocs=new_iocs,
            scam_analysis=scam_analysis,
            previous_stage=prev_stage,
            current_stage=next_stage,
            updated_dossier=updated_dossier,
        )

    def run_scenario_simulation(
        self, session_id: str, scenario: ScamCategory
    ) -> List[TurnProcessingResponse]:
        """Run all scripted turns of a fraud scenario sequentially."""
        turns_script = SCAM_SCENARIOS.get(
            scenario, SCAM_SCENARIOS[ScamCategory.DIGITAL_ARREST]
        )
        results: List[TurnProcessingResponse] = []
        for step in turns_script:
            res = self.process_scammer_turn(
                session_id=session_id,
                turn_req=TurnInputRequest(
                    scammer_text=step["scammer_text"],
                    input_sample_rate_hz=8000,
                ),
            )
            results.append(res)
        return results


def create_router(
    orchestrator: HoneypotOrchestrator,
    api_key: Optional[str] = None,
) -> APIRouter:
    """Create the FastAPI APIRouter with REST, Phase 2 SIP, Phase 3 Threat Feed, and WebSocket endpoints."""
    effective_api_key = api_key if api_key is not None else CONFIG.api_key
    router = APIRouter()

    def verify_auth(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> None:
        if not effective_api_key:
            return
        if not x_api_key or not secrets.compare_digest(x_api_key, effective_api_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing X-API-Key header",
            )

    auth_dep = [Depends(verify_auth)]

    @router.get("/api/v1/health")
    def health_check() -> Dict[str, Any]:
        return {
            "status": "OPERATIONAL",
            "system": CONFIG.app_name,
            "version": CONFIG.version,
            "models": {
                "voice_clone": {
                    "id": CONFIG.vachana_model_id,
                    "tensor_shape": [1, 768],
                    "dtype": "torch.bfloat16",
                    "reference_window_sec": 10.0,
                },
                "telephonic_asr": {
                    "id": CONFIG.prisma_model_id,
                    "sample_rate_hz": 8000,
                    "bandpass_filter_hz": "300-3400Hz",
                },
                "deception_agent": {
                    "id": CONFIG.evon_model_id,
                    "language": "Hinglish (Code-Switched Hindi-English)",
                },
            },
            "roadmap_modules": {
                "phase_2_sip_bridge": "ACTIVE (ITU-T G.711 PCMU/8000 + RFC 3515 SIP REFER)",
                "phase_3_threat_feed": "ACTIVE (STIX-3.0 + Pre-Transaction Mule Screening)",
            },
        }

    @router.get("/api/v1/scenarios")
    def list_scenarios() -> Dict[str, Any]:
        return {
            "scenarios": {
                cat.value: steps for cat, steps in SCAM_SCENARIOS.items()
            }
        }

    @router.post("/api/v1/sessions", response_model=CallSession, dependencies=auth_dep)
    def create_session(req: CreateSessionRequest) -> CallSession:
        return orchestrator.create_session(req)

    @router.get("/api/v1/sessions", response_model=List[CallSession], dependencies=auth_dep)
    def list_sessions() -> List[CallSession]:
        return orchestrator.db.list_sessions()

    @router.get("/api/v1/sessions/{session_id}", response_model=CallSession, dependencies=auth_dep)
    def get_session(session_id: str) -> CallSession:
        session = orchestrator.db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
        return session

    @router.post(
        "/api/v1/sessions/{session_id}/turn",
        response_model=TurnProcessingResponse,
        dependencies=auth_dep,
    )
    def submit_turn(session_id: str, req: TurnInputRequest) -> TurnProcessingResponse:
        try:
            return orchestrator.process_scammer_turn(session_id, req)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.post(
        "/api/v1/sessions/{session_id}/simulate",
        response_model=List[TurnProcessingResponse],
        dependencies=auth_dep,
    )
    def simulate_scenario(
        session_id: str, scenario: ScamCategory = ScamCategory.DIGITAL_ARREST
    ) -> List[TurnProcessingResponse]:
        try:
            return orchestrator.run_scenario_simulation(session_id, scenario)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get("/api/v1/sessions/{session_id}/dossier", response_model=I4CDossier, dependencies=auth_dep)
    def get_dossier(session_id: str) -> I4CDossier:
        dossier = orchestrator.db.get_dossier(session_id)
        if not dossier:
            raise HTTPException(
                status_code=404, detail=f"Dossier for session '{session_id}' not found"
            )
        return dossier

    @router.post("/api/v1/sessions/{session_id}/sip-merge", dependencies=auth_dep)
    def merge_sip_call(
        session_id: str, req: SIPMergeRequest = SIPMergeRequest()
    ) -> Dict[str, Any]:
        """Phase 2: Initiate SIP/WebRTC IMS conference merge and mute human victim uplink."""
        session = orchestrator.db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
        return orchestrator.sip_bridge.initiate_sip_call_merge(
            session=session, victim_msisdn=req.victim_msisdn
        )

    @router.get("/api/v1/threat-feed", response_model=List[ThreatFeedEntry], dependencies=auth_dep)
    def get_threat_feed(limit: int = 100) -> List[ThreatFeedEntry]:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
        return orchestrator.db.list_threat_feed(limit=limit)

    @router.post("/api/v1/threat-feed/check-transaction", dependencies=auth_dep)
    def check_transaction(req: TransactionCheckRequest) -> Dict[str, Any]:
        """Phase 3: Pre-transaction UPI/IMPS mule screening for Fintech Fraud Engines."""
        return orchestrator.fraud_engine.check_transaction_risk(
            recipient_vpa=req.recipient_vpa,
            account_number=req.account_number,
            ifsc_code=req.ifsc_code,
            amount_inr=req.amount_inr,
        )

    @router.post("/api/v1/threat-feed/broadcast/{session_id}", dependencies=auth_dep)
    def broadcast_session_threat_intel(session_id: str) -> Dict[str, Any]:
        """Phase 3: Broadcast HMAC-SHA256 signed STIX-3.0 bundle of extracted mule IOCs."""
        try:
            return orchestrator.fraud_engine.broadcast_session_iocs(session_id=session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.websocket("/ws/call/{session_id}")
    async def websocket_call_stream(websocket: WebSocket, session_id: str) -> None:
        """
        Full-duplex WebSocket streaming endpoint for real-time scam call takeover.
        """
        session = orchestrator.db.get_session(session_id)
        if not session:
            await websocket.close(code=1008)
            return

        await websocket.accept()
        await websocket.send_json(
            {
                "event": "handover_established",
                "session_id": session.session_id,
                "status": session.status.value,
                "speaker_embedding": session.speaker_embedding.dict(),
                "current_stage": session.current_stage.value,
            }
        )

        try:
            while True:
                raw_msg = await websocket.receive_text()
                try:
                    payload = json.loads(raw_msg)
                except json.JSONDecodeError:
                    await websocket.send_json(
                        {"event": "error", "detail": "Invalid JSON frame"}
                    )
                    continue

                msg_type = payload.get("type", "scammer_turn")
                if msg_type == "ping":
                    await websocket.send_json({"event": "pong", "session_id": session_id})
                    continue

                scammer_text = str(payload.get("scammer_text", "")).strip()
                if not scammer_text:
                    await websocket.send_json(
                        {"event": "error", "detail": "scammer_text is required"}
                    )
                    continue

                turn_req = TurnInputRequest(
                    scammer_text=scammer_text,
                    audio_pcm_base64=payload.get("audio_pcm_base64"),
                    input_sample_rate_hz=int(payload.get("input_sample_rate_hz", 8000)),
                )
                result = orchestrator.process_scammer_turn(session_id, turn_req)
                await websocket.send_json(
                    {
                        "event": "honeypot_turn_result",
                        "data": json.loads(result.json()),
                    }
                )
        except WebSocketDisconnect:
            return

    return router
