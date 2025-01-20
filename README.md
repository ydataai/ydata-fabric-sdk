# YData SDK

<p></p>
<p align="center"><img width="500" src="https://assets.ydata.ai/sdk/logo_SDK_col_red_black.png" alt="YData Logo"></p>
<p></p>

[![pypi](https://img.shields.io/pypi/v/ydata-fabric-sdk)](https://pypi.org/project/ydata-fabric-sdk)
![Pythonversion](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)
[![downloads](https://pepy.tech/badge/ydata-fabric-sdk/month)](https://pepy.tech/project/ydata-fabric-sdk)

---
🚀 YData SDK Version 1.0 Released! 🎉 - Data quality everywhere!

*ydata-fabric-sdk* v1 is here! Create a [YData Fabric account](https://ydata.ai/ydata-fabric-free-trial) so you can start using today!

We are excited to announce the release of YData Fabric SDK v1.0! This major release marks the beginning of long-term support for the package,
ensuring stability, continuous improvements, and ongoing support for all users. YData SDK empowers developers with easy access to state-of-the-art
data quality tools and generative AI capabilities. Stay tuned for more updates and new features!

---

<p align="center">
  <a href="https://docs.sdk.ydata.ai">Documentation</a>
  |
  <a href="https://ydata.ai">More on YData</a>
</p>


## Overview

The YData SDK is an ecosystem of methods that allows users to, through a python interface, adopt a Data-Centric approach towards the AI development. The solution includes a set of integrated components for data ingestion, standardized data quality evaluation and data improvement, such as synthetic data generation, allowing an iterative improvement of the datasets used in high-impact business applications.

Synthetic data can be used as Machine Learning performance enhancer, to augment or mitigate the presence of bias in real data. Furthermore, it can be used as a Privacy Enhancing Technology, to enable data-sharing initiatives or even to fuel testing environments.

Under the YData SDK hood, you can find a set of algorithms and metrics based on statistics and deep learning based techniques, that will help you to accelerate your data preparation.

### What you can expect:

YData SDK is composed by the following main modules:

- **Datasources**
  - YData’s SDK includes several connectors for easy integration with existing data sources. It supports several storage types, like filesystems and RDBMS. Check the list of connectors.
  - SDK’s Datasources run on top of Dask, which allows it to deal with not only small workloads but also larger volumes of data.

- **Synthesizers**
  - Simplified interface to train a generative model and learn in a data-driven manner the behavior, the patterns and original data distribution. Optimize your model for privacy or utility use-cases.
  - From a trained synthesizer, you can generate synthetic samples as needed and parametrise the number of records needed.

- **Synthetic data quality report** *Coming soon*
  - An extensive synthetic data quality report that measures 3 dimensions: privacy, utility and fidelity of the generated data. The report can be downloaded in PDF format for ease of sharing and compliance purposes or as a JSON to enable the integration in data flows.

- **Profiling** *Coming soon*
  - A set of metrics and algorithms summarizes datasets quality in three main dimensions: warnings, univariate analysis and a multivariate perspective.

### Supported data formats

- **Tabular**
The **RegularSynthesizer** is perfect to synthesize high-dimensional data, that is time-independent with high quality results.
- **Time-Series**
The **TimeSeriesSynthesizer** is perfect to synthesize both regularly and not evenly spaced time-series, from smart-sensors to stock.
