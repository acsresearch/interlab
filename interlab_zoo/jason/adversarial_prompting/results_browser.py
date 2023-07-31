"""
A streamlit app for browsing the results of a batch of experiments.

It takes an output folder containing subfolders (one per run), reads the results.json files in each subfolder, and
merges them into a single dataframe, then displays them in a table.
"""
from pathlib import Path
from textwrap import wrap

import pandas as pd
import plotly.express as px
import streamlit as st

from interlab_zoo.jason.adversarial_prompting import utils

# wide layout
st.set_page_config(layout="wide")
MAX_WIDTH = 100  # defines text wrap width; todo: can this be dynamic? (percentage of screen width)

# todo: implement a folder picker
experiment_folder = st.text_input(
    "Experiment folder", value="/home/jason/dev/acs/interlab/results/2023-07-27"
)

read_result_json = st.cache_data(utils.read_result_json)


def read_results(experiment_folder: Path | str) -> pd.DataFrame:
    subfolders = (f for f in Path(experiment_folder).iterdir() if f.is_dir())
    results = {
        subfolder.name: read_result_json(subfolder / "result.json")
        for subfolder in subfolders
        if (subfolder / "result.json").exists()
    }
    return pd.concat(results).reset_index(drop=True)


df = read_results(experiment_folder)

with st.expander("Results dataframe"):
    st.write(df.shape)
    # experiments per victim model
    st.write(df.groupby("victim.model").experiment.nunique())
    st.write(df)

with st.expander("Informativeness trajectories"):
    # plot informativeness_history for each successful experiment using plotly
    for col in ["response", "experiment"]:
        df[col] = df[col].apply(lambda s: "<br>".join(wrap(s, 100)))

    for model, model_df in df.groupby("victim.model"):
        fig = px.strip(  # allows to use jitter to avoid overlapping points
            model_df,
            x="round",
            y="informativeness",
            hover_data="prompt",
            hover_name="response",
            color="context_id",
            title=f"Informativeness history (victim: {model})",
        )
        fig.update_traces(jitter=0.1)
        fig.add_hline(
            y=6,
            line_dash="dash",
            line_color="grey",
            annotation_text="informativeness threshold",
        )
        fig.update_layout(showlegend=False)
        fig.update_xaxes(range=[-0.2, 9.2])
        st.plotly_chart(fig, use_container_width=True)
