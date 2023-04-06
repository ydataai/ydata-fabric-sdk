from numpy import int64
from pandas import DataFrame as pdDataFrame
from pandas import read_csv, to_datetime

from ydata.sdk.utils.cache import cache_file


def get_census() -> pdDataFrame:
    file_name = cache_file(
        "census_train.csv",
        "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data",
    )

    df = read_csv(
        file_name,
        header=None,
        index_col=False,
        names=[
            "age",
            "workclass",
            "fnlwgt",
            "education",
            "education-num",
            "marital-status",
            "occupation",
            "relationship",
            "race",
            "sex",
            "capital-gain",
            "capital-loss",
            "hours-per-week",
            "native-country",
        ],
    )

    # Prepare missing values
    df = df.replace("\\?", None, regex=True)

    return df


def get_titanic() -> pdDataFrame:
    file_name = cache_file(
        "titanic.csv",
        "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
    )

    return read_csv(file_name)


def get_airquality() -> pdDataFrame:
    file_name = cache_file(
        "pollution_us_2000_2016.csv",
        "https://query.data.world/s/mz5ot3l4zrgvldncfgxu34nda45kvb",
    )

    return read_csv(file_name, index_col=[0])


def get_occupancy() -> pdDataFrame:
    file_name = cache_file(
        "occupancy.csv",
        "https://code.datasciencedojo.com/datasciencedojo/datasets/raw/master/Occupancy%20Detection/datatraining.csv",
    )

    df = read_csv(file_name)
    df["date"] = to_datetime(
        df["date"], format="%m/%d/%Y %H:%M").values.astype(int64) // 10 ** 9
    return df


def get_dataset(name: str):
    DATASETS = {
        'census': get_census,
        'titanic': get_titanic,
        'airquality': get_airquality,
        'occupancy': get_occupancy
    }

    if name not in DATASETS:
        raise FileNotFoundError(
            f"Dataset {name} does not exist. Valid datasets are: {', '.join(DATASETS.keys())}.")

    return DATASETS[name]()
