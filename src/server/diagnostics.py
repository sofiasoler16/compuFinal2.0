

def analizar_riesgo_ventana(historial_movimientos, historial_temperaturas):
    """
    Módulo Clínico: Analiza una ventana de tiempo buscando patrones de cólico.
    """
    alertas = []
    
    if len(historial_movimientos) < 30:
        return alertas
        
    revolcones = historial_movimientos.count("revolcandose")
    rascadas = historial_movimientos.count("rascar piso")
    guaneadas = historial_movimientos.count("guaneando")
    
    # 1. Patrón obstructivo
    if revolcones >= 2 and rascadas >= 2 and guaneadas == 0:
        alertas.append(f"PATRÓN CRÍTICO: {revolcones} revolcones y {rascadas} rascadas sin guanear.")
        
    # 2. Patrón de fiebre
    temp_promedio = sum(historial_temperaturas) / len(historial_temperaturas)
    if temp_promedio >= 40.0:
        alertas.append(f"FIEBRE SOSTENIDA: Promedio de {temp_promedio:.1f}°C")
        
    return alertas