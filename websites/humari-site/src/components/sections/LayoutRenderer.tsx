// /var/www/megahub/websites/humari-site/src/components/sections/LayoutRenderer.tsx
import React from 'react'
import type { SectionProps, LayoutConfig } from '@/lib/types/sections'

interface LayoutRendererProps {
  type: 'columns' | 'grid' | 'stack'
  config: LayoutConfig
  sections: SectionProps[]
  renderSection: (section: SectionProps) => React.ReactNode
}

export function LayoutRenderer({ type, config, sections, renderSection }: LayoutRendererProps) {
  
  if (type === 'columns') {
    const columns = config.columns || [12]
    const gap = config.gap || '2rem'
    
    // 🔧 FIX: Mapping statique pour Tailwind
    const getColSpanClass = (span: number): string => {
      const spanMap: Record<number, string> = {
        1: 'lg:col-span-1',
        2: 'lg:col-span-2', 
        3: 'lg:col-span-3',
        4: 'lg:col-span-4',
        5: 'lg:col-span-5',
        6: 'lg:col-span-6',
        7: 'lg:col-span-7',
        8: 'lg:col-span-8',
        9: 'lg:col-span-9',
        10: 'lg:col-span-10',
        11: 'lg:col-span-11',
        12: 'lg:col-span-12'
      }
      return spanMap[span] || 'lg:col-span-12'
    }
    
    return (
      <section className="w-full grid grid-cols-12" style={{ gap }}>
        {sections.map((section, index) => {
          const colSpan = columns[index] || 12
          return (
            <div
              key={section.section_id}
              className={`col-span-12 ${getColSpanClass(colSpan)} min-w-0`}
            >
              {renderSection(section)}
            </div>
          )
        })}
      </section>
    )
  }

  if (type === 'grid') {
    const gridCols = config.grid_columns || 3
    const gap = config.gap || '2rem'
    
    return (
      <section
        className="w-full grid"
        style={{
          gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
          gap
        }}
      >
        {sections.map(section => (
          <div key={section.section_id}>
            {renderSection(section)}
          </div>
        ))}
      </section>
    )
  }

  if (type === 'stack') {
    const gap = config.gap || '1rem'
    
    return (
      <section className="w-full flex flex-col" style={{ gap }}>
        {sections.map(section => (
          <React.Fragment key={section.section_id}>
            {renderSection(section)}
          </React.Fragment>
        ))}
      </section>
    )
  }

  return null
}