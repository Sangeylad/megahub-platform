// /var/www/megahub/websites/humari-site/src/components/sections/FeaturesSection.tsx
import type { FeaturesGridProps, SectionComponentProps } from '@/lib/types/sections'

export function FeaturesSection({ data }: SectionComponentProps<FeaturesGridProps>) {
  const { title, subtitle, features = [], columns = 3 } = data

  let gridClass = 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'

  if (columns === 2) {
    gridClass = 'grid-cols-1 md:grid-cols-2'
  } else if (columns === 4) {
    gridClass = 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  }

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {(title || subtitle) && (
          <div className="text-center mb-12">
            {title && (
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                {subtitle}
              </p>
            )}
          </div>
        )}
        
        <div className={`grid ${gridClass} gap-8`}>
          {features.map((feature, index) => (
            <div key={index} className="card-base text-center">
              {feature.icon && (
                <div className="text-4xl mb-4">
                  {feature.icon}
                </div>
              )}
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}