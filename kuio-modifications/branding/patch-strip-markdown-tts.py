#!/usr/bin/env python3
"""
Inserisce nel motore (file crates/zeroclaw-channels/src/tts.rs) una funzione
helper `strip_markdown_for_tts()` e la chiama dentro
`TtsManager::synthesize_with_provider` per ripulire il testo dai simboli
markdown PRIMA di passarlo al provider TTS.

Motivazione: il sintetizzatore vocale Edge TTS legge LETTERALMENTE i caratteri
del testo. Se il modello AI risponde con "**ciao**" o "# Riepilogo", l'utente
sente "asterisco asterisco ciao asterisco asterisco" o "cancelletto Riepilogo".
Anche rinforzando la regola in SOUL.md/SKILL.md, il modello sbaglia a volte:
serve un filtro deterministico nel motore.

Cosa viene strippato:
- `**bold**` -> bold
- `__bold__` -> bold
- `*italic*` -> italic
- `_italic_` -> italic
- `` `code` `` -> code
- `# header` -> header
- `[testo](url)` -> testo
- `~~strike~~` -> strike
- `> quote` -> quote

Fail-loud: se le iniezioni non trovano gli agganci, la build esce rossa.
"""

import re
import sys
from pathlib import Path


def fail(msg: str) -> None:
    raise RuntimeError(f"patch-strip-markdown-tts: {msg}")


# Codice Rust della funzione helper. La aggiungiamo come modulo private
# in tts.rs. Usa la crate `regex` che e' gia' tra le dipendenze di
# zeroclaw-channels.
HELPER_BLOCK = r'''
// --- KUIO patch: strip markdown formatting before TTS (build #28+) ---
// Rimuove i simboli markdown dal testo prima di passarlo al provider TTS,
// altrimenti il sintetizzatore vocale li leggerebbe letteralmente
// ("asterisco asterisco", "cancelletto", ecc.). Soluzione deterministica
// e indipendente dal prompt.
fn strip_markdown_for_tts(input: &str) -> String {
    use std::sync::OnceLock;
    use regex::Regex;

    static RE_LINK: OnceLock<Regex> = OnceLock::new();
    static RE_IMG: OnceLock<Regex> = OnceLock::new();
    static RE_CODE_BLOCK: OnceLock<Regex> = OnceLock::new();
    static RE_INLINE_CODE: OnceLock<Regex> = OnceLock::new();
    static RE_HEADER: OnceLock<Regex> = OnceLock::new();
    static RE_QUOTE: OnceLock<Regex> = OnceLock::new();
    static RE_BULLET: OnceLock<Regex> = OnceLock::new();
    static RE_HRULE: OnceLock<Regex> = OnceLock::new();
    static RE_BOLD_STAR: OnceLock<Regex> = OnceLock::new();
    static RE_BOLD_UNDER: OnceLock<Regex> = OnceLock::new();
    static RE_STRIKE: OnceLock<Regex> = OnceLock::new();
    static RE_MULTI_NL: OnceLock<Regex> = OnceLock::new();

    let s = input;

    // 1) Blocchi di codice fenced: ```lang\n...\n``` -> contenuto, niente backtick.
    let s = RE_CODE_BLOCK
        .get_or_init(|| Regex::new(r"(?s)```[^\n]*\n(.*?)```").unwrap())
        .replace_all(s, "$1");

    // 2) Immagini ![alt](url) -> alt (eseguire PRIMA dei link per non confondersi).
    let s = RE_IMG
        .get_or_init(|| Regex::new(r"!\[([^\]]*)\]\([^)]*\)").unwrap())
        .replace_all(&s, "$1");

    // 3) Link [testo](url) -> testo.
    let s = RE_LINK
        .get_or_init(|| Regex::new(r"\[([^\]]+)\]\([^)]*\)").unwrap())
        .replace_all(&s, "$1");

    // 4) Codice inline `code` -> code.
    let s = RE_INLINE_CODE
        .get_or_init(|| Regex::new(r"`([^`]*)`").unwrap())
        .replace_all(&s, "$1");

    // 5) Strike-through ~~testo~~ -> testo.
    let s = RE_STRIKE
        .get_or_init(|| Regex::new(r"~~([^~]+)~~").unwrap())
        .replace_all(&s, "$1");

    // 6) Bold/italic con asterischi: **x**, *x* (l'ordine importa: prima i doppi).
    let s = RE_BOLD_STAR
        .get_or_init(|| Regex::new(r"\*+([^*\n]+)\*+").unwrap())
        .replace_all(&s, "$1");

    // 7) Bold/italic con underscore: __x__, _x_ (solo se preceduti/seguiti da
    //    word boundary, per non rompere snake_case in nomi propri).
    let s = RE_BOLD_UNDER
        .get_or_init(|| Regex::new(r"(?:^|\b)_+([^_\n]+)_+(?:\b|$)").unwrap())
        .replace_all(&s, "$1");

    // 8) Headers '# Titolo' -> 'Titolo' (a inizio riga).
    let s = RE_HEADER
        .get_or_init(|| Regex::new(r"(?m)^[ \t]*#{1,6}[ \t]+").unwrap())
        .replace_all(&s, "");

    // 9) Quote '> testo' -> 'testo'.
    let s = RE_QUOTE
        .get_or_init(|| Regex::new(r"(?m)^[ \t]*>[ \t]+").unwrap())
        .replace_all(&s, "");

    // 10) Bullet list: '- foo', '* foo', '+ foo' (a inizio riga) -> 'foo'.
    let s = RE_BULLET
        .get_or_init(|| Regex::new(r"(?m)^[ \t]*[-*+][ \t]+").unwrap())
        .replace_all(&s, "");

    // 11) Righe orizzontali --- *** ___ -> rimosse.
    let s = RE_HRULE
        .get_or_init(|| Regex::new(r"(?m)^[ \t]*(?:[-*_][ \t]*){3,}[ \t]*$").unwrap())
        .replace_all(&s, "");

    // 12) Comprime righe vuote multiple.
    let s = RE_MULTI_NL
        .get_or_init(|| Regex::new(r"\n{3,}").unwrap())
        .replace_all(&s, "\n\n");

    s.trim().to_string()
}
// --- /KUIO patch ---
'''


