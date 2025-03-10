# Quickstart

Fabric SDK allows you to with an easy and familiar interface, to adopt a Data-Centric AI approach for the development of AI solutions.
Fabric SDK features were designed to support structure data, including *tabular data*, *time-series* and *transactional data*.

## Read data
To start leveraging the package features you should consume your data either through the Connectors or pandas.Dataframe.
The list of available connectors can be found here [add a link].

=== "From pandas dataframe"
    ```python
        # Example for a Google Cloud Storage Connector
        credentials = "{insert-credentials-file-path}"

        # We create a new connector for Google Cloud Storage
        connector = Connector(connector_type='gcs', credentials=credentials)

        # Create a Datasource from the connector
        # Note that a connector can be re-used for several datasources
        X = DataSource(connector=connector, path='gs://<my_bucket>.csv')
    ```
=== "From a connector"
    ```python
        # Load a small dataset
        X = pd.read_csv('{insert-file-path.csv}')

        # Init a synthesizer
        synth = RegularSynthesizer()

        # Train the synthesizer with the pandas Dataframe as input
        # The data is then sent to the cluster for processing
        synth.fit(X)
    ```

The synthesis process returns a `pandas.DataFrame` object.
Note that if you are using the `ydata-fabric-sdk` free version, all of your data is sent to a remote cluster on YData's infrastructure.

## Data synthesis flow
The process of data synthesis can be described into the following steps:

``` mermaid
stateDiagram-v2
  state read_data
  read_data --> init_synth
  init_synth --> train_synth
  train_synth --> generate_samples
  generate_samples --> [*]
```

The code snippet below shows how easy can be to start generating new synthetic data. The package includes a set of examples datasets for a quickstart.

```python
    from ydata.sdk.dataset import get_dataset

    #read the example data
    X = get_dataset('census')

    # Init a synthesizer
    synth = RegularSynthesizer()

    # Fit the synthesizer to the input data
    synth.fit(X)

    # Sample new synthetic data. The below request ask for new 1000 synthetic rows
    synth.sample(n_samples=1000)
```

!!! note "Do I need to prepare my data before synthesis?"
    The sdk ensures that the original behaviour is replicated. For that reason, there is no need to preprocess outlier observations or missing data.

    By default all the missing data is replicated as NaN.
