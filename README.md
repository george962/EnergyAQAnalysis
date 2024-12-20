# EnergyAQAnalysis

This repository contains the workflow, analysis, and visualizations for the project "Energy and Air Quality Analysis" for CDS DS 598 Fall 2024, at Boston University.

## Overview

The project utilizes historical and real-time data streams to analyze patterns, predict trends, and provide actionable insights into the impact of energy consumption on air quality in the regions of Los Angeles and New England. The repository includes workflows for data ingestion, exploratory data analysis (EDA), predictive modeling, visualization dashboards, and our paper.

## Data Sources

Historical energy generation data was sourced from the [U.S. Energy Information Administration (EIA)](https://www.eia.gov) via their official platform. Specifically, we utilized the **“hourly generation by energy source”** dataset, filtered by natural gas and coal, to align with daily air quality data integration from [OpenWeather](https://openweathermap.org/history).

For real-time streaming data, [ISO New England](https://webservices.iso-ne.com/docs/v1.1/) provided real-time data on natural gas and coal energy generation and [Ambee](https://www.getambee.com/api/air-quality) supplied real-time air quality information.

Our focus areas for analysis were **Boston** and **Los Angeles**, chosen for their contrasting environmental and energy usage patterns.

## Repository Structure

- `Arm Templates/`
  - Contains ARM templates for infrastructure as code.
- `Data Architecture/`
  - Includes architecture diagrams and related documentation.
- `EDA/`
  - Contains the exploratory data analysis (EDA) notebooks and scripts.
- `Power BI/`
  - Power BI files and related resources for data visualization and reporting.
- `Presentation and Paper/`
  - Contains slides, notes, and materials used for project presentations and technical paper.
- `Stream/`
  - Contains configurations and scripts for handling real-time data streaming.
- `Training Models/`
  - Contains Python files used for training machine learning models and their associated results.


## Tools and Technologies

- **Azure Data Factory**: Used for data ingestion and orchestration of data pipelines.
- **Azure Function App**: Utilized for serverless execution of custom functions to process or transform data in real-time.
- **Azure Event Hubs**: Used for handling real-time streaming data from various sources, enabling continuous monitoring of air quality and energy data.
- **Azure Databricks**: Leveraged for advanced analytics and machine learning model training, enabling scalable data processing and predictive modeling.
- **Azure Stream Analytics**: Used for real-time analytics and monitoring of data streams, providing insights into the impact of energy generation on air quality.
- **Power BI**: For creating interactive dashboards and visualizations, displaying trends and insights derived from the analysis.
- **Python**: Python notebooks are used locally for exploratory data analysis (EDA), model training, and data processing tasks.

## Future Scope

- Extend real-time data pipelines to enable continuous monitoring and improved anomaly detection.
- Incorporate additional data sources for more comprehensive regional analysis.
- Enhance model performance using advanced deep learning techniques.
