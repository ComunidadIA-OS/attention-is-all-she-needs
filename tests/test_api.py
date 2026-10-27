# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import json
import subprocess

import pytest
from fastapi.testclient import TestClient
from test_gold import NLP_SILVER, SILVER

from aiasn.api import jobs
from aiasn.api.app import create_app, new_video_id
from aiasn.pipelines.context import RunContext
from aiasn.pipelines.gold import GoldPipeline
from aiasn.settings import Settings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import OK, RUNNING, Manifest


class FakeLauncher:
    def __init__(self, busy=False, fails=False, alive=()):
        self.launched, self._busy, self._fails, self._alive = [], busy, fails, set(alive)

    def launch(self, video_id):
        if self._fails:
            raise RuntimeError("no worker")
        self.launched.append(video_id)

    def busy(self):
        return self._busy

    def running(self, video_id):
        return video_id in self._alive


@pytest.fixture
def settings(tmp_path):
    return Settings(lake_uri=str(tmp_path / "lake"), tmp_dir=tmp_path / "tmp")


def client(settings, launcher):
    return TestClient(create_app(settings, launcher))


def upload(api, name="Entrevista CSIC.mp4"):
    return api.post("/videos", files={"file": (name, b"video bytes", "video/mp4")})


def test_health(settings):
    with client(settings, FakeLauncher()) as api:
        assert api.get("/health").json() == {"ok": True}


def test_upload_stores_the_video_and_launches_the_worker(settings):
    launcher = FakeLauncher()
    with client(settings, launcher) as api:
        r = upload(api)
    assert r.status_code == 202
    video_id = r.json()["video_id"]
    assert video_id.startswith("entrevista-csic-") and launcher.launched == [video_id]
    lake = Lake.from_settings(settings)
    assert lake.landing_file(video_id).endswith(f"{video_id}.mp4")
    assert Manifest.load(lake, video_id)["status"] == "en_cola"


def test_upload_rejects_what_is_not_a_video(settings):
    launcher = FakeLauncher()
    with client(settings, launcher) as api:
        assert upload(api, "notes.txt").status_code == 400
    assert launcher.launched == []


def test_one_video_at_a_time(settings):
    with client(settings, FakeLauncher(busy=True)) as api:
        assert upload(api).status_code == 409
    assert not (Lake.from_settings(settings).fs.exists(f"{settings.lake_uri}/landing"))   # the upload is not kept


def test_worker_that_does_not_start_leaves_an_error(settings):
    with client(settings, FakeLauncher(fails=True)) as api:
        assert upload(api).status_code == 500
        [run] = Lake.from_settings(settings).fs.ls(f"{settings.lake_uri}/runs")
        status = api.get(f"/videos/{run.rsplit('=', 1)[1]}").json()["status"]
    assert status["estado"] == "error" and "no worker" in status["error"]


def test_unknown_video(settings):
    with client(settings, FakeLauncher()) as api:
        assert api.get("/videos/nope").status_code == 404
        assert api.get("/videos/..%2Fsecret").status_code == 404


def test_a_video_whose_worker_is_gone_is_marked_as_failed(settings):
    lake = Lake.from_settings(settings)
    for video_id in ("alive", "dead"):
        manifest = Manifest(lake, video_id)
        manifest.start("audio"); manifest.done("audio"); manifest.start("video")
        manifest.set_status(RUNNING)
    with client(settings, FakeLauncher(alive={"alive"})) as api:
        assert api.get("/videos/alive").json()["status"]["estado"] == "procesando"
        dead = api.get("/videos/dead").json()["status"]
        listed = {v["video_id"]: v["estado"] for v in api.get("/videos").json()}
    assert dead["estado"] == "error" and "se interrumpió" in dead["error"]
    assert dead["pasos"] == {"audio": "ok", "video": "error"}   # the step cut short, not left running
    assert listed == {"alive": "procesando", "dead": "error"}
    assert Manifest.load(lake, "dead")["status"] == "error"   # recorded, not only reported


def test_status_while_processing(settings):
    lake = Lake.from_settings(settings)
    manifest = Manifest(lake, "vid1")
    manifest.set_status(RUNNING)
    manifest.start("audio")
    with client(settings, FakeLauncher(alive={"vid1"})) as api:
        body = api.get("/videos/vid1").json()
    assert body["status"] == {"estado": "procesando", "pasos": {"audio": "running"}, "error": None}
    assert body["resultado"] is None


