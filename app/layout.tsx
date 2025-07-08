import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "Assistant UI App",
  description: "Assistant UI with Local Runtime and Agent Mode",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
