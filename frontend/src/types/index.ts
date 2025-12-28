// Старые типы удалены - используем универсальную систему ContentPage

export interface Contact {
  id: number;
  phone: string;
  phone_secondary?: string;
  inn?: string;
  email?: string;
}

export interface Branch {
  id: number;
  name: string;
  address: string;
  metro: string;
  phone: string;
  image?: string | null;
  order: number;
  content_page?: {
    id: number;
    title: string;
    slug: string;
    url: string;
  } | null;  // Страница филиала (если есть)
}

export interface MenuItem {
  id: number;
  item_type?: 'link' | 'branch_selector';
  title?: string;
  image?: string;
  url: string;
  is_external?: boolean;
  children?: MenuItem[];
}

export interface AnswerOption {
  id: number;
  text: string;
  points: number;
  order: number;
}

export interface Question {
  id: number;
  text: string;
  question_type: 'single' | 'multiple' | 'text';
  is_required: boolean;
  order: number;
  options: AnswerOption[];
}

export interface ResultRange {
  id: number;
  min_points: number;
  max_points?: number;
  title: string;
  description: string;
  image?: string;
  order: number;
}

export interface Quiz {
  id: number;
  title: string;
  slug: string;
  description: string;
  questions: Question[];
  result_ranges: ResultRange[];
}

export interface QuizSubmission {
  id: number;
  quiz: number;
  quiz_title: string;
  total_points: number;
  result?: number;
  result_title?: string;
  user_name?: string;
  user_phone?: string;
  user_email?: string;
  answers: SubmissionAnswer[];
  created_at: string;
}

export interface SubmissionAnswer {
  id: number;
  question: number;
  question_text: string;
  selected_options: number[];
  selected_options_text: string[];
  text_answer?: string;
  points: number;
}

export interface CatalogItem {
  width?: 'narrow' | 'medium' | 'wide' | 'full';
  id: number;
  title: string;
  card_description?: string;  // Описание для карточки (превью) с форматированием
  description?: string;  // Описание для страницы элемента
  card_image?: string;  // Изображение для карточки (превью)
  image?: string;  // Изображение для страницы
  image_align?: 'left' | 'right' | 'center' | 'full';
  image_size?: 'small' | 'medium' | 'large' | 'full';
  image_position?: 'top' | 'bottom' | 'left' | 'right' | 'none';
  image_target_width?: number;
  image_target_height?: number;
  has_own_page?: boolean;
  slug?: string;
  url?: string | null;
  video_url?: string;  // URL видео (YouTube, Rutube и т.д.)
  video_width?: number;  // Ширина видео-фрейма в пикселях
  video_height?: number;  // Высота видео-фрейма в пикселях
  gallery_page?: ContentPage | null;  // Страница галереи для отображения на странице элемента
  button_type: 'booking' | 'quiz' | 'external' | 'none';
  button_text: string;
  button_booking_form_id?: number;
  button_quiz_slug?: string;
  button_url?: string;
  order: number;
}

export interface GalleryImage {
  id: number;
  content_type: 'image' | 'video';
  image?: string | null;
  video_file?: string | null;
  video_url?: string | null;
  video_embed_url?: string | null;
  description: string;
  order: number;
}

export interface HomePageBlock {
  id: number;
  content_page: number;
  title?: string;
  show_title: boolean;
  title_tag: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
  title_align: 'left' | 'center' | 'right' | 'justify';
  title_size: 'small' | 'medium' | 'large' | 'xlarge';
  title_color: string;
  title_bold: boolean;
  title_italic: boolean;
  title_custom_css?: string;
  order: number;
  is_active: boolean;
  content_page_data?: ContentPage;
}

export interface FAQItem {
  id: number;
  question: string;
  answer: string;
  order: number;
}

