import os
from pathlib import Path
from typing import Generator, List
#import matplotlib
#import librosa
#from librosa import display
import streamlit as st
import streamlit.components.v1 as stc
import click
from spleeter.separator import Codec
#import matplotlib.pyplot as plt

from utils import (ProcessingMode, SpleeterMode, SpleeterSettings,
                   get_split_audio)

UPLOAD_DIR = Path("./upload_files/")
OUTPUT_DIR = Path("./output/")

if 'audio_files' not in st.session_state:
    st.session_state.audio_files = []
if 'output_files' not in st.session_state:
    st.session_state.output_files = []
if 'spleeter_settings' not in st.session_state:
    st.session_state.spleeter_settings = None
if 'selected_music_file' not in st.session_state:
    st.session_state.selected_music_file = None
if 'selected_music_files' not in st.session_state:
    st.session_state.selected_music_files = None


def add_audio_files(audio_file: Path):
    if(audio_file not in st.session_state.audio_files):
        st.session_state.audio_files.append(audio_file)


def save_uploaded_file(upload_file) -> Path:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    escaped_file_path = Path(upload_file.name)

    if(escaped_file_path.stem[-1] == " "):
        escaped_file_path = escaped_file_path.parent / \
            f"{escaped_file_path.stem[:-1]}{escaped_file_path.suffix}"

    file_path = UPLOAD_DIR / escaped_file_path
    print(f"upload file:{file_path}")
    with open(file_path, 'wb') as f:
        f.write(upload_file.read())

    return file_path


st.title("Stem Player")

# audio file uploader
upload_files = st.file_uploader("Upload audio from local file", type=[
    "wav", "mp3"], accept_multiple_files=True)

for audio_file in upload_files:
    upload_path = save_uploaded_file(audio_file)
    add_audio_files(upload_path)

current_mode = ProcessingMode.SINGLE
selected_music: Path
select_stems: SpleeterMode
select_codec: Codec
select_bitrate: int
output_files_generator: Generator[Path, None, None]

if(current_mode == ProcessingMode.SINGLE):
    with st.form("single_mode"):
        st.subheader("Mode: "+current_mode.value)
        selected_music = st.selectbox(
            "Select an audio file", st.session_state.audio_files,
            format_func=lambda x: x.name)

        select_stems = SpleeterMode.FIVESTEMS
        select_codec = Codec.MP3
        select_bitrate = 192
        duaration_minutes = 60
        use_16kHz = True
        use_mwf = True

        if st.form_submit_button("Split"):
            if(selected_music == None or select_stems == None):
                st.error("Please select an audio file")

            else:
                current_settings = SpleeterSettings(
                    select_stems,
                    select_codec,
                    select_bitrate,
                    use_mwf,
                    use_16kHz,
                    duaration_minutes*60
                )
                st.session_state.spleeter_settings = current_settings
                st.session_state.selected_music_file = selected_music
                st.session_state.output_files = []
                with st.spinner('Processing...'):
                    output_files_generator, is_exist = get_split_audio(
                        st.session_state.spleeter_settings,
                        selected_music,
                        OUTPUT_DIR)
                    for x in output_files_generator:
                        st.session_state.output_files.append(x)
                st.success("Done!")

    with st.container():
        st.subheader("Output")
        if(st.session_state.selected_music_file != None and select_stems != None):
            st.caption("Original: " +
                       st.session_state.selected_music_file.name)
            st.audio(str(selected_music))

            for i, audio_file in enumerate(st.session_state.output_files):
                st.caption(audio_file.name)
                st.audio(str(audio_file))

                # wav, sr = librosa.load(audio_file)
                # fig, ax = plt.subplots()
                # librosa.display.waveplot(wav, sr=sr, x_axis="time", ax=ax)
                # st.pyplot(fig)
