// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { afterEach, describe, expect, it } from "vitest";
import { I18nProvider } from "../i18n";
import { skeletonFor } from "../lib/ratingPrompts";
import { NotePrompts } from "./NotePrompts";

/** Kontrolirano polje kakvo komponenta dobiva u DetailSheetu / EveningSessionSheetu. */
function Harness({ context }: { context: "pairing" | "cigar" | "drink" }) {
  const [note, setNote] = useState("");
  return (
    <I18nProvider>
      <NotePrompts context={context} value={note} onChange={setNote} showRatingScale />
      <textarea data-testid="note" value={note} onChange={() => {}} />
    </I18nProvider>
  );
}

const note = () => (screen.getByTestId("note") as HTMLTextAreaElement).value;

afterEach(cleanup);

describe("NotePrompts", () => {
  it("chip pitanja umeće starter, a ponovni klik ga ne duplicira", () => {
    render(<Harness context="pairing" />);
    fireEvent.click(screen.getByRole("button", { name: "Most" }));
    expect(note()).toBe("Most: ");
    fireEvent.click(screen.getByRole("button", { name: "Trećina" }));
    // prazan starter gubi svoj razmak na kraju kad iza njega dođe nova linija
    expect(note()).toBe("Most:\nTrećina: ");
    fireEvent.click(screen.getByRole("button", { name: "Most" }));
    expect(note()).toBe("Most:\nTrećina: ");
  });

  it("prijedlog puni liniju svog pitanja, a drugi se dodaje zarezom", () => {
    render(<Harness context="pairing" />);
    fireEvent.click(screen.getByRole("button", { name: "kakao" }));
    expect(note()).toBe("Most: kakao");
    fireEvent.click(screen.getByRole("button", { name: "orah" }));
    expect(note()).toBe("Most: kakao, orah");
    fireEvent.click(screen.getByRole("button", { name: "kakao" }));
    expect(note()).toBe("Most: kakao, orah");
  });

  it("„Umetni predložak” puni prazno polje i potom se zaključava", () => {
    render(<Harness context="cigar" />);
    const btn = screen.getByRole("button", { name: "Umetni predložak" });
    expect((btn as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(btn);
    expect(note()).toBe(skeletonFor("cigar", "hr"));
    const after = screen.getByRole("button", { name: "Umetni predložak" });
    expect((after as HTMLButtonElement).disabled).toBe(true);
  });

  it("promjena konteksta prebacuje aktivno pitanje na prvo iz tog konteksta", () => {
    const { rerender } = render(<Harness context="drink" />);
    // piće otvara „Tijelo / završetak”, ne „Most”
    expect(screen.getByRole("button", { name: "lagano, kratko" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "kakao" })).toBeNull();
    rerender(<Harness context="cigar" />);
    expect(screen.getByRole("button", { name: "prelak" })).toBeTruthy();
  });

  it("ljestvica ocjene se ispisuje uz prijedloge", () => {
    render(<Harness context="pairing" />);
    expect(screen.getByText(/1–3 ne radi · 4–5 prolazno/)).toBeTruthy();
  });
});
