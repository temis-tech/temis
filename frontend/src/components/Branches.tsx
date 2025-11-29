import { Branch } from '@/types';
import { normalizeImageUrl } from '@/lib/utils';
import styles from './Branches.module.css';
import Image from 'next/image';

interface BranchesProps {
  branches: Branch[];
}

export default function Branches({ branches }: BranchesProps) {
  return (
    <section className={styles.branches} id="branches">
      <div className={styles.container}>
        <h2 className={styles.title}>2 филиала с опытными логопедами</h2>
        <div className={styles.grid}>
          {branches.map((branch) => (
            <div key={branch.id} className={styles.card}>
              {branch.image && (
                <div className={styles.imageWrapper}>
                  <Image
                    src={normalizeImageUrl(branch.image)}
                    alt={branch.name}
                    width={400}
                    height={300}
                    className={styles.image}
                  />
                </div>
              )}
              <h3 className={styles.cardTitle}>{branch.name}</h3>
              <p className={styles.address}>{branch.address}</p>
              <p className={styles.metro}>🚇 {branch.metro}</p>
              <p className={styles.phone}>{branch.phone}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