# Punto di iniezione della CHIAMATA dentro synthesize_with_provider.
# Inseriamo subito dopo i due check (empty + max_length) e prima del
# get del provider.
CALL_ANCHOR = '        let tts = self.tts_providers.get(provider_alias).ok_or_else(|| {'

CALL_INSERT = '''        // KUIO: rimuovo i caratteri markdown prima di sintetizzare a voce.
        let __kuio_tts_clean = strip_markdown_for_tts(text);
        let text = __kuio_tts_clean.as_str();

'''


def patch_tts_rs(repo: Path) -> None:
    path = repo / "crates" / "zeroclaw-channels" / "src" / "tts.rs"
    text = path.read_text(encoding="utf-8")

    # 1) Inserisco la funzione helper alla fine del file (idempotente).
    if "strip_markdown_for_tts" not in text:
        text = text.rstrip() + "\n" + HELPER_BLOCK + "\n"

    # 2) Inietto la chiamata dentro synthesize_with_provider.
    if "__kuio_tts_clean" not in text:
        if CALL_ANCHOR not in text:
            fail(
                f"Aggancio per la chiamata strip_markdown_for_tts non trovato in "
                f"{path}. Cercato: {CALL_ANCHOR!r}"
            )
        text = text.replace(CALL_ANCHOR, CALL_INSERT + CALL_ANCHOR, 1)

    path.write_text(text, encoding="utf-8")


def find_repo_root() -> Path:
    cur = Path.cwd().resolve()
    for cand in [cur, *cur.parents]:
        if (cand / "crates" / "zeroclaw-channels" / "src" / "tts.rs").exists():
            return cand
    fail("repo Kuio non trovato (cerco crates/zeroclaw-channels/src/tts.rs)")


def main() -> int:
    if len(sys.argv) >= 2:
        repo = Path(sys.argv[1])
    else:
        repo = find_repo_root()
    if not (repo / "crates" / "zeroclaw-channels" / "src" / "tts.rs").exists():
        fail(f"Non sembra un repo Kuio valido: {repo}")
    patch_tts_rs(repo)
    print("patch-strip-markdown-tts: OK (filtro markdown applicato a TtsManager::synthesize_with_provider)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
