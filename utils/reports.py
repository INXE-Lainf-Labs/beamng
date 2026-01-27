import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def minimap(pdf, df):
    # Gerando gráfico do plano cartesiano da rota
    plt.figure(figsize=(8, 8))
    scatter = plt.scatter(df['posX'], df['posY'], c=df['posZ'], cmap='viridis', s=100, alpha=0.7)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xlabel('Posição X')
    plt.ylabel('Posição Y')

    cbar = plt.colorbar(scatter)
    cbar.set_label('Posição Z')

    delta_t = df['time'].iloc[-1] - df['time'].iloc[0]
    plt.title(f'Trajeto percorrido na simulação - ({delta_t:.2f}s)')
    pdf.savefig()
    plt.close()

def generate_report(sim_path):
    
    df = pd.read_csv(f'./data/{sim_path}/readable.csv', sep=';')

    with PdfPages(f'./data/{sim_path}/report.pdf') as pdf:

        # Gera o gráfico do plano cartesiano
        minimap(pdf, df)