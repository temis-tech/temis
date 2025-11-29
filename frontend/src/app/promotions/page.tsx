import { contentApi } from '@/lib/api';
import Header from '@/components/Header';
import Promotions from '@/components/Promotions';
import Footer from '@/components/Footer';

export default async function PromotionsPage() {
  const promotions = await contentApi.getPromotions().then(res => res.data.results || res.data);

  return (
    <>
      <Header />
      <main>
        <Promotions promotions={promotions} />
      </main>
      <Footer />
    </>
  );
}

