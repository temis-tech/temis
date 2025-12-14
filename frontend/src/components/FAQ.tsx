'use client'

import { useState } from 'react'
import Image from 'next/image'
import { normalizeImageUrl } from '@/lib/utils'
import { normalizeHtmlContent } from '@/lib/htmlUtils'
import styles from './FAQ.module.css'

export interface FAQItem {
  id: number
  question: string
  answer: string
  order: number
}

interface FAQProps {
  items: FAQItem[]
  icon?: string | null
  iconPosition?: 'left' | 'right'
  backgroundColor?: string
  backgroundImage?: string | null
  animation?: 'slide' | 'fade' | 'none'
}

export default function FAQ({
  items,
  icon,
  iconPosition = 'left',
  backgroundColor = '#FFFFFF',
  backgroundImage,
  animation = 'slide'
}: FAQProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const toggleItem = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  const getAnimationClass = () => {
    switch (animation) {
      case 'slide':
        return styles.animationSlide
      case 'fade':
        return styles.animationFade
      case 'none':
        return styles.animationNone
      default:
        return styles.animationSlide
    }
  }

  const containerStyle: React.CSSProperties = {
    backgroundColor: backgroundColor || '#FFFFFF',
    backgroundImage: backgroundImage ? `url(${normalizeImageUrl(backgroundImage)})` : undefined,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
  }

  return (
    <div className={styles.faqContainer} style={containerStyle}>
      <div className={styles.faqList}>
        {items.map((item, index) => {
          const isOpen = openIndex === index
          
          return (
            <div
              key={item.id}
              className={`${styles.faqItem} ${isOpen ? styles.faqItemOpen : ''} ${getAnimationClass()}`}
            >
              <button
                className={styles.faqQuestion}
                onClick={() => toggleItem(index)}
                aria-expanded={isOpen}
                aria-controls={`faq-answer-${item.id}`}
              >
                <div className={styles.faqQuestionContent}>
                  {icon && iconPosition === 'left' && (
                    <div className={styles.faqIcon}>
                      <Image
                        src={normalizeImageUrl(icon)}
                        alt=""
                        width={24}
                        height={24}
                        style={{ objectFit: 'contain' }}
                      />
                    </div>
                  )}
                  <span className={styles.faqQuestionText}>{item.question}</span>
                  {icon && iconPosition === 'right' && (
                    <div className={styles.faqIcon}>
                      <Image
                        src={normalizeImageUrl(icon)}
                        alt=""
                        width={24}
                        height={24}
                        style={{ objectFit: 'contain' }}
                      />
                    </div>
                  )}
                </div>
                <span className={`${styles.faqToggle} ${isOpen ? styles.faqToggleOpen : ''}`}>
                  {isOpen ? '−' : '+'}
                </span>
              </button>
              <div
                id={`faq-answer-${item.id}`}
                className={`${styles.faqAnswer} ${isOpen ? styles.faqAnswerOpen : ''}`}
                aria-hidden={!isOpen}
              >
                <div
                  className={styles.faqAnswerContent}
                  dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(item.answer) }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
