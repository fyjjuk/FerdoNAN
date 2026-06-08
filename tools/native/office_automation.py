import pandas as pd

def run(input_data: dict) -> dict:
    # Regla: Manipulación headless a nivel de datos (Regla #13)
    file_path = input_data.get("file_path")
    operation = input_data.get("operation")
    try:
        if operation == "read_excel":
            df = pd.read_excel(file_path)
            return {"result": df.to_dict()}
        return {"error": "Operación no soportada"}
    except Exception as e:
        return {"error": str(e)}
