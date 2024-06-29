# Statistical Forecasting Engine

This Statistical Forecasting Engine is a powerful tool built using the `statsforecast` library. It provides a standardized approach to time series forecasting, allowing users to generate forecasts using multiple models, evaluate their performance, and select the best-performing model for each unique time series.

## Features

1. **Flexible Input**: 
   - Accepts input data in CSV or Parquet format
   - Configurable parameters via an Excel file

2. **Multiple Forecasting Models**:
   - Supports various models including ARIMA, Holt-Winters, Croston, Dynamic Optimized Theta, Seasonal Naive, Auto ETS, Auto ARIMA, Naive, and Window Average
   - Allows selection of multiple models for comparison

3. **Time Series Handling**:
   - Supports various time frequencies (Hourly, Daily, Weekly, Monthly, Yearly)
   - Automatically handles missing data points

4. **Cross-Validation**:
   - Implements cross-validation to evaluate model performance
   - Configurable number of cross-validation windows

5. **Model Evaluation**:
   - Supports multiple error metrics (MSE, RMSE, MAPE)
   - Selects the best-performing model for each unique time series

6. **Fallback Model**:
   - Option to specify a fallback model for robustness

7. **Baseline Comparison**:
   - Generates forecasts using a specified baseline model for comparison

8. **Visualization**:
   - Includes plotting functionality to visualize forecasts

9. **Output**:
   - Generates a comprehensive Excel file containing:
     - Final data (including historical data and forecasts)
     - Evaluation data (model performance metrics)

## Usage

1. Prepare your input data in CSV or Parquet format
2. Set up the configuration file (`Forecasting_config.xlsx`) with desired parameters
3. Run the script to generate forecasts and evaluate models
4. Retrieve the output Excel file containing results and evaluations

## Requirements

- Python 3.x
- Libraries: statsforecast, pandas, xlsxwriter, datasetsforecast

## Configuration Options

- Baseline models
- Forecasting models (multiple can be selected)
- Forecasting period
- Validation period
- Forecast time level (Hourly, Daily, Weekly, Monthly, Yearly)
- Error metric (MSE, RMSE, MAPE)
- Fallback model
- Number of cross-validation windows

## Output

The script generates an Excel file with two sheets:
1. **Final Data**: Contains historical data, forecasts from all models, best-fit forecast, and baseline forecast
2. **Evaluation Data**: Provides performance metrics for each model and identifies the best model for each unique time series

This Statistical Forecasting Engine provides a comprehensive solution for time series forecasting, model evaluation, and selection, making it a valuable tool for demand planning, inventory management, and other forecasting applications.
