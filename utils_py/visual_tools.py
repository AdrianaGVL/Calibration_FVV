#!/usr/bin/env python

#######################
#  Created on: June 9, 2024
#  Author: Adriana GV
#######################

# Libraries
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from statsmodels.nonparametric.smoothers_lowess import lowess
import seaborn as sns

# Histogram
def hist_chart(data, title, xlabl, ylabl, saveplace, axxis_lim=False, axyis_lim=False):
    sns.histplot(data, kde=True, color='blue')
    if axxis_lim:
        plt.xlim(1000, 6000)
    if axyis_lim:
        plt.ylim(1000, 6000)
    plt.title(f'{title}')
    plt.xlabel(f'{xlabl}')
    plt.ylabel(f'{ylabl}')
    plt.savefig(f'{saveplace}.png')
    plt.close()
    return

# Double Histogram
def double_hist_chart(data1, data2, title, xlabl, ylabl, label1, label2, saveplace, axxis_lim=False, axyis_lim=False):
    plt.hist(data1, alpha=0.5, label=f'{label1}', color='orange')
    plt.hist(data2, alpha=0.5, label=f'{label2}', color='blue')
    if axxis_lim:
        plt.xlim(1000, 6000)
    if axyis_lim:
        plt.ylim(1000, 6000)
    plt.title(f'{title}')
    plt.xlabel(f'{xlabl}')
    plt.ylabel(f'{ylabl}')
    plt.legend(loc='best')
    plt.savefig(f'{saveplace}.png')
    plt.close()
    return

# Double Boxplot
def double_boxplot(data1, data2, title, xlabl, ylabl, label1, label2, saveplace):
    data = [data1, data2]
    sns.boxplot(data=data)
    plt.xticks([0, 1], [f'{label1}', f'{label2}'])
    plt.title(f'{title}')
    plt.xlabel(f'{xlabl}')
    plt.ylabel(f'{ylabl}')
    plt.savefig(f'{saveplace}.png')
    plt.close()
    return

# Joint KDE
def double_kde(data1, data2, title, xlabl, ylabl, label1, label2, saveplace):
    sns.kdeplot(data1, shade=True, label=f'{label1}')
    sns.kdeplot(data2, shade=True, label=f'{label2}')
    plt.title(f'{title}')
    plt.xlabel(f'{xlabl}')
    plt.ylabel(f'{ylabl}')
    plt.legend(loc='best')
    plt.savefig(f'{saveplace}.png')
    plt.close()
    return

# Bland-Altman (Bland-Altman plot)
def bla(data1, data2, title, xlabl, ylabl, saveplace, axxis_lim=False, axyis_lim=False):
    data1_np = np.array(data1)
    data2_np = np.array(data2)
    differences = data1_np - data2_np
    averages = (data1_np + data2_np) / 2
    plt.scatter(averages, differences, s=3)
    plt.title(f'{title}')
    if axxis_lim:
        plt.xlim(1000, 6000)
    if axyis_lim:
        plt.ylim(1000, 6000)
    plt.xlabel(f'Average between {xlabl} and {ylabl} depth values (mm)')
    plt.ylabel(f'Difference between {xlabl} and {ylabl}')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.grid(True)
    plt.savefig(f'{saveplace}.png')
    plt.close()
    return

# Regression
def reg_con_trend(data1, data2, title, xlabl, ylabl, label1, label2, saveplace, axxis_lim=False, axyis_lim=False):
    fig = px.scatter(pd.DataFrame({f'{label1}': data1, f'{label2}': data2}), x=f'{label1}', y=f'{label2}', labels={'x':f'{xlabl}', 'y':f'{ylabl}'}, title=f'{title}', trendline='ols', trendline_color_override='red')
    fig.write_html(f'{saveplace}.html')
    return

def reg_sin_trend(data1, data2, title, xlabl, ylabl, label1, label2, saveplace, axxis_lim=False, axyis_lim=False):
    fig = px.scatter(pd.DataFrame({f'{label1}': data1, f'{label2}': data2}), x=f'{label1}', y=f'{label2}', labels={'x':f'{xlabl}', 'y':f'{ylabl}'}, title=f'{title}')
    fig.write_html(f'{saveplace}.html')
    return

# Scatter
def scat_con_trend(data1, data2, title, xlabl, ylabl, label1, label2, saveplace):
    fig = px.scatter(pd.DataFrame({f'{label1}': data1, f'{label2}': data2}), x=f'{label1}', y=f'{label2}', labels={'x':f'{xlabl}', 'y':f'{ylabl}'}, title=f'{title}', trendline='ols', trendline_color_override='red')
    fig.write_html(f'{saveplace}.html')
    return

# Scatter
def scat_sin_trend(data1, data2, title, xlabl, ylabl, label1, label2, saveplace):
    fig = px.scatter(pd.DataFrame({f'{label1}': data1, f'{label2}': data2}), x=f'{label1}', y=f'{label2}', labels={'x':f'{xlabl}', 'y':f'{ylabl}'}, title=f'{title}')
    # fig.update_yaxes(range=[-3000,3000])
    # fig.update_xaxes(range=[min(data1),max(data1)])
    fig.write_html(f'{saveplace}.html')
    return

def lines(data1, data2, title, xlabl, ylabl, scenes, saveplace, regression='quadratic'):
    fig = go.Figure()
    for i in range(len(data1)):
        if regression == 'lowess':
            lowess_smoothed = lowess(data2[i], data1[i], frac=0.1)
            x_smooth = lowess_smoothed[:, 0]
            y_smooth = lowess_smoothed[:, 1]
        elif regression == 'quadratic':
            z = np.polyfit(data1[i], data2[i], 2)
            p = np.poly1d(z)
            x_smooth = np.linspace(min(data1[i]), max(data1[i]))
            y_smooth = p(x_smooth)
        elif regression == 'lineal':
            model = LinearRegression()
            model.fit(data1[i].reshape(-1, 1), data2[i])
            y_pred = model.predict(data1[i].reshape(-1, 1))
            x_smooth = np.linspace(data1[i].min(), data1[i].max(), 100)
            y_smooth = model.predict(x_smooth.reshape(-1, 1))

        # Añadir la traza de la línea suavizada
        fig.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines', name=f'{scenes[i]}'))

    # Configurar el layout del gráfico
    fig.update_layout(
        title=f'{title}',
        xaxis_title=f'{xlabl}',
        yaxis_title=f'{ylabl}'
    )
    fig.update_traces(showlegend=True)
    fig.write_html(f'{saveplace}_{regression}.html')
    return

def multifigs(df, saveplace):
    figs = []
    for col in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines+markers', name=col))
        fig.update_layout(title=f'Error values for {col}mm depth')
        fig.update_yaxes(title_text='Error values', range=[1000,6000])
        fig.update_xaxes(title_text='Index', range=[1000,6000])
        figs.append(fig)
    num_cols = len(df.columns)
    fig = make_subplots(rows=num_cols, cols=1, subplot_titles=df.columns)
    for i, f in enumerate(figs):
        fig.add_trace(f.data[0], row=i+1, col=1)
        fig.update_layout(height=800, width=1000, showlegend=True)
    fig.write_html(f'{saveplace}.html')
    return