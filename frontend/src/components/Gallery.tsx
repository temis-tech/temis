'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { normalizeImageUrl } from '@/lib/utils'
import { normalizeHtmlContent } from '@/lib/htmlUtils'
import { GalleryImage } from '@/types'
import styles from './Gallery.module.css'

// Компонент для полноэкранного просмотра
function FullscreenView({
  items,
  currentIndex,
  onClose,
  onPrevious,
  onNext
}: {
  items: GalleryImage[]
  currentIndex: number
  onClose: () => void
  onPrevious: (e: React.MouseEvent) => void
  onNext: (e: React.MouseEvent) => void
}) {
  const item = items[currentIndex]
  const isVideo = item.content_type === 'video'
  const videoEmbedUrl = item.video_embed_url || (item.video_url ? null : null)
  const videoFile = item.video_file

  return (
    <div className={styles.fullscreenOverlay} onClick={onClose}>
      <button 
        className={styles.fullscreenClose}
        onClick={onClose}
        aria-label="Закрыть"
      >
        ×
      </button>
      <button 
        className={styles.fullscreenNav} 
        onClick={onPrevious}
        aria-label="Предыдущее"
      >
        ‹
      </button>
      <div className={styles.fullscreenContent} onClick={(e) => e.stopPropagation()}>
        {isVideo ? (
          videoEmbedUrl ? (
            <div style={{ width: '100%', maxWidth: '90vw', aspectRatio: '16/9' }}>
              <iframe
                src={videoEmbedUrl}
                style={{ width: '100%', height: '100%', border: 'none' }}
                allowFullScreen
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                frameBorder="0"
              />
            </div>
          ) : videoFile ? (
            <video
              src={normalizeImageUrl(videoFile)}
              controls
              autoPlay
              style={{ width: '100%', maxHeight: '90vh' }}
            />
          ) : null
        ) : item.image ? (
          <Image
            src={normalizeImageUrl(item.image)}
            alt={item.description || 'Изображение галереи'}
            fill
            style={{ objectFit: 'contain' }}
            priority
          />
        ) : null}
        {item.description && (
          <div 
            className={styles.fullscreenDescription}
            dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(item.description) }}
          />
        )}
      </div>
      <button 
        className={`${styles.fullscreenNav} ${styles.fullscreenNavRight}`}
        onClick={onNext}
        aria-label="Следующее"
      >
        ›
      </button>
      <div className={styles.fullscreenCounter}>
        {currentIndex + 1} / {items.length}
      </div>
    </div>
  )
}

interface GalleryProps {
  images: GalleryImage[]
  displayType?: 'grid' | 'carousel' | 'masonry'
  enableFullscreen?: boolean
}

export default function Gallery({ images, displayType = 'grid', enableFullscreen = true }: GalleryProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState<number | null>(null)
  const [carouselIndex, setCarouselIndex] = useState(0)

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
        setCurrentImageIndex(null)
        document.body.style.overflow = 'unset'
      } else if (e.key === 'ArrowLeft') {
        setCurrentImageIndex((prev) => prev !== null ? (prev - 1 + images.length) % images.length : null)
      } else if (e.key === 'ArrowRight') {
        setCurrentImageIndex((prev) => prev !== null ? (prev + 1) % images.length : null)
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

  // Проверка на пустой массив (после всех хуков)
  if (!images || images.length === 0) {
    return null
  }

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
                  {image.content_type === 'video' ? (
                    image.video_embed_url ? (
                      <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', width: '100%' }}>
                        <iframe
                          src={image.video_embed_url}
                          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                          allowFullScreen
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          frameBorder="0"
                        />
                      </div>
                    ) : image.video_file ? (
                      <video
                        src={normalizeImageUrl(image.video_file)}
                        controls
                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                      />
                    ) : null
                  ) : image.image ? (
                    <Image
                      src={normalizeImageUrl(image.image)}
                      alt={image.description || 'Изображение галереи'}
                      fill
                      style={{ objectFit: 'contain' }}
                    />
                  ) : null}
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
          <FullscreenView
            items={images}
            currentIndex={currentImageIndex}
            onClose={handleCloseFullscreen}
            onPrevious={handlePrevious}
            onNext={handleNext}
          />
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
              {image.content_type === 'video' ? (
                image.video_embed_url ? (
                  <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', width: '100%' }}>
                    <iframe
                      src={image.video_embed_url}
                      style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                      allowFullScreen
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      frameBorder="0"
                    />
                  </div>
                ) : image.video_file ? (
                  <video
                    src={normalizeImageUrl(image.video_file)}
                    controls
                    style={{ width: '100%', height: 'auto', maxHeight: '400px' }}
                  />
                ) : null
              ) : image.image ? (
                <div className={styles.masonryImageWrapper}>
                  <Image
                    src={normalizeImageUrl(image.image)}
                    alt={image.description || 'Изображение галереи'}
                    width={400}
                    height={300}
                    style={{ width: '100%', height: 'auto', objectFit: 'cover' }}
                  />
                </div>
              ) : null}
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
          <FullscreenView
            items={images}
            currentIndex={currentImageIndex}
            onClose={handleCloseFullscreen}
            onPrevious={handlePrevious}
            onNext={handleNext}
          />
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
            {image.content_type === 'video' ? (
              image.video_embed_url ? (
                <div className={styles.videoWrapper}>
                  <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', width: '100%' }}>
                    <iframe
                      src={image.video_embed_url}
                      style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                      allowFullScreen
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      frameBorder="0"
                    />
                  </div>
                  {image.description && (
                    <div 
                      className={styles.gridDescription}
                      dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(image.description) }}
                    />
                  )}
                </div>
              ) : image.video_file ? (
                <div className={styles.videoWrapper}>
                  <video
                    src={normalizeImageUrl(image.video_file)}
                    controls
                    style={{ width: '100%', height: 'auto', maxHeight: '400px' }}
                    onClick={(e) => {
                      if (enableFullscreen) {
                        e.stopPropagation()
                        handleImageClick(index)
                      }
                    }}
                  />
                  {image.description && (
                    <div 
                      className={styles.gridDescription}
                      dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(image.description) }}
                    />
                  )}
                </div>
              ) : null
            ) : image.image ? (
              <>
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
              </>
            ) : null}
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
