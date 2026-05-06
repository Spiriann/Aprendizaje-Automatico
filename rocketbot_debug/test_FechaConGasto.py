"""
Test de FechaConGasto.py corregido con valores reales de Rocketbot.
Prueba multiples escenarios para validar todas las ramas.
"""
from datetime import datetime
import calendar

# =========================
# Simulacion de GetVar/SetVar
# =========================
variables_rocketbot = {}

def GetVar(nombre):
    val = variables_rocketbot.get(nombre, '')
    return val

def SetVar(nombre, valor):
    variables_rocketbot[nombre] = valor


MESES_ES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}

CALENDARIO = {
    '2025-DICIEMBRE': '31/01/2026',
    '2026-ENERO':     '02/02/2026',
    '2026-FEBRERO':   '02/03/2026',
    '2026-MARZO':     '05/04/2026',
    '2026-ABRIL':     '03/05/2026',
    '2026-MAYO':      '02/06/2026',
    '2026-JUNIO':     '02/07/2026',
    '2026-JULIO':     '02/08/2026',
    '2026-AGOSTO':    '02/09/2026',
    '2026-SEPTIEMBRE':'01/10/2026',
    '2026-OCTUBRE':   '03/11/2026',
    '2026-NOVIEMBRE': '02/12/2026',
    '2026-DICIEMBRE': '31/01/2027'
}


def ejecutar_script(flujo, fecha_cont_gasto, fecha_ejecucion_override=None):
    """Ejecuta la logica del script con los parametros dados."""
    informacion_calendario_tributario = CALENDARIO
    trazabilidad_db = {}

    fecha_ejecucion = fecha_ejecucion_override or datetime.now()
    anio_actual = fecha_ejecucion.year
    mes_actual = fecha_ejecucion.month

    fecha_cont_gasto_dt = datetime.strptime(fecha_cont_gasto, "%d/%m/%Y")
    anio_con_gast = fecha_cont_gasto_dt.year
    mes_con_gast = fecha_cont_gasto_dt.month

    resultado_fecha = None

    if flujo == "Activo":
        if mes_actual == 1:
            if fecha_cont_gasto_dt.year != anio_actual:
                nueva_fecha = datetime(anio_actual - 1, 12, 31).strftime("%d.%m.%Y")
                resultado_fecha = nueva_fecha
                trazabilidad_db["EstadoFase6"] = "Exitoso"
                trazabilidad_db["ObservacionesFase6"] = "Cierre anio: fecha ajustada a 31.12 del anio anterior"
                trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"
            else:
                resultado_fecha = "(sin cambio)"
                trazabilidad_db["EstadoFase6"] = "Exitoso"
                trazabilidad_db["ObservacionesFase6"] = "Cierre anio: fecha corresponde al anio en curso"
                trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"
        else:
            resultado_fecha = "(sin cambio)"
            trazabilidad_db["EstadoFase6"] = "Exitoso"
            trazabilidad_db["ObservacionesFase6"] = "Cierre anio activo pero no es enero, sin cambios"
            trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"
    else:
        if fecha_cont_gasto_dt.year != anio_actual:
            resultado_fecha = "(sin cambio - ASISTIDA)"
            trazabilidad_db["EstadoFase6"] = "Exitoso"
            trazabilidad_db["ObservacionesFase6"] = "Registro cuenta con fecha cont gasto del anio anterior"
            trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION ASISTIDA"
        else:
            mes_es = MESES_ES[mes_con_gast]
            clave_buscar = f"{anio_con_gast}-{mes_es}"
            fecha_limite_str = informacion_calendario_tributario.get(clave_buscar, "")

            if fecha_limite_str:
                fecha_limite_dt = datetime.strptime(fecha_limite_str, "%d/%m/%Y")

                if fecha_ejecucion.date() <= fecha_limite_dt.date():
                    if fecha_cont_gasto_dt.month != mes_actual:
                        ultimo_dia = calendar.monthrange(anio_con_gast, mes_con_gast)[1]
                        nueva_fecha = datetime(
                            anio_con_gast, mes_con_gast, ultimo_dia
                        ).strftime("%d.%m.%Y")
                        resultado_fecha = nueva_fecha
                        trazabilidad_db["EstadoFase6"] = "Exitoso"
                        trazabilidad_db["ObservacionesFase6"] = f"Dentro de plazo. Fecha ajustada: {nueva_fecha}"
                        trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"
                    else:
                        resultado_fecha = "(sin cambio)"
                        trazabilidad_db["EstadoFase6"] = "Exitoso"
                        trazabilidad_db["ObservacionesFase6"] = "Dentro de plazo. Mes coincide"
                        trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"
                else:
                    resultado_fecha = "(sin cambio - ASISTIDA)"
                    trazabilidad_db["EstadoFase6"] = "Exitoso"
                    trazabilidad_db["ObservacionesFase6"] = f"Fecha limite vencida ({fecha_limite_str})"
                    trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION ASISTIDA"
            else:
                resultado_fecha = "(sin cambio - ASISTIDA)"
                trazabilidad_db["EstadoFase6"] = "Exitoso"
                trazabilidad_db["ObservacionesFase6"] = f"No se encontro fecha limite para {clave_buscar}"
                trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION ASISTIDA"

    return resultado_fecha, trazabilidad_db


