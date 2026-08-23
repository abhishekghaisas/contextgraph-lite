export default function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="state-block loading">
      <div className="spinner" />
      <p>{label}</p>
    </div>
  )
}
