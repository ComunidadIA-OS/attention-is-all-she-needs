"""
Script de prueba para AI Endpoints de OVHcloud
Reto «Mujeres por la IA Abierta» — Equipo 1: Attention Is All She Needs

Ejecución:
    python scripts/test_audio_ovh.py audio.wav [idioma]
"""

import os
import sys
import json
import requests
from pathlib import Path

BASE = os.environ.get("OVH_BASE_URL", "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1")
RAW_TOKEN = os.environ.get("OVH_AI_ENDPOINTS_ACCESS_TOKEN") or os.environ.get("OVH_API_TOKEN") or ""
TOKEN = RAW_TOKEN.strip().replace("\r", "").replace("\n", "").replace(" ", "")
ASR_MODEL = os.environ.get("OVH_ASR_MODEL", "whisper-large-v3")

def transcribir(audio, idioma="ca"):
    p = Path(audio)
    if not p.exists():
        sys.exit(f"No existe el archivo de audio: {audio}")
    
    print(f"[*] Enviando '{p.name}' a OVHcloud ({ASR_MODEL}, diarize=true, lang={idioma})...")
    with open(p, "rb") as f:
        r = requests.post(
            f"{BASE}/audio/transcriptions",
            headers={"Authorization": f"Bearer {TOKEN}"},
            files={"file": (p.name, f)},
            data={
                "model": ASR_MODEL,
                "language": idioma,
                "response_format": "verbose_json",
                "diarize": "true"
            },
            timeout=180,
        )
    if not r.ok:
        sys.exit(f"[X] Error {r.status_code}: {r.text[:500]}")
    return r.json()

if __name__ == "__main__":
    if not TOKEN:
        print("[!] No se encontró la variable OVH_AI_ENDPOINTS_ACCESS_TOKEN ni OVH_API_TOKEN.")
        TOKEN = input("Pega tu token de OVHcloud: ").strip().replace("\r", "").replace("\n", "").replace(" ", "")
        if not TOKEN:
            sys.exit("Operación cancelada: falta el token.")

    if len(sys.argv) < 2:
        sys.exit("Uso: python scripts/test_audio_ovh.py ruta/al/audio.wav [idioma]")

    archivo = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "ca"

    res = transcribir(archivo, lang)
    
    # Guardamos el JSON crudo para trazabilidad y depuración
    salida_json = Path("salida_ovh.json")
    salida_json.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] JSON completo guardado en: {salida_json.resolve()}")

    # Análisis de diarización y cálculo de tiempos agregados por hablante
    # OVHcloud devuelve la lista con hablantes en la clave 'diarization'
    turnos = res.get("diarization") or res.get("segments", [])
    print(f"\n[+] Total de turnos detectados: {len(turnos)}")
    print("-" * 75)
    for s in turnos[:8]:
        ini = s.get('start', 0.0)
        fin = s.get('end', 0.0)
        spk_raw = s.get('speaker', 'Desconocido')
        spk = f"Hablante_{spk_raw}" if isinstance(spk_raw, int) else str(spk_raw)
        txt = s.get('text', '').strip()[:65]
        print(f"[{ini:6.1f}s - {fin:6.1f}s] {spk:14}: \"{txt}...\"")
    print("-" * 75)

    # Cálculo determinista del tiempo total por hablante (KPI para el reto)
    tiempos = {}
    for s in turnos:
        spk_raw = s.get("speaker", "Desconocido")
        spk = f"Hablante_{spk_raw}" if isinstance(spk_raw, int) else str(spk_raw)
        dur = max(0.0, s.get("end", 0.0) - s.get("start", 0.0))
        tiempos[spk] = tiempos.get(spk, 0.0) + dur

    tiempo_total = sum(tiempos.values())
    print("\n📊 Resumen de Tiempos de Habla por Hablante:")
    for spk, t in sorted(tiempos.items(), key=lambda x: x[1], reverse=True):
        pct = (t / tiempo_total * 100) if tiempo_total > 0 else 0
        print(f"   • {spk:14}: {t:6.1f} segundos ({pct:5.1f} %)")
    print(f"   Total voz detectada: {tiempo_total:6.1f} segundos\n")
