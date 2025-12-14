'use client'

import { useEffect } from 'react'
import { CatalogItem } from '@/types'

interface GalleryDebugProps {
  item: CatalogItem
}

export default function GalleryDebug({ item }: GalleryDebugProps) {
  useEffect(() => {
    console.log('🔍 [CLIENT] Catalog item full data:', {
      title: item.title,
      has_own_page: item.has_own_page,
      has_gallery_page: !!item.gallery_page,
      gallery_page: item.gallery_page ? {
        id: item.gallery_page.id,
        title: item.gallery_page.title,
        is_active: item.gallery_page.is_active,
        gallery_images_count: item.gallery_page.gallery_images?.length || 0,
        gallery_images: item.gallery_page.gallery_images?.map(img => ({
          id: img.id,
          content_type: img.content_type,
          has_image: !!img.image,
          has_video_url: !!img.video_url,
          has_video_file: !!img.video_file,
          has_video_embed_url: !!img.video_embed_url
        })),
        gallery_display_type: item.gallery_page.gallery_display_type,
        gallery_enable_fullscreen: item.gallery_page.gallery_enable_fullscreen
      } : null,
      full_item: item
    });
  }, [item]);

  return null;
}
