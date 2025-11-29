import { quizzesApi } from '@/lib/api';
import Quiz from '@/components/Quiz';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default async function QuizPage({ 
  params,
  searchParams 
}: { 
  params: { slug: string };
  searchParams: { service_id?: string; form_id?: string };
}) {
  let quiz;
  try {
    const response = await quizzesApi.getQuizBySlug(params.slug);
    quiz = response.data;
  } catch (error: any) {
    return (
      <>
        <Header />
        <main style={{ 
          minHeight: '80vh', 
          padding: '2rem'
        }}>
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <h1>Квиз не найден</h1>
            <p>Квиз с указанным адресом не существует или был удален.</p>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main style={{ 
        minHeight: '80vh', 
        padding: '2rem'
      }}>
        <Quiz 
          quiz={quiz} 
          serviceId={searchParams.service_id ? parseInt(searchParams.service_id) : undefined}
          formId={searchParams.form_id ? parseInt(searchParams.form_id) : undefined}
        />
      </main>
      <Footer />
    </>
  );
}

