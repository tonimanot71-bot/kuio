#!/usr/bin/env python3
"""
Aggiunge al gateway un endpoint POST /api/channels/signal/start-pairing
che fa proxy al daemon signal-cli HTTP (chiamando JSON-RPC `startLink`)
e restituisce alla Stanza l'URI di pairing per disegnare il QR.

Nessuna modifica a niente di esistente: solo nuovo modulo + nuovo route +
nuova dipendenza reqwest nel Cargo.toml del gateway.

Fail-loud: se un'iniezione non trova l'aggancio, la patch lancia
RuntimeError cosi' la build esce rossa e il bug si vede subito.
"""

import re
import sys
from pathlib import Path


def fail(msg: str) -> None:
    raise RuntimeError(f"patch-signal-start-pairing: {msg}")


def patch_cargo_toml(repo: Path) -> bool:
    """Aggiunge reqwest come dipendenza al gateway se non c'e' gia'."""
    path = repo / "crates" / "zeroclaw-gateway" / "Cargo.toml"
    text = path.read_text(encoding="utf-8")
    if "reqwest" in text:
        return False  # gia' presente, niente da fare
    # Inserisco la riga reqwest subito dopo la sezione [dependencies] header.
    marker = "[dependencies]\n"
    if marker not in text:
        fail(f"Cargo.toml non ha sezione [dependencies] in {path}")
    new_dep = (
        'reqwest = { version = "0.12", default-features = false, '
        'features = ["json", "rustls-tls-webpki-roots-no-provider", "__rustls-ring"] }\n'
    )
    text = text.replace(marker, marker + new_dep, 1)
    path.write_text(text, encoding="utf-8")
    return True


def write_api_signal_module(repo: Path) -> None:
    """Crea il file crates/zeroclaw-gateway/src/api_signal.rs con l'handler."""
    path = repo / "crates" / "zeroclaw-gateway" / "src" / "api_signal.rs"
    if path.exists():
        # Idempotente: se la patch e' gia' stata applicata su un clone fresco,
        # NON e' un errore.
        return
    body = '''//! Signal channel HTTP helpers used by the Stanza UI.
//!
//! Currently exposes a single endpoint that brokers the device-pairing
//! flow between the browser and the local `signal-cli` JSON-RPC daemon.
//! The browser cannot talk to the daemon directly because of CORS, so
//! the gateway forwards the call.

use axum::{
    extract::State,
    http::{HeaderMap, StatusCode, header},
    response::{IntoResponse, Json},
};
use serde::{Deserialize, Serialize};

use crate::AppState;

#[derive(Debug, Serialize)]
pub struct StartPairingResponse {
    pub device_link_uri: String,
}

#[derive(Debug, Deserialize)]
struct JsonRpcResponse {
    #[serde(default)]
    result: Option<serde_json::Value>,
    #[serde(default)]
    error: Option<serde_json::Value>,
}

/// `POST /api/channels/signal/start-pairing` — ask the local signal-cli
/// daemon for a fresh device-link URI. Returns `{device_link_uri: "sgnl://..."}`
/// so the Stanza can render it as a QR code.
pub async fn start_pairing(
    State(state): State<AppState>,
    headers: HeaderMap,
) -> impl IntoResponse {
    if state.pairing.require_pairing() {
        let token = headers
            .get(header::AUTHORIZATION)
            .and_then(|v| v.to_str().ok())
            .and_then(|auth| auth.strip_prefix("Bearer "))
            .unwrap_or("");
        if !state.pairing.is_authenticated(token) {
            return (StatusCode::UNAUTHORIZED, "Unauthorized").into_response();
        }
    }

    let device_name = "Kuio";

    // Read the configured signal-cli daemon URL from the first enabled
    // signal channel; fall back to localhost:8686.
    let http_url = {
        let cfg = state.config.read();
        cfg.channels
            .signal
            .values()
            .find(|c| c.enabled)
            .map(|c| c.http_url.clone())
            .unwrap_or_else(|| "http://127.0.0.1:8686".to_string())
    };

    let rpc_url = format!("{}/api/v1/rpc", http_url.trim_end_matches('/'));
    let client = match reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(30))
        .build()
    {
        Ok(c) => c,
        Err(e) => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Impossibile creare il client HTTP: {e}"),
            )
                .into_response();
        }
    };

    let rpc_body = serde_json::json!({
        "jsonrpc": "2.0",
        "method": "startLink",
        "params": { "deviceName": device_name },
        "id": 1,
    });

    let resp = match client.post(&rpc_url).json(&rpc_body).send().await {
        Ok(r) => r,
        Err(e) => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                format!(
                    "Servizio Signal non raggiungibile su {http_url}. \
                     Verifica che il daemon sia attivo. ({e})"
                ),
            )
                .into_response();
        }
    };

    if !resp.status().is_success() {
        let status = resp.status();
        let text = resp.text().await.unwrap_or_default();
        return (
            StatusCode::BAD_GATEWAY,
            format!("Servizio Signal ha risposto {status}: {text}"),
        )
            .into_response();
    }

    let parsed: JsonRpcResponse = match resp.json().await {
        Ok(p) => p,
        Err(e) => {
            return (
                StatusCode::BAD_GATEWAY,
                format!("Risposta non valida dal servizio Signal: {e}"),
            )
                .into_response();
        }
    };

    if let Some(err) = parsed.error {
        return (
            StatusCode::BAD_GATEWAY,
            format!("Servizio Signal ha rifiutato la richiesta: {err}"),
        )
            .into_response();
    }

    let uri = parsed
        .result
        .as_ref()
        .and_then(|r| r.get("deviceLinkUri"))
        .and_then(|v| v.as_str())
        .map(str::to_string);

    match uri {
        Some(uri) if uri.starts_with("sgnl://") => {
            Json(StartPairingResponse {
                device_link_uri: uri,
            })
            .into_response()
        }
        _ => (
            StatusCode::BAD_GATEWAY,
            "Servizio Signal non ha restituito un codice di collegamento valido.".to_string(),
        )
            .into_response(),
    }
}
'''
    path.write_text(body, encoding="utf-8")


