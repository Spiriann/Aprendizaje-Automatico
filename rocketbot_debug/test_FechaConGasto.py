"""
Script de prueba: simula el entorno Rocketbot con los valores reales
para identificar donde falla FechaConGasto.py
"""
from datetime import datetime, timedelta
import calendar

# =========================
# Simulacion de GetVar/SetVar de Rocketbot
# =========================
variables_rocketbot = {
    'vGblStrFlujoCierreAnio': 'INACTIVO',
    'vGblStrFechaContGasto': '30/03/2026',
    'vGblDicInformacionCalendarioTributario': str({
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
    })
}

def GetVar(nombre):
    val = variables_rocketbot.get(nombre, '')
    print(f"  [GetVar] {nombre} = {repr(val)}")
    return val

def SetVar(nombre, valor):
    variables_rocketbot[nombre] = valor
    print(f"  [SetVar] {nombre} = {repr(valor)}")

# =========================
# SCRIPT ORIGINAL FechaConGasto.py (tal como lo subiste)
# =========================
print("=" * 60)
print("INICIO EJECUCION FechaConGasto.py")
print("=" * 60)

try:
    MESES_ES = {
        1: "ENERO",
        2: "FEBRERO",
        3: "MARZO",
        4: "ABRIL",
        5: "MAYO",
        6: "JUNIO",
        7: "JULIO",
        8: "AGOSTO",
        9: "SEPTIEMBRE",
        10: "OCTUBRE",
        11: "NOVIEMBRE",
        12: "DICIEMBRE"
    }

    # =========================
    # VARIABLES DE ENTRADA
    # =========================
    flujo_cierre_anio = GetVar('vGblStrFlujoCierreAnio')
    informacion_calendario_tributario = eval(GetVar('vGblDicInformacionCalendarioTributario'))

    # Primera fecha cont gasto
    fecha_cont_gasto = GetVar('vGblStrFechaContGasto')  # formato dd/mm/yyyy

    # Fecha contab automatica SAP (solo informativa aqui)
    fecha_contab_actual = 'FECHA SAP'

    trazabilidad_db = {}

    # =========================
    # FECHA EJECUCION BOT
    # =========================
    fecha_ejecucion = datetime.now()
    anio_actual = fecha_ejecucion.year
    mes_actual = fecha_ejecucion.month

    print(f"\n--- Datos de ejecucion ---")
    print(f"  fecha_ejecucion: {fecha_ejecucion}")
    print(f"  anio_actual: {anio_actual}")
    print(f"  mes_actual: {mes_actual}")

    fecha_cont_gasto_dt = datetime.strptime(fecha_cont_gasto, "%d/%m/%Y")
    anio_con_gast = fecha_cont_gasto_dt.year
    mes_con_gast = fecha_cont_gasto_dt.month

    print(f"  fecha_cont_gasto_dt: {fecha_cont_gasto_dt}")
    print(f"  anio_con_gast: {anio_con_gast}")
    print(f"  mes_con_gast: {mes_con_gast}")

    print("Fecha ejecucion bot:", fecha_ejecucion)
    print("Fecha cont gasto:", fecha_cont_gasto)

    # =========================
    # FLUJO ACTIVO (SOLO ENERO)
    # =========================
    if flujo_cierre_anio == "Activo":
        print("\n>>> RAMA: Flujo cierre anio ACTIVO")

        if mes_actual == 1:
            if fecha_cont_gasto_dt.year != anio_actual:
                nueva_fecha = datetime(anio_actual - 1, 12, 31).strftime("%d.%m.%Y")
                print("Fecha cont gasto NO corresponde al anio en curso")
                print("Fecha contab debe diligenciarse con:", nueva_fecha)
                SetVar('vGblStrFechaContGasto', nueva_fecha)
            else:
                print("Fecha cont gasto corresponde al anio en curso")
                print("Fecha contab se conserva:", fecha_contab_actual)
                SetVar('vGblStrFechaContGasto', fecha_contab_actual)
        else:
            print("Flujo Activo pero NO es Enero")
            print("Fecha contab se conserva:", fecha_contab_actual)
            SetVar('vGblStrFechaContGasto', fecha_contab_actual)

    # =========================
    # FLUJO INACTIVO (RESTO DEL ANIO)
    # =========================
    else:
        print("\n>>> RAMA: Flujo cierre anio INACTIVO")

        if fecha_cont_gasto_dt.year != anio_actual:
            print(">>> SUB-RAMA: anio NO corresponde")
            print("Accion: marcar registro como CONTABILIZACION ASISTIDA")

            trazabilidad_db["EstadoFase6"] = "Exitoso"
            trazabilidad_db["ObservacionesFase6"] = f"Registro cuenta con fecha. cont gasto del anio anterior"
            trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION ASISTIDA"

        else:
            print(">>> SUB-RAMA: anio SI corresponde")

            # Buscar fecha limite
            mes_es = MESES_ES[mes_con_gast]
            clave_buscar = f"{anio_con_gast}-{mes_es}"

            print(f"  mes_es: {mes_es}")
            print(f"  clave_buscar: {clave_buscar}")
            fecha_limite_str = informacion_calendario_tributario.get(clave_buscar, "")
            print(f"  fecha_limite_str: {repr(fecha_limite_str)}")

            if fecha_limite_str:
                fecha_limite_dt = datetime.strptime(fecha_limite_str, "%d/%m/%Y")
                print(f"  fecha_limite_dt: {fecha_limite_dt.date()}")
                print(f"  fecha_ejecucion.date(): {fecha_ejecucion.date()}")
                print(f"  Comparacion: {fecha_ejecucion.date()} <= {fecha_limite_dt.date()} = {fecha_ejecucion.date() <= fecha_limite_dt.date()}")

                if fecha_ejecucion.date() <= fecha_limite_dt.date():
                    print(">>> Fecha ejecucion <= Fecha limite")

                    print(f"  fecha_cont_gasto_dt.month ({fecha_cont_gasto_dt.month}) != mes_actual ({mes_actual}) = {fecha_cont_gasto_dt.month != mes_actual}")

                    if fecha_cont_gasto_dt.month != mes_actual:
                        # Ultimo dia del mes anterior
                        mes_anterior = mes_actual - 1 or 12
                        anio_mes_anterior = anio_actual if mes_actual != 1 else anio_actual - 1
                        ultimo_dia = calendar.monthrange(anio_mes_anterior, mes_anterior)[1]

                        print(f"  mes_anterior: {mes_anterior}")
                        print(f"  anio_mes_anterior: {anio_mes_anterior}")
                        print(f"  ultimo_dia: {ultimo_dia}")

                        nueva_fecha = datetime(
                            anio_mes_anterior, mes_anterior, ultimo_dia
                        ).strftime("%d.%m.%Y")

                        print("Mes cont gasto diferente al mes de ejecucion")
                        print("Fecha contab debe diligenciarse con:", nueva_fecha)
                        SetVar('vGblStrFechaContGasto', nueva_fecha)
                    else:
                        print("Mes cont gasto igual al mes de ejecucion")
                        print("Fecha contab se conserva:", fecha_contab_actual)
                        SetVar('vGblStrFechaContGasto', fecha_contab_actual)

                else:
                    print(">>> Fecha ejecucion > Fecha limite")
                    print("Fecha contab se conserva:", fecha_contab_actual)
                    SetVar('vGblStrFechaContGasto', fecha_contab_actual)

            else:
                print(">>> No existe fecha limite para el anio/mes")
                print("Fecha contab se conserva:", fecha_contab_actual)
                SetVar('vGblStrFechaContGasto', fecha_contab_actual)

    SetVar('vGblDicTrazabilidadDb', trazabilidad_db)

    print("\n" + "=" * 60)
    print("FIN EJECUCION - SIN ERRORES")
    print("=" * 60)

except Exception as e:
    print("\n" + "=" * 60)
    print(f"ERROR DETECTADO: {type(e).__name__}: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()

# Mostrar estado final de variables
print("\n--- Estado final de variables Rocketbot ---")
for k, v in variables_rocketbot.items():
    print(f"  {k} = {repr(v)}")
