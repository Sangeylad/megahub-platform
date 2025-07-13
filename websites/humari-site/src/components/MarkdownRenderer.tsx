interface MarkdownRendererProps {
  content: string
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  // Version simple sans parser markdown pour l'instant
  // On peut ajouter une lib comme react-markdown plus tard
  
  return (
    <div 
      className="markdown-content"
      dangerouslySetInnerHTML={{ 
        __html: content
          .replace(/\n/g, '<br/>')
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
      }} 
    />
  )
}