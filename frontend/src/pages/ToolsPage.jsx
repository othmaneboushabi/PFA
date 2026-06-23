import { useState } from "react"
import { api } from "../services/api"

const LANGS = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
  { value: "ar", label: "العربية" },
  { value: "es", label: "Español" },
]

export default function ToolsPage() {
  const [summaryText, setSummaryText] = useState("")
  const [numPoints, setNumPoints] = useState(5)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [summaryResult, setSummaryResult] = useState(null)

  const [acronymText, setAcronymText] = useState("")
  const [acronymSrc, setAcronymSrc] = useState("fr")
  const [acronymTgt, setAcronymTgt] = useState("en")
  const [acronymLoading, setAcronymLoading] = useState(false)
  const [acronymResult, setAcronymResult] = useState(null)

  const summarize = async () => {
    if (!summaryText.trim()) return
    setSummaryLoading(true); setSummaryResult(null)
    try { setSummaryResult(await api.summarize(summaryText, numPoints)) }
    finally { setSummaryLoading(false) }
  }

  const extract = async () => {
    if (!acronymText.trim()) return
    setAcronymLoading(true); setAcronymResult(null)
    try { setAcronymResult(await api.processAcronyms(acronymText, acronymSrc, acronymTgt)) }
    finally { setAcronymLoading(false) }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
      {/* RÉSUMÉ */}
      <div className="card">
        <div className="card-title">Résumé Automatique</div>
        

        <label className="input-label">Texte à résumer (min. 100 mots)</label>
        <textarea className="textarea" value={summaryText}
          onChange={e => setSummaryText(e.target.value)}
          placeholder="Collez votre transcription ici..."
          rows={6} style={{ marginBottom: "16px" }} />

        <div style={{ marginBottom: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
            <label className="input-label" style={{ marginBottom: 0 }}>Nombre de points</label>
            <span style={{ fontSize: "12px", color: "var(--gold)", fontWeight: "700" }}>{numPoints}</span>
          </div>
          <input type="range" min="3" max="10" value={numPoints}
            onChange={e => setNumPoints(Number(e.target.value))} style={{ width: "100%" }} />
        </div>

        <button onClick={summarize} disabled={summaryLoading} className="btn-gold"
          style={{ marginBottom: "16px" }}>
          {summaryLoading ? "Résumé en cours..." : "Générer le Résumé"}
        </button>

        {summaryResult && (
          <div>
            {!summaryResult.summarized
              ? <div style={{ color: "var(--orange)", fontSize: "12px" }}>
                  Texte trop court ({summaryResult.word_count} mots). Minimum 100 mots.
                </div>
              : <>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                    <span style={{ fontSize: "11px", color: "var(--text-dim)" }}>{summaryResult.word_count} mots</span>
                    <span style={{ fontSize: "11px", color: "var(--gold)" }}>
                      -{Math.round((1 - summaryResult.compression_ratio) * 100)}% compression
                    </span>
                  </div>
                  {(Array.isArray(summaryResult.summary) ? summaryResult.summary : [summaryResult.summary]).map((pt, i) => (
                    <div key={i} className="bullet-item">
                      <span className="bullet-num">{i + 1}</span>
                      <span className="bullet-text">{pt}</span>
                    </div>
                  ))}
                </>
            }
          </div>
        )}
      </div>

      {/* ACRONYMES */}
      <div className="card">
        <div className="card-title">Extraction d'Acronymes</div>
        

        <label className="input-label">Texte contenant des acronymes</label>
        <textarea className="textarea" value={acronymText}
          onChange={e => setAcronymText(e.target.value)}
          placeholder="Ex: L'OPCVM investit dans le PIB. L'ONU surveille l'OTAN..."
          rows={4} style={{ marginBottom: "12px" }} />

        <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", gap: "8px", alignItems: "end", marginBottom: "16px" }}>
          <div>
            <label className="input-label">Source</label>
            <select className="select" value={acronymSrc} onChange={e => setAcronymSrc(e.target.value)}>
              {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
          </div>
          <div style={{ color: "var(--gold-dim)", fontSize: "18px", paddingBottom: "8px" }}>›</div>
          <div>
            <label className="input-label">Cible</label>
            <select className="select" value={acronymTgt} onChange={e => setAcronymTgt(e.target.value)}>
              {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
          </div>
        </div>

        <button onClick={extract} disabled={acronymLoading} className="btn-gold"
          style={{ marginBottom: "16px" }}>
          {acronymLoading ? "Extraction..." : "Extraire les Acronymes"}
        </button>

        {acronymResult && (
          <div>
            {(acronymResult.acronyms || []).length === 0
              ? <div className="empty-state">Aucun acronyme détecté</div>
              : <>
                  <div style={{ fontSize: "11px", color: "var(--text-dim)", marginBottom: "10px" }}>
                    {acronymResult.acronyms_found} acronyme(s) détecté(s)
                  </div>
                  {acronymResult.acronyms.map((a, i) => (
                    <div key={i} className="acronym-card">
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span className="acronym-abbr">{a.acronym}</span>
                        <span className="acronym-arrow">›</span>
                        <span className="acronym-full">{a.full_form}</span>
                        <span className={a.source === "glossary" ? "acronym-source-glossary" : "acronym-source-ai"}>
                          {a.source === "glossary" ? "Glossaire" : "IA"}
                        </span>
                      </div>
                      <span className="acronym-conf" style={{ color: a.confidence >= 0.9 ? "var(--green)" : "var(--gold)" }}>
                        {Math.round(a.confidence * 100)}%
                      </span>
                    </div>
                  ))}
                </>
            }
          </div>
        )}
      </div>
    </div>
  )
}
