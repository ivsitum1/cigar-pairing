import { useEffect, useRef, useState } from "react";

// Pozadinska glazba — playlist na jednom gumbu. Klik cikliše:
//   isključeno → track 1 → track 2 → … → isključeno.
// Izbor se pamti; ako je zadnji put svirala, pokušamo nastaviti na prvu
// korisničku gestu (preglednici blokiraju autoplay bez interakcije).
const BASE = import.meta.env.BASE_URL;
const TRACKS: { src: string; title: string }[] = [
  { src: `${BASE}music/night-in-venice.mp3`, title: "Night in Venice" },
];
const STORAGE_KEY = "cnr.music";
const VOLUME = 0.32;

export function MusicToggle() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [idx, setIdx] = useState(-1); // -1 = isključeno

  // jednom napravi <audio> element (izvan React stabla, da preživi rerender)
  if (audioRef.current === null && typeof Audio !== "undefined") {
    const el = new Audio();
    el.loop = true;
    el.volume = VOLUME;
    el.preload = "none";
    audioRef.current = el;
  }

  const playIndex = (i: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.src = TRACKS[i].src;
    audio.play().then(
      () => {
        setIdx(i);
        localStorage.setItem(STORAGE_KEY, String(i));
      },
      () => {},
    );
  };

  const stop = () => {
    audioRef.current?.pause();
    setIdx(-1);
    localStorage.setItem(STORAGE_KEY, "off");
  };

  // ako je zadnji put svirala neka pjesma, pokušaj nastaviti — ako preglednik
  // blokira autoplay, čekaj prvu gestu pa tek onda kreni
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    const i = saved != null && saved !== "off" ? Number(saved) : -1;
    if (!(i >= 0 && i < TRACKS.length)) return;
    const audio = audioRef.current;
    if (!audio) return;
    audio.src = TRACKS[i].src;

    let cleanup = () => {};
    const start = () => audio.play().then(() => setIdx(i), () => {});
    audio.play().then(
      () => setIdx(i),
      () => {
        const resume = () => {
          start();
          cleanup();
        };
        window.addEventListener("pointerdown", resume, { once: true });
        window.addEventListener("keydown", resume, { once: true });
        cleanup = () => {
          window.removeEventListener("pointerdown", resume);
          window.removeEventListener("keydown", resume);
        };
      },
    );
    return () => cleanup();
  }, []);

  const cycle = () => {
    const next = idx + 1;
    if (next >= TRACKS.length) stop();
    else playIndex(next);
  };

  const on = idx >= 0;
  const hasNext = on && idx < TRACKS.length - 1;
  const title = on
    ? `Glazba: ${TRACKS[idx].title} — klikni za ${hasNext ? "sljedeću podlogu" : "isključivanje"}`
    : "Glazba isključena — klikni za uključivanje";

  return (
    <button
      onClick={cycle}
      className="flex h-8 w-8 items-center justify-center rounded-full border border-zlato/40 text-zlato hover:bg-zlato/10"
      aria-label={on ? "Promijeni ili isključi glazbu" : "Uključi glazbu"}
      aria-pressed={on}
      title={title}
    >
      {/* nota = uključi; prekrižena nota = isključeno/promjena */}
      <span className="relative inline-flex text-base leading-none">
        ♪
        {on && (
          <span
            aria-hidden
            className="pointer-events-none absolute left-1/2 top-1/2 h-[1.5px] w-[130%] -translate-x-1/2 -translate-y-1/2 rotate-45 rounded-full bg-current"
          />
        )}
      </span>
    </button>
  );
}
