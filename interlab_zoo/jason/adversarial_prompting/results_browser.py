"""
A streamlit app for browsing the results of a batch of experiments.

It takes an output folder containing subfolders (one per run), reads the results.json files in each subfolder, and
merges them into a single dataframe, then displays them in a table.
"""
from pathlib import Path
from textwrap import wrap

import pandas as pd

# from matplotlib import pyplot as plt
import plotly.express as px
import streamlit as st

from interlab_zoo.jason.adversarial_prompting import utils

# from streamlit.components.v1 import html

MAX_WIDTH = 100

# wide layout
st.set_page_config(layout="wide")

# todo: implement a folder picker
experiment_folder = st.text_input(
    "Experiment folder", value="/home/jason/dev/acs/interlab/results/2023-07-27"
)
experiment_folder = Path(experiment_folder)

# # load the contexts from the experiment folder
# storage = context.FileStorage(experiment_folder)
# # html(storage.display())#, height=1000, width=MAX_WIDTH) # display the contexts in a tree view; does not work yet


read_result_json = st.cache_data(utils.read_result_json)


subfolders = [f for f in experiment_folder.iterdir() if f.is_dir()]
results = {
    subfolder.name: read_result_json(subfolder / "result.json")
    for subfolder in subfolders
    if (subfolder / "result.json").exists()
}

# # the context IDs are the filenames of '*.root.gz' files in the result subfolder
# context_suffix = ".root.gz"
# context_ids = {
#     subfolder.name: next(f.name[:-len(context_suffix)] for f in subfolder.glob(f"*{context_suffix}"))
#     for subfolder in subfolders
# }
# # st.write(context_ids)

# # try to read a context directly from the storage
# result_key = next(iter(results.keys()))
# st.write(storage.read_context(context_ids[result_key]))

df = pd.concat(results).reset_index(drop=True)
st.write(df.shape)
# experiments per victim model
st.write(df.groupby("victim.model").experiment.nunique())
st.write(df)

# plot informativeness_history for each successful experiment using plotly
for col in ["response", "experiment"]:
    df[col] = df[col].apply(lambda s: "<br>".join(wrap(s, 100)))

for model, model_df in df.groupby("victim.model"):
    fig = px.strip(  # allows to use jitter to avoid overlapping points
        model_df,
        x="round",
        y="informativeness",
        hover_data=[
            # "experiment",
            "prompt",
            # "response",
        ],
        hover_name="response",
        color="context_id",
        color_discrete_sequence=px.colors.qualitative.Dark24,  # default looks better
        # symbol_sequence=[  # if using scatter plot instead
        #     "square",
        #     "diamond",
        #     "circle",
        #     "x",
        #     "triangle-up",
        #     "star",
        # ],  # does not work for some reason
        # opacity=0.5,
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

# # check logs for those experiments that did not produce a result.json file
# for subfolder, context_id in context_ids.items():
#     ctx = storage.read_context(context_id)
#     if ctx.error is not None:
#         st.write(f"Error in {subfolder}:")
#         st.write(ctx.error)
