import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Логопедический центр "Радуга слов" - СПб',
  description: 'Детский логопед в Санкт-Петербурге. Занятия с опытным логопедом, запуск речи, постановка звуков.',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://static.tildacdn.com" crossOrigin="anonymous" />
        <meta httpEquiv="Permissions-Policy" content="local-network-access=()" />
      </head>
      <body suppressHydrationWarning>{children}</body>
    </html>
  )
}

