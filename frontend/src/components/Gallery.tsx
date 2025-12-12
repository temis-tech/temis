'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { normalizeImageUrl } from '@/lib/utils'
import { normalizeHtmlContent } from '@/lib/htmlUtils'
import { GalleryImage } from '@/types'
import styles from './Gallery.module.css'

interface GalleryProps {
  images: GalleryImage[]
  displayType?: 'grid' | 'carousel' | 'masonry'
  enableFullscreen?: boolean
}

export default function Gallery({ images, displayType = 'grid', enableFullscreen = true }: GalleryProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState<number | null>(null)
  const [carouselIndex, setCarouselIndex] = useState(0)

  // Проверка на пустой массив
  if (!images || images.length === 0) {
    return null
  }

  // Обработка открытия изображения на весь экран
  const handleImageClick = (index: number) => {
    if (enableFullscreen) {
      setCurrentImageIndex(index)
      document.body.style.overflow = 'hidden' // Блокируем прокрутку страницы
    }
  }

  // Закрытие полноэкранного режима
  const handleCloseFullscreen = () => {
    setCurrentImageIndex(null)
    document.body.style.overflow = 'unset'
  }

  // Навигация в полноэкранном режиме
  const handlePrevious = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (currentImageIndex !== null) {
      setCurrentImageIndex((currentImageIndex - 1 + images.length) % images.length)
    }
  }

  const handleNext = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (currentImageIndex !== null) {
      setCurrentImageIndex((currentImageIndex + 1) % images.length)
    }
  }

  // Обработка клавиатуры в полноэкранном режиме
  useEffect(() => {
    if (currentImageIndex === null) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleCloseFullscreen()
      } else if (e.key === 'ArrowLeft') {
        handlePrevious(e as any)
      } else if (e.key === 'ArrowRight') {
        handleNext(e as any)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentImageIndex, images.length])

  // Карусель: автоматическая прокрутка
  useEffect(() => {
    if (displayType === 'carousel' && images.length > 0) {
      const interval = setInterval(() => {
        setCarouselIndex((prev) => (prev + 1) % images.length)
      }, 5000) // Меняем изображение каждые 5 секунд

      return () => clearInterval(interval)
    }
  }, [displayType, images.length])

  // Рендеринг в зависимости от типа отображения
  if (displayType === 'carousel') {
    return (
      <>
        <div className={styles.carousel}>
          <div 
            className={styles.carouselTrack}
            style={{ transform: `translateX(-${carouselIndex * 100}%)` }}
          >
            {images.map((image, index) => (
              <div key={image.id} className={styles.carouselSlide}>
                <div 
                  className={styles.carouselImageWrapper}
                  onClick={() => handleImageClick(index)}
                  style={{ cursor: enableFullscreen ? 'pointer' : 'default' }}
                >
                  <Image
                    src={normalizeImageUrl(image.image)}
                    alt={image.description || 'Изображение галереи'}
                    fill
                    style={{ objectFit: 'contain' }}
                  />
                </div>
                {image.description && (
                  <div 
                    className={styles.carouselDescription}
                    dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(image.description) }}
                  />
                )}
              </div>
            ))}
          </div>
          {images.length > 1 && (
            <>
              <button 
                className={styles.carouselButton} 
                onClick={() => setCarouselIndex((carouselIndex - 1 + images.length) % images.length)}
                aria-label="Предыдущее изображение"
              >
                ‹
              </button>
              <button 
                className={`${styles.carouselButton} ${styles.carouselButtonRight}`}
                onClick={() => setCarouselIndex((carouselIndex + 1) % images.length)}
                aria-label="Следующее изображение"
              >
                ›
              </button>
              <div className={styles.carouselIndicators}>
                {images.map((_, index) => (
                  <button
                    key={index}
                    className={`${styles.carouselIndicator} ${index === carouselIndex ? styles.active : ''}`}
                    onClick={() => setCarouselIndex(index)}
                    aria-label={`Перейти к изображению ${index + 1}`}
                  />
                ))}
              </div>
            </>
          )}
        </div>

        {/* Полноэкранный просмотр */}
        {currentImageIndex !== null && enableFullscreen && (
          <div className={styles.fullscreenOverlay} onClick={handleCloseFullscreen}>
            <button 
              className={styles.fullscreenClose}
              onClick={handleCloseFullscreen}
              aria-label="Закрыть"
            >
              ×
            </button>
            <button 
              className={styles.fullscreenNav} 
              onClick={handlePrevious}
              aria-label="Предыдущее изображение"
            >
              ‹
            </button>
            <div className={styles.fullscreenContent} onClick={(e) => e.stopPropagation()}>
              <Image
                src={normalizeImageUrl(images[currentImageIndex].image)}
                alt={images[currentImageIndex].description || 'Изображение галереи'}
                fill
                style={{ objectFit: 'contain' }}
                priority
              />
              {images[currentImageIndex].description && (
                <div 
                  className={styles.fullscreenDescription}
                  dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(images[currentImageIndex].description) }}
                />
              )}
            </div>
            <button 
              className={`${styles.fullscreenNav} ${styles.fullscreenNavRight}`}
              onClick={handleNext}
              aria-label="Следующее изображение"
            >
              ›
            </button>
            <div className={styles.fullscreenCounter}>
              {currentImageIndex + 1} / {images.length}
            </div>
          </div>
        )}
      </>
    )
  }

  if (displayType === 'masonry') {
    return (
      <>
        <div className={styles.masonry}>
          {images.map((image, index) => (
            <div 
              key={image.id} 
              className={styles.masonryItem}
              onClick={() => handleImageClick(index)}
              style={{ cursor: enableFullscreen ? 'pointer' : 'default' }}
            >
              <div className={styles.masonryImageWrapper}>
                <Image
                  src={normalizeImageUrl(image.image)}
                  alt={image.description || 'Изображение галереи'}
                  width={400}
                  height={300}
                  style={{ width: '100%', height: 'auto', objectFit: 'cover' }}
                />
              </div>
              {image.description && (
                <div 
                  className={styles.masonryDescription}
                  dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(image.description) }}
                />
              )}
            </div>
          ))}
        </div>

        {/* Полноэкранный просмотр */}
        {currentImageIndex !== null && enableFullscreen && (
          <div className={styles.fullscreenOverlay} onClick={handleCloseFullscreen}>
            <button 
              className={styles.fullscreenClose}
              onClick={handleCloseFullscreen}
              aria-label="Закрыть"
            >
              ×
            </button>
            <button 
              className={styles.fullscreenNav} 
              onClick={handlePrevious}
              aria-label="Предыдущее изображение"
            >
              ‹
            </button>
            <div className={styles.fullscreenContent} onClick={(e) => e.stopPropagation()}>
              <Image
                src={normalizeImageUrl(images[currentImageIndex].image)}
                alt={images[currentImageIndex].description || 'Изображение галереи'}
                fill
                style={{ objectFit: 'contain' }}
                priority
              />
              {images[currentImageIndex].description && (
                <div 
                  className={styles.fullscreenDescription}
                  dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(images[currentImageIndex].description) }}
                />
              )}
            </div>
            <button 
              className={`${styles.fullscreenNav} ${styles.fullscreenNavRight}`}
              onClick={handleNext}
              aria-label="Следующее изображение"
            >
              ›
            </button>
            <div className={styles.fullscreenCounter}>
              {currentImageIndex + 1} / {images.length}
            </div>
          </div>
        )}
      </>
    )
  }

  // По умолчанию: плитка (grid)
  return (
    <>
      <div className={styles.grid}>
        {images.map((image, index) => (
          <div 
            key={image.id} 
            className={styles.gridItem}
            onClick={() => handleImageClick(index)}
            style={{ cursor: enableFullscreen ? 'pointer' : 'default' }}
          >
            <div className={styles.gridImageWrapper}>
              <Image
                src={normalizeImageUrl(image.image)}
                alt={image.description || 'Изображение галереи'}
                width={600}
                height={400}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            </div>
            {image.description && (
              <div 
                className={styles.gridDescription}
                dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(image.description) }}
              />
            )}
          </div>
        ))}
      </div>

      {/* Полноэкранный просмотр */}
      {currentImageIndex !== null && enableFullscreen && (
        <div className={styles.fullscreenOverlay} onClick={handleCloseFullscreen}>
          <button 
            className={styles.fullscreenClose}
            onClick={handleCloseFullscreen}
            aria-label="Закрыть"
          >
            ×
          </button>
          <button 
            className={styles.fullscreenNav} 
            onClick={handlePrevious}
            aria-label="Предыдущее изображение"
          >
            ‹
          </button>
          <div className={styles.fullscreenContent} onClick={(e) => e.stopPropagation()}>
            <Image
              src={normalizeImageUrl(images[currentImageIndex].image)}
              alt={images[currentImageIndex].description || 'Изображение галереи'}
              fill
              style={{ objectFit: 'contain' }}
              priority
            />
            {images[currentImageIndex].description && (
              <div 
                className={styles.fullscreenDescription}
                dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(images[currentImageIndex].description) }}
              />
            )}
          </div>
          <button 
            className={`${styles.fullscreenNav} ${styles.fullscreenNavRight}`}
            onClick={handleNext}
            aria-label="Следующее изображение"
          >
            ›
          </button>
          <div className={styles.fullscreenCounter}>
            {currentImageIndex + 1} / {images.length}
          </div>
        </div>
      )}
    </>
  )
}
