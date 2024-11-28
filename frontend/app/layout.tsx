// Import global styles - this is essential for Tailwind CSS to work
import '@/styles/globals.css'

// Import for proper font handling in Next.js
import { Inter } from 'next/font/google'

// Initialize the Inter font with Latin character subset
// Using a subset helps with performance by loading only the characters we need
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',  // This connects to your Tailwind config's font family
})

// Enhance metadata for better SEO and browser presentation
export const metadata = {
  title: 'Billify - Cash Flow Management',
  description: 'Simplify your business cash flow management and invoice tracking',
}

// Root layout component that wraps all pages
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`min-h-screen bg-background font-sans antialiased ${inter.variable}`}>
        {/* The main element improves accessibility */}
        <main>{children}</main>
      </body>
    </html>
  )
}