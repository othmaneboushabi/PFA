"""Route WebSocket pour la transcription en temps réel."""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.services.streaming_service import get_streaming_service
from app.services.translation_service import get_translation_service

router = APIRouter()


@router.websocket("/ws/transcribe")
async def websocket_transcribe(
    websocket: WebSocket,
    language: str = "fr",
    translate: bool = False,
    target_lang: str = "en",
):
    """WebSocket pour transcription temps réel."""
    await websocket.accept()
    logger.info(f"🔌 WebSocket connecté | langue={language}")

    streaming_service = get_streaming_service()
    translation_service = get_translation_service() if translate else None

    # Accumuler TOUT l'audio jusqu'à l'arrêt
    audio_buffer = []
    total_bytes = 0

    try:
        await websocket.send_json({
            "type": "ready",
            "message": f"Connexion établie — langue={language}"
        })

        while True:
            data = await websocket.receive()

            if "bytes" in data:
                chunk = data["bytes"]
                audio_buffer.append(chunk)
                total_bytes += len(chunk)
                logger.info(f"📊 Chunk reçu : {len(chunk)} bytes | Total : {total_bytes} bytes")

                # Envoyer confirmation que l'audio est reçu
                await websocket.send_json({
                    "type": "receiving",
                    "total_bytes": total_bytes
                })

            elif "text" in data:
                try:
                    command = json.loads(data["text"])

                    if command.get("action") == "stop":
                        logger.info(f"⏹ Stop reçu — transcription de {total_bytes} bytes...")

                        if audio_buffer:
                            result = await streaming_service.transcribe_stream(
                                audio_chunks=audio_buffer,
                                language=language,
                            )

                            if result.get("text"):
                                response = {
                                    "type": "transcription",
                                    "text": result["text"],
                                    "language": result.get("language", language),
                                    "is_final": True,
                                }

                                if translate and translation_service:
                                    try:
                                        translation = translation_service.translate(
                                            text=result["text"],
                                            src_lang=language,
                                            tgt_lang=target_lang,
                                        )
                                        response["translation"] = translation.get("translated_text", "")
                                        response["target_lang"] = target_lang
                                    except Exception as e:
                                        logger.warning(f"⚠️ Erreur traduction : {e}")

                                await websocket.send_json(response)
                            else:
                                await websocket.send_json({
                                    "type": "transcription",
                                    "text": "",
                                    "is_final": True,
                                })

                        await websocket.send_json({"type": "stopped"})
                        break

                    elif command.get("action") == "ping":
                        await websocket.send_json({"type": "pong"})

                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket déconnecté")
    except Exception as e:
        logger.error(f"❌ Erreur WebSocket : {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        logger.info("🔌 Session WebSocket terminée")