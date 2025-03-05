# Connectors

Fabric SDK allows users to consume data assets from remote storages through **Connectors**. YData **Connectors** support different types of storages, from filesystems to RDBMS'.

Below the list of available connectors:

| **Connector Name**   	| **Type**              	| **Supported File Types** 	  | **Useful Links**                                                      	| **Notes**                                                                                        	|
|----------------------	|-----------------------	|-----------------------------|-----------------------------------------------------------------------	|--------------------------------------------------------------------------------------------------	|
| AWS S3               	| Remote object storage 	| CSV, Parquet              	 | https://aws.amazon.com/s3/                                            	|                                                                                                  	|
| Google Cloud Storage 	| Remote object storage 	| CSV, Parquet              	 | https://cloud.google.com/storage                                      	|                                                                                                  	|
| Azure Blob Storage   	| Remote object storage 	| CSV, Parquet              	 | https://azure.microsoft.com/en-us/services/storage/blobs/             	|                                                                                                  	|
| File Upload          	| Local                 	| CSV                      	  | -                                                                     	| Maximum file size is 220MB. Bigger files should be uploaded and read from remote object storages 	|
| MySQL                	| RDBMS                 	| Not applicable           	  | https://www.mysql.com/                                                	| Supports reading whole schemas or specifying a query                                             	|
| Azure SQL Server     	| RDBMS                 	| Not applicable           	  | https://azure.microsoft.com/en-us/services/sql-database/campaign/     	| Supports reading whole schemas or specifying a query                                             	|
| PostgreSQL           	| RDBMS                 	| Not applicable           	  | https://www.postgresql.org/                                           	| Supports reading whole schemas or specifying a query                                             	|
| Snowflake            	| RDBMS                 	| Not applicable           	  | https://docs.snowflake.com/en/sql-reference-commands                  	| Supports reading whole schemas or specifying a query                                             	|
| Google BigQuery      	| Data warehouse        	| Not applicable           	  | https://cloud.google.com/bigquery                                     	|                                                                                                  	|
| Azure Data Lake      	| Data lake             	| CSV, Parquet         	      | https://azure.microsoft.com/en-us/services/storage/data-lake-storage/ 	|                                                                                                  	|

More details can be found at [**Connectors APi Reference Docs**](../reference/api/connectors/connector.md).
