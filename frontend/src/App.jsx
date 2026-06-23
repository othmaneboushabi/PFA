import { useState, useEffect } from "react"
import { api } from "./services/api"
import RealtimePage from "./pages/RealtimePage"
import BatchPage from "./pages/BatchPage"
import GlossaryPage from "./pages/GlossaryPage"
import ToolsPage from "./pages/ToolsPage"
import LandingPage from "./pages/LandingPage"

const tabs = [
  { id: "realtime", label: "Temps Reel", icon: "O", sub: "WebSocket Live" },
  { id: "batch", label: "Fichier Audio", icon: "=", sub: "Pipeline Complet" },
  { id: "glossary", label: "Glossaires", icon: "<>", sub: "Terminologie" },
  { id: "tools", label: "Outils IA", icon: "*", sub: "Resume & Acronymes" },
]

export default function App() {
  const [showLanding, setShowLanding] = useState(true)
  const [activeTab, setActiveTab] = useState("realtime")
  const [apiStatus, setApiStatus] = useState("checking")
  const [time, setTime] = useState(new Date())
  const [isLight, setIsLight] = useState(false)

  useEffect(() => {
    api.health()
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"))
    const interval = setInterval(() => {
      api.health()
        .then(() => setApiStatus("online"))
        .catch(() => setApiStatus("offline"))
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    if (showLanding) {
      window.history.pushState({ page: "landing" }, "", "/")
    } else {
      window.history.pushState({ page: "app" }, "", "/app")
    }
  }, [showLanding])

  useEffect(() => {
    const handlePop = (e) => {
      if (e.state?.page === "landing" || !e.state) {
        setShowLanding(true)
      } else {
        setShowLanding(false)
      }
    }
    window.addEventListener("popstate", handlePop)
    return () => window.removeEventListener("popstate", handlePop)
  }, [])

  useEffect(() => {
    if (isLight) {
      document.body.classList.add("light")
    } else {
      document.body.classList.remove("light")
    }
  }, [isLight])

  const fmt = (d) => d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })
  const fmtDate = (d) => d.toLocaleDateString("fr-FR", { weekday: "long", day: "2-digit", month: "long", year: "numeric" })

  if (showLanding) {
    return <LandingPage onEnter={() => setShowLanding(false)} />
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <circle cx="14" cy="14" r="13" stroke="#C9A84C" strokeWidth="1.5"/>
              <path d="M8 14 Q14 6 20 14 Q14 22 8 14Z" fill="#C9A84C" opacity="0.8"/>
              <circle cx="14" cy="14" r="3" fill="#C9A84C"/>
            </svg>
          </div>
          <div>
            <div className="logo-title">AIS</div>
            <div className="logo-sub">Interprete Simultane</div>
          </div>
        </div>

        <div className="sidebar-status">
          <div className={`status-dot ${apiStatus === "online" ? "online" : apiStatus === "offline" ? "offline" : "checking"}`}></div>
          <span className="status-text">{apiStatus === "online" ? "Systeme actif" : apiStatus === "offline" ? "Hors ligne" : "Connexion..."}</span>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-label">NAVIGATION</div>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`nav-item ${activeTab === tab.id ? "active" : ""}`}
            >
              <span className="nav-icon">{tab.icon}</span>
              <div className="nav-text">
                <span className="nav-title">{tab.label}</span>
                <span className="nav-sub">{tab.sub}</span>
              </div>
              {activeTab === tab.id && <span className="nav-indicator"></span>}
            </button>
          ))}
        </nav>

        {/* THEME TOGGLE */}
        <div style={{
          padding: "16px 20px",
          borderTop: "1px solid var(--border)",
        }}>
          <div className="nav-label" style={{ marginBottom: "10px" }}>THEME</div>
          <button
            onClick={() => setIsLight(l => !l)}
            style={{
              width: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              background: "var(--black-hover)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              padding: "10px 14px",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            <span style={{ fontSize: "12px", color: "var(--text-dim)", fontFamily: "inherit" }}>
              {isLight ? "Mode Clair" : "Mode Sombre"}
            </span>
            <span style={{ fontSize: "16px" }}>
              {isLight ? "☀️" : "🌙"}
            </span>
          </button>
        </div>

        <div className="sidebar-clock">
          <div className="clock-time">{fmt(time)}</div>
          <div className="clock-date">{fmtDate(time)}</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <div className="breadcrumb">
              <span className="breadcrumb-root" style={{ cursor: "pointer" }}
                onClick={() => setShowLanding(true)}>AIS</span>
              <span className="breadcrumb-sep">›</span>
              <span className="breadcrumb-current">{tabs.find(t => t.id === activeTab)?.label}</span>
            </div>
            <p className="topbar-sub">{tabs.find(t => t.id === activeTab)?.sub}</p>
          </div>
        </header>

        <div className="page-content">
          {activeTab === "realtime" && <RealtimePage />}
          {activeTab === "batch" && <BatchPage />}
          {activeTab === "glossary" && <GlossaryPage />}
          {activeTab === "tools" && <ToolsPage />}
        </div>
      </main>
    </div>
  )
}