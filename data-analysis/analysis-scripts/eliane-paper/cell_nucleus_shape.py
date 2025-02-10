#!/usr/bin/env python
# coding: utf-8

import os
from argparse import ArgumentParser

import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde, pearsonr

plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": ["Fira Sans"],
        "text.latex.preamble": r"\usepackage{siunitx}\usepackage[sfdefault]{FiraSans}\usepackage{newtxsf}\usepackage{sansmath}",
    }
)


def cell_nucleus_shape(df_file: str, parent_dir_out: str):

    # read in combined cell tracking dataframe from ipc file
    big_dataframe: pl.DataFrame = pl.read_ipc(df_file, memory_map=False)

    font_size = 12

    for cln in ["hela", "caski"]:
        cell_line_df = big_dataframe.filter(
            pl.col("cell_line_name").str.to_lowercase().eq(cln)
        )
        for ccm in ["co-culture", "control"]:
            current_df = cell_line_df.filter(
                pl.col("cell_culture_methodology").str.to_lowercase().eq(ccm)
            )
            current_sampled_df = current_df.sample(n=30_000)

            pR = pearsonr(current_df["cell_shape"], current_df["nucleus_shape"])

            # Calculate the local density using gaussian_kde
            kde = gaussian_kde(
                [current_sampled_df["cell_shape"], current_sampled_df["nucleus_shape"]]
            )
            density = kde(
                [current_sampled_df["cell_shape"], current_sampled_df["nucleus_shape"]]
            )
            f = plt.figure(figsize=(5, 5))
            ax = f.add_subplot(111)
            sns.scatterplot(
                data=current_sampled_df,
                x="cell_shape",
                y="nucleus_shape",
                s=0.75,
                hue=density,
                palette="Reds",
                edgecolor=None,
            )

            f.tight_layout()
            ax.set_title(
                f"Nucleus Shape ($ns$) vs. Cell Shape ($cs$): {cln} / {ccm} (Pearson's $R$: {pR[0]:.2f})",
                fontsize=int(1.4 * font_size),
            )

            ax.get_legend().remove()
            # Set axis line width (spines)
            ax.spines["top"].set_linewidth(2)
            ax.spines["right"].set_linewidth(2)
            ax.spines["bottom"].set_linewidth(2)
            ax.spines["left"].set_linewidth(2)
            # You can also set tick width
            ax.tick_params(width=2)
            # Set tick label sizes
            ax.tick_params(
                axis="both", which="major", labelsize=12
            )  # both x and y axes
            ax.set_xlabel("Cell Shape ($cs$)", fontsize=font_size)
            ax.set_ylabel("Nucleus Shape ($ns$)", fontsize=font_size)
            ax.set_xlim(
                current_sampled_df["cell_shape"].min(),
                current_sampled_df["cell_shape"].quantile(0.99),
            )
            ax.set_ylim(
                current_sampled_df["nucleus_shape"].min(),
                current_sampled_df["nucleus_shape"].quantile(0.99),
            )

            sns.despine(f, ax)
            f.savefig(
                os.path.join(parent_dir_out, f"cell_nucleus_shape_{cln}_{ccm}.png"),
                bbox_inches="tight",
                dpi=500,
            )


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--dataframe_file", type=str, required=True)
    parser.add_argument("--parent_dir_out", type=str, required=True)
    args = parser.parse_args()

    cell_nucleus_shape(args.dataframe_file, args.parent_dir_out)