export interface ContentPage {
  id: number;
  title: string;
  slug: string;
  page_type: 'catalog' | 'gallery' | 'home' | 'text' | 'faq';
  description: string;
  image?: string;
  image_align?: 'left' | 'right' | 'center' | 'full';
  image_size?: 'small' | 'medium' | 'large' | 'full';
  gallery_display_type?: 'grid' | 'carousel' | 'masonry';  // Вид отображения галереи
  gallery_enable_fullscreen?: boolean;  // Открывать изображения на весь экран
  show_title?: boolean;
  show_catalog_navigator?: boolean;  // Показывать рубрикатор (навигационный список)
  is_active: boolean;
  catalog_items?: CatalogItem[];
  gallery_images?: GalleryImage[];
  home_blocks?: HomePageBlock[];
  // FAQ настройки
  faq_items?: FAQItem[];
  faq_icon?: string | null;
  faq_icon_position?: 'left' | 'right';
  faq_background_color?: string;
  faq_background_image?: string | null;
  faq_animation?: 'slide' | 'fade' | 'none';
  faq_columns?: number;
  // Филиалы
  branches?: Branch[];  // Филиалы, связанные через content_page (для страницы филиала)
  display_branches?: Branch[];  // Филиалы для отображения на странице (ManyToMany)
  // Выбранные страницы для отображения (для типа "Описание")
  selected_catalog_page?: {
    id: number;
    title: string;
    slug: string;
    catalog_items?: CatalogItem[];
  } | null;
  selected_gallery_page?: {
    id: number;
    title: string;
    slug: string;
    gallery_images?: GalleryImage[];
    gallery_display_type?: 'grid' | 'carousel' | 'masonry';
    gallery_enable_fullscreen?: boolean;
  } | null;
  // Услуги для отображения на странице
  display_services?: Service[];
  services_show_title?: boolean;
  services_title?: string;
  services_card_style?: 'standard' | 'compact' | 'detailed' | 'minimal';
  services_card_standard_width?: number;
  services_card_standard_height?: number;
  services_card_compact_width?: number;
  services_card_compact_height?: number;
  services_card_detailed_width?: number;
  services_card_detailed_height?: number;
  services_card_minimal_width?: number;
  services_card_minimal_height?: number;
}

export interface WelcomeBannerCard {
  id: number;
  title: string;
  description?: string;
  image?: string;
  button_type: 'none' | 'link' | 'booking' | 'quiz';
  button_text?: string;
  button_url?: string;
  button_booking_form_id?: number;
  button_quiz_slug?: string;
  order: number;
  is_active?: boolean;
}

export interface WelcomeBanner {
  id: number;
  title?: string;
  subtitle?: string;
  background_color: string;
  text_color: string;
  content_width: 'narrow' | 'medium' | 'wide' | 'full';
  display_type: 'section' | 'modal';
  blur_background: number;
  start_at?: string | null;
  end_at?: string | null;
  cards: WelcomeBannerCard[];
}

export interface ServiceBranch {
  id: number;
  branch?: Branch | number;  // Может быть объектом Branch или ID
  branch_id?: number;
  branch_name?: string;
  price?: number | null;
  price_with_abonement?: number | null;
  final_price?: number | null;
  final_price_with_abonement?: number | null;
  is_available: boolean;
  order: number;
  crm_item_id?: string | null;
  crm_item_data?: any;
}

export interface Service {
  id: number;
  title: string;
  slug: string;
  description: string;
  card_short_description?: string;
  price: number;
  price_is_from?: boolean;  // Показывать "От" перед ценой
  price_with_abonement?: number | null;
  price_with_abonement_is_from?: boolean;  // Показывать "От" перед ценой по абонементу
  image?: string | null;
  image_align?: 'left' | 'right' | 'center' | 'full';
  image_size?: 'small' | 'medium' | 'large' | 'full';
  has_own_page?: boolean;
  url?: string | null;
  order: number;
  show_booking_button?: boolean;
  booking_form_id?: number | null;
  booking_form_title?: string | null;
  service_branches?: ServiceBranch[];
  price_range?: number | { min: number; max: number } | null;
  price_with_abonement_range?: number | { min: number; max: number } | null;
}

