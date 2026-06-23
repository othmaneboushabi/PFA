import { useState, useRef } from "react"
import { api } from "../services/api"

const LANGS = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
  { value: "ar", label: "العربية" },
  { value: "es", label: "Español" },
]

export default function GlossaryPage() {
  const [file, setFile] = useState(null)
  const [format, setFormat] = useState("csv")
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [uploadError, setUploadError] = useState("")

  const [term, setTerm] = useState("")
  const [srcLang, setSrcLang] = useState("fr")
  const [tgtLang, setTgtLang] = useState("en")
  const [threshold, setThreshold] = useState(80)
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState(null)
  const inputRef = useRef()

  const upload = async () => {
    if (!file) return setUploadError("Sélectionnez un fichier")
    setUploading(true); setUploadError("")
    try {
      const data = await api.uploadGlossary(file, format)
      setUploadResult(data)
    } catch { setUploadError("Erreur lors de l'import") }
    finally { setUploading(false) }
  }

  const search = async () => {
    if (!term.trim()) return
    setSearching(true)
    try {
      const data = await api.searchGlossary(term, srcLang, tgtLang, threshold)
      setResults(data.results || [])
    } catch { setResults([]) }
    finally { setSearching(false) }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
      {/* UPLOAD */}
      <div className="card">
        <div className="card-title">Importer un Glossaire</div>

        <div className="upload-zone" onClick={() => inputRef.current.click()}
          onDragOver={e => e.preventDefault()}
          onDrop={e => { e.preventDefault(); setFile(e.dataTransfer.files[0]); setFormat(e.dataTransfer.files[0]?.name.split(".").pop() || "csv") }}>
          <input ref={inputRef} type="file" accept=".csv,.json,.xlsx" style={{ display: "none" }}
            onChange={e => { setFile(e.target.files[0]); setFormat(e.target.files[0]?.name.split(".").pop() || "csv") }} />
          <div className="upload-icon">◇</div>
          {file
            ? <div style={{ color: "var(--gold)", fontSize: "13px", fontWeight: "600" }}>✓ {file.name}</div>
            : <>
                <div className="upload-text">CSV, JSON ou Excel (XLSX)</div>
                <div className="upload-sub">Colonnes : source_term, target_term, source_lang, target_lang</div>
              </>
          }
        </div>

        <div style={{ height: "16px" }} />

        <label className="input-label">Format</label>
        <select className="select" value={format} onChange={e => setFormat(e.target.value)}
          style={{ marginBottom: "16px" }}>
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
          <option value="xlsx">Excel (XLSX)</option>
        </select>

        {uploadError && <div style={{ color: "var(--red)", fontSize: "12px", marginBottom: "12px" }}>{uploadError}</div>}

        {uploadResult && (
          <div style={{ background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.2)", borderRadius: "8px", padding: "12px 16px", marginBottom: "12px" }}>
            <div style={{ color: "var(--green)", fontSize: "13px", fontWeight: "600" }}>
              ✓ {uploadResult.entries_count} termes importés
            </div>
            <div style={{ color: "var(--text-dim)", fontSize: "11px", marginTop: "2px" }}>
                {uploadResult.entries_count} termes dans la base
            </div>
          </div>
        )}

        <button onClick={upload} disabled={uploading} className="btn-gold">
          {uploading ? "Import en cours..." : "Importer le Glossaire"}
        </button>
      </div>

      {/* SEARCH */}
      <div className="card">
        <div className="card-title">Recherche de Termes</div>

        <label className="input-label">Terme à rechercher</label>
        <input className="input" type="text" value={term}
          onChange={e => setTerm(e.target.value)}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="Ex: OPCVM, GDP, ONU..."
          style={{ marginBottom: "12px" }} />

        <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", gap: "8px", alignItems: "end", marginBottom: "16px" }}>
          <div>
            <label className="input-label">Source</label>
            <select className="select" value={srcLang} onChange={e => setSrcLang(e.target.value)}>
              {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
          </div>
          <div style={{ color: "var(--gold-dim)", fontSize: "18px", paddingBottom: "8px" }}>›</div>
          <div>
            <label className="input-label">Cible</label>
            <select className="select" value={tgtLang} onChange={e => setTgtLang(e.target.value)}>
              {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
          </div>
        </div>

        <div style={{ marginBottom: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
            <label className="input-label" style={{ marginBottom: 0 }}>Seuil de similarité</label>
            <span style={{ fontSize: "12px", color: "var(--gold)", fontWeight: "700" }}>{threshold}%</span>
          </div>
          <input type="range" min="50" max="100" value={threshold}
            onChange={e => setThreshold(Number(e.target.value))} style={{ width: "100%" }} />
        </div>

        <button onClick={search} disabled={searching} className="btn-gold" style={{ marginBottom: "16px" }}>
          {searching ? "Recherche..." : "Rechercher"}
        </button>

        {results !== null && (
          <div>
            {results.length === 0
              ? <div className="empty-state">Aucun résultat trouvé</div>
              : results.map((r, i) => (
                  <div key={i} className="glossary-result">
                    <div>
                      <span style={{ fontWeight: "700", color: "var(--gold-light)", fontSize: "13px" }}>{r.source_term}</span>
                      <span style={{ color: "var(--text-dim)", margin: "0 8px" }}>›</span>
                      <span style={{ color: "var(--text)", fontSize: "13px" }}>{r.target_term}</span>
                      {r.domain && (
                        <span style={{ marginLeft: "8px", fontSize: "10px", color: "var(--text-dim)",
                          background: "var(--black-hover)", padding: "2px 6px", borderRadius: "4px" }}>
                          {r.domain}
                        </span>
                      )}
                    </div>
                    <span className={r.match_score >= 90 ? "score-high" : "score-mid"}>{r.match_score}%</span>
                  </div>
                ))
            }
          </div>
        )}
      </div>
    </div>
  )
}
