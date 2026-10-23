import pandas as pd
import pytest

from aiasn.storage.lake import Lake


def test_write_read_roundtrip_and_partition_column(tmp_path):
    lake = Lake(tmp_path)
    df = pd.DataFrame({"frame": [0, 1], "t": [0.0, 0.04]})
    lake.write("bronze", "detections", "vid1", df)
    lake.write("bronze", "detections", "vid2", df)

    pd.testing.assert_frame_equal(lake.read("bronze", "detections", "vid1"), df)
    # Reading the whole table recovers video_id from the folder names
    table = pd.read_parquet(tmp_path / "bronze" / "detections")
    assert sorted(table["video_id"].astype(str).unique()) == ["vid1", "vid2"]


def test_unknown_layer_raises(tmp_path):
    with pytest.raises(ValueError):
        Lake(tmp_path).table_dir("platinum", "detections", "vid1")


def test_landing_file_requires_exactly_one_file(tmp_path):
    lake = Lake(tmp_path)
    landing = lake.landing_dir("vid1")
    landing.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        lake.landing_file("vid1")

    (landing / "a.mp4").touch()
    assert lake.landing_file("vid1").name == "a.mp4"

    (landing / "b.mp4").touch()
    with pytest.raises(FileNotFoundError):
        lake.landing_file("vid1")
