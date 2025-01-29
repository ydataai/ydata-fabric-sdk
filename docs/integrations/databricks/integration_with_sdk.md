# YData SDK in Databricks Notebooks

The [YData Fabric SDK](https://pypi.org/project/ydata-fabric-sdk/) provides a powerful set of tools for integrating and enhancing data within Databricks notebooks.
This guide covers the installation, basic usage, and advanced features of the Fabric SDK, helping users maximize
the potential of their data for AI and machine learning applications.

👨‍💻 ^^[Full code example and recipe can be found here](https://raw.githubusercontent.com/ydataai/academy/master/5%20-%20Integrations/databricks/YData%20Fabric%20SDK%20in%20Databricks%20notebooks)^^.

!!! note "Prerequisites"
    Before using the YData Fabric SDK in Databricks notebooks, ensure the following prerequisites are met:

    - Access to a Databricks workspace
    - A valid YData Fabric account and API key
    - Basic knowledge of Python and Databricks notebooks
    - A safe connection between your Databricks cluster and Fabric

**Best Practices**

- *Data Security:* Ensure API keys and sensitive data are securely managed.
- *Efficient Coding:* Use vectorized operations for data manipulation where possible.
- *Resource Management:* Monitor and manage the resources used by your clusters (Databricks and Fabric)
Databricks cluster to optimize performance.

### Installation

To install the YData SDK in a Databricks notebook, use the following command:
```python
%pip install ydata-fabric-sdk
dbutils.library.restartPython()
```
Ensure the installation is successful before proceeding to the next steps.

## Basic Usage - data integration
This section provides step-by-step instructions on connecting to YData Fabric and performing essential
data operations using the YData SDK within Databricks notebooks. This includes establishing a secure connection
to YData Fabric and accessing datasets.

### Connecting to YData Fabric
First, establish a connection to YData Fabric using your API key:

```python
import os

# Add your Fabric token as part of your environment variables for authentication
os.environ["YDATA_TOKEN"] = '<TOKEN>'
```

### Data access & manipulation
Once connected, you can access and manipulate data within YData Fabric. For example, to list available datasets:

```python
from ydata.sdk.datasources import DataSource

#return the list of available DataSources
DataSource.list()
```

To load a specific dataset into a Pandas DataFrame:

```python
#get the data from an existing datasource
dataset = DataSource.get('<DATASOURCE-ID>')
```

## Advanced Usage - Synthetic data generation

This section explores one of the most powerful features of the Fabric SDK for enhancing and refining data
within Databricks notebooks. This includes as generating synthetic data to augment
datasets or to generate privacy-preserving data.
By leveraging these advanced capabilities, users can significantly enhance the robustness and performance of their AI
and machine learning models, unlocking the full potential of their data.

### Privacy-preserving
Leveraging synthetic data allows to create privacy-preserving datasets that maintain real-world value,
enabling users to work with sensitive information securely while accessing utility of real data.

Check the SDK documentation for more information regarding [privacy-controls and anonymization](../../sdk/examples/synthesize_with_privacy_control.md).

#### From a datasource in YData Fabric
Users can generate synthetic data from datasource's existing in Fabric:

```python title="Train a synthetic data generator"
# From an existing Fabric datasource
from ydata.sdk.synthesizers import RegularSynthesizer

synth = RegularSynthesizer(name='<NAME-YOUR-MODEL>')
synth.fit(X=dataset)
```

```python title="Sample from a Synthetic data generator"
# From an existing Fabric datasource
from ydata.sdk.synthesizers import RegularSynthesizer

synth = RegularSynthesizer(name='<NAME-YOUR-MODEL>')
synth.fit(X=dataset)
```
After your synthetic data generator have been trained successfully you can generate as many synthetic datasets as needed
```python title='Sampling from the model that we have just trained'
from ydata.sdk.synthesizers import RegularSynthesizer
sample = synth.sample(100)
sample.head()
```

It is also possible to generate data from other synthetic data generation models previously trained:

```python title='Generating synthetic data from a previously trained model'
from ydata.sdk.synthesizers import RegularSynthesizer

existing_synth = RegularSynthesizer('<INSERT-SYNTHETIC-DATA-GENERATOR-ID>').get()
sample = existing_synth.sample(100)
```

#### From a datasource in Databricks
Another important integration is to train a synthetic data generator from a dataset that you are currently exploring
in your notebook environment.
In order to do so, we recommend that you create your dataset using
[YData Fabric integration connector to your Delta Lake](integration_connectors_catalog.md) and follow the flow for the creation
of a synthetic data generation models from Fabric existing dasources.

For a small dataset you can also follow [this tutorial](../../sdk/examples/synthesize_tabular_data.md).

### Data augmentation
Another key focus is on generating synthetic data to augment existing datasets.
This technique, particularly through conditional synthetic data generation, allows users to create targeted,
realistic datasets. By addressing data imbalances and enriching the training data, conditional synthetic data generation
significantly enhances the robustness and performance of machine learning (ML) models,
leading to more accurate and reliable outcomes.

```python title='Read data from a delta table'
# Read data from the catalog
df = spark.sql("SELECT * FROM ydata.default.credit_scoring_labeled")

# Display the dataframe
display(df)
```

After reading the data we need to convert it to pandas dataframe in order to create our synthetic data generation model.
For the augmentation use-case we will be leveraging Conditional Synthetic data generation.

```python title='Training a conditional synthetic data generator'
from ydata.sdk.synthesizers import RegularSynthesizer

# Convert Spark dataframe to pandas dataframe
pandas_df = df.toPandas()
pandas_df = pandas_df.drop('ID', axis=1)

# Train a synthetic data generator using ydata-fabric-sdk
synth = RegularSynthesizer(name='Synth credit scoring | Conditional')
synth.fit(pandas_df, condition_on='Label')

# Display the synthetic dataframe
display(synth)
```

Now that we have a trained conditional synthetic data generator we are able to generate a few samples controlling the
population behaviour based on the columns that we have conditioned the process to.

```python title="Generating a synthetic sample conditioned to column 'Label'"
#generate synthetic samples condition to Label
synthetic_sample = synth.sample(n_samples=len(pandas_df), condition_on={
            "Label": {
                        "categories": [{
                            "category": 1,
                            "percentage": 0.7
                        }]
        }
    }
)
```

After generating the synthetic data we can combine it with our dataset.

```python title='Convert the dataframe to Spark dataframe'
# Enable Arrow-based columnar data transfers
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")

#Create a spark dataframe from the synthetic dataframe
synthetic_df = spark.createDataFrame(synthetic_sample)

display(synthetic_df)
```

```python title="Combining the datasets"
# Concatenate the original dataframe with the synthetic dataframe
#removing the column ID as it is not used
df = df.drop('ID')
concatenated_df = df.union(synthetic_df)

# Display the concatenated dataframe
display(concatenated_df)
```

Afterwards you can use your augmented dataset to train a ^^[Machine Learning model using MLFlow](https://docs.databricks.com/en/mlflow/tracking-ex-scikit.html)^^.
