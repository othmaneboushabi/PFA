import { useEffect, useRef } from "react"

const features = [
  {
    num: "01", icon: "◉", tag: "ASR",
    title: "Transcription Temps Reel",
    desc: "Whisper small transcrit FR, EN, ES, AR avec 97% de precision via WebSocket streaming en temps reel.",
  },
  {
    num: "02", icon: "◈", tag: "LLM",
    title: "Traduction Intelligente",
    desc: "Qwen 2.5 7B traduit avec contexte entre 4 langues. Cache Redis pour reponses instantanees en moins de 10ms.",
  },
  {
    num: "03", icon: "◆", tag: "NER",
    title: "Extraction d'Entites",
    desc: "spaCy (FR/EN/ES) et CAMeL BERT (AR) detectent personnes, lieux et organisations automatiquement.",
  },
  {
    num: "04", icon: "◇", tag: "GLOSSAIRE",
    title: "Glossaires Terminologiques",
    desc: "Import CSV/JSON/XLSX de terminologie metier. Fuzzy matching avec rapidfuzz pour tolerer les fautes de frappe.",
  },
  {
    num: "05", icon: "○", tag: "PIPELINE",
    title: "Pipeline Orchestre",
    desc: "POST /process traite audio de bout en bout : transcription + NER + traduction en parallele via asyncio.gather.",
  },
  {
    num: "06", icon: "●", tag: "IA",
    title: "Resume et Acronymes",
    desc: "Resume automatique en bullet points et extraction d'acronymes via systeme hybride glossaire et Qwen 2.5 7B.",
  },
]

const marqueeItems = [
  "Transcription Multilingue", "Traduction FR-AR", "NER Arabe (CAMeL BERT)",
  "Glossaires Terminologiques", "Pipeline Orchestre", "Qwen 2.5 7B",
  "faster-whisper", "FastAPI Async", "WebSocket Live", "Fuzzy Matching",
  "Resume Automatique", "Extraction Acronymes", "PostgreSQL", "Redis Cache",
]

const footerCols = [
  { title: "PLATEFORME", items: ["Transcription", "Traduction", "Glossaires", "Acronymes", "Pipeline"] },
  { title: "TECHNOLOGIES", items: ["Whisper ASR", "Qwen 2.5 7B", "CAMeL BERT", "spaCy", "FastAPI"] },
  { title: "PROJET", items: ["EMSI Rabat", "SmartILab", "ACM Chapter", "PFA 2025/2026", "Dr. H. Chaabi"] },
]

