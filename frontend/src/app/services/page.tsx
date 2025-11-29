import { contentApi } from '@/lib/api';
import Header from '@/components/Header';
import Services from '@/components/Services';
import Footer from '@/components/Footer';

export default async function ServicesPage() {
  const services = await contentApi.getServices().then(res => res.data.results || res.data);

  return (
    <>
      <Header />
      <main>
        <Services services={services} />
      </main>
      <Footer />
    </>
  );
}

