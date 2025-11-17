/**
 * Language Selector - Phase 7
 * Multi-language OCR selection dropdown
 */
import { useState, useEffect } from 'react'
import { Globe } from 'lucide-react'

interface Language {
  code: string
  name: string
  paddleocr: string
  tesseract: string
}

interface LanguageSelectorProps {
  selectedLanguage: string
  autoDetect: boolean
  onLanguageChange: (lang: string) => void
  onAutoDetectChange: (autoDetect: boolean) => void
}

export function LanguageSelector({
  selectedLanguage,
  autoDetect,
  onLanguageChange,
  onAutoDetectChange
}: LanguageSelectorProps) {
  const [languages, setLanguages] = useState<Language[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadLanguages()
  }, [])

  const loadLanguages = async () => {
    try {
      const response = await window.electronAPI.getSupportedLanguages()
      if (response.success && response.result) {
        setLanguages(response.result.languages)
      }
    } catch (error) {
      console.error('Failed to load languages:', error)
    } finally {
      setLoading(false)
    }
  }

  const selectedLang = languages.find(l => l.code === selectedLanguage)
  const displayName = autoDetect ? 'Auto Detect' : (selectedLang?.name || selectedLanguage)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-1.5 bg-obsidian-bg-secondary
                   hover:bg-obsidian-bg-hover rounded text-sm text-obsidian-text
                   transition-colors"
        title="Select OCR Language"
      >
        <Globe className="w-4 h-4 text-obsidian-accent" />
        <span className="max-w-[120px] truncate">{displayName}</span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown Menu */}
          <div className="absolute right-0 mt-2 w-64 bg-obsidian-bg-secondary border border-obsidian-border
                          rounded-lg shadow-xl z-20 max-h-96 overflow-y-auto">
            {/* Auto Detect Option */}
            <div
              onClick={() => {
                onAutoDetectChange(true)
                setIsOpen(false)
              }}
              className={`px-4 py-2 hover:bg-obsidian-bg-hover cursor-pointer transition-colors
                         ${autoDetect ? 'bg-obsidian-accent/20 text-obsidian-accent' : ''}`}
            >
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4" />
                <div>
                  <div className="font-medium">Auto Detect</div>
                  <div className="text-xs text-obsidian-text/60">
                    Automatically detect language
                  </div>
                </div>
              </div>
            </div>

            <div className="border-t border-obsidian-border my-1" />

            {/* Language Options */}
            {loading ? (
              <div className="px-4 py-3 text-sm text-obsidian-text/60">
                Loading languages...
              </div>
            ) : languages.length === 0 ? (
              <div className="px-4 py-3 text-sm text-obsidian-text/60">
                No languages available
              </div>
            ) : (
              languages.map((lang) => (
                <div
                  key={lang.code}
                  onClick={() => {
                    onAutoDetectChange(false)
                    onLanguageChange(lang.code)
                    setIsOpen(false)
                  }}
                  className={`px-4 py-2 hover:bg-obsidian-bg-hover cursor-pointer transition-colors
                             ${!autoDetect && selectedLanguage === lang.code ? 'bg-obsidian-accent/20 text-obsidian-accent' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{lang.name}</div>
                      <div className="text-xs text-obsidian-text/60">
                        {lang.code}
                      </div>
                    </div>
                    {!autoDetect && selectedLanguage === lang.code && (
                      <svg
                        className="w-5 h-5 text-obsidian-accent"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}
