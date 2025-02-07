import os

from ydata.sdk.dataset import get_dataset
from ydata.sdk.synthesizers import PrivacyLevel, RegularSynthesizer

# Do not forget to add your token as env variables
os.environ["YDATA_TOKEN"] = '{insert-your-token}'  # Remove if already defined


def main():
    """In this example, we demonstrate how to train a synthesizer
    with a high-privacy setting from a pandas DataFrame.
    After training a Regular Synthesizer, we request a sample.
    """
    X = get_dataset('titanic')

    # We initialize a regular synthesizer
    # As long as the synthesizer does not call `fit`, it exists only locally
    synth = RegularSynthesizer(name='Titanic Privacy')

    # We train the synthesizer on our dataset setting the privacy level to high
    synth.fit(
        X,
        privacy_level=PrivacyLevel.HIGH_PRIVACY
    )

    # We request a synthetic dataset with 50 rows
    sample = synth.sample(n_samples=50)
    print(sample)


if __name__ == "__main__":
    main()
