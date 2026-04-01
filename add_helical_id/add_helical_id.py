import argparse
import starfile
import numpy as np


def main(input_file: str, output_file: str, cutoff: float):
    data = starfile.read(input_file)
    array = data[
        [
            "rlnCenteredCoordinateXAngst",
            "rlnCenteredCoordinateYAngst",
            "rlnCenteredCoordinateZAngst",
        ]
    ].to_numpy()

    # quickly produce distances between the particle and the next
    distances = np.sum((array - np.roll(array, -1, axis=0)) ** 2, axis=1) ** 0.5
    val = 1
    # need to randomize initial subset as this runs for 1 tomo only
    subset = np.random.choice([1,2])
    # don't keep randomizing subsets as we assume this has less drift from the wanted 50/50
    new_subset = {1: 2, 2: 1}
    subsets = []
    values = []
    for dist in distances:
        values.append(val)
        subsets.append(subset)
        if dist >= cutoff:
            val += 1
            subset = new_subset[subset]
    data["rlnHelicalTubeID"] = values
    data["rlnRandomSubset"] = subsets
    starfile.write(data, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process a starfile to include the rlnHelicalTubeID, it increments this value every time the distance between two sequential particles is bigger than the cutoff value."
    )

    parser.add_argument("input_file", help="Path to the input starfile")
    parser.add_argument("output_file", help="Path to the output starfile")
    parser.add_argument(
        "-c",
        "--cutoff",
        type=float,
        required=False,
        default=500,
        help="Cutoff value in Angstrom to split into new helix",
    )

    args = parser.parse_args()

    main(args.input_file, args.output_file, args.cutoff)
