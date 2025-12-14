'use client';

import { useState, useEffect } from 'react';
import { useBranch } from '@/hooks/useBranch';
import { Branch } from '@/types';
import { contentApi } from '@/lib/api';
import styles from './BranchSelector.module.css';

interface BranchSelectorProps {
  onBranchChange?: (branch: Branch | null) => void;
  showLabel?: boolean;
  className?: string;
}

export default function BranchSelector({ 
  onBranchChange, 
  showLabel = true,
  className = '' 
}: BranchSelectorProps) {
  const { selectedBranch, selectBranch, clearBranch, isLoading } = useBranch();
  const [branches, setBranches] = useState<Branch[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoadingBranches, setIsLoadingBranches] = useState(true);

  useEffect(() => {
    const loadBranches = async () => {
      try {
        setIsLoadingBranches(true);
        const response = await contentApi.getBranches();
        const branchesData = response.data.results || response.data || [];
        setBranches(Array.isArray(branchesData) ? branchesData : []);
      } catch (error: any) {
        console.error('Error loading branches:', error);
        // Устанавливаем пустой массив при ошибке, чтобы компонент не сломался
        setBranches([]);
      } finally {
        setIsLoadingBranches(false);
      }
    };

    loadBranches();
  }, []);

  const handleBranchSelect = (branch: Branch) => {
    selectBranch(branch);
    setIsOpen(false);
    if (onBranchChange) {
      onBranchChange(branch);
    }
  };

  const handleClear = () => {
    clearBranch();
    setIsOpen(false);
    if (onBranchChange) {
      onBranchChange(null);
    }
  };

  if (isLoadingBranches) {
    return (
      <div className={`${styles.container} ${className}`}>
        {showLabel && <span className={styles.label}>Загрузка филиалов...</span>}
      </div>
    );
  }

  if (branches.length === 0) {
    return null;
  }

  return (
    <div className={`${styles.container} ${className}`}>
      {showLabel && (
        <span className={styles.label}>
          {selectedBranch ? 'Выбранный филиал:' : 'Выберите филиал:'}
        </span>
      )}
      <div className={styles.selector}>
        <button
          type="button"
          className={styles.button}
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
        >
          <span className={styles.buttonText}>
            {selectedBranch ? (
              <>
                <span className={styles.branchName}>{selectedBranch.name}</span>
                {selectedBranch.metro && (
                  <span className={styles.metro}>🚇 {selectedBranch.metro}</span>
                )}
              </>
            ) : (
              'Все филиалы'
            )}
          </span>
          <span className={styles.arrow}>{isOpen ? '▲' : '▼'}</span>
        </button>

        {isOpen && (
          <>
            <div 
              className={styles.overlay}
              onClick={() => setIsOpen(false)}
            />
            <div className={styles.dropdown} role="listbox">
              <button
                type="button"
                className={`${styles.option} ${!selectedBranch ? styles.optionActive : ''}`}
                onClick={handleClear}
                role="option"
                aria-selected={!selectedBranch}
              >
                <span>Все филиалы</span>
              </button>
              {branches.map((branch) => (
                <button
                  key={branch.id}
                  type="button"
                  className={`${styles.option} ${selectedBranch?.id === branch.id ? styles.optionActive : ''}`}
                  onClick={() => handleBranchSelect(branch)}
                  role="option"
                  aria-selected={selectedBranch?.id === branch.id}
                >
                  <div className={styles.optionContent}>
                    <span className={styles.optionName}>{branch.name}</span>
                    {branch.metro && (
                      <span className={styles.optionMetro}>🚇 {branch.metro}</span>
                    )}
                    {branch.address && (
                      <span className={styles.optionAddress}>📍 {branch.address}</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
