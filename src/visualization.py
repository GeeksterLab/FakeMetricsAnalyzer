# src/visualization.py

import matplotlib.pyplot as plt 
import seaborn as sns 
import plotly.express as px
import os 
import pandas as pd

def plot_metrics(data, save_path='plots/metrics_scatter.png'):
    # Creates a scatter plot comparing 'views' and 'likes', highlighting anomalies
    # A constant name when the path is always the same (in plot_metrics)
    # A dynamic name based on a variable (in plot_distribution)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    plt.figure(figsize=(10,6))
    sns.scatterplot(data=data, x='views', y='likes', hue='anomaly', palette=['blue','red'])
    plt.title("Scatter plot des vues vs likes avec anomalies")
    plt.xlabel("Vues")
    plt.ylabel("Likes")

    # Save the figure before displaying it
    plt.savefig(save_path)
    plt.show()
    print(f"Scratter saved to {save_path}")
    plt.close()

def plot_distribution(data, column, save_path=None):
    # Displays the distribution of a given column with a histogram

    # Defines a saved path by default if it is not provided
    if save_path is None:
        save_path = f'plots/distribution_{column}.png'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    plt.figure(figsize=(8,5))
    sns.histplot(data[column], kde=True)
    plt.title(f"Distribution de {column}")
    plt.xlabel(column)
    plt.ylabel("Fréquence")

    # Save the figure before displaying it
    plt.savefig(save_path)
    print(f"Figure saved to {save_path}")
    plt.show()
    plt.close()

def interactive_plot_metrics(data, output_file='plots/metrics_scatter_interactive.html'):
    """
    Creates an interactive scatter plot with Plotly and saves it as an HTML file.
    The plot allows exploration of the relationship between 'views' and 'likes',
    highlighting anomalies.

    :param data: DataFrame containing at least 'views' and 'likes'. May or may not have 'anomaly'.
    :param output_file: File path for the output HTML file.
    :return: The Plotly figure.
    """

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Work on a copy to avoid altering the original DataFrame
    df = data.copy()
    
    # If 'anomaly' is not present, we create a new column 'status' with all values set to 'Normal'
    if 'anomaly' not in df.columns:
        print("Warning: the 'anomaly' column is not present; all points will be marked 'Normal'.")
        # On crée une colonne status tout à 'Normal'
        df['status'] = 'Normal'
    else:
        # Otherwise we mappe anomaly → status
        df['status'] = df['anomaly'].apply(lambda x: 'Anomaly' if x == 1 else 'Normal')
    
    # Creating an interactive scatter plot
    fig = px.scatter(
        df,
        x='views',
        y='likes',
        color='status',
        title="Scatter Plot interactif des vues vs likes"
    )
    
    # Save in HTML
    fig.write_html(output_file)
    print(f"Interactive plot saved as {output_file}")
    return fig

# Create a sample DataFrame
data = pd.DataFrame({
    'views': [100, 200, 300, 400],
    'likes': [10, 20, 15, 30],
    'anomaly': [0, 1, 0, 0]
})

# Call the function
fig = interactive_plot_metrics(data)

def interactive_plot_distribution(data, column, output_file=None):
    # Create a interactif histogram with Plotly and save it
        # param data: DataFrame containing the data.
        # param column: The column for which to generate the histogram.
        # param output_file: File path for saving the output HTML file.
        # Defaults to 'plots/distribution_<column>_interactive.html'
        # return: The Plotly figure.

    if output_file is None:
        output_file = f'plots/distribution_{column}_interactive.html'

    # Ensure the file exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Create a interactif histogram 
    fig = px.histogram(data, x=column, nbins=30,
                        title=f"Histograme interactif de {column}",
                        labels={column: column.capitalize()})
    
    fig.write_html(output_file)
    print(f"Interactive distribution plot saved as {output_file}")
    return fig

# Call the function
fig = interactive_plot_distribution(data, column='views')
    