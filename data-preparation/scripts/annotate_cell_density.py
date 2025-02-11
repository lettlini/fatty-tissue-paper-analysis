import os
import pickle
from argparse import ArgumentParser

import cv2
import numpy as np
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.transformations import BaseMultiDataSetTransformation


class AnnotateCellDensityTransformation(BaseMultiDataSetTransformation):

    def __init__(self, mum_per_px: float):
        self._mum_per_px = mum_per_px
        super().__init__()

    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:
        ast: dict = entry.data["abstract_structure"]
        cellapprox: np.array = entry.data["cell_approximation"]

        occupied_area_fraction = (cellapprox > 0).mean()

        num_labels, _, _, _ = cv2.connectedComponentsWithStats(
            (cellapprox > 0).astype(np.uint8), connectivity=8
        )
        cell_density_per_mum_squared = (num_labels - 1) / (
            cellapprox.shape[0] * cellapprox.shape[1] * self._mum_per_px**2
        )

        for _, props in ast.items():
            props["occupied_area_fraction"] = occupied_area_fraction
            props["cell_density_per_mum_squared"] = cell_density_per_mum_squared

        return BaseDataSetEntry(identifier=entry.identifier, data=ast)

    def __call__(self, abstract_structure, cell_approximation, cpus: int = 1):
        return super()._transform(
            cpus=cpus,
            abstract_structure=abstract_structure,
            cell_approximation=cell_approximation,
        )


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--ast_infile", type=str, required=True)
    parser.add_argument("--cell_approximation_infile", type=str, required=True)
    parser.add_argument("--outfile", type=str, required=True)
    parser.add_argument("--mum_per_px", type=float, required=True)
    parser.add_argument(
        "--cpus",
        required=True,
        type=int,
        help="CPU cores to use.",
    )

    args = parser.parse_args()

    cell_approx_ds = BaseDataSet.from_pickle(args.cell_approximation_infile)
    abstract_structure_ds = BaseDataSet.from_pickle(args.ast_infile)

    x = AnnotateCellDensityTransformation(args.mum_per_px)(
        cpus=1,
        abstract_structure=abstract_structure_ds,
        cell_approximation=cell_approx_ds,
    )

    x.to_pickle(args.outfile)
