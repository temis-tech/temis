'use client'

import { ContentPage as ContentPageType } from '@/types'
import { normalizeImageUrl } from '@/lib/utils'
import { normalizeHtmlContent } from '@/lib/htmlUtils'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import BookingForm from './BookingForm'
import Gallery from './Gallery'
import FAQ from './FAQ'
import BranchesList from './BranchesList'
import styles from './ContentPage.module.css'

interface ContentPageProps {
  page: ContentPageType
}

export default function ContentPage({ page }: ContentPageProps) {
  const router = useRouter()
  const [showBookingForm, setShowBookingForm] = useState(false)
  const [selectedFormId, setSelectedFormId] = useState<number | null>(null)
  const [selectedServiceId, setSelectedServiceId] = useState<number | null>(null)
  const [selectedServiceTitle, setSelectedServiceTitle] = useState<string>('')

  const openBookingForm = (formId: number, title?: string, serviceId?: number | null) => {
    setSelectedFormId(formId)
    setSelectedServiceTitle(title || '')
    setSelectedServiceId(serviceId ?? null)
    setShowBookingForm(true)
  }

  const handleButtonClick = (item: any) => {
    if (item.button_type === 'booking') {
      if (!item.button_booking_form_id) {
        alert('Ошибка: не указана форма записи для этой услуги')
        return
      }

      openBookingForm(item.button_booking_form_id, item.title, item.service_id ?? null)
      return
    }

    if (item.button_type === 'quiz' && item.button_quiz_slug) {
      router.push(`/quizzes/${item.button_quiz_slug}`)
      return
    }

    if (item.button_type === 'external' && item.button_url) {
      window.open(item.button_url, '_blank')
      return
    }

    alert('Ошибка: не настроена кнопка для этой услуги')
  }

  const renderBookingForm = () => {
    if (!showBookingForm || !selectedFormId) {
      return null
    }

    return (
      <BookingForm
        formId={selectedFormId}
        serviceId={selectedServiceId || 0}
        serviceTitle={selectedServiceTitle}
        onClose={() => {
          setShowBookingForm(false)
          setSelectedFormId(null)
          setSelectedServiceId(null)
          setSelectedServiceTitle('')
        }}
      />
    )
  }

  const renderCatalogItems = (items: any[]) => {
    const getWidthClass = (width: string) => {
      switch (width) {
        case 'narrow':
          return styles.catalogItemNarrow
        case 'medium':
          return styles.catalogItemMedium
        case 'wide':
          return styles.catalogItemWide
        case 'full':
          return styles.catalogItemFull
        default:
          return styles.catalogItemMedium
      }
    }

    return (
      <div className={styles.catalogGrid}>
        {items.map((item) => {
          const hasPage = item.has_own_page && item.url
          const widthClass = getWidthClass(item.width || 'medium')
          
          const getImageSize = (size?: string) => {
            switch (size) {
              case 'small': return { width: 200, height: 150 }
              case 'medium': return { width: 400, height: 300 }
              case 'large': return { width: 600, height: 450 }
              case 'full': return { width: 800, height: 600 }
              default: return { width: 400, height: 300 }
            }
          }

          const getImageAlignClass = (align?: string) => {
            switch (align) {
              case 'left': return styles.imageLeft
              case 'right': return styles.imageRight
              case 'center': return styles.imageCenter
              case 'full': return styles.imageFull
              default: return styles.imageCenter
            }
          }

          const imageSize = getImageSize(item.image_size)
          const imageAlignClass = getImageAlignClass(item.image_align)
          
          // Используем card_image для карточки, если есть, иначе image
          const cardImage = item.card_image || item.image;
          
          const cardContent = (
            <div className={`${styles.catalogItem} ${widthClass}`}>
              {cardImage && (
                <div className={`${styles.imageWrapper} ${imageAlignClass}`}>
                  <Image
                    src={normalizeImageUrl(cardImage)}
                    alt={item.title}
                    width={imageSize.width}
                    height={imageSize.height}
                    className={styles.image}
                    style={{
                      maxWidth: item.image_size === 'full' ? '100%' : `${imageSize.width}px`,
                      width: item.image_size === 'full' ? '100%' : 'auto',
                      height: 'auto'
                    }}
                  />
                </div>
              )}
              <h3 className={styles.itemTitle}>{item.title}</h3>
              {item.card_description && (
                <div
                  className={styles.itemDescription}
                  dangerouslySetInnerHTML={{ __html: item.card_description }}
                />
              )}
              {item.button_type !== 'none' && (
                <button
                  type="button"
                  className={styles.button}
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    handleButtonClick(item)
                  }}
                >
                  {item.button_text || 'Записаться'}
                </button>
              )}
            </div>
          )
          
          if (hasPage) {
            return (
              <Link key={item.id} href={item.url} className={`${styles.catalogItemLink} ${widthClass}`}>
                {cardContent}
              </Link>
            )
          }
          
          return (
            <div key={item.id} className={widthClass}>
              {cardContent}
            </div>
          )
        })}
      </div>
    )
  }

  // Рендерим каталог и галерею для всех типов страниц
  const renderCatalog = () => {
    if (page.catalog_items && page.catalog_items.length > 0) {
      return renderCatalogItems(page.catalog_items)
    }
    return null
  }

  const renderBranches = () => {
    // Отображаем филиалы, если они выбраны для отображения на странице
    if (page.display_branches && page.display_branches.length > 0) {
      return <BranchesList branches={page.display_branches} />
    }
    return null
  }

  const renderGallery = () => {
    if (page.gallery_images && page.gallery_images.length > 0) {
      return (
        <div className={styles.galleryGrid}>
          {page.gallery_images.map((image) => (
            <div key={image.id} className={styles.galleryItem}>
              <div className={styles.imageWrapper}>
                <Image
                  src={normalizeImageUrl(image.image)}
                  alt={image.description || 'Изображение'}
                  width={600}
                  height={400}
                  className={styles.image}
                />
              </div>
              {image.description && (
                <p className={styles.imageDescription}>{image.description}</p>
              )}
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  if (page.page_type === 'catalog') {
    return (
      <>
        <div className={styles.container}>
          {page.description && (
            <div
              className={styles.description}
              dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(page.description) }}
            />
          )}
          {renderCatalog()}
          {/* Галерея для страницы типа 'catalog' */}
          {page.gallery_images && page.gallery_images.length > 0 ? (
            <Gallery
              images={page.gallery_images}
              displayType={page.gallery_display_type || 'grid'}
              enableFullscreen={page.gallery_enable_fullscreen !== false}
            />
          ) : null}
          {renderBranches()}
        </div>

        {renderBookingForm()}
      </>
    )
  }

  if (page.page_type === 'gallery') {
    // Отладочная информация (можно убрать после проверки)
    console.log('Gallery page data:', {
      page_type: page.page_type,
      gallery_images: page.gallery_images,
      gallery_images_length: page.gallery_images?.length,
      gallery_display_type: page.gallery_display_type,
      gallery_enable_fullscreen: page.gallery_enable_fullscreen
    })

    return (
      <div className={styles.container}>
        {page.description && (
          <div
            className={styles.description}
            dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(page.description) }}
          />
        )}
        {renderCatalog()}
        {/* Галерея для страницы типа 'gallery' */}
        {page.gallery_images && page.gallery_images.length > 0 ? (
          <Gallery
            images={page.gallery_images}
            displayType={page.gallery_display_type || 'grid'}
            enableFullscreen={page.gallery_enable_fullscreen !== false}
          />
        ) : (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#999' }}>
            {page.gallery_images ? 
              'Нет изображений в галерее. Добавьте изображения в админке.' :
              'Галерея не загружена. Проверьте настройки страницы.'}
          </div>
        )}
        {renderBranches()}
        {renderBookingForm()}
      </div>
    )
  }

  if (page.page_type === 'home') {
    const activeBlocks = page.home_blocks?.filter((block) => block.is_active) || [];
    
    if (process.env.NODE_ENV === 'development') {
      console.log('Home page blocks:', {
        total_blocks: page.home_blocks?.length || 0,
        active_blocks: activeBlocks.length,
        blocks: activeBlocks.map(b => ({
          id: b.id,
          is_active: b.is_active,
          has_content_page_data: !!b.content_page_data,
          content_page_type: b.content_page_data?.page_type,
          content_page_title: b.content_page_data?.title
        }))
      });
    }
    
    return (
      <div className={styles.container}>
        {page.description && (
          <div
            className={styles.description}
            dangerouslySetInnerHTML={{ __html: page.description }}
          />
        )}
        {activeBlocks.length === 0 && (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#999' }}>
            Нет активных блоков для отображения. Добавьте блоки в админке.
          </div>
        )}
        {activeBlocks.map((block) => {
          if (!block.content_page_data) {
            console.warn('Home block missing content_page_data:', block.id);
            return null;
          }
          const contentPage = block.content_page_data

          // Пропускаем страницы типа 'home', чтобы избежать рекурсии
          if (contentPage.page_type === 'home') {
            console.warn('Skipping home page block with home page type:', block.id);
            return null;
          }

          const TitleTag = block.title_tag || 'h2'
          const displayTitle = block.title || contentPage.title
          const titleSizeClass = block.title_size ? styles[`titleSize_${block.title_size}`] : styles.titleSize_large

          // Определяем тип страницы для правильного отображения
          const pageType = contentPage.page_type

          // Отладочная информация
          if (process.env.NODE_ENV === 'development') {
            console.log('Rendering home block:', {
              block_id: block.id,
              page_type: pageType,
              has_description: !!contentPage.description,
              description_length: contentPage.description?.length || 0,
              has_faq_items: !!contentPage.faq_items,
              faq_items_count: contentPage.faq_items?.length || 0,
              has_catalog_items: !!contentPage.catalog_items,
              catalog_items_count: contentPage.catalog_items?.length || 0,
              has_gallery_images: !!contentPage.gallery_images,
              gallery_images_count: contentPage.gallery_images?.length || 0,
            });
          }

          return (
            <div key={block.id} className={styles.homeBlock}>
              {block.show_title && displayTitle && (
                <TitleTag
                  className={`${styles.blockTitle} ${titleSizeClass}`}
                  style={{
                    textAlign: block.title_align || 'center',
                    color: block.title_color || '#333',
                    fontWeight: block.title_bold ? 'bold' : 'normal',
                    fontStyle: block.title_italic ? 'italic' : 'normal',
                    ...(block.title_custom_css ? (() => {
                      try {
                        // Парсим CSS строку в объект стилей
                        const stylesObj: Record<string, string> = {};
                        block.title_custom_css.split(';').forEach(rule => {
                          const [key, value] = rule.split(':').map(s => s.trim());
                          if (key && value) {
                            // Конвертируем kebab-case в camelCase
                            const camelKey = key.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
                            stylesObj[camelKey] = value;
                          }
                        });
                        return stylesObj;
                      } catch (e) {
                        return {};
                      }
                    })() : {})
                  }}
                >
                  {displayTitle}
                </TitleTag>
              )}

              {/* Описание страницы (для типов catalog и gallery) */}
              {contentPage.description && 
               (pageType === 'catalog' || pageType === 'gallery') && (
                <div
                  className={styles.description}
                  dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(contentPage.description) }}
                />
              )}

              {/* Текст для страниц типа 'text' - отображаем описание и изображение */}
              {pageType === 'text' && (
                <>
                  {contentPage.image && (
                    <div className={styles.textImageWrapper}>
                      <Image
                        src={normalizeImageUrl(contentPage.image)}
                        alt={contentPage.title}
                        width={600}
                        height={400}
                        className={styles.textImage}
                        style={{ objectFit: 'cover', borderRadius: '8px' }}
                      />
                    </div>
                  )}
                  {contentPage.description && (
                    <div 
                      className={styles.textContent} 
                      dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(contentPage.description) }} 
                    />
                  )}
                  {/* Выбранный каталог или галерея для страницы типа 'text' */}
                  {contentPage.selected_catalog_page?.catalog_items && contentPage.selected_catalog_page.catalog_items.length > 0 && (
                    renderCatalogItems(contentPage.selected_catalog_page.catalog_items)
                  )}
                  {contentPage.selected_gallery_page?.gallery_images && contentPage.selected_gallery_page.gallery_images.length > 0 && (
                    <Gallery
                      images={contentPage.selected_gallery_page.gallery_images}
                      displayType={contentPage.selected_gallery_page.gallery_display_type || 'grid'}
                      enableFullscreen={contentPage.selected_gallery_page.gallery_enable_fullscreen !== false}
                    />
                  )}
                  {/* Обычный каталог и галерея, если не выбраны специальные страницы */}
                  {!contentPage.selected_catalog_page && contentPage.catalog_items && contentPage.catalog_items.length > 0 && (
                    renderCatalogItems(contentPage.catalog_items)
                  )}
                  {!contentPage.selected_gallery_page && contentPage.gallery_images && contentPage.gallery_images.length > 0 && (
                    <Gallery
                      images={contentPage.gallery_images}
                      displayType={contentPage.gallery_display_type || 'grid'}
                      enableFullscreen={contentPage.gallery_enable_fullscreen !== false}
                    />
                  )}
                </>
              )}

              {/* FAQ для страниц типа 'faq' */}
              {pageType === 'faq' && (
                <>
                  {contentPage.description && (
                    <div
                      className={styles.description}
                      dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(contentPage.description) }}
                    />
                  )}
                  {contentPage.faq_items && Array.isArray(contentPage.faq_items) && contentPage.faq_items.length > 0 ? (
                    <FAQ
                      items={contentPage.faq_items}
                      icon={contentPage.faq_icon}
                      iconPosition={contentPage.faq_icon_position || 'left'}
                      backgroundColor={contentPage.faq_background_color || '#FFFFFF'}
                      backgroundImage={contentPage.faq_background_image}
                      animation={contentPage.faq_animation || 'slide'}
                    />
                  ) : (
                    process.env.NODE_ENV === 'development' && (
                      <div style={{ padding: '1rem', background: '#fff3cd', border: '1px solid #ffc107', borderRadius: '4px', margin: '1rem 0' }}>
                        <strong>Отладка FAQ:</strong> FAQ блок найден (page_type: {pageType}), но faq_items: {JSON.stringify({
                          exists: !!contentPage.faq_items,
                          isArray: Array.isArray(contentPage.faq_items),
                          length: contentPage.faq_items?.length || 0,
                          items: contentPage.faq_items
                        })}. 
                        Проверьте, что в админке добавлены элементы FAQ для этой страницы и они активны.
                      </div>
                    )
                  )}
                </>
              )}

              {/* Каталог и галерея могут быть на любой странице (если не используется selected_catalog_page/selected_gallery_page) */}
              {pageType !== 'text' && contentPage.catalog_items && contentPage.catalog_items.length > 0 && (
                renderCatalogItems(contentPage.catalog_items)
              )}

              {pageType !== 'text' && contentPage.gallery_images && contentPage.gallery_images.length > 0 && (
                <Gallery
                  images={contentPage.gallery_images}
                  displayType={contentPage.gallery_display_type || 'grid'}
                  enableFullscreen={contentPage.gallery_enable_fullscreen !== false}
                />
              )}

              {/* Филиалы для отображения на странице */}
              {contentPage.display_branches && contentPage.display_branches.length > 0 && (
                <BranchesList branches={contentPage.display_branches} />
              )}
            </div>
          )
        })}
        {renderBookingForm()}
      </div>
    )
  }

  if (page.page_type === 'faq') {
    return (
      <>
        <div className={styles.container}>
          {page.show_title && page.title && (
            <h1 className={styles.title}>{page.title}</h1>
          )}
          {page.description && (
            <div
              className={styles.description}
              dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(page.description) }}
            />
          )}
          {page.faq_items && page.faq_items.length > 0 && (
            <FAQ
              items={page.faq_items}
              icon={page.faq_icon}
              iconPosition={page.faq_icon_position || 'left'}
              backgroundColor={page.faq_background_color || '#FFFFFF'}
              backgroundImage={page.faq_background_image}
              animation={page.faq_animation || 'slide'}
            />
          )}
        </div>
        {renderCatalogItems(page.catalog_items || [])}
        {page.gallery_images && page.gallery_images.length > 0 && (
          <Gallery
            images={page.gallery_images}
            displayType={page.gallery_display_type || 'grid'}
            enableFullscreen={page.gallery_enable_fullscreen !== false}
          />
        )}
        {renderBranches()}
        {renderBookingForm()}
      </>
    )
  }

  if (page.page_type === 'text') {
    const getImageSize = (size?: string) => {
      switch (size) {
        case 'small': return { width: 200, height: 150 }
        case 'medium': return { width: 400, height: 300 }
        case 'large': return { width: 600, height: 450 }
        case 'full': return { width: 1200, height: 600 }
        default: return { width: 400, height: 300 }
      }
    }

    const getImageAlignClass = (align?: string) => {
      switch (align) {
        case 'left': return styles.imageLeft
        case 'right': return styles.imageRight
        case 'center': return styles.imageCenter
        case 'full': return styles.imageFull
        default: return styles.imageCenter
      }
    }

    const imageSize = getImageSize(page.image_size)
    const imageAlignClass = page.image ? getImageAlignClass(page.image_align) : ''

    return (
      <div className={styles.container}>
        {page.image && (
          <div className={`${styles.textImageWrapper} ${imageAlignClass}`}>
            <Image
              src={normalizeImageUrl(page.image)}
              alt={page.title}
              width={imageSize.width}
              height={imageSize.height}
              className={styles.textImage}
              style={{
                maxWidth: page.image_size === 'full' ? '100%' : `${imageSize.width}px`,
                width: page.image_size === 'full' ? '100%' : 'auto',
                height: 'auto'
              }}
            />
          </div>
        )}
        {page.description && (
          <div
            className={styles.textContent}
            dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(page.description) }}
          />
        )}
        {/* Выбранный каталог для страницы типа 'text' */}
        {page.selected_catalog_page?.catalog_items && page.selected_catalog_page.catalog_items.length > 0 && (
          renderCatalogItems(page.selected_catalog_page.catalog_items)
        )}
        
        {/* Выбранная галерея для страницы типа 'text' */}
        {page.selected_gallery_page?.gallery_images && page.selected_gallery_page.gallery_images.length > 0 && (
          <Gallery
            images={page.selected_gallery_page.gallery_images}
            displayType={page.selected_gallery_page.gallery_display_type || 'grid'}
            enableFullscreen={page.selected_gallery_page.gallery_enable_fullscreen !== false}
          />
        )}
        
        {/* Обычный каталог и галерея (если не выбраны специальные страницы) */}
        {!page.selected_catalog_page && renderCatalog()}
        {!page.selected_gallery_page && page.gallery_images && page.gallery_images.length > 0 ? (
          <Gallery
            images={page.gallery_images}
            displayType={page.gallery_display_type || 'grid'}
            enableFullscreen={page.gallery_enable_fullscreen !== false}
          />
        ) : null}
        {renderBranches()}
        {renderBookingForm()}
      </div>
    )
  }

  return null
}
