import { contentApi } from '@/lib/api';
import Header from '@/components/Header';
import Reviews from '@/components/Reviews';
import Footer from '@/components/Footer';

export default async function ReviewsPage() {
  const reviews = await contentApi.getReviews().then(res => res.data.results || res.data);

  return (
    <>
      <Header />
      <main>
        <Reviews reviews={reviews} />
      </main>
      <Footer />
    </>
  );
}

