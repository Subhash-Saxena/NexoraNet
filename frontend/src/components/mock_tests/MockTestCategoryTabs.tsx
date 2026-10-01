import React from 'react'
import {
  Layers,
  Star,
  ShieldCheck,
  Sliders,
  Cpu,
  FileSpreadsheet,
  Award,
} from 'lucide-react'
import type { CatalogCategoryItem } from '../../types'

interface MockTestCategoryTabsProps {
  categories: CatalogCategoryItem[]
  activeCategory: string
  onCategoryChange: (categoryKey: string) => void
}

export const MockTestCategoryTabs: React.FC<MockTestCategoryTabsProps> = ({
  categories,
  activeCategory,
  onCategoryChange,
}) => {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'Star':
        return <Star size={15} />
      case 'ShieldCheck':
        return <ShieldCheck size={15} />
      case 'Sliders':
        return <Sliders size={15} />
      case 'Cpu':
        return <Cpu size={15} />
      case 'FileSpreadsheet':
        return <FileSpreadsheet size={15} />
      case 'Award':
        return <Award size={15} />
      case 'Layers':
      default:
        return <Layers size={15} />
    }
  }

  return (
    <div className="mt-category-tabs" data-testid="mock-test-category-tabs">
      {categories.map((cat) => {
        const isActive = activeCategory === cat.key
        return (
          <button
            key={cat.key}
            type="button"
            className={`mt-category-tab ${isActive ? 'active' : ''}`}
            onClick={() => onCategoryChange(cat.key)}
            title={cat.description}
            data-testid={`category-tab-${cat.key}`}
          >
            {getIcon(cat.icon)}
            <span>{cat.title}</span>
            <span className="mt-category-count">{cat.test_count}</span>
          </button>
        )
      })}
    </div>
  )
}
