import { contentApi } from '@/lib/api';
import Header from '@/components/Header';
import Hero from '@/components/Hero';
import Services from '@/components/Services';
import Branches from '@/components/Branches';
import Reviews from '@/components/Reviews';
import Promotions from '@/components/Promotions';
import Footer from '@/components/Footer';

export default async function Home() {
  const [services, branches, reviews, promotions] = await Promise.all([
    contentApi.getServices().then(res => res.data.results || res.data).catch(err => {
      console.error('Error fetching services:', err);
      return [];
    }),
    contentApi.getBranches().then(res => res.data.results || res.data).catch(err => {
      console.error('Error fetching branches:', err);
      return [];
    }),
    contentApi.getReviews().then(res => res.data.results || res.data).catch(err => {
      console.error('Error fetching reviews:', err);
      return [];
    }),
    contentApi.getPromotions().then(res => res.data.results || res.data).catch(err => {
      console.error('Error fetching promotions:', err);
      return [];
    }),
  ]);

  return (
    <>
      <Header />
      <main style={{ minHeight: '100vh' }}>
        <Hero />
        <Services services={services} />
        <Branches branches={branches} />
        <Reviews reviews={reviews} />
        {promotions && promotions.length > 0 && <Promotions promotions={promotions} />}
      </main>
      <Footer />
    </>
  );
}

