// Zadnja obrana od bijelog ekrana.
//
// PWA se registrira s `registerType: "prompt"`, pa korisnik ostaje na starom
// service workeru dok sam ne osvježi. Ako u međuvremenu izađe novi deploy,
// stari hashirani chunk nestane s Pagesa i `import()` lazy stranice odbije se
// — bez granice to je prazan ekran bez izlaza. Isto vrijedi za svaku grešku u
// renderu: podaci su u localStorageu i preživljavaju, ali korisnik to ne zna.
import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  /** Poruke su dvojezične bez i18n konteksta — granica mora raditi i kad provider padne. */
  lang?: "hr" | "en";
}

interface State {
  error: Error | null;
}

const TEXT = {
  hr: {
    title: "Nešto je zapelo",
    chunk:
      "Vjerojatno je u međuvremenu izašla nova verzija. Osvježi da je dohvatiš.",
    generic: "Dogodila se neočekivana greška.",
    safe: "Tvoja kolekcija i dnevnik su spremljeni na uređaju i nisu izgubljeni.",
    reload: "Osvježi",
    home: "Natrag na početak",
  },
  en: {
    title: "Something went wrong",
    chunk: "A new version was probably released. Reload to pick it up.",
    generic: "An unexpected error occurred.",
    safe: "Your collection and journal are stored on this device and are safe.",
    reload: "Reload",
    home: "Back to start",
  },
} as const;

/** Nestali chunk nakon deploya izgleda drugačije od obične greške u renderu. */
function isStaleChunkError(error: Error): boolean {
  const msg = `${error.name} ${error.message}`;
  return (
    /ChunkLoadError|Loading chunk|Importing a module script failed|dynamically imported module|Failed to fetch/i.test(
      msg,
    )
  );
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Nema backend telemetrije — konzola je jedino mjesto gdje ovo možemo vidjeti.
    console.error("[boundary]", error, info.componentStack);
  }

  private reload = () => {
    window.location.reload();
  };

  private goHome = () => {
    window.location.hash = "#/pairing";
    window.location.reload();
  };

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;

    const t = TEXT[this.props.lang ?? "hr"];
    const stale = isStaleChunkError(error);

    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center gap-4 px-6 text-center">
        <div className="font-display text-lg uppercase tracking-[0.2em] text-zlato-2">
          {t.title}
        </div>
        <div className="band-rule w-full" />
        <p className="text-sm leading-relaxed text-papir">
          {stale ? t.chunk : t.generic}
        </p>
        <p className="text-xs leading-relaxed text-dim">{t.safe}</p>
        <div className="mt-2 flex flex-wrap items-center justify-center gap-2">
          <button
            onClick={this.reload}
            className="rounded-lg border border-zlato/40 bg-zlato/10 px-4 py-2 text-sm text-zlato-2 hover:bg-zlato/20"
          >
            {t.reload}
          </button>
          <button
            onClick={this.goHome}
            className="rounded-lg border border-dim/30 px-4 py-2 text-sm text-dim hover:text-papir"
          >
            {t.home}
          </button>
        </div>
      </div>
    );
  }
}
