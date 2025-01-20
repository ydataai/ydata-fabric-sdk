# Overview

This sections provides a detailed guide on integrating ^^[YData Fabric](https://ydata.ai/products/fabric)^^ with Databricks.
By combining Databricks and YData Fabric, users gain a comprehensive AI solution.
Fabric enables access to previously siloed data, enhances understanding,
and improves data quality. Meanwhile, Databricks provides the scalability needed to deliver robust AI capabilities.

## Integration benefits

- Enhanced Data Accessibility: Seamlessly access and integrate previously siloed data.
- Improved Data Quality: Use YData Fabric's tools to enhance the quality of your data through data preparation and augmentation.
- Scalability: Leverage Databricks' robust infrastructure to scale data processing and AI workloads.
- Streamlined Workflows: Simplify data workflows with connectors and SDKs, reducing manual effort and potential errors.
- Comprehensive Support: Benefit from extensive documentation and support for both platforms, ensuring smooth integration and operation.

## Integration methods

### Data Catalog - Connectors
YData Fabric provides a range of connectors that enable direct integration with Databricks' Unity Catalog and Delta Lake.
These connectors streamline data transfer and ensure seamless interoperability between the two platforms.

**Key Features:**

- Easy configuration
- Secure data transfer
- Data synchronization

### SDK
The ^^[YData Fabric SDK](https://pypi.org/project/ydata-fabric-sdk/)^^ offers a programmatic approach to integrating with Databricks.
It provides developers with the tools and libraries needed to automate and customize data workflows between
YData Fabric and Databricks.

**Key Features:**

- Python based interface
- Flexible and customizable
- Comprehensive documentation and support

Find a comprehensive guideline on using ^^[YData Fabric SDK in Databricks Notebooks](integration_with_sdk.md)^^.

### API
The YData Fabric API allows for integration via RESTful services, providing a versatile method to interact
with Databricks. This approach is ideal for applications requiring direct API calls and custom integrations.

**Key Features:**

- RESTful architecture
- Language-agnostic integration
- Detailed API documentation
- Support for a wide range of operations

## Integration diagram

The integration diagram below illustrates the interaction between **YData Fabric** and **Databricks**,
highlighting the data flow and key components involved in the integration process.

![Databricks diagram.png](..%2F..%2Fassets%2Fintegrations%2FDatabricks%20diagram.png)
