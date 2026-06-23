import { useState, useRef } from "react"
import { WS_URL, api } from "../services/api"
import EntityBadge from "../components/EntityBadge"

const LANGS = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
  { value: "ar", label: "العربية" },
  { value: "es", label: "Español" },
]

export default function RealtimePage() {
  const [srcLang, setSrcLang] = useState("fr")
  const [tgtLang, setTgtLang] = useState("en")
  const [translate, setTranslate] = useState(false)
  const [recording, setRecording] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [transcription, setTranscription] = useState("")
  const [translation, setTranslation] = useState("")
  const [entities, setEntities] = useState([])
  const [timer, setTimer] = useState(0)
  const [status, setStatus] = useState("Cliquez sur le micro pour démarrer")

  const wsRef = useRef(null)
  const recorderRef = useRef(null)
  const timerRef = useRef(null)

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const ws = new WebSocket(`${WS_URL}?language=${srcLang}&translate=${translate}&target_lang=${tgtLang}`)
      wsRef.current = ws

      ws.onmessage = async (e) => {
        const data = JSON.parse(e.data)
        if (data.type === "transcription" && data.text) {
          setTranscription(prev => prev + (prev ? " " : "") + data.text)
          if (data.translation) setTranslation(data.translation)
          setProcessing(false)
          setStatus("Transcription reçue")
          try {
            const ner = await api.ner(data.text, srcLang)
            setEntities(prev => {
              const all = [...prev, ...(ner.entities || [])]
              return [...new Map(all.map(e => [e.text, e])).values()]
            })
          } catch {}
        }
        if (data.type === "stopped") ws.close()
      }

      const recorder = new MediaRecorder(stream)
      recorderRef.current = recorder
      recorder.ondataavailable = async (e) => {
        if (e.data.size > 0 && ws.readyState === WebSocket.OPEN) {
          ws.send(await e.data.arrayBuffer())
        }
      }
      recorder.start(3000)
      setRecording(true)
      setStatus("Enregistrement en cours...")
      setTimer(0)
      timerRef.current = setInterval(() => setTimer(t => t + 1), 1000)
    } catch {
      setStatus("Accès microphone refusé")
    }
  }

  const stopRecording = () => {
    clearInterval(timerRef.current)
    setRecording(false)
    setProcessing(true)
    setStatus("Traitement en cours...")
    if (recorderRef.current) {
      recorderRef.current.addEventListener("stop", () => {
        setTimeout(() => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: "stop" }))
          }
        }, 500)
      }, { once: true })
      recorderRef.current.stop()
      recorderRef.current.stream.getTracks().forEach(t => t.stop())
    }
  }

  const clear = () => {
    setTranscription(""); setTranslation(""); setEntities([])
    setStatus("Cliquez sur le micro pour démarrer"); setTimer(0)
  }

  const fmt = (s) => `${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`

  return (
    <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: "24px" }}>
      {/* CONFIG */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div className="card">
          <div className="card-title">Configuration</div>

          <label className="input-label">Langue source</label>
          <select className="select" value={srcLang} onChange={e => setSrcLang(e.target.value)}
            style={{ marginBottom: "12px" }}>
            {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
          </select>

          <label className="input-label">Traduire vers</label>
          <select className="select" value={tgtLang} onChange={e => setTgtLang(e.target.value)}
            style={{ marginBottom: "16px" }}>
            {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
          </select>

          <div className="toggle-wrap" onClick={() => setTranslate(t => !t)} style={{ marginBottom: "24px" }}>
            <div className={`toggle ${translate ? "on" : "off"}`}>
              <div className="toggle-thumb"></div>
            </div>
            <span className="toggle-label">Traduction automatique</span>
          </div>

          {/* MIC */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "16px", padding: "16px 0" }}>
            <button
              onClick={recording ? stopRecording : startRecording}
              className={`mic-btn ${recording ? "recording" : ""}`}
            >
              {recording ? "⬛" : "🎤"}
            </button>
            <div className="timer">{fmt(timer)}</div>
            <div className={recording ? "status-recording" : processing ? "status-processing" : "status-idle"}
              style={{ fontSize: "12px" }}>
              {recording ? "● " : ""}{status}
            </div>
          </div>

          <button onClick={clear} className="btn-ghost" style={{ marginTop: "8px" }}>
            Effacer tout
          </button>
        </div>
      </div>

      {/* OUTPUT */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div className="card" style={{ flex: 1 }}>
          <div className="card-title" style={{ justifyContent: "space-between" }}>
            <span>Transcription</span>
            <button className="btn-copy" onClick={() => navigator.clipboard.writeText(transcription)}>
              Copier
            </button>
          </div>
          <div style={{ minHeight: "120px", fontSize: "14px", lineHeight: "1.7", color: transcription ? "var(--text-bright)" : "var(--text-dim)" }}>
            {transcription || <span className="empty-state">La transcription apparaîtra ici...</span>}
          </div>
        </div>

        {translate && (
          <div className="card-gold">
            <div className="card-title card-title-gold" style={{ justifyContent: "space-between" }}>
              <span>Traduction</span>
              <button className="btn-copy" onClick={() => navigator.clipboard.writeText(translation)}>
                Copier
              </button>
            </div>
            <div style={{ minHeight: "80px", fontSize: "14px", lineHeight: "1.7", color: translation ? "var(--text-bright)" : "var(--text-dim)" }}>
              {translation || <span className="empty-state">La traduction apparaîtra ici...</span>}
            </div>
          </div>
        )}

        <div className="card">
          <div className="card-title">Entités Détectées</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", minHeight: "40px" }}>
            {entities.length === 0
              ? <span className="empty-state">Les entités apparaîtront après la transcription...</span>
              : entities.map((e, i) => <EntityBadge key={i} text={e.text} label={e.label} />)
            }
          </div>
        </div>
      </div>
    </div>
  )
}
