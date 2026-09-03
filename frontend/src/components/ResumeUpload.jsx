import { useRef, useState } from 'react'

export default function ResumeUpload({ title, subtitle, onUpload, loading, error }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFile = (file) => {
    if (!file) return
    onUpload(file)
  }

  return (
    <section className="panel">
      <h2 className="panel-title">{title}</h2>
      {subtitle && <p className="panel-subtitle">{subtitle}</p>}

      <div
        className={`dropzone ${dragOver ? 'dropzone-active' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          handleFile(e.dataTransfer.files?.[0])
        }}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          hidden
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <span className="dropzone-mark" aria-hidden="true">+</span>
        <p className="dropzone-text">
          {loading ? 'Reading your resume…' : 'Drop a PDF or DOCX, or click to browse'}
        </p>
      </div>

      {error && <p className="field-error">{error}</p>}
    </section>
  )
}
