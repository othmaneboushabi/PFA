export default function EntityBadge({ text, label }) {
  return (
    <span className={`entity-badge badge-${label}`}>
      {text}
      <span className="entity-tag">{label}</span>
    </span>
  )
}
