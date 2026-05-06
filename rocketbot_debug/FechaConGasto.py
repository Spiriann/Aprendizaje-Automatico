from datetime import datetime
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

# Primera fecha cont gasto
fecha_cont_gasto = GetVar('vGblStrFechaContGasto')  # formato dd/mm/yyyy

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
            trazabilidad_db["EstadoFase6"] = "Exitoso"
            trazabilidad_db["ObservacionesFase6"] = "Cierre anio: fecha ajustada a 31.12 del anio anterior"
            trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"
        else:
            print("Fecha cont gasto corresponde al anio en curso")
            print("Fecha contab se conserva (no se modifica)")
            trazabilidad_db["EstadoFase6"] = "Exitoso"
            trazabilidad_db["ObservacionesFase6"] = "Cierre anio: fecha corresponde al anio en curso"
            trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"
    else:
        print("Flujo Activo pero NO es Enero, no se modifica fecha")
        trazabilidad_db["EstadoFase6"] = "Exitoso"
        trazabilidad_db["ObservacionesFase6"] = "Cierre anio activo pero no es enero, sin cambios"
        trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"

# =========================
# FLUJO INACTIVO (RESTO DEL ANIO)
# =========================
else:
    print("Flujo cierre anio: INACTIVO")

    if fecha_cont_gasto_dt.year != anio_actual:
        print("Fecha cont gasto NO corresponde al anio en curso")
        print("Accion: marcar registro como CONTABILIZACION ASISTIDA")
        print("Observacion: Registro cuenta con fecha cont gasto del anio anterior")
        print("Continuar con siguiente registro")

        trazabilidad_db["EstadoFase6"] = "Exitoso"
        trazabilidad_db["ObservacionesFase6"] = "Registro cuenta con fecha cont gasto del anio anterior"
        trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION ASISTIDA"

    else:
        print("Fecha cont gasto corresponde al anio en curso")

        # Buscar fecha limite en calendario tributario
        mes_es = MESES_ES[mes_con_gast]
        clave_buscar = f"{anio_con_gast}-{mes_es}"

        print("CLAVE BUSCAR:", clave_buscar)
        fecha_limite_str = informacion_calendario_tributario.get(clave_buscar, "")

        if fecha_limite_str:
            fecha_limite_dt = datetime.strptime(fecha_limite_str, "%d/%m/%Y")
            print("Fecha limite encontrada:", fecha_limite_dt.date())
            print("Fecha ejecucion:", fecha_ejecucion.date())

            if fecha_ejecucion.date() <= fecha_limite_dt.date():
                print("Fecha ejecucion <= Fecha limite (dentro de plazo)")

                if fecha_cont_gasto_dt.month != mes_actual:
                    # Fecha cont gasto es de un mes anterior: usar ultimo dia de ese mes
                    ultimo_dia = calendar.monthrange(anio_con_gast, mes_con_gast)[1]
                    nueva_fecha = datetime(
                        anio_con_gast, mes_con_gast, ultimo_dia
                    ).strftime("%d.%m.%Y")

                    print("Mes cont gasto diferente al mes de ejecucion")
                    print("Fecha contab debe diligenciarse con:", nueva_fecha)
                    SetVar('vGblStrFechaContGasto', nueva_fecha)
                    trazabilidad_db["EstadoFase6"] = "Exitoso"
                    trazabilidad_db["ObservacionesFase6"] = f"Dentro de plazo. Fecha ajustada a ultimo dia del mes cont gasto: {nueva_fecha}"
                    trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"
                else:
                    print("Mes cont gasto igual al mes de ejecucion")
                    print("Fecha contab se conserva (no se modifica)")
                    trazabilidad_db["EstadoFase6"] = "Exitoso"
                    trazabilidad_db["ObservacionesFase6"] = "Dentro de plazo. Mes coincide, fecha sin cambios"
                    trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION AUTOMATICA"

            else:
                # Fecha limite vencida: el registro debe ir a contabilizacion asistida
                print("Fecha ejecucion > Fecha limite (plazo vencido)")
                print(f"Plazo para {clave_buscar} vencio el {fecha_limite_str}")
                print("Accion: marcar registro como CONTABILIZACION ASISTIDA")

                trazabilidad_db["EstadoFase6"] = "Exitoso"
                trazabilidad_db["ObservacionesFase6"] = f"Fecha limite vencida ({fecha_limite_str}). Registro requiere contabilizacion asistida"
                trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION ASISTIDA"

        else:
            print(f"No existe fecha limite para {clave_buscar} en calendario tributario")
            print("Accion: marcar registro como CONTABILIZACION ASISTIDA")

            trazabilidad_db["EstadoFase6"] = "Exitoso"
            trazabilidad_db["ObservacionesFase6"] = f"No se encontro fecha limite para {clave_buscar}"
            trazabilidad_db["ResultadoSAP"] = "CONTABILIZACION ASISTIDA"

SetVar('vGblDicTrazabilidadDb', trazabilidad_db)
print("Trazabilidad:", trazabilidad_db)
