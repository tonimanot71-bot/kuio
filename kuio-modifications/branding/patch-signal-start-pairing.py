#!/usr/bin/env python3
"""
Aggiunge al gateway DUE endpoint per il flusso completo di pairing Signal:

  POST /api/channels/signal/start-pairing
       -> chiama JSON-RPC `startLink` sul daemon signal-cli, ottiene l'URI
          di pairing, genera un pairing_id (UUID), e lancia in background
          un task tokio che chiama `finishLink` con quell'URI. Il task
          aspetta fino a 120s la conferma dal telefono primario; al
          ritorno aggiorna lo stato interno e (in caso di successo) salva
          il numero account associato.
       Risposta: {"device_link_uri": "sgnl://...", "pairing_id": "<uuid>"}.

  GET  /api/channels/signal/pairing-status?id=<pairing_id>
       -> ritorna lo stato corrente del pairing:
          {"status": "pending|linked|expired|error",
           "account": "<numero>" (solo se linked),
           "error": "..."        (solo se error)}

Il front-end (Stanza) polla il secondo endpoint ogni 3s invece di
pollare /api/config (che non cambia quando il pairing chiude perche'
il numero resta lo stesso).

Stato tenuto in memoria del processo (HashMap dietro RwLock). Pulito
automaticamente dopo 600s per ogni entry per evitare leak.

NESSUNA modifica al file config sul disco: la Stanza, quando vede
"linked", fa le sue PUT /api/config/prop per persistere l'account (stesso
pattern di Telegram/Email).

Fail-loud: se un'iniezione non trova il suo aggancio, la patch lancia
RuntimeError e la build esce rossa.
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


API_SIGNAL_RS_BODY = r'''//! Signal channel HTTP helpers used by the Stanza UI.
//!
//! Esposto al browser:
//!  - POST /api/channels/signal/start-pairing
//!  - GET  /api/channels/signal/pairing-status?id=<uuid>
//!
//! Il browser non puo' parlare direttamente al daemon signal-cli
//! (no CORS), quindi il gateway fa da proxy per la prima chiamata
//! (startLink) e tiene una macchina a stati in memoria che orchestra
//! la seconda chiamata (finishLink, bloccante fino a 120s) in un
//! task tokio in background. Il front-end polla pairing-status per
//! sapere quando il telefono primario ha confermato.

use axum::{
    extract::{Query, State},
    http::{HeaderMap, StatusCode, header},
    response::{IntoResponse, Json},
};
use parking_lot::RwLock;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::OnceLock;
use std::time::Duration;
use uuid::Uuid;

use crate::AppState;

/// Quanto teniamo in memoria una entry del pairing dopo l'ultimo update.
const PAIRING_TTL_SECS: u64 = 600;
/// Timeout del finishLink JSON-RPC. signal-cli aspetta ~120s la conferma
/// dal device primario; lasciamo qualche secondo di margine sul client HTTP.
const FINISH_LINK_TIMEOUT_SECS: u64 = 140;

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "lowercase")]
enum PairingStatus {
    Pending,
    Linked,
    Expired,
    Error,
}

#[derive(Debug, Clone, Serialize)]
struct PairingState {
    status: PairingStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    account: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<String>,
    /// epoch seconds dell'ultimo update di questa entry.
    updated_at: u64,
}

fn pairing_store() -> &'static RwLock<HashMap<String, PairingState>> {
    static STORE: OnceLock<RwLock<HashMap<String, PairingState>>> = OnceLock::new();
    STORE.get_or_init(|| RwLock::new(HashMap::new()))
}

fn now_secs() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

/// Rimuove dalle entry quelle ferme da piu' di PAIRING_TTL_SECS.
fn gc_expired_entries() {
    let now = now_secs();
    let mut store = pairing_store().write();
    store.retain(|_, st| now.saturating_sub(st.updated_at) <= PAIRING_TTL_SECS);
}

fn set_state(id: &str, status: PairingStatus, account: Option<String>, error: Option<String>) {
    let mut store = pairing_store().write();
    store.insert(
        id.to_string(),
        PairingState {
            status,
            account,
            error,
            updated_at: now_secs(),
        },
    );
}

fn get_state(id: &str) -> Option<PairingState> {
    pairing_store().read().get(id).cloned()
}

fn require_auth_inline(state: &AppState, headers: &HeaderMap) -> Result<(), StatusCode> {
    if !state.pairing.require_pairing() {
        return Ok(());
    }
    let token = headers
        .get(header::AUTHORIZATION)
        .and_then(|v| v.to_str().ok())
        .and_then(|auth| auth.strip_prefix("Bearer "))
        .unwrap_or("");
    if state.pairing.is_authenticated(token) {
        Ok(())
    } else {
        Err(StatusCode::UNAUTHORIZED)
    }
}

fn read_signal_http_url(state: &AppState) -> String {
    let cfg = state.config.read();
    cfg.channels
        .signal
        .values()
        .find(|c| c.enabled)
        .map(|c| c.http_url.clone())
        .unwrap_or_else(|| "http://127.0.0.1:8686".to_string())
}

#[derive(Debug, Deserialize)]
struct JsonRpcResponse {
    #[serde(default)]
    result: Option<serde_json::Value>,
    #[serde(default)]
    error: Option<serde_json::Value>,
}

#[derive(Debug, Serialize)]
pub struct StartPairingResponse {
    pub device_link_uri: String,
    pub pairing_id: String,
}

/// `POST /api/channels/signal/start-pairing`
///
/// Step 1: chiama `startLink` per ottenere l'URI da disegnare come QR.
/// Step 2: spawna in background un task che chiama `finishLink` per
/// chiudere il pairing quando il telefono primario conferma.
pub async fn start_pairing(
    State(state): State<AppState>,
    headers: HeaderMap,
) -> impl IntoResponse {
    if let Err(code) = require_auth_inline(&state, &headers) {
        return (code, "Unauthorized").into_response();
    }

    gc_expired_entries();

    let device_name = "Kuio";
    let http_url = read_signal_http_url(&state);
    let rpc_url = format!("{}/api/v1/rpc", http_url.trim_end_matches('/'));

    let start_client = match reqwest::Client::builder()
        .timeout(Duration::from_secs(30))
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

    let start_body = serde_json::json!({
        "jsonrpc": "2.0",
        "method": "startLink",
        "params": { "deviceName": device_name },
        "id": 1,
    });

    let resp = match start_client.post(&rpc_url).json(&start_body).send().await {
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

    let uri = match uri {
        Some(u) if u.starts_with("sgnl://") => u,
        _ => {
            return (
                StatusCode::BAD_GATEWAY,
                "Servizio Signal non ha restituito un codice di collegamento valido.".to_string(),
            )
                .into_response();
        }
    };

    // Genero un pairing_id e marco lo stato come "pending".
    let pairing_id = Uuid::new_v4().to_string();
    set_state(&pairing_id, PairingStatus::Pending, None, None);

    // Lancio il task in background che chiamera' finishLink.
    let pairing_id_for_task = pairing_id.clone();
    let uri_for_task = uri.clone();
    let rpc_url_for_task = rpc_url.clone();
    let device_name_for_task = device_name.to_string();
    tokio::spawn(async move {
        run_finish_link(
            pairing_id_for_task,
            rpc_url_for_task,
            uri_for_task,
            device_name_for_task,
        )
        .await;
    });

    Json(StartPairingResponse {
        device_link_uri: uri,
        pairing_id,
    })
    .into_response()
}

/// Task in background che chiama `finishLink` su signal-cli e aggiorna
/// lo stato del pairing al ritorno.
async fn run_finish_link(
    pairing_id: String,
    rpc_url: String,
    device_link_uri: String,
    device_name: String,
) {
    let client = match reqwest::Client::builder()
        .timeout(Duration::from_secs(FINISH_LINK_TIMEOUT_SECS))
        .build()
    {
        Ok(c) => c,
        Err(e) => {
            set_state(
                &pairing_id,
                PairingStatus::Error,
                None,
                Some(format!("client HTTP non creato: {e}")),
            );
            return;
        }
    };

    let finish_body = serde_json::json!({
        "jsonrpc": "2.0",
        "method": "finishLink",
        "params": {
            "deviceLinkUri": device_link_uri,
            "deviceName": device_name,
        },
        "id": 2,
    });

    let resp = match client.post(&rpc_url).json(&finish_body).send().await {
        Ok(r) => r,
        Err(e) => {
            // Distinguo timeout da errore di connessione.
            let is_timeout = e.is_timeout();
            let (status, msg) = if is_timeout {
                (
                    PairingStatus::Expired,
                    "Tempo scaduto. Il QR non e' stato confermato in tempo.".to_string(),
                )
            } else {
                (
                    PairingStatus::Error,
                    format!("Servizio Signal non raggiungibile: {e}"),
                )
            };
            set_state(&pairing_id, status, None, Some(msg));
            return;
        }
    };

    if !resp.status().is_success() {
        let status_code = resp.status();
        let text = resp.text().await.unwrap_or_default();
        set_state(
            &pairing_id,
            PairingStatus::Error,
            None,
            Some(format!("Servizio Signal ha risposto {status_code}: {text}")),
        );
        return;
    }

    let parsed: JsonRpcResponse = match resp.json().await {
        Ok(p) => p,
        Err(e) => {
            set_state(
                &pairing_id,
                PairingStatus::Error,
                None,
                Some(format!("Risposta finishLink non valida: {e}")),
            );
            return;
        }
    };

    if let Some(err) = parsed.error {
        // Cerco un eventuale messaggio di errore strutturato.
        let msg = err
            .get("message")
            .and_then(|m| m.as_str())
            .map(str::to_string)
            .unwrap_or_else(|| err.to_string());
        // Heuristica: se contiene "timeout" o "expired" lo classifico come expired.
        let status = if msg.to_lowercase().contains("timeout")
            || msg.to_lowercase().contains("expired")
        {
            PairingStatus::Expired
        } else {
            PairingStatus::Error
        };
        set_state(&pairing_id, status, None, Some(msg));
        return;
    }

    // finishLink di signal-cli ritorna il numero account collegato sotto
    // result.number (oppure direttamente come stringa, dipende dalla versione).
    let account = parsed
        .result
        .as_ref()
        .and_then(|r| {
            r.get("number")
                .and_then(|v| v.as_str())
                .map(str::to_string)
                .or_else(|| {
                    r.as_str().map(str::to_string)
                })
                .or_else(|| {
                    r.get("account")
                        .and_then(|v| v.as_str())
                        .map(str::to_string)
                })
        });

    set_state(&pairing_id, PairingStatus::Linked, account, None);
}

#[derive(Debug, Deserialize)]
pub struct PairingStatusQuery {
    pub id: String,
}

/// `GET /api/channels/signal/pairing-status?id=<uuid>`
pub async fn pairing_status(
    State(state): State<AppState>,
    headers: HeaderMap,
    Query(query): Query<PairingStatusQuery>,
) -> impl IntoResponse {
    if let Err(code) = require_auth_inline(&state, &headers) {
        return (code, "Unauthorized").into_response();
    }

    gc_expired_entries();

    match get_state(&query.id) {
        Some(st) => Json(st).into_response(),
        None => (
            StatusCode::NOT_FOUND,
            "Identificativo pairing sconosciuto o scaduto.".to_string(),
        )
            .into_response(),
    }
}
'''


def write_api_signal_module(repo: Path) -> None:
    """Crea/sovrascrive crates/zeroclaw-gateway/src/api_signal.rs con la nuova logica."""
    path = repo / "crates" / "zeroclaw-gateway" / "src" / "api_signal.rs"
    # Idempotente: scrivo sempre il contenuto corrente. Se la vecchia
    # versione era gia' presente (build #25), viene sostituita con quella
    # nuova che ha anche finishLink + pairing-status.
    path.write_text(API_SIGNAL_RS_BODY, encoding="utf-8")


def patch_lib_rs(repo: Path) -> None:
    """Aggiunge `pub mod api_signal;` e i due route nel router."""
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

    # 2) Aggiungo i route subito dopo "/api/config/list".
    route_marker = '.route("/api/config/list", get(api_config::handle_list))'
    if route_marker not in text:
        fail(f"Aggancio route non trovato in {path} (cercato `{route_marker}`)")

    # 2a) start-pairing
    if "/api/channels/signal/start-pairing" not in text:
        new_route = (
            route_marker
            + '\n        .route(\n'
            + '            "/api/channels/signal/start-pairing",\n'
            + '            post(api_signal::start_pairing),\n'
            + '        )'
        )
        text = text.replace(route_marker, new_route, 1)

    # 2b) pairing-status (route GET). Lo aggancio sull'esistente start-pairing
    #     in modo che resti adiacente.
    start_pairing_route_marker = (
        '.route(\n'
        '            "/api/channels/signal/start-pairing",\n'
        '            post(api_signal::start_pairing),\n'
        '        )'
    )
    if "/api/channels/signal/pairing-status" not in text:
        if start_pairing_route_marker not in text:
            fail(
                f"Aggancio per pairing-status non trovato in {path} "
                "(cercato il route start-pairing che dovrebbe essere stato "
                "appena aggiunto)"
            )
        addition = (
            start_pairing_route_marker
            + '\n        .route(\n'
            + '            "/api/channels/signal/pairing-status",\n'
            + '            get(api_signal::pairing_status),\n'
            + '        )'
        )
        text = text.replace(start_pairing_route_marker, addition, 1)

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
    msg = "patch-signal-start-pairing: OK (startLink + finishLink + pairing-status)"
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
