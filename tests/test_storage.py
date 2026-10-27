import uuid
from pathlib import Path

import pandas as pd
import pytest

from aiasn.settings import Settings, StorageSettings
from aiasn.storage.lake import Lake
from aiasn.storage.manifest import Manifest


@pytest.fixture(params=["local", "remote"])
def lake(request, tmp_path) -> Lake:
    """A lake in a local folder, and one in an in-memory filesystem that behaves like an object store (S3/MinIO)."""
    return Lake(tmp_path / "lake") if request.param == "local" else Lake(f"memory://lake-{uuid.uuid4().hex}")


def test_write_read_roundtrip(lake):
    df = pd.DataFrame({"frame": [0, 1], "t": [0.0, 0.04]})
    lake.write("bronze", "detections", "vid1", df)
    pd.testing.assert_frame_equal(lake.read("bronze", "detections", "vid1"), df)
    assert lake.exists("bronze", "detections", "vid1") and not lake.exists("bronze", "detections", "vid2")
    with pytest.raises(FileNotFoundError):
        lake.read("bronze", "detections", "vid2")


def test_partitions_by_video_id(tmp_path):
    lake = Lake(tmp_path)
    df = pd.DataFrame({"frame": [0, 1]})
    lake.write("bronze", "detections", "vid1", df)
    lake.write("bronze", "detections", "vid2", df)
    # Reading the whole table recovers video_id from the folder names
    table = pd.read_parquet(tmp_path / "bronze" / "detections")
    assert sorted(table["video_id"].astype(str).unique()) == ["vid1", "vid2"]


def test_unknown_layer_raises(lake):
    with pytest.raises(ValueError):
        lake.table_dir("platinum", "detections", "vid1")


def test_landing_holds_exactly_one_video(lake, tmp_path):
    with pytest.raises(FileNotFoundError):
        lake.landing_file("vid1")
    video = tmp_path / "a.mp4"
    video.write_bytes(b"video")
    lake.upload_to_landing("vid1", video)
    assert lake.landing_file("vid1").endswith("video_id=vid1/a.mp4")
    lake.upload_to_landing("vid1", video.rename(tmp_path / "b.mp4"))
    with pytest.raises(FileNotFoundError):
        lake.landing_file("vid1")


def test_fetch_landing(lake, tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"video bytes")
    lake.upload_to_landing("vid1", video)
    local = lake.fetch_landing("vid1", tmp_path / "work")
    assert local.read_bytes() == b"video bytes"
    if lake.local:
        assert local == Path(lake.landing_file("vid1"))   # a local lake is read in place, not copied
    else:
        assert local == tmp_path / "work" / "clip.mp4"


def test_manifest_in_the_lake(lake):
    manifest = Manifest(lake, "vid1")
    manifest.start("video")
    manifest.done("video")
    assert manifest.read()["steps"]["video"]["status"] == "ok"
    assert lake.fs.exists(f"{lake.root}/runs/video_id=vid1/manifest.json")


def test_storage_options_only_for_s3():
    storage = StorageSettings(endpoint_url="http://minio:9000", access_key="aiasn", secret_key="secret")
    assert storage.options("data") == {}
    assert storage.options("s3://aiasn") == {"key": "aiasn", "secret": "secret", "use_listings_cache": False,
                                             "client_kwargs": {"endpoint_url": "http://minio:9000"}}
    assert Settings(lake_uri="s3://aiasn", storage=storage).storage.options("s3://aiasn")["key"] == "aiasn"


def test_manifest_lists_the_videos(lake):
    for video_id in ("b", "a"):
        Manifest(lake, video_id)
    assert Manifest.video_ids(lake) == ["a", "b"]
