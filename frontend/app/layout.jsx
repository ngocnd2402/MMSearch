import { Open_Sans } from 'next/font/google'
import "../styles/index.css"

const openSans = Open_Sans({ subsets: ['latin'] })

export const metadata = {
  title: 'MMSearch',
  description: 'Video Browser website',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={openSans.className}>
        {children}
      </body>
    </html>
  )
}