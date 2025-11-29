import { contentApi } from '@/lib/api';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ServiceDetail from '@/components/ServiceDetail';
import { notFound } from 'next/navigation';

export default async function ServicePage({ params }: { params: { slug: string } }) {
  try {
    const service = await contentApi.getServiceBySlug(params.slug).then(res => res.data);
    
    if (!service) {
      notFound();
    }

    return (
      <>
        <Header />
        <main>
          <ServiceDetail service={service} />
        </main>
        <Footer />
      </>
    );
  } catch (error) {
    notFound();
  }
}

