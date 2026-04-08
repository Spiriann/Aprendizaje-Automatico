from datetime import datetime, timedelta
import calendar

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
flujo_cierre_anio = GetVar('vGblStrFlujoCierreAnio')  # 'Activo' | 'Inactivo'
informacion_calendario_tributario = eval(GetVar('vGblDicInformacionCalendarioTributario'))

# Extraer fecha cont gasto desde informacion de factura
informacion_factura = eval(GetVar('vGblRegInformacionFactura'))
fecha_cont_gasto_valor = (informacion_factura[0]['FecContGasto_hoc']).split('|')[0]
SetVar('vGblStrFechaContGasto', fecha_cont_gasto_valor)

# Primera fecha cont gasto (ejemplo)
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

fecha_cont_gasto_dt = datetime.strptime(fecha_cont_gasto, "%d/%m/%Y")
anio_con_gast = fecha_cont_gasto_dt.year
mes_con_gast = fecha_cont_gasto_dt.month

#fecha_ejecucion = fecha_ejecucion.strftime("%d/%m/%Y")
print("Fecha ejecucion bot:", fecha_ejecucion)
print("Fecha cont gasto:", fecha_cont_gasto)

# =========================
# FLUJO ACTIVO (SOLO ENERO)
# =========================
if flujo_cierre_anio == "Activo":
    print("Flujo cierre anio: ACTIVO")

    if mes_actual == 1:  # Enero
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
    print("Flujo cierre anio: INACTIVO")

    if fecha_cont_gasto_dt.year != anio_actual:
        print("Fecha cont gasto NO corresponde al anio en curso")
        print("Accion: marcar registro como CONTABILIZACION ASISTIDA")
        print("Observacion: Registro cuenta con fecha. cont gasto del anio anterior")
        print("Continuar con siguiente registro")

        trazabilidad_db["EstadoFase6"] = "Exitoso"
        trazabilidad_db["ObservacionesFase6"] = f"Registro cuenta con fecha. cont gasto del anio anterior"
        trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION ASISTIDA"

    else:
        print("Fecha cont gasto corresponde al anio en curso")

        # Buscar fecha limite
        mes_es = MESES_ES[mes_con_gast]
        clave_buscar = f"{anio_con_gast}-{mes_es}"

        print("CLAVE BUSCAR: ", clave_buscar)
        fecha_limite_str = informacion_calendario_tributario.get(clave_buscar, "")

        if fecha_limite_str:
            fecha_limite_dt = datetime.strptime(fecha_limite_str, "%d/%m/%Y")
            print("Fecha limite encontrada:", fecha_limite_dt.date())
            print("Fecha ejecucion:", fecha_ejecucion.date())

            if fecha_ejecucion.date() <= fecha_limite_dt.date():
                print("Fecha ejecucion <= Fecha limite")

                if fecha_cont_gasto_dt.month != mes_actual:
                    # Ultimo dia del mes anterior
                    mes_anterior = mes_actual - 1 or 12
                    anio_mes_anterior = anio_actual if mes_actual != 1 else anio_actual - 1
                    ultimo_dia = calendar.monthrange(anio_mes_anterior, mes_anterior)[1]

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
                print("Fecha ejecucion > Fecha limite")
                print("Fecha contab se conserva:", fecha_contab_actual)
                SetVar('vGblStrFechaContGasto', fecha_contab_actual)

        else:
            print("No existe fecha limite para el anio/mes")
            print("Fecha contab se conserva:", fecha_contab_actual)
            SetVar('vGblStrFechaContGasto', fecha_contab_actual)

SetVar('vGblDicTrazabilidadDb', trazabilidad_db)
