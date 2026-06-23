import { useState, useRef } from "react"
import { api } from "../services/api"
import EntityBadge from "../components/EntityBadge"

const LANGS = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
  { value: "ar", label: "العربية" },
  { value: "es", label: "Español" },
]

export default function BatchPage() {
  const [file, setFile] = useState(null)
  const [srcLang, setSrcLang] = useState("fr")
  const [tgtLang, setTgtLang] = useState("en")
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState("")
  const inputRef = useRef()

  const process = async () => {
    if (!file) return setError("Sélectionnez un fichier audio")
    setLoading(true); setError(""); setResult(null); setProgress(0)
    const interval = setInterval(() => setProgress(p => Math.min(p + Math.random() * 5, 88)), 800)
    try {
      const data = await api.process(file, srcLang, tgtLang)
      clearInterval(interval); setProgress(100); setResult(data)
    } catch { setError("Erreur lors du traitement") }
    finally { clearInterval(interval); setLoading(false) }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: "24px" }}>
      {/* LEFT */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div className="card">
          <div className="card-title">Fichier Audio</div>

          <div className="upload-zone" onClick={() => inputRef.current.click()}
            onDragOver={e => e.preventDefault()}
            onDrop={e => { e.preventDefault(); setFile(e.dataTransfer.files[0]) }}>
            <input ref={inputRef} type="file" accept=".mp3,.wav,.m4a,.flac" className="hidden"
              onChange={e => setFile(e.target.files[0])} style={{ display: "none" }} />
            <div className="upload-icon">◈</div>
            {file
              ? <div style={{ color: "var(--gold)", fontSize: "13px", fontWeight: "600" }}>✓ {file.name}</div>
              : <>
                  <div className="upload-text">Glissez votre fichier ici</div>
                  <div className="upload-sub">MP3, WAV, M4A — Max 25 MB</div>
                </>
            }
          </div>

          <div style={{ height: "16px" }} />

          <label className="input-label">Langue source</label>
          <select className="select" value={srcLang} onChange={e => setSrcLang(e.target.value)}
            style={{ marginBottom: "12px" }}>
            {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
          </select>

          <label className="input-label">Langue cible</label>
          <select className="select" value={tgtLang} onChange={e => setTgtLang(e.target.value)}
            style={{ marginBottom: "16px" }}>
            {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
          </select>

          {loading && (
            <div style={{ marginBottom: "12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                <span style={{ fontSize: "11px", color: "var(--text-dim)" }}>Traitement...</span>
                <span style={{ fontSize: "11px", color: "var(--gold)" }}>{Math.round(progress)}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
              </div>
            </div>
          )}

          {error && <div style={{ color: "var(--red)", fontSize: "12px", marginBottom: "12px" }}>{error}</div>}

          <button onClick={process} disabled={loading} className="btn-gold">
            {loading ? "Traitement en cours..." : "Analyser l'Audio"}
          </button>
        </div>

        {/* Stats */}
        {result && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
            {[
              { label: "Durée", value: `${Math.round(result.transcription?.duration || 0)}s` },
              { label: "Caractères", value: result.transcription?.text?.length || 0 },
              { label: "Entités", value: (result.entities || []).length },
              { label: "Termes", value: (result.glossary_matches || []).length },
            ].map(s => (
              <div key={s.label} className="stat-card">
                <div className="stat-value">{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* RIGHT */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div className="card">
          <div className="card-title" style={{ justifyContent: "space-between" }}>
            <span>Transcription</span>
            {result && <button className="btn-copy" onClick={() => navigator.clipboard.writeText(result.transcription?.text || "")}>Copier</button>}
          </div>
          <textarea readOnly className="textarea" value={result?.transcription?.text || ""}
            placeholder="La transcription apparaîtra ici..." rows={7} />
        </div>

        <div className="card-gold">
          <div className="card-title card-title-gold" style={{ justifyContent: "space-between" }}>
            <span>Traduction</span>
            {result && <button className="btn-copy" onClick={() => navigator.clipboard.writeText(result.translation?.translated_text || "")}>Copier</button>}
          </div>
          <textarea readOnly className="textarea" value={result?.translation?.translated_text || ""}
            placeholder="La traduction apparaîtra ici..." rows={5}
            style={{ background: "transparent" }} />
        </div>

        {result && (
          <div className="card">
            <div className="card-title">Entités Nommées</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {(result.entities || []).length === 0
                ? <span className="empty-state">Aucune entité détectée</span>
                : [...new Map((result.entities || []).map(e => [e.text, e])).values()]
                    .map((e, i) => <EntityBadge key={i} text={e.text} label={e.label} />)
              }
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
