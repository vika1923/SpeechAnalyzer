import type { Metadata } from "next";
import { Lora } from "next/font/google";
import "./globals.css";

const lora = Lora({ 
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Speech Analyzer",
  description: "Analyze your speech with AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={lora.className}>
      <body className="min-h-screen bg-cream text-blackbase antialiased">
        {children}
      </body>
    </html>
  );
}
