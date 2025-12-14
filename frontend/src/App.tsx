import { useState } from 'react'
import { Leaf, Mic, FileText, Clock, Sparkles, ChevronRight, Search, Copy, Check, AlertCircle } from 'lucide-react'
import { generatePodcast } from './api/podcast'
import type { GenerateResponse } from './types/podcast'
import './App.css'

function App() {
  const [topic, setTopic] = useState('')
  const [duration, setDuration] = useState(5)
  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState<GenerateResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleGenerate = async () => {
    if (!topic.trim()) return

    setIsGenerating(true)
    setError(null)
    setResult(null)

    try {
      const response = await generatePodcast({
        topic: topic.trim(),
        duration_minutes: duration,
      })
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate podcast')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCopy = async () => {
    if (!result?.script) return
    await navigator.clipboard.writeText(result.script)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="app">
      {/* Decorative botanical elements */}
      <div className="botanical-accent botanical-accent--top-right" />
      <div className="botanical-accent botanical-accent--bottom-left" />

      {/* Header */}
      <header className="header">
        <div className="container header__container">
          <div className="header__brand">
            <div className="header__logo">
              <Leaf className="header__logo-icon" />
            </div>
            <div className="header__title">
              <h1>Podcast Generator</h1>
              <span className="header__subtitle">Research-powered audio</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        <div className="container">
          {/* Hero Section */}
          <section className="hero animate-slide-up">
            <div className="hero__content">
              <h2 className="hero__title">
                Turn <span className="text-gradient">Research</span> into
                <br />Engaging Podcasts
              </h2>
              <p className="hero__description">
                Enter a topic, and our AI will search academic papers on arXiv,
                synthesize the findings, and generate an engaging podcast script.
              </p>
            </div>
          </section>

          {/* Generator Card */}
          <section className="generator-card animate-bloom stagger-2">
            <div className="generator-card__header">
              <Sparkles className="generator-card__icon" />
              <h3>Create New Episode</h3>
            </div>

            <div className="generator-card__body">
              {/* Topic Input */}
              <div className="form-group">
                <label htmlFor="topic" className="form-label">
                  <Search size={16} />
                  Research Topic
                </label>
                <input
                  id="topic"
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., Transformer architectures, SAM3, Quantum computing..."
                  className="form-input"
                  disabled={isGenerating}
                  onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                />
                <span className="form-hint">
                  We'll search arXiv for recent papers on this topic
                </span>
              </div>

              {/* Duration Selector */}
              <div className="form-group">
                <label className="form-label">
                  <Clock size={16} />
                  Episode Duration
                </label>
                <div className="duration-selector">
                  {[2, 5, 10, 15, 20].map((mins) => (
                    <button
                      key={mins}
                      className={`duration-btn ${duration === mins ? 'duration-btn--active' : ''}`}
                      onClick={() => setDuration(mins)}
                      disabled={isGenerating}
                    >
                      {mins} min
                    </button>
                  ))}
                </div>
              </div>

              {/* Generate Button */}
              <button
                className={`generate-btn ${isGenerating ? 'generate-btn--loading' : ''}`}
                onClick={handleGenerate}
                disabled={!topic.trim() || isGenerating}
              >
                {isGenerating ? (
                  <>
                    <div className="generate-btn__spinner" />
                    Researching & Writing...
                  </>
                ) : (
                  <>
                    <Mic size={20} />
                    Generate Podcast
                    <ChevronRight size={20} />
                  </>
                )}
              </button>

              {/* Error Message */}
              {error && (
                <div className="error-message">
                  <AlertCircle size={18} />
                  <span>{error}</span>
                </div>
              )}
            </div>
          </section>

          {/* Generated Script */}
          {result && (
            <section className="result-section animate-slide-up">
              <div className="result-card">
                <div className="result-card__header">
                  <div className="result-card__title">
                    <FileText size={20} />
                    <h3>{result.topic}</h3>
                  </div>
                  <div className="result-card__meta">
                    <span className="badge">{result.duration_minutes} min</span>
                    <span className="badge">{result.word_count} words</span>
                    <button className="copy-btn" onClick={handleCopy}>
                      {copied ? <Check size={16} /> : <Copy size={16} />}
                      {copied ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                </div>
                <div className="result-card__content">
                  <pre className="script-text">{result.script}</pre>
                </div>
              </div>
            </section>
          )}

          {/* Placeholder when no result */}
          {!result && !isGenerating && (
            <section className="episodes-section animate-slide-up stagger-3">
              <div className="section-header">
                <h3>Generated Script</h3>
              </div>
              <div className="episodes-placeholder">
                <FileText size={48} className="episodes-placeholder__icon" />
                <p>Your podcast script will appear here</p>
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>Built with arXiv MCP Server + Claude + ElevenLabs</p>
        </div>
      </footer>
    </div>
  )
}

export default App
