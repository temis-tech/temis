import { contentApi } from '@/lib/api';
import Header from '@/components/Header';
import Branches from '@/components/Branches';
import Footer from '@/components/Footer';

export default async function BranchesPage() {
  const branches = await contentApi.getBranches().then(res => res.data.results || res.data);

  return (
    <>
      <Header />
      <main>
        <Branches branches={branches} />
      </main>
      <Footer />
    </>
  );
}

