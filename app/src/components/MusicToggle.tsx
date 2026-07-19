import { useEffect, useRef, useState } from "react";

// Diskretan pozadinski svirač. Preglednici ne daju da zvuk krene bez
// korisničke geste, pa: klik uključi/isključi, izbor se pamti, a ako je
// zadnji put bio uključen pokušamo nastaviti na prvu interakciju.
const SRC = `${import.meta.env.BASE_URL}music/lounge.mp3`;
const STORAGE_KEY = "cnr.music";
const VOLUME = 0.32;

export function MusicToggle() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [on, setOn] = useState(false);

  // jednom napravi <audio> element (izvan React stabla, da preživi rerender)
  if (audioRef.current === null && typeof Audio !== "undefined") {
    const el = new Audio(SRC);
    el.loop = true;
    el.volume = VOLUME;
    el.preload = "none";
    audioRef.current = el;
  }

  // ako je zadnji put bio uključen, pokušaj nastaviti — ako preglednik
  // blokira autoplay, čekaj prvu gestu korisnika pa tek onda kreni
  useEffect(() => {
    if (localStorage.getItem(STORAGE_KEY) !== "on") return;
    const audio = audioRef.current;
    if (!audio) return;

    let cleanup = () => {};
    const start = () => {
      audio.play().then(
        () => setOn(true),
        () => {},
      );
    };
    audio.play().then(
      () => setOn(true),
      () => {
        // blokirano — pričekaj prvu gestu
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

  const toggle = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (on) {
      audio.pause();
      setOn(false);
      localStorage.setItem(STORAGE_KEY, "off");
    } else {
      audio.play().then(
        () => {
          setOn(true);
          localStorage.setItem(STORAGE_KEY, "on");
        },
        () => {},
      );
    }
  };

  return (
    <button
      onClick={toggle}
      className="rounded-full border border-zlato/40 px-3 py-1.5 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
      aria-label={on ? "Zaustavi glazbu" : "Pusti glazbu"}
      aria-pressed={on}
      title={on ? "Glazba: uključena" : "Glazba: isključena"}
    >
      {on ? "♪" : "♫"}
    </button>
  );
}
