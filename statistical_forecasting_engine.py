# -*- coding: utf-8 -*-
"""Statistical_Forecasting_Engine.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EKcthbVCRHmOFaKtBltVP1sgiyaOn3eq
"""

from statsforecast import StatsForecast
from utilsforecast.losses import *
from utilsforecast.evaluation import evaluate
import pandas as pd
from statsforecast.models import (
    ARIMA, HoltWinters, CrostonClassic as Croston, HistoricAverage,
    DynamicOptimizedTheta as DOT, SeasonalNaive, AutoETS, AutoARIMA, Naive, WindowAverage
)
import os
import time

def print_timestamp(process_name):
    print(f"{process_name} - {time.strftime('%Y-%m-%d %H:%M:%S')}")

config_df = pd.read_excel("/content/Forecasting_config.xlsx", engine='openpyxl')
config = config_df.set_index('Parameters').to_dict()['Values']

BASELINE_MODEL = config.get('Baseline models')
FORECAST_MODELS = config.get('Forecasting models').split(',')
FORECAST_PERIOD = int(config.get('Forecasting period'))
VALIDATION_PERIOD = int(config.get('Validation period'))
FORECAST_TIME_LEVEL = config.get('Forecast Time level')
ERROR_METRIC = config.get('Error metric')
FALLBACK_MODEL = config.get('Fallback model')
NUM_CROSSVALIDATION = int(config.get('Number of Crossvalidation'))

time_level_mapping = {
    'Hourly': 24,
    'Daily': 365,
    'Weekly': 52,
    'Monthly': 12,
    'Yearly': 1
}

time_level = config.get('Forecast Time level')
season_length = time_level_mapping.get(time_level, 1)

models = {
    'Croston': Croston(),
    'Historic Average': HistoricAverage(),
    'HoltWinters': HoltWinters(),
    'SeasonalNaive': SeasonalNaive(season_length=season_length),
    'DynamicOptimisedTheta': DOT(season_length=season_length),
    'AutoETS': AutoETS(),
    'AutoArima': AutoARIMA(),
    'Naive': Naive(),
    'Window Average': WindowAverage(window_size=season_length)
}

model_name = config.get('Baseline models')
if model_name in models:
    BASELINE_MODEL = models[model_name]
else:
    BASELINE_MODEL = None

print(BASELINE_MODEL)

fallback_model = models.get(FALLBACK_MODEL.strip(), None)

TIME_LEVEL = {
    'Weekly': 'W',
    'Hourly': 'H',
    'Daily': 'D',
    'Monthly': 'M',
    'Yearly': 'Y',
}

time_level = config.get('Forecast Time level')
if time_level in TIME_LEVEL:
    FORECAST_TIME_LEVEL = TIME_LEVEL[time_level]
else:
    FORECAST_TIME_LEVEL = 1

print(FORECAST_TIME_LEVEL)

error_metrics = {
    'MSE': mse,
    'RMSE': rmse,
    'MAPE': mape
}

ERROR_METRIC = config.get('Error metric')
if ERROR_METRIC in error_metrics:
    ERROR_METRIC = error_metrics[ERROR_METRIC]

print(ERROR_METRIC)

def load_data(file_path):
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == '.csv':
        return pd.read_csv(file_path)
    elif file_extension == '.parquet':
        return pd.read_parquet(file_path)
    else:
        raise ValueError("Unsupported file format: only CSV and Parquet are supported.")

"""Data Preprocessing"""

print_timestamp("Start loading configuration")

file_path = '/content/Book2.csv'
Y_df = load_data(file_path)


Y_df['ds'] = pd.to_datetime(Y_df['ds'], format='%Y-%m-%d')
start_dates = Y_df.groupby('unique_id')['ds'].min().reset_index()
end_date = Y_df['ds'].max()


full_date_ranges = pd.DataFrame()

for index, row in start_dates.iterrows():
    unique_id = row['unique_id']
    start_date = row['ds']
    date_range = pd.date_range(start=start_date, end=end_date, freq='W')
    temp_df = pd.DataFrame({'unique_id': unique_id, 'ds': date_range})
    full_date_ranges = pd.concat([full_date_ranges, temp_df], ignore_index=True)


merged_df = pd.merge(full_date_ranges, Y_df, on=['unique_id', 'ds'], how='left')
merged_df['y'] = merged_df['y'].fillna(0)
merged_df = merged_df.sort_values(by=['unique_id', 'ds']).reset_index(drop=True)

Y_df=merged_df
print_timestamp("Finished loading configuration")

uids = Y_df['unique_id'].unique()[:]
Y_df = Y_df.query('unique_id in @uids')

Y_df

Y_df['ds'] = pd.to_datetime(Y_df['ds'], errors='coerce')
Y_df.dropna(subset=['ds'], inplace=True)

"""Build desired models"""

models = [models[model.strip()] for model in FORECAST_MODELS]

sf = StatsForecast(
    models=models,
    freq=FORECAST_TIME_LEVEL,
    fallback_model=fallback_model,
    n_jobs=-1,
)

"""Forecast on desired models"""

print_timestamp("Start loading configuration")
forecasts_df = sf.forecast(df=Y_df, h=FORECAST_PERIOD)
forecasts_df.()
print_timestamp("Finished loading configuration")

forecasts_df.tail()

print_timestamp("Start loading configuration")
baseline_sf = StatsForecast(
    models=[BASELINE_MODEL],
    freq=FORECAST_TIME_LEVEL,
    n_jobs=-1,
)
baseline_forecasts_df = baseline_sf.forecast(df=Y_df, h=FORECAST_PERIOD)
print_timestamp("Finished loading configuration")

baseline_forecasts_df.head()

train_df = Y_df.groupby('unique_id').apply(lambda x: x.head(len(x) - VALIDATION_PERIOD)).reset_index(drop=True)

"""Cross-validation for Evaluating models"""

min_length = VALIDATION_PERIOD * (NUM_CROSSVALIDATION + 1)
df = Y_df.groupby('unique_id').filter(lambda x: len(x) >= min_length)

print_timestamp("Start loading configuration")
crossvalidation_df = sf.cross_validation(
    df=df,
    h=VALIDATION_PERIOD,
    step_size=VALIDATION_PERIOD,
    n_windows=NUM_CROSSVALIDATION
)
print_timestamp("Finished loading configuration")

crossvalidation_df.head()

def evaluate_cross_validation(df, metric):
    df = df.reset_index()
    models = df.drop(columns=['unique_id', 'ds', 'cutoff', 'y']).columns.tolist()
    evals = []
    for cutoff in df['cutoff'].unique():
        eval_ = evaluate(df[df['cutoff'] == cutoff], metrics=[metric], models=models)
        evals.append(eval_)
    evals = pd.concat(evals)
    evals = evals.groupby('unique_id').mean(numeric_only=True)
    evals['best_model'] = evals.idxmin(axis=1)
    return evals

evaluation_df = evaluate_cross_validation(crossvalidation_df, ERROR_METRIC)

summary_df = evaluation_df.groupby('best_model').size().sort_values().to_frame()
summary_df.reset_index().columns = ["Model", "Nr. of unique_ids"]

print(summary_df)

def get_best_model_forecast(forecasts_df, evaluation_df):
    forecasts_df = forecasts_df.reset_index()
    df = forecasts_df.set_index(['unique_id', 'ds']).stack().to_frame().reset_index(level=2)
    df.columns = ['model', 'best_model_forecast']
    df = df.join(evaluation_df[['best_model']])
    df = df.query('model.str.replace("-lo-90|-hi-90", "", regex=True) == best_model').copy()
    df.loc[:, 'model'] = [model.replace(bm, 'best_model') for model, bm in zip(df['model'], df['best_model'])]
    df = df.drop(columns='best_model').set_index('model', append=True).unstack()
    df.columns = df.columns.droplevel()
    df.columns.name = None
    df = df.reset_index()
    return df

prod_forecasts_df = get_best_model_forecast(forecasts_df, evaluation_df)
prod_forecasts_df['best_model'] = prod_forecasts_df['best_model'].apply(lambda x: 0 if x < 0 else round(x, 2))
prod_forecasts_df.head()

comparison_df = pd.merge(prod_forecasts_df, baseline_forecasts_df, on=['unique_id', 'ds'], suffixes=('_best', '_baseline'))
comparison_df.head()

sf.plot(Y_df, comparison_df)

"""Return final File
- uniqid | ds | y |models|best fit|baseline|
- unique id | models (error) | bestfit

"""

Y_df['ds'] = pd.to_datetime(Y_df['ds'])
forecasts_df['ds'] = pd.to_datetime(forecasts_df['ds'])
comparison_df['ds'] = pd.to_datetime(comparison_df['ds'])

merged_df = pd.merge(forecasts_df, comparison_df, on=['unique_id', 'ds'], how='outer')
final_df = pd.merge(Y_df, merged_df, on=['unique_id', 'ds'], how='outer')
final_df = final_df[final_df['ds'].isin(Y_df['ds']) | final_df['ds'].isin(forecasts_df['ds'])]

final_df['ds'] = pd.to_datetime(final_df['ds'])
final_df.tail(200)

evaluation_df

output_file_path = '/content/Output.xlsx'
with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
    final_df.to_excel(writer, sheet_name='Final Data', index=False)
    evaluation_df.to_excel(writer, sheet_name='Evaluation Data', index=True)
