'use client';

import { useState, useEffect, useCallback } from 'react';
import { Branch } from '@/types';

const BRANCH_COOKIE_NAME = 'selected_branch_id';
const COOKIE_EXPIRY_DAYS = 30;

/**
 * Хук для работы с выбором филиала и сохранением в cookies
 */
export function useBranch() {
  const [selectedBranch, setSelectedBranch] = useState<Branch | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Загружаем выбранный филиал из cookies при монтировании
  useEffect(() => {
    const loadBranchFromCookie = async () => {
      try {
        const branchId = getCookie(BRANCH_COOKIE_NAME);
        if (branchId) {
          // Загружаем данные филиала из API
          const { contentApi } = await import('@/lib/api');
          try {
            const response = await contentApi.getBranchById(parseInt(branchId, 10));
            if (response.data) {
              setSelectedBranch(response.data);
            }
          } catch (error) {
            // Если филиал не найден, удаляем cookie
            console.error('Error loading branch:', error);
            deleteCookie(BRANCH_COOKIE_NAME);
          }
        }
      } catch (error) {
        console.error('Error loading branch from cookie:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadBranchFromCookie();
  }, []);

  // Сохраняем выбранный филиал в cookies
  const selectBranch = useCallback((branch: Branch | null) => {
    setSelectedBranch(branch);
    if (branch) {
      setCookie(BRANCH_COOKIE_NAME, branch.id.toString(), COOKIE_EXPIRY_DAYS);
    } else {
      deleteCookie(BRANCH_COOKIE_NAME);
    }
  }, []);

  // Очищаем выбор филиала
  const clearBranch = useCallback(() => {
    setSelectedBranch(null);
    deleteCookie(BRANCH_COOKIE_NAME);
  }, []);

  return {
    selectedBranch,
    selectBranch,
    clearBranch,
    isLoading,
  };
}

/**
 * Утилиты для работы с cookies
 */
function setCookie(name: string, value: string, days: number) {
  if (typeof document === 'undefined') return;
  
  const date = new Date();
  date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
  const expires = `expires=${date.toUTCString()}`;
  document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
}

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  
  const nameEQ = `${name}=`;
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

function deleteCookie(name: string) {
  if (typeof document === 'undefined') return;
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}
