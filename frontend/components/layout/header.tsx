import Link from 'next/link';

export function Header() {
  return (
    <header className="border-b bg-white">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Venâncio RPA</h1>
        <nav className="flex gap-4">
          <Link href="/" className="text-sm hover:underline">
            Dashboard
          </Link>
          <Link href="/reclamacoes" className="text-sm hover:underline">
            Reclamações
          </Link>
          <Link href="/benchmark" className="text-sm hover:underline">
            Benchmark
          </Link>
        </nav>
      </div>
    </header>
  );
}
