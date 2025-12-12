import { redirect } from 'next/navigation';

/**
 * Редирект со старой страницы /privacy на новую /policies
 * Пытаемся найти политику с slug 'privacy' или перенаправляем на список
 */
export default async function PrivacyPage() {
  // Перенаправляем на новую страницу политик
  redirect('/policies');
}

