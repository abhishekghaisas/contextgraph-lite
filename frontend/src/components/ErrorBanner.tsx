export default function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="state-block error">
      <p>⚠ {message}</p>
    </div>
  )
}
