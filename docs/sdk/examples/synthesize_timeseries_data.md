# Synthesize time-series data

**Use YData's *TimeSeriesSynthesizer* to generate time-series synthetic data**

Tabular data is the most common type of data we encounter in data problems.

When thinking about tabular data, we assume independence between different records, but this does not happen in reality. Suppose we check events from our day-to-day life, such as room temperature changes, bank account transactions, stock price fluctuations, and air quality measurements in our neighborhood. In that case, we might end up with datasets where measures and records evolve and are related through time. This type of data is known to be sequential or time-series data.

Thus, sequential or time-series data refers to any data containing elements ordered into sequences in a structured format.
Dissecting any time-series dataset, we see differences in variables' behavior that need to be understood for an effective generation of synthetic data. Typically any time-series dataset is composed of the following:

- Variables that define the order of time (these can be simple with one variable or composed)
- Time-variant variables
- Variables that refer to entities (single or multiple entities)
- Variables that are attributes (those that don't depend on time but rather on the entity)

For a more detailed tutorial please check [YData Fabric Academy ydata-fabric-sdk notebooks](https://github.com/ydataai/academy/tree/master).

Below find an example:

```python
--8<-- "examples/synthesizers/time_series_quickstart.py"
```
