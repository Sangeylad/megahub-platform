// /var/www/megahub/websites/humari-site/src/components/sections/RichTextSection.tsx
import type { RichTextProps, SectionComponentProps } from '@/lib/types/sections'

export function RichTextSection({ data }: SectionComponentProps<RichTextProps>) {
  const { content, max_width = 'prose', text_align = 'left' } = data

  let containerClass = 'max-w-4xl mx-auto px-4 sm:px-6 lg:px-8'

  if (max_width === 'full') {
    containerClass = 'max-w-none mx-auto px-4 sm:px-6 lg:px-8'
  } else if (max_width === 'narrow') {
    containerClass = 'max-w-2xl mx-auto px-4 sm:px-6 lg:px-8'
  }

  let textAlignClass = 'text-left'
  if (text_align === 'center') {
    textAlignClass = 'text-center'
  }

  // Simple markdown parsing
  const parseMarkdown = (text: string) => {
    return text
      .replace(/^# (.+)$/gim, '<h1 class="text-3xl font-bold mb-4">$1</h1>')
      .replace(/^## (.+)$/gim, '<h2 class="text-2xl font-bold mb-3">$1</h2>')
      .replace(/^### (.+)$/gim, '<h3 class="text-xl font-bold mb-2">$1</h3>')
      .replace(/\*\*(.+?)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/gim, '<em>$1</em>')
      .replace(/\n/gim, '<br>')
  }

  return (
    <section className="py-16 bg-white">
      <div className={`${containerClass} ${textAlignClass}`}>
        <div 
          className="prose prose-lg max-w-none"
          dangerouslySetInnerHTML={{
            __html: parseMarkdown(content)
          }}
        />
      </div>
    </section>
  )
}