#!/usr/bin/env python3
"""
Aggiunge al gateway l'endpoint:

  POST /api/dialog/folder
       -> apre il dialogo nativo Windows "Sfoglia cartella" (FolderBrowserDialog
          di System.Windows.Forms) via PowerShell -Sta, aspetta che l'utente
          scelga (o cancelli), e restituisce il path scelto.

       Body opzionale: {"initial": "C:\\Users\\..."} per impostare la
       cartella iniziale del dialogo (default: Desktop dell'utente).

       Risposta:
         200 {"path": "C:\\Users\\Lenovo M710Q\\Desktop\\KUIO"}  se sceglie
         200 {"cancelled": true}                                  se annulla
         5xx in caso di errore tecnico (PowerShell non risponde, ecc.)

Serve a permettere alla Stanza italiana di offrire una "vera" scelta cartella
all'utente B2B, senza dipendere dai limiti di sicurezza del browser.

Fail-loud: se un'iniezione non trova il suo aggancio, la patch lancia
RuntimeError e la build esce rossa.
"""

import sys
from pathlib import Path


def fail(msg: str) -> None:
    raise RuntimeError(f"patch-folder-dialog: {msg}")


API_DIALOG_RS_BODY = r'''//! Native folder picker via Windows FolderBrowserDialog.
//!
//! Espone:
//!  - POST /api/dialog/folder
//!
//! Il motore lancia un sub-processo PowerShell in modalita' STA che apre
//! il dialogo nativo Windows "Sfoglia cartella", aspetta la scelta
//! dell'utente, e restituisce il path al gateway che lo invia al client.
//! Su sistemi non-Windows ritorna 501 Not Implemented.

use axum::{
    extract::State,
    http::{HeaderMap, StatusCode, header},
    response::{IntoResponse, Json},
};
use serde::{Deserialize, Serialize};
use std::time::Duration;
use tokio::process::Command;

use crate::AppState;

#[derive(Debug, Deserialize, Default)]
pub struct PickFolderRequest {
    #[serde(default)]
    pub initial: Option<String>,
    #[serde(default)]
    pub title: Option<String>,
}

#[derive(Debug, Serialize)]
#[serde(untagged)]
pub enum PickFolderResponse {
    Chosen { path: String },
    Cancelled { cancelled: bool },
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

/// `POST /api/dialog/folder`
///
/// Apre il FolderBrowserDialog nativo Windows. Bloccante (fino a 5 minuti
/// di attesa per la scelta dell'utente).
pub async fn pick_folder(
    State(state): State<AppState>,
    headers: HeaderMap,
    body: Option<axum::Json<PickFolderRequest>>,
) -> impl IntoResponse {
    if let Err(code) = require_auth_inline(&state, &headers) {
        return (code, "Unauthorized").into_response();
    }

    #[cfg(not(target_os = "windows"))]
    {
        let _ = body;
        return (
            StatusCode::NOT_IMPLEMENTED,
            "Folder dialog supportato solo su Windows.",
        )
            .into_response();
    }

    #[cfg(target_os = "windows")]
    {
        let req = body.map(|axum::Json(b)| b).unwrap_or_default();
        let initial = req.initial.unwrap_or_default();
        let title = req
            .title
            .unwrap_or_else(|| "Scegli la cartella di lavoro di Kuio".to_string());

        // Costruisco lo script PowerShell. Doppi backslash, single-quote
        // escape, etc. La stringa finale e' passata come argomento -Command.
        // NB: il dialogo deve essere "topmost" perche' altrimenti finisce
        // dietro la finestra del browser. Trucco: creo una piccola Form
        // invisibile come owner, con TopMost=true.
        let initial_ps = initial.replace('\\', "\\\\").replace('\'', "''");
        let title_ps = title.replace('\'', "''");

        let script = format!(
            r#"
Add-Type -AssemblyName System.Windows.Forms
$owner = New-Object System.Windows.Forms.Form
$owner.TopMost = $true
$owner.Opacity = 0
$owner.ShowInTaskbar = $false
$owner.WindowState = 'Minimized'
$owner.Show() | Out-Null
$d = New-Object System.Windows.Forms.FolderBrowserDialog
$d.Description = '{title}'
$d.ShowNewFolderButton = $true
$initial = '{initial}'
if ([string]::IsNullOrEmpty($initial)) {{
  $d.SelectedPath = [Environment]::GetFolderPath('Desktop')
}} else {{
  $d.SelectedPath = $initial
}}
$result = $d.ShowDialog($owner)
$owner.Close()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
  Write-Output $d.SelectedPath
  exit 0
}} else {{
  exit 1
}}
"#,
            title = title_ps,
            initial = initial_ps
        );

        let output = Command::new("powershell")
            .args([
                "-Sta",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                &script,
            ])
            .kill_on_drop(true)
            .output();

        let output = match tokio::time::timeout(Duration::from_secs(300), output).await {
            Ok(Ok(o)) => o,
            Ok(Err(e)) => {
                return (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    format!("Impossibile lanciare PowerShell: {e}"),
                )
                    .into_response();
            }
            Err(_) => {
                return (
                    StatusCode::REQUEST_TIMEOUT,
                    "Tempo scaduto in attesa della scelta utente (5 minuti).".to_string(),
                )
                    .into_response();
            }
        };

        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let chosen = stdout.trim().to_string();
            if chosen.is_empty() {
                return Json(PickFolderResponse::Cancelled { cancelled: true })
                    .into_response();
            }
            return Json(PickFolderResponse::Chosen { path: chosen })
                .into_response();
        } else {
            // Exit non-zero = utente ha cancellato (exit 1 nel nostro script).
            return Json(PickFolderResponse::Cancelled { cancelled: true })
                .into_response();
        }
    }
}
'''


def write_api_dialog_module(repo: Path) -> None:
    """Crea/sovrascrive crates/zeroclaw-gateway/src/api_dialog.rs."""
    path = repo / "crates" / "zeroclaw-gateway" / "src" / "api_dialog.rs"
    path.write_text(API_DIALOG_RS_BODY, encoding="utf-8")


def patch_lib_rs(repo: Path) -> None:
    """Aggiunge `pub mod api_dialog;` e il route nel router."""
    path = repo / "crates" / "zeroclaw-gateway" / "src" / "lib.rs"
    text = path.read_text(encoding="utf-8")

    # 1) modulo
    if "pub mod api_dialog;" not in text:
        anchor = "pub mod api_pairing;"
        if anchor not in text:
            fail(f"Aggancio modulo non trovato in {path} (cercato `{anchor}`)")
        text = text.replace(
            anchor,
            anchor + "\npub mod api_dialog;",
            1,
        )

    # 2) route. Lo aggancio dopo /api/config/list (stesso pattern di api_signal).
    route_marker = '.route("/api/config/list", get(api_config::handle_list))'
    if route_marker not in text:
        fail(f"Aggancio route non trovato in {path} (cercato `{route_marker}`)")
    if "/api/dialog/folder" not in text:
        new_route = (
            route_marker
            + '\n        .route(\n'
            + '            "/api/dialog/folder",\n'
            + '            post(api_dialog::pick_folder),\n'
            + '        )'
        )
        text = text.replace(route_marker, new_route, 1)

    path.write_text(text, encoding="utf-8")


def find_repo_root() -> Path:
    cur = Path.cwd().resolve()
    for cand in [cur, *cur.parents]:
        if (cand / "crates" / "zeroclaw-gateway" / "src" / "lib.rs").exists():
            return cand
    fail("repo Kuio non trovato")


def main() -> int:
    if len(sys.argv) >= 2:
        repo = Path(sys.argv[1])
    else:
        repo = find_repo_root()
    if not (repo / "crates" / "zeroclaw-gateway" / "src" / "lib.rs").exists():
        fail(f"Non sembra un repo Kuio valido: {repo}")
    write_api_dialog_module(repo)
    patch_lib_rs(repo)
    print("patch-folder-dialog: OK (endpoint POST /api/dialog/folder via PowerShell -Sta)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
