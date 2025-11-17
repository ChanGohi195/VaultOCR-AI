import { BookOpen, Hash, Table, FileText, CheckCircle, AlertCircle, Globe, Languages } from 'lucide-react'

interface DocumentInfoProps {
  metadata?: {
    page_count?: number
    layout_type?: string
    section_count?: number
    total_tables?: number
    table_count?: number
    confidence?: {
      average: number
      min: number
      max: number
      low_confidence_ratio: number
      total_lines?: number
      low_confidence_lines?: number
    }
    // Phase 7: Multi-language support
    detected_language?: string
    language_confidence?: number
    mixed_languages?: Array<{
      lang: string
      percentage: number
      char_count: number
    }>
  }
  toc?: Array<{
    title: string
    level: number
    page: number
  }>
  sections?: Array<{
    title: string
    level: number
    paragraphs: any[]
  }>
}

export default function DocumentInfo({ metadata, toc, sections }: DocumentInfoProps) {
  if (!metadata && !toc && !sections) {
    return null
  }

  return (
    <div className="w-64 bg-obsidian-sidebar border-l border-obsidian-border overflow-y-auto">
      <div className="p-4 space-y-6">
        {/* Metadata */}
        {metadata && (
          <div>
            <h3 className="text-xs font-semibold mb-3 text-obsidian-text/80 flex items-center space-x-2">
              <FileText className="w-3 h-3" />
              <span>DOCUMENT INFO</span>
            </h3>
            <div className="space-y-2 text-xs text-obsidian-text/60">
              {metadata.page_count && (
                <div className="flex justify-between">
                  <span>Pages:</span>
                  <span className="font-medium text-obsidian-text">{metadata.page_count}</span>
                </div>
              )}
              {metadata.section_count !== undefined && (
                <div className="flex justify-between">
                  <span>Sections:</span>
                  <span className="font-medium text-obsidian-text">{metadata.section_count}</span>
                </div>
              )}
              {metadata.layout_type && (
                <div className="flex justify-between">
                  <span>Layout:</span>
                  <span className="font-medium text-obsidian-text capitalize">
                    {metadata.layout_type.replace('_', ' ')}
                  </span>
                </div>
              )}
              {(metadata.total_tables || metadata.table_count) && (
                <div className="flex justify-between">
                  <span>Tables:</span>
                  <span className="font-medium text-obsidian-text">
                    {metadata.total_tables || metadata.table_count}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* OCR Confidence */}
        {metadata?.confidence && (
          <div>
            <h3 className="text-xs font-semibold mb-3 text-obsidian-text/80 flex items-center space-x-2">
              <CheckCircle className="w-3 h-3" />
              <span>OCR QUALITY</span>
            </h3>
            <div className="space-y-2 text-xs text-obsidian-text/60">
              <div className="flex justify-between items-center">
                <span>Confidence:</span>
                <div className="flex items-center gap-1">
                  <div className="w-16 h-2 bg-obsidian-bg-secondary rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        metadata.confidence.average >= 0.9
                          ? 'bg-green-500'
                          : metadata.confidence.average >= 0.7
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${metadata.confidence.average * 100}%` }}
                    />
                  </div>
                  <span className="font-medium text-obsidian-text">
                    {(metadata.confidence.average * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              {metadata.confidence.low_confidence_lines !== undefined && (
                <div className="flex justify-between items-center">
                  <span>Low conf. lines:</span>
                  <div className="flex items-center gap-1">
                    {metadata.confidence.low_confidence_ratio > 0.2 && (
                      <AlertCircle className="w-3 h-3 text-yellow-500" />
                    )}
                    <span className="font-medium text-obsidian-text">
                      {metadata.confidence.low_confidence_lines} / {metadata.confidence.total_lines}
                    </span>
                  </div>
                </div>
              )}
              <div className="flex justify-between">
                <span>Range:</span>
                <span className="font-medium text-obsidian-text">
                  {(metadata.confidence.min * 100).toFixed(0)}% - {(metadata.confidence.max * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Phase 7: Language Detection */}
        {metadata?.detected_language && (
          <div>
            <h3 className="text-xs font-semibold mb-3 text-obsidian-text/80 flex items-center space-x-2">
              <Globe className="w-3 h-3" />
              <span>LANGUAGE</span>
            </h3>
            <div className="space-y-2 text-xs text-obsidian-text/60">
              <div className="flex justify-between items-center">
                <span>Detected:</span>
                <span className="font-medium text-obsidian-text uppercase">
                  {metadata.detected_language}
                </span>
              </div>
              {metadata.language_confidence !== undefined && (
                <div className="flex justify-between items-center">
                  <span>Confidence:</span>
                  <div className="flex items-center gap-1">
                    <div className="w-16 h-2 bg-obsidian-bg-secondary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500"
                        style={{ width: `${metadata.language_confidence * 100}%` }}
                      />
                    </div>
                    <span className="font-medium text-obsidian-text">
                      {(metadata.language_confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}
              {metadata.mixed_languages && metadata.mixed_languages.length > 0 && (
                <div className="mt-3">
                  <div className="flex items-center gap-1 mb-2">
                    <Languages className="w-3 h-3 text-obsidian-accent" />
                    <span className="text-[10px] font-semibold text-obsidian-text/70">
                      MIXED LANGUAGES
                    </span>
                  </div>
                  {metadata.mixed_languages.map((langInfo, idx) => (
                    <div key={idx} className="flex justify-between items-center py-1">
                      <span className="uppercase text-[10px]">{langInfo.lang}</span>
                      <div className="flex items-center gap-1">
                        <div className="w-12 h-1.5 bg-obsidian-bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-obsidian-accent"
                            style={{ width: `${langInfo.percentage * 100}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-medium text-obsidian-text">
                          {(langInfo.percentage * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Table of Contents */}
        {toc && toc.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold mb-3 text-obsidian-text/80 flex items-center space-x-2">
              <BookOpen className="w-3 h-3" />
              <span>TABLE OF CONTENTS</span>
            </h3>
            <div className="space-y-1">
              {toc.map((item, idx) => (
                <div
                  key={idx}
                  className="text-xs text-obsidian-text/70 hover:text-obsidian-accent cursor-pointer py-1 px-2 rounded hover:bg-obsidian-hover"
                  style={{ paddingLeft: `${(item.level - 1) * 12 + 8}px` }}
                >
                  <div className="flex items-start space-x-2">
                    <Hash className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <span className="flex-1 truncate">{item.title}</span>
                    <span className="text-obsidian-text/40 text-[10px]">p{item.page}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sections Summary */}
        {sections && sections.length > 0 && !toc && (
          <div>
            <h3 className="text-xs font-semibold mb-3 text-obsidian-text/80 flex items-center space-x-2">
              <Hash className="w-3 h-3" />
              <span>SECTIONS</span>
            </h3>
            <div className="space-y-2">
              {sections.map((section, idx) => (
                <div
                  key={idx}
                  className="text-xs text-obsidian-text/70 hover:text-obsidian-accent cursor-pointer py-1.5 px-2 rounded hover:bg-obsidian-hover"
                >
                  <div className="font-medium truncate">{section.title}</div>
                  <div className="text-[10px] text-obsidian-text/40 mt-0.5">
                    {section.paragraphs?.length || 0} paragraphs
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
