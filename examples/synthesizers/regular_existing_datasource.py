import os

from ydata.sdk.datasources import DataSource
from ydata.sdk.synthesizers import RegularSynthesizer

# Authenticate to Fabric to leverage the SDK - https://docs.sdk.ydata.ai/latest/sdk/installation/
# Make sure to add your token as env variable.
os.environ["YDATA_TOKEN"] = '{insert-token}'  # Remove if already defined


# In this example, we demonstrate how to train a synthesizer from an existing RDBMS Dataset.
# Make sure to follow the step-by-step gu ide to create a Dataset in Fabric's catalog: https://docs.sdk.ydata.ai/latest/get-started/create_multitable_dataset/
X = DataSource.get('{insert-datasource-id}')

# Init a multi-table synthesizer. Provide a connector so that the process of data synthesis write the
# synthetic data into the destination database
# Provide a connector ID as the write_connector argument. See in this tutorial how to get a connector ID
synth = RegularSynthesizer(name='existing_DS')

# Start the training of your synthetic data generator
synth.fit(X)

# As soon as the training process is completed you are able to sample a synthetic database
# The input expected is a percentage of the original database size
# In this case it was requested a synthetic database with the same size as the original
# Your synthetic sample was written to the database provided in the write_connector
synth.sample(n_samples=1000)
