#!/usr/bin/env python
import json

import numpy as np
import pandas as pd

import tagger


def filter_no_speech(transcription, k=1.01, threshold=0.1):
    no_speech = transcription.copy()
    no_speech["segments"] = []
    speech = transcription.copy()
    speech["segments"] = []

    is_no_speech = True
    current_text = ""
    for s in transcription["segments"]:
        if s["no_speech_prob"] - k * np.exp(s["avg_logprob"]) > threshold or (
            is_no_speech and s["text"] == current_text
        ):
            no_speech["segments"].append(s)
            is_no_speech = True
            current_text = s["text"]
            continue

        speech["segments"].append(s)
        is_no_speech = False
        current_text = s["text"]
        continue

    return no_speech, speech


def get_segment_scores(transcription):
    # Return a list of segment scores
    scores = [
        {
            "start": int(segment["start"]),
            "avg_logprob": segment["avg_logprob"],
            "no_speech_prob": segment["no_speech_prob"],
            "text": segment["text"],
        }
        for segment in transcription["segments"]
    ]
    return scores


if __name__ == "__main__":
    file = "jsons/_3mcJPm79CU.json"
    with open(file) as f:
        transcription = json.load(f)

    segments = get_segment_scores(transcription)

    df = pd.DataFrame(segments)

    df.to_csv("segments.csv", index=False)

    logprob_nospeech = df[["avg_logprob", "no_speech_prob"]]
    logprob_nospeech = logprob_nospeech.astype(float)
    logprob_nospeech = logprob_nospeech.drop_duplicates()
    logprob_nospeech["no_speech"] = 0

    logprob_nospeech.to_csv("scores.csv", index=False)