def patch_lib_rs(repo: Path) -> None:
    """Aggiunge `pub mod api_signal;` e il route nel router."""
    path = repo / "crates" / "zeroclaw-gateway" / "src" / "lib.rs"
    text = path.read_text(encoding="utf-8")

    # 1) Aggiungo il modulo accanto agli altri api_* moduli.
    if "pub mod api_signal;" not in text:
        anchor = "pub mod api_pairing;"
        if anchor not in text:
            fail(f"Aggancio modulo non trovato in {path} (cercato `{anchor}`)")
        text = text.replace(
            anchor,
            anchor + "\npub mod api_signal;",
            1,
        )

    # 2) Aggiungo il route subito dopo "/api/config/list".
    route_marker = '.route("/api/config/list", get(api_config::handle_list))'
    if route_marker not in text:
        fail(f"Aggancio route non trovato in {path} (cercato `{route_marker}`)")
    if "/api/channels/signal/start-pairing" not in text:
        new_route = (
            route_marker
            + '\n        .route(\n'
            + '            "/api/channels/signal/start-pairing",\n'
            + '            post(api_signal::start_pairing),\n'
            + '        )'
        )
        text = text.replace(route_marker, new_route, 1)

    path.write_text(text, encoding="utf-8")


def find_repo_root() -> Path:
    """Risale dalla cwd finche' non trova il marker crates/zeroclaw-gateway/src/lib.rs."""
    cur = Path.cwd().resolve()
    for cand in [cur, *cur.parents]:
        if (cand / "crates" / "zeroclaw-gateway" / "src" / "lib.rs").exists():
            return cand
    fail("repo Kuio non trovato (cerco crates/zeroclaw-gateway/src/lib.rs)")


def main() -> int:
    if len(sys.argv) >= 2:
        repo = Path(sys.argv[1])
    else:
        repo = find_repo_root()
    if not (repo / "crates" / "zeroclaw-gateway" / "src" / "lib.rs").exists():
        fail(f"Non sembra un repo Kuio valido: {repo}")
    added_dep = patch_cargo_toml(repo)
    write_api_signal_module(repo)
    patch_lib_rs(repo)
    msg = "patch-signal-start-pairing: OK"
    if added_dep:
        msg += " (aggiunta dipendenza reqwest al gateway)"
    print(msg)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
