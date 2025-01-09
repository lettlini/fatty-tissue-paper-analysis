import numpy as np
import pickle
import os
from argparse import ArgumentParser

import cv2
from core_data_utils.datasets import BaseDataSet, BaseDataSetEntry
from core_data_utils.datasets.image import ImageDataset
from core_data_utils.transformations import BaseMultiDataSetTransformation


class AnnotateCellDensityTransformation(BaseMultiDataSetTransformation):

    def _transform_single_entry(
        self, entry: BaseDataSetEntry, dataset_properties: dict
    ) -> BaseDataSetEntry:
        ast: dict = entry.data["abstract_structure"]
        cellapprox: np.array = entry.data["cell_approximation"]

        cell_density = (cellapprox > 0).mean()

        for _, props in ast.items():
            props["cell_density_fraction"] = cell_density

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
    parser.add_argument(
        "--cpus",
        required=True,
        type=int,
        help="CPU cores to use.",
    )

    args = parser.parse_args()

    cell_approx_ds = BaseDataSet.from_pickle(args.cell_approximation_infile)
    abstract_structure_ds = BaseDataSet.from_pickle(args.ast_infile)

    x = AnnotateCellDensityTransformation()(
        cpus=1,
        abstract_structure=abstract_structure_ds,
        cell_approximation=cell_approx_ds,
    )

    x.to_pickle(args.outfile)
