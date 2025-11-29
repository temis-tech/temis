export interface Branch {
  id: number;
  name: string;
  address: string;
  metro: string;
  phone: string;
  image?: string;
  order: number;
}

export interface Service {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description?: string;
  price: string;
  price_with_abonement?: string;
  duration: string;
  image?: string;
  order: number;
  show_booking_button?: boolean;
  booking_form_id?: number;
  booking_form_title?: string;
}

export interface Specialist {
  id: number;
  name: string;
  position: string;
  bio?: string;
  photo?: string;
  branch?: number;
  branch_name?: string;
  order: number;
}

export interface Review {
  id: number;
  author_name: string;
  author_photo?: string;
  text: string;
  rating: number;
  order: number;
  created_at: string;
}

export interface Promotion {
  id: number;
  title: string;
  slug: string;
  description: string;
  image?: string;
  start_date?: string;
  end_date?: string;
  order: number;
  created_at: string;
}

export interface Article {
  id: number;
  title: string;
  slug: string;
  content: string;
  short_description?: string;
  image?: string;
  views_count: number;
  created_at: string;
  updated_at: string;
}

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