export default function LandingPage({ onEnter }) {
  const marqueeRef = useRef(null)

  useEffect(() => {
    window.history.pushState(null, "", window.location.href)
    const handlePop = () => window.history.pushState(null, "", window.location.href)
    window.addEventListener("popstate", handlePop)
    return () => window.removeEventListener("popstate", handlePop)
  }, [])

  useEffect(() => {
    const el = marqueeRef.current
    if (!el) return
    let pos = 0
    let raf
    const animate = () => {
      pos -= 0.6
      if (pos <= -el.scrollWidth / 2) pos = 0
      el.style.transform = `translateX(${pos}px)`
      raf = requestAnimationFrame(animate)
    }
    raf = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(raf)
  }, [])

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0A0A0B",
      color: "#F0F0F2",
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
      overflowX: "hidden",
    }}>

      {/* NAV */}
      <nav style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "20px 64px",
        borderBottom: "1px solid #1E1E22",
        position: "sticky", top: 0, zIndex: 50,
        background: "rgba(10,10,11,0.90)",
        backdropFilter: "blur(16px)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="15" stroke="#C9A84C" strokeWidth="1.5"/>
            <path d="M8 16 Q16 6 24 16 Q16 26 8 16Z" fill="#C9A84C" opacity="0.9"/>
            <circle cx="16" cy="16" r="4" fill="#C9A84C"/>
          </svg>
          <span style={{ fontSize: "17px", fontWeight: 800, color: "#C9A84C", letterSpacing: "0.18em" }}>AIS</span>
        </div>

        {/* Status pill */}
        <div style={{
          display: "flex", alignItems: "center", gap: "8px",
          background: "rgba(34,197,94,0.08)",
          border: "1px solid rgba(34,197,94,0.2)",
          borderRadius: "20px",
          padding: "6px 14px",
        }}>
          <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#22C55E", boxShadow: "0 0 6px #22C55E" }}/>
          <span style={{ fontSize: "11px", color: "#22C55E", fontWeight: 600, letterSpacing: "0.08em" }}>ALL SYSTEMS</span>
        </div>

        <button onClick={onEnter} style={{
          background: "linear-gradient(135deg, #8A6F30, #C9A84C)",
          color: "#0A0A0B", fontSize: "12px", fontWeight: 800,
          padding: "10px 24px", border: "none", borderRadius: "6px",
          cursor: "pointer", letterSpacing: "0.08em", textTransform: "uppercase",
          fontFamily: "inherit",
        }}>
          Lancer AIS
        </button>
      </nav>

      {/* HERO */}
      <section style={{
        position: "relative", minHeight: "88vh",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        textAlign: "center", padding: "80px 64px 60px",
        overflow: "hidden",
      }}>
        {/* BG image */}
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: "url('/hero.png')",
          backgroundSize: "cover", backgroundPosition: "center",
          opacity: 0.18,
        }}/>
        <div style={{
          position: "absolute", inset: 0,
          background: "linear-gradient(to bottom, rgba(10,10,11,0.3) 0%, rgba(10,10,11,0.7) 60%, #0A0A0B 100%)",
        }}/>
        {/* Radial glow */}
        <div style={{
          position: "absolute", top: "30%", left: "50%",
          transform: "translate(-50%, -50%)",
          width: "600px", height: "400px",
          background: "radial-gradient(ellipse, rgba(201,168,76,0.08) 0%, transparent 70%)",
          pointerEvents: "none",
        }}/>

        {/* Badge */}
        <div style={{
          position: "relative",
          display: "inline-flex", alignItems: "center", gap: "10px",
          background: "rgba(201,168,76,0.07)",
          border: "1px solid rgba(201,168,76,0.2)",
          borderRadius: "20px", padding: "6px 18px", marginBottom: "36px",
        }}>
          <div style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#C9A84C" }}/>
          <span style={{ fontSize: "11px", color: "#C9A84C", letterSpacing: "0.2em", fontWeight: 700, textTransform: "uppercase" }}>
            PFA 2025/2026 — EMSI Rabat — SmartILab
          </span>
        </div>

        {/* Title */}
        <h1 style={{
          position: "relative",
          fontSize: "clamp(52px, 9vw, 104px)",
          fontWeight: 900, lineHeight: 1.02,
          margin: "0 0 20px", letterSpacing: "-0.03em",
        }}>
          <span style={{ color: "#F4F4F5", display: "block" }}>Interprete</span>
          <span style={{ color: "#C9A84C", fontStyle: "italic", display: "block" }}>Simultane.</span>
        </h1>

        {/* Subtitle */}
        <p style={{
          position: "relative",
          fontSize: "16px", color: "#8A8A95",
          maxWidth: "500px", lineHeight: 1.75,
          margin: "0 0 52px",
        }}>
          Transcription multilingue en temps reel, traduction intelligente
          et extraction d'entites — propulse par Whisper et Qwen 2.5 7B.
        </p>

        {/* CTAs */}
        <div style={{ position: "relative", display: "flex", gap: "12px", alignItems: "center", marginBottom: "64px" }}>
          <button onClick={onEnter} style={{
            background: "linear-gradient(135deg, #8A6F30, #C9A84C)",
            color: "#0A0A0B", fontSize: "13px", fontWeight: 800,
            padding: "15px 40px", border: "none", borderRadius: "6px",
            cursor: "pointer", letterSpacing: "0.08em", textTransform: "uppercase",
            fontFamily: "inherit", boxShadow: "0 4px 32px rgba(201,168,76,0.35)",
            transition: "all 0.2s",
          }}
            onMouseEnter={e => { e.target.style.transform = "translateY(-2px)"; e.target.style.boxShadow = "0 8px 48px rgba(201,168,76,0.5)" }}
            onMouseLeave={e => { e.target.style.transform = "translateY(0)"; e.target.style.boxShadow = "0 4px 32px rgba(201,168,76,0.35)" }}
          >
            Lancer AIS →
          </button>
          
        </div>

        {/* Stats bar */}
        <div style={{
          position: "relative",
          display: "flex",
          border: "1px solid #1E1E22",
          borderRadius: "12px", overflow: "hidden",
          background: "rgba(17,17,19,0.8)",
          backdropFilter: "blur(8px)",
        }}>
          {[
            { value: "11", label: "Endpoints API" },
            { value: "4", label: "Langues" },
            { value: "97%", label: "Precision ASR" },
            { value: "7B", label: "Parametres LLM" },
            { value: "<10ms", label: "Cache Redis" },
          ].map((s, i) => (
            <div key={s.label} style={{
              padding: "20px 36px",
              borderRight: i < 4 ? "1px solid #1E1E22" : "none",
              textAlign: "center",
            }}>
              <div style={{ fontSize: "22px", fontWeight: 800, color: "#C9A84C" }}>{s.value}</div>
              <div style={{ fontSize: "10px", color: "#6B6B75", textTransform: "uppercase", letterSpacing: "0.1em", marginTop: "4px" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* MARQUEE */}
      <div style={{
        overflow: "hidden",
        borderTop: "1px solid #1E1E22", borderBottom: "1px solid #1E1E22",
        padding: "14px 0",
        background: "rgba(201,168,76,0.025)",
      }}>
        <div ref={marqueeRef} style={{ display: "flex", gap: "56px", whiteSpace: "nowrap", willChange: "transform" }}>
          {[...marqueeItems, ...marqueeItems, ...marqueeItems].map((item, i) => (
            <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: "14px" }}>
              <span style={{ width: "4px", height: "4px", borderRadius: "50%", background: "#C9A84C", display: "inline-block", flexShrink: 0 }}/>
              <span style={{ fontSize: "11px", color: "#5A5A65", letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 600 }}>{item}</span>
            </span>
          ))}
        </div>
      </div>

      {/* FEATURES */}
      <section style={{ padding: "96px 64px" }}>
        <div style={{ textAlign: "center", marginBottom: "64px" }}>
          <div style={{ fontSize: "10px", color: "#C9A84C", letterSpacing: "0.25em", textTransform: "uppercase", marginBottom: "16px", fontWeight: 700 }}>
            FONCTIONNALITES
          </div>
          <h2 style={{ fontSize: "clamp(32px, 5vw, 52px)", fontWeight: 800, color: "#F4F4F5", margin: 0, letterSpacing: "-0.02em", lineHeight: 1.1 }}>
            Un pipeline complet.
            <br/>
            <span style={{ color: "#C9A84C", fontStyle: "italic" }}>Zero friction.</span>
          </h2>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", maxWidth: "1100px", margin: "0 auto" }}>
          {features.map(f => (
            <div key={f.num}
              style={{
                background: "#0F0F11", border: "1px solid #1E1E22",
                borderRadius: "14px", padding: "32px",
                transition: "all 0.25s", cursor: "default",
                position: "relative", overflow: "hidden",
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = "#2A2516"
                e.currentTarget.style.background = "#131108"
                e.currentTarget.style.transform = "translateY(-4px)"
                e.currentTarget.style.boxShadow = "0 12px 40px rgba(201,168,76,0.08)"
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = "#1E1E22"
                e.currentTarget.style.background = "#0F0F11"
                e.currentTarget.style.transform = "translateY(0)"
                e.currentTarget.style.boxShadow = "none"
              }}
            >
              {/* Top row */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px" }}>
                <div style={{
                  width: "44px", height: "44px",
                  background: "rgba(201,168,76,0.08)",
                  border: "1px solid rgba(201,168,76,0.15)",
                  borderRadius: "10px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "18px", color: "#C9A84C",
                }}>
                  {f.icon}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{
                    fontSize: "10px", color: "#C9A84C",
                    background: "rgba(201,168,76,0.08)",
                    border: "1px solid rgba(201,168,76,0.15)",
                    padding: "3px 8px", borderRadius: "10px",
                    fontWeight: 700, letterSpacing: "0.08em",
                  }}>{f.tag}</span>
                  <span style={{ fontSize: "11px", color: "#2A2A35", fontWeight: 700, letterSpacing: "0.1em" }}>· {f.num}</span>
                </div>
              </div>
              <h3 style={{ fontSize: "17px", fontWeight: 700, color: "#F4F4F5", margin: "0 0 10px", letterSpacing: "-0.01em" }}>{f.title}</h3>
              <p style={{ fontSize: "13px", color: "#6B6B75", lineHeight: 1.65, margin: 0 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA SECTION */}
      <section style={{
        margin: "0 64px 96px",
        background: "linear-gradient(135deg, #0E0C05, #131108)",
        border: "1px solid #2A2516",
        borderRadius: "20px",
        padding: "64px",
        textAlign: "center",
        position: "relative", overflow: "hidden",
      }}>
        <div style={{
          position: "absolute", top: "50%", left: "50%",
          transform: "translate(-50%, -50%)",
          width: "500px", height: "300px",
          background: "radial-gradient(ellipse, rgba(201,168,76,0.07) 0%, transparent 70%)",
          pointerEvents: "none",
        }}/>
        <div style={{ fontSize: "10px", color: "#C9A84C", letterSpacing: "0.2em", textTransform: "uppercase", marginBottom: "16px", fontWeight: 700 }}>
          PRET A COMMENCER
        </div>
        <h2 style={{ fontSize: "40px", fontWeight: 800, color: "#F4F4F5", margin: "0 0 16px", letterSpacing: "-0.02em" }}>
          Lancez votre session
          <br/>
          <span style={{ color: "#C9A84C", fontStyle: "italic" }}>d'interpretation.</span>
        </h2>
        <p style={{ fontSize: "15px", color: "#6B6B75", margin: "0 0 36px" }}>
          Systeme complet, 100% local, zero cloud requis.
        </p>
        <button onClick={onEnter} style={{
          background: "linear-gradient(135deg, #8A6F30, #C9A84C)",
          color: "#0A0A0B", fontSize: "13px", fontWeight: 800,
          padding: "16px 48px", border: "none", borderRadius: "8px",
          cursor: "pointer", letterSpacing: "0.08em", textTransform: "uppercase",
          fontFamily: "inherit", boxShadow: "0 4px 32px rgba(201,168,76,0.35)",
          transition: "all 0.2s",
        }}
          onMouseEnter={e => { e.target.style.transform = "translateY(-2px)"; e.target.style.boxShadow = "0 8px 48px rgba(201,168,76,0.5)" }}
          onMouseLeave={e => { e.target.style.transform = "translateY(0)"; e.target.style.boxShadow = "0 4px 32px rgba(201,168,76,0.35)" }}
        >
          Lancer AIS →
        </button>
      </section>

      {/* FOOTER */}
      <footer style={{ borderTop: "1px solid #1E1E22", padding: "56px 64px 28px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: "48px", marginBottom: "48px" }}>
          {/* Brand */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "14px" }}>
              <svg width="26" height="26" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="15" stroke="#C9A84C" strokeWidth="1.5"/>
                <path d="M8 16 Q16 6 24 16 Q16 26 8 16Z" fill="#C9A84C" opacity="0.9"/>
                <circle cx="16" cy="16" r="4" fill="#C9A84C"/>
              </svg>
              <span style={{ fontSize: "15px", fontWeight: 800, color: "#C9A84C", letterSpacing: "0.18em" }}>AIS</span>
            </div>
            <p style={{ fontSize: "13px", color: "#5A5A65", lineHeight: 1.65, margin: "0 0 20px", maxWidth: "240px" }}>
              Assistant Interprete Simultane — systeme IA multilingue pour conferences professionnelles.
            </p>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: "6px",
              background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.15)",
              borderRadius: "20px", padding: "5px 12px",
            }}>
              <div style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#22C55E" }}/>
              <span style={{ fontSize: "10px", color: "#22C55E", fontWeight: 600, letterSpacing: "0.08em" }}>ALL SYSTEMS</span>
            </div>
          </div>

          {footerCols.map(col => (
            <div key={col.title}>
              <div style={{ fontSize: "10px", color: "#C9A84C", letterSpacing: "0.18em", fontWeight: 700, marginBottom: "18px", textTransform: "uppercase" }}>{col.title}</div>
              {col.items.map(item => (
                <div key={item} style={{ fontSize: "13px", color: "#5A5A65", marginBottom: "10px", cursor: "default", transition: "color 0.15s" }}
                  onMouseEnter={e => e.target.style.color = "#A0A0AA"}
                  onMouseLeave={e => e.target.style.color = "#5A5A65"}
                >{item}</div>
              ))}
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div style={{
          borderTop: "1px solid #1A1A1E", paddingTop: "22px",
          display: "flex", justifyContent: "space-between", alignItems: "center",
        }}>
          <span style={{ fontSize: "11px", color: "#2A2A35", letterSpacing: "0.06em" }}>
            © 2026 AIS. EMSI RABAT. TOUS DROITS RESERVES.
          </span>
          <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
            {["v0.1.0", "·", "Othmane Boushabi", "·", "Dr. Hasnaa Chaabi"].map((item, i) => (
              <span key={i} style={{ fontSize: "11px", color: "#2A2A35" }}>{item}</span>
            ))}
          </div>
        </div>
      </footer>
    </div>
  )
}