#!/usr/bin/env python
# coding: utf-8

import os
from argparse import ArgumentParser

import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde, pearsonr, spearmanr
from tqdm import tqdm


def cell_density(df_file: str, parent_dir_out: str):

    big_df = pl.read_ipc(
        df_file,
        memory_map=False,
    )

    lag_times_minutes = "30,60,90,120,150,180,210,240".split(",")

    for lt in tqdm(lag_times_minutes):
        target_column = f"D2min_{lt}_minutes"

        filtered_df = big_df.filter(pl.col(target_column).is_not_nan())

        sampled_df = filtered_df.sample(20_000)
        # Calculate the local density using gaussian_kde

        print(
            spearmanr(
                filtered_df["local_density_per_mum_squared"], filtered_df[target_column]
            )
        )

        kde = gaussian_kde(
            [sampled_df["local_density_per_mum_squared"], sampled_df[target_column]]
        )
        density = kde(
            [sampled_df["local_density_per_mum_squared"], sampled_df[target_column]]
        )

        f = plt.figure(figsize=(5, 5))
        ax = f.add_subplot(111)
        sns.scatterplot(
            ax=ax,
            data=sampled_df,
            x="local_density_per_mum_squared",
            y=target_column,
            hue=density,
            s=2,
            palette="Reds",
            edgecolor=None,
        )

        ax.set_ylim(0, np.percentile(sampled_df[target_column], 97))
        ax.set_xlim(0, np.percentile(sampled_df["local_density_per_mum_squared"], 97))
        ax.set_title(
            f"Motility vs. Density at {lt} minutes (Pearson: {pearsonr(filtered_df['local_density_per_mum_squared'], filtered_df[target_column])[0]:.2f})"
        )

        f.savefig(
            os.path.join(parent_dir_out, f"motility_vs_density_{lt}_minutes.png"),
            bbox_inches="tight",
            dpi=400,
        )


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--dataframe_file", type=str, required=True)
    parser.add_argument("--parent_dir_out", type=str, required=True)
    args = parser.parse_args()

    cell_density(args.dataframe_file, args.parent_dir_out)