# =========================
# ESCENARIOS DE PRUEBA
# =========================
print("=" * 80)
print("PRUEBAS FechaConGasto.py CORREGIDO")
print("=" * 80)

escenarios = [
    {
        "nombre": "TU CASO: Inactivo, marzo, ejecutado 8 abril (plazo vencido)",
        "flujo": "INACTIVO",
        "fecha_cont_gasto": "30/03/2026",
        "fecha_ejecucion": datetime(2026, 4, 8),
    },
    {
        "nombre": "Inactivo, marzo, ejecutado 3 abril (dentro de plazo)",
        "flujo": "INACTIVO",
        "fecha_cont_gasto": "30/03/2026",
        "fecha_ejecucion": datetime(2026, 4, 3),
    },
    {
        "nombre": "Inactivo, abril, ejecutado 8 abril (mismo mes)",
        "flujo": "INACTIVO",
        "fecha_cont_gasto": "15/04/2026",
        "fecha_ejecucion": datetime(2026, 4, 8),
    },
    {
        "nombre": "Inactivo, fecha del anio anterior",
        "flujo": "INACTIVO",
        "fecha_cont_gasto": "15/12/2025",
        "fecha_ejecucion": datetime(2026, 4, 8),
    },
    {
        "nombre": "Activo, enero, fecha anio anterior",
        "flujo": "Activo",
        "fecha_cont_gasto": "20/12/2025",
        "fecha_ejecucion": datetime(2026, 1, 15),
    },
    {
        "nombre": "Activo, enero, fecha mismo anio",
        "flujo": "Activo",
        "fecha_cont_gasto": "05/01/2026",
        "fecha_ejecucion": datetime(2026, 1, 15),
    },
]

for i, esc in enumerate(escenarios, 1):
    fecha_resultado, traz = ejecutar_script(
        esc["flujo"], esc["fecha_cont_gasto"], esc["fecha_ejecucion"]
    )
    print(f"\n--- Escenario {i}: {esc['nombre']} ---")
    print(f"  Entrada:  flujo={esc['flujo']}, fecha_cont_gasto={esc['fecha_cont_gasto']}, ejecucion={esc['fecha_ejecucion'].strftime('%d/%m/%Y')}")
    print(f"  Fecha resultado: {fecha_resultado}")
    print(f"  ResultadoSAP:    {traz.get('ResultadoSAP', 'NO DEFINIDO')}")
    print(f"  Observacion:     {traz.get('ObservacionesFase6', 'NO DEFINIDO')}")
