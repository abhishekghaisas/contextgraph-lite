export default function EmptyState({ label }: { label: string }) {
  return (
    <div className="state-block empty">
      <p>{label}</p>
    </div>
  )
}