def test_result_by_sections_of_the_front(settings):
    ctx = RunContext.for_video(settings, "vid1")
    for ref, df in (SILVER | NLP_SILVER).items():
        ctx.lake.write(*ref.split("/"), "vid1", df)
    GoldPipeline(settings)(ctx)
    ctx.manifest.set_status(OK)
    with client(settings, FakeLauncher()) as api:
        r = api.get("/videos/vid1")
    json.loads(r.text, parse_constant=lambda c: pytest.fail(f"{c} in the JSON"))   # no NaN
    res = r.json()["resultado"]
    assert set(res) == {"veredicto", "metricas", "personas", "temas", "poder", "roles", "clima", "autoridad",
                        "constelacion", "kpis", "segmentos", "segmentos_dudosos"}
    # Marta speaks from authority: testimony by role, but her caption title shows it
    assert res["autoridad"]["voz_con_autoridad_pct"]["mujer"] == 100.0
    assert res["poder"]["area_media"]["mujer"] == 0.3
    first = res["segmentos"][0]
    assert first == {"inicio": 0.0, "fin": 10.0, "segundos": 10.0, "cuadrante": 1, "tipo": first["tipo"],
                     "genero": "mujer", "persona": "p1", "texto": "Hola"}   # Marta speaking on screen
    assert {s["persona"] for s in res["segmentos"] if s["cuadrante"] == 3} == {"v1"}   # the narrator, off screen
    assert res["segmentos_dudosos"] == []   # every span has a known gender here
    assert res["veredicto"]["valoracion_ciudadana"] is None
    assert res["veredicto"]["alerta_infrarrepresentacion"] is False   # 50 % on screen: above the 40 % floor
    tif = res["veredicto"]["bechdel"]   # one woman (Marta) and a man: "no supera", with no score
    assert (tif["estado"], tif["motivo"], tif["puntuacion_0_3"], tif["supera"]) == ("no_supera", "una_mujer", None, False)
    assert tif["reglas"]["regla_3_dialogo_horizontal"] is None and tif["mujeres_presentes"] == 1
    assert res["metricas"]["voz_pct"]["mujer"] == 66.7 and res["metricas"]["pantalla_pct"]["mujer"] == 50.0
    assert res["metricas"]["referentes"] == {"mujer": 1, "hombre": 1}
    assert "no_determinado" not in res["metricas"]["voz_pct"]   # shares of determined time; the rest apart
    assert res["metricas"]["sin_determinar_pct"] == {"voz": 0.0, "pantalla": 0.0}
    # RVP: share of voice over share of screen (66.7 / 50); Marta speaks 20 of her 30 s on screen
    assert res["metricas"]["ratio_voz_pantalla"]["mujer"] == 1.33
    assert res["metricas"]["voz_activa_en_pantalla"]["mujer"] == 0.667
    marta = next(p for p in res["personas"] if p["id"] == "p1")
    assert marta | {"pantalla_s": None} == {"id": "p1", "nombre": "Marta Ruiz", "cargo": "Investigadora", "genero": "mujer",
                                            "rol": "testimonio", "autoridad": True, "pantalla_s": None, "voz_s": 20.0,
                                            "area": 0.3, "centralidad": 0.9}
    sp = res["veredicto"]["salvaguarda_paridad"]
    assert sp["regimen_aplicado"] == "FASE_1_ABSORCION_TECHO_MASCULINO" and sp["suelo_femenino_exigido"] == 0.4
    assert {"tema": "tecnología", "clave": "technology", "genero": "mujer", "turnos": 1, "pct": 50.0,
            "sesgo": -0.04} in res["temas"]
    assert res["clima"] == {"mujer": {"técnico/asertivo": 100.0}, "hombre": {"disenso": 100.0}}
    assert {n["id"] for n in res["constelacion"]["nodos"]} >= {"p1", "p2", "v1", "tema:technology"}


def test_new_video_id():
    assert new_video_id("Robot social (CSIC).MP4").startswith("robot-social-csic-")
    assert new_video_id("¿?.mp4").startswith("video-") and new_video_id("a.mp4") != new_video_id("a.mp4")


