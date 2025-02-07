#!/usr/bin/env python
# coding: utf-8

import os
from argparse import ArgumentParser

import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from tqdm import tqdm

font_size = 16


def motility(data_preparation_dir: str, cell_class: str, parent_dir_out: str):

    # read in combined cell tracking dataframe from ipc file
    big_dataframe: pl.DataFrame = pl.read_ipc(
        os.path.join(data_preparation_dir, cell_class, "all_cell_tracks.ipc")
    )
    lag_times_minutes = "30,60,90,120,150,180,210,240".split(",")
    cell_line_names = ["hela", "caski"]

    for lt in tqdm(lag_times_minutes):
        target_column = f"D2min_{lt}_minutes"

        for cln in cell_line_names:
            # we need to filter the dataframe
            df = big_dataframe.filter(
                pl.col("cell_line_name").str.to_lowercase().eq(cln)
            )
            df = df.filter(pl.col(target_column).is_not_nan())
            f = plt.figure(figsize=(5 * 1.618, 5))
            ax = f.add_subplot(111)
            sns.histplot(
                ax=ax,
                data=df,
                x=target_column,
                hue="cell_culture_methodology",
                common_norm=False,
                stat="density",
            )
            legend = ax.get_legend()
            legend.set_title(title="Cell Culture Methodology")
            plt.xlim(0, df[target_column].quantile(0.96))
            f.tight_layout()

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
            ax.set_xlabel(r"$D^2_\text{min}$ in [$\mu m^2$]", fontsize=font_size)
            ax.set_ylabel("Probability Density", fontsize=font_size)
            sns.despine(f, trim=False)
            f.savefig(
                os.path.join(parent_dir_out, f"motility_{cln}_{lt}_minutes.png"),
                bbox_inches="tight",
            )


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--data_preparation_dir", type=str, required=True)
    parser.add_argument("--parent_dir_out", type=str, required=True)
    parser.add_argument("--cell_class", type=str, required=True)
    args = parser.parse_args()

    motility(args.data_preparation_dir, args.cell_class, args.parent_dir_out)
