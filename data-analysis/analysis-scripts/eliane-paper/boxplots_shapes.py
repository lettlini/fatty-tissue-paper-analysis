#!/usr/bin/env python
# coding: utf-8

import os
from argparse import ArgumentParser

import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt

plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": ["Fira Sans"],
        "text.latex.preamble": r"\usepackage{siunitx}\usepackage[sfdefault]{FiraSans}\usepackage{newtxsf}\usepackage{sansmath}",
    }
)


def boxplot_shapes(data_preparation_dir: str, cell_class: str, parent_dir_out: str):
    big_dataframe: pl.DataFrame = pl.read_ipc(
        os.path.join(data_preparation_dir, cell_class, "all_cell_tracks.ipc")
    )

    for cln in ["hela", "caski"]:
        cdf = big_dataframe.filter(pl.col("cell_line_name").str.to_lowercase().eq(cln))
        f = plt.figure(figsize=(5, 5))
        ax = f.add_subplot(111)
        sns.violinplot(data=cdf, ax=ax, x="cell_culture_methodology", y="cell_shape")
        ax.set_title(cln)

        sns.despine(f, ax)
        f.tight_layout()

        f.savefig(
            os.path.join(parent_dir_out, f"{cln}_cell_shape_boxplot.png"),
            dpi=500,
            bbox_inches="tight",
        )


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--data_preparation_dir", type=str, required=True)
    parser.add_argument("--parent_dir_out", type=str, required=True)
    parser.add_argument("--cell_class", type=str, required=True)
    args = parser.parse_args()

    boxplot_shapes(args.data_preparation_dir, args.cell_class, args.parent_dir_out)