def test_process_launcher_is_busy_while_the_worker_runs(monkeypatch):
    popen = subprocess.Popen
    monkeypatch.setattr(jobs.subprocess, "Popen", lambda cmd: popen(["sleep", "0.3"]))
    launcher = jobs.ProcessLauncher()
    assert not launcher.busy()
    launcher.launch("vid1")
    assert launcher.busy() and launcher.running("vid1") and not launcher.running("vid2")
    launcher._process.wait()
    assert not launcher.busy()


class FakeClient:
    def __init__(self, runtimes=("runc", "nvidia")):
        self.containers, self.runtimes = FakeContainers(), runtimes

    def info(self):
        return {"Runtimes": {r: {} for r in self.runtimes}}


class FakeContainers:
    def __init__(self):
        self.runs, self.removed, self.state, self.labels = [], [], {}, {}   # name -> running / exited, its labels

    def run(self, image, command, **kwargs):
        self.runs.append((image, command, kwargs))
        self.state[kwargs["name"]], self.labels[kwargs["name"]] = "running", kwargs["labels"]

    def list(self, all=False, filters=None):
        key, _, value = filters["label"].partition("=")   # "label" or "label=value", as Docker filters
        return [FakeContainer(self, name) for name, state in self.state.items()
                if state == filters["status"] and key in self.labels[name] and value in ("", self.labels[name][key])]


class FakeContainer:
    def __init__(self, containers, name):
        self.containers, self.name = containers, name

    def remove(self):
        self.containers.removed.append(self.name)
        del self.containers.state[self.name]


def test_docker_launcher_runs_one_worker_container(monkeypatch):
    pytest.importorskip("docker")
    monkeypatch.setenv("LAKE_URI", "s3://aiasn")
    monkeypatch.setenv("OVH_AI_ENDPOINTS_ACCESS_TOKEN", "token")
    monkeypatch.setenv("HOME", "/root")
    client = FakeClient()
    launcher = jobs.DockerLauncher(Settings().api.worker, client)
    assert not launcher.busy()
    launcher.launch("vid1")
    image, command, kwargs = client.containers.runs[0]
    assert image == "aiasn-worker" and command[-2:] == ["--video-id", "vid1"]
    assert kwargs["environment"] == {"LAKE_URI": "s3://aiasn", "OVH_AI_ENDPOINTS_ACCESS_TOKEN": "token"}
    assert kwargs["volumes"] == {"aiasn-models": {"bind": "/models", "mode": "rw"}} and kwargs["device_requests"]
    assert launcher.busy()
    client.containers.state["aiasn-worker-vid1"] = "exited"
    launcher.launch("vid2")   # the finished one is removed first
    assert client.containers.removed == ["aiasn-worker-vid1"] and launcher.busy()
    assert launcher.running("vid2") and not launcher.running("vid1")


def test_docker_launcher_without_gpu_runs_on_the_cpu(caplog):
    pytest.importorskip("docker")
    client = FakeClient(runtimes=("runc",))
    jobs.DockerLauncher(Settings().api.worker, client).launch("vid1")
    assert client.containers.runs[0][2]["device_requests"] is None and "CPU" in caplog.text


def test_worker_env_by_name_or_prefix():
    env = {"LAKE_URI": "s3://a", "STORAGE__ENDPOINT_URL": "http://s3", "STORAGE": "x", "PATH": "/bin"}
    assert jobs.worker_env(["LAKE_URI", "STORAGE__"], env) == {"LAKE_URI": "s3://a", "STORAGE__ENDPOINT_URL": "http://s3"}


def test_launcher_choice(monkeypatch):
    def no_docker(cfg, client=None):
        raise ConnectionError("no docker")
    monkeypatch.setattr(jobs.DockerLauncher, "__init__", no_docker)
    assert isinstance(jobs.make_launcher(Settings().api), jobs.ProcessLauncher)   # auto falls back
    assert isinstance(jobs.make_launcher(Settings(api={"launcher": "process"}).api), jobs.ProcessLauncher)
    with pytest.raises(ConnectionError):
        jobs.make_launcher(Settings(api={"launcher": "docker"}).api)


def test_list_of_videos_latest_first(settings):
    lake = Lake.from_settings(settings)
    for video_id, status in [("old", OK), ("new", RUNNING)]:
        manifest = Manifest(lake, video_id)
        manifest.start("audio")
        manifest.set_status(status)
    with client(settings, FakeLauncher(alive={"new"})) as api:
        body = api.get("/videos").json()
    assert [(v["video_id"], v["estado"]) for v in body] == [("new", "procesando"), ("old", "ok")]
