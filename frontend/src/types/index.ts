// Старые типы удалены - используем универсальную систему ContentPage

export interface Contact {
  id: number;
  phone: string;
  phone_secondary?: string;
  inn?: string;
  email?: string;
}

export interface MenuItem {
  id: number;
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
  description: string;
  card_image?: string;  // Изображение для карточки (превью)
  image?: string;  // Изображение для страницы
  image_align?: 'left' | 'right' | 'center' | 'full';
  image_size?: 'small' | 'medium' | 'large' | 'full';
  has_own_page?: boolean;
  slug?: string;
  url?: string | null;
  button_type: 'booking' | 'quiz' | 'external' | 'none';
  button_text: string;
  button_booking_form_id?: number;
  button_quiz_slug?: string;
  button_url?: string;
  order: number;
}

export interface GalleryImage {
  id: number;
  image: string;
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

export interface ContentPage {
  id: number;
  title: string;
  slug: string;
  page_type: 'catalog' | 'gallery' | 'home' | 'text';
  description: string;
  image?: string;
  image_align?: 'left' | 'right' | 'center' | 'full';
  image_size?: 'small' | 'medium' | 'large' | 'full';
  show_title?: boolean;
  is_active: boolean;
  catalog_items?: CatalogItem[];
  gallery_images?: GalleryImage[];
  home_blocks?: HomePageBlock[];
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

