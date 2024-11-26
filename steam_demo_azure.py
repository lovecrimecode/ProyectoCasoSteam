import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import pandas as pd

# Replace with your Azure ML endpoint and API key
AZURE_ML_ENDPOINT = "http://bfb00433-95cc-474b-b0d9-81c3cfeacafb.southcentralus.azurecontainer.io/score"
API_KEY = "8Z6rpOoTFkQJHBuecFEP04KMs0urb88q"

# Azure ML Client for Predictions
class AzureMLClient:
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

def predict(self, input_data):
        response = requests.post(self.endpoint, headers=self.headers, json=input_data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

def prepare_payload(comments):
    # Prepara los datos en el formato esperado por el modelo
    payload = {
        "Inputs": {
            "input1": [{"Comment": comment} for comment in comments]
        }
    }
    return payload

# Process CSV with Azure ML
def process_predictions(response, original_comments, output_csv):
    # Procesa la respuesta del modelo y guarda un archivo CSV con los resultados
    predictions = response["Results"]["output1"]  # Ajusta según el esquema de salida de tu API
    predictions_df = pd.DataFrame(predictions)
    
    # Combina los comentarios originales con las predicciones
    results = pd.concat([original_comments.reset_index(drop=True), predictions_df], axis=1)
    results.to_csv(output_csv, index=False)
    print(f"Predicciones guardadas en {output_csv}")

def main():
    input_csv = "comentarios.csv"  # Archivo CSV de entrada con una columna 'Comment'
    output_csv = "predicciones.csv"  # Archivo CSV de salida con predicciones
    # Leer comentarios del archivo CSV
    try:
        df = pd.read_csv(input_csv)
        if "Comment" not in df.columns:
            raise ValueError("El archivo CSV no contiene una columna llamada 'Comment'.")

        comments = df["Comment"].tolist()
        print(f"Se encontraron {len(comments)} comentarios para procesar.")

        # Preparar y enviar los datos al servicio
        client = AzureMLClient(AZURE_ML_ENDPOINT, API_KEY)
        payload = prepare_payload(comments)
        response = client.predict(payload)

        # Guardar las predicciones en un nuevo archivo CSV
        process_predictions(response, df, output_csv)

    except Exception as e:
        print(f"Error: {e}")

# Load CSV Button Function
def load_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not save_path:
        return
    try:
        process_csv(file_path, save_path)
        messagebox.showinfo("Success", f"Predictions saved to {save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

    # Prompt user to save the processed CSV file
    save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if not save_path:
        return

    try:
        process_csv(file_path, save_path)
        messagebox.showinfo("Success", f"Predictions saved to {save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Main GUI
def setup_gui():
    root = tk.Tk()
    root.title("Azure ML CSV Analyzer")
    root.geometry("600x400")
    root.config(bg="#1B1B1B")

    # Add description label
    description_label = tk.Label(
        root,
        text="Carga tu CSV de prueba",
        font=("Arial", 16),
        fg="#FFFFFF",
        bg="#1B1B1B",
        pady=20
    )
    description_label.pack()

    # Add Upload CSV button
    load_csv_button = tk.Button(
        root,
        text="Upload CSV",
        command=load_csv,
        bg="#4CAF50",
        fg="white",
        bd=0,
        padx=20,
        pady=10
    )
    load_csv_button.pack(pady=20)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    setup_gui()