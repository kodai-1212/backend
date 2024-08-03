import hashlib
import os
import re
import shutil
from dataclasses import dataclass
from enum import Enum
from gc import callbacks
from importlib.resources import path
from pathlib import Path
from typing import Callable, Generator, List, Tuple
from spleeter.separator import Codec, Separator


class ProcessingMode(Enum):
    SINGLE = "Split a single audio file"


@dataclass
class SpleeterStems:
    name: str
    stems: list
    label: str


class SpleeterMode(Enum):
    FIVESTEMS: SpleeterStems = SpleeterStems(
        name="5stems",
        stems=["vocals", "drums", "bass", "piano", "other"],
        label="5stems: vocals, drums, bass, piano and other"
    )


@dataclass
class SpleeterSettings:
    split_mode: SpleeterMode
    codec: Codec
    bitrate: int
    usemwf: bool = False
    use16kHZ: bool = False
    duration: int = 600


def strip_ansi_escape_codes(s):
    ansi_escape = re.compile(r'\x1b[^m]*m')
    return ansi_escape.sub('', s)


def get_split_audio(config: SpleeterSettings,
                    audio_file: Path,
                    output_path: Path) -> Tuple[Generator[Path, None, None], bool]:

    is_exist = False
    output_path_base = Path(
        output_path/f"{audio_file.stem}/{config.split_mode.value.name}{'-16kHz' if config.use16kHZ else '-11kHz'}{'' if config.usemwf else '-noMWF'}/")
    print("output_path_base:" + str(output_path_base))

    if os.path.exists(output_path_base/f"{audio_file.stem}_vocals.{config.codec.value}"):
        print(
            f"{audio_file.stem} [{config.split_mode.value.name}{'-16kHz' if config.use16kHZ else ''}] : already splited")
        is_exist = True

    else:
        os.makedirs(str(output_path_base.absolute()), exist_ok=True)

        separator = Separator(
            params_descriptor=f"spleeter:{config.split_mode.value.name}{'-16kHz' if config.use16kHZ else ''}",
            MWF=config.usemwf, multiprocess=False
        )
        separator.separate_to_file(
            str(audio_file),
            bitrate=f"{config.bitrate}k",
            destination=str(output_path),
            codec=config.codec,
            filename_format=f"{{filename}}/{config.split_mode.value.name}{'-16kHz' if config.use16kHZ else '-11kHz'}{'' if config.usemwf else '-noMWF'}/{{filename}}_{{instrument}}.{{codec}}",
            duration=config.duration
        )

    return output_path_base.glob(f'*.{config.codec.value}'), is_exist
