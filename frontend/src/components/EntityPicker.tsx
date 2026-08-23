import { useEffect, useRef, useState } from 'react'

export interface PickerOption {
  id: string
  label: string
  sublabel?: string
}

interface EntityPickerProps {
  placeholder: string
  fetchOptions: (query: string) => Promise<PickerOption[]>
  onSelect: (option: PickerOption) => void
}

/**
 * Type-ahead picker so nobody ever has to know or paste a raw node id —
 * they search by name/title and the id travels along invisibly.
 */
export default function EntityPicker({ placeholder, fetchOptions, onSelect }: EntityPickerProps) {
  const [query, setQuery] = useState('')
  const [options, setOptions] = useState<PickerOption[]>([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    if (!open) return
    setLoading(true)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      fetchOptions(query)
        .then(setOptions)
        .catch(() => setOptions([]))
        .finally(() => setLoading(false))
    }, 200)
    return () => clearTimeout(debounceRef.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, open])

  return (
    <div className="picker">
      <input
        className="input"
        placeholder={placeholder}
        value={query}
        onFocus={() => setOpen(true)}
        onChange={(e) => {
          setQuery(e.target.value)
          setOpen(true)
        }}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
      />
      {open && (
        <div className="picker-dropdown">
          {loading && <div className="picker-item dim">Searching…</div>}
          {!loading && options.length === 0 && <div className="picker-item dim">No matches</div>}
          {!loading &&
            options.map((opt) => (
              <div
                key={opt.id}
                className="picker-item"
                onMouseDown={() => {
                  setQuery(opt.label)
                  setOpen(false)
                  onSelect(opt)
                }}
              >
                <strong>{opt.label}</strong>
                {opt.sublabel && <span>{opt.sublabel}</span>}
              </div>
            ))}
        </div>
      )}
    </div>
  )
}