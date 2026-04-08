"""
Diagnostico para el error:
  SyntaxError: invalid syntax (<string>, line 0)
en Rocketbot execpython.

Ejecuta este script FUERA de Rocketbot pasando la ruta del .py problema:
  python diagnostico_execpython.py "C:\ruta\al\script\FechaConGasto.py"

O bien, pega la ruta directamente en RUTA_SCRIPT abajo.
"""

import sys
import os

# --- Configura aqui si no pasas argumento por linea de comandos ---
RUTA_SCRIPT = r"C:\ruta\al\script\FechaConGasto.py"
# ------------------------------------------------------------------

def diagnosticar(ruta):
    print(f"=== Diagnostico execpython Rocketbot ===\n")
    print(f"Ruta recibida: '{ruta}'")
    print(f"Longitud ruta: {len(ruta)}")

    # 1. Verificar que la ruta existe
    if not os.path.exists(ruta):
        print(f"\n[ERROR] El archivo NO existe en: {ruta}")
        print("  -> Verifica que la variable {{vGblStrRutaPython}} termina en '\\\\'")
        print(f"  -> Directorio padre existe: {os.path.exists(os.path.dirname(ruta))}")

        # Mostrar que hay en el directorio padre si existe
        directorio = os.path.dirname(ruta)
        if os.path.isdir(directorio):
            archivos = os.listdir(directorio)
            print(f"  -> Contenido del directorio ({directorio}):")
            for a in archivos:
                print(f"       {a}")
        return

    print(f"[OK] El archivo existe")
    print(f"[OK] Tamano: {os.path.getsize(ruta)} bytes")

    # 2. Leer bytes crudos y verificar BOM
    with open(ruta, "rb") as f:
        raw = f.read()

    if raw[:3] == b"\xef\xbb\xbf":
        print("\n[ERROR] El archivo tiene BOM (Byte Order Mark) UTF-8")
        print("  -> ESTA ES LA CAUSA MAS PROBABLE del error en linea 0")
        print("  -> Solucion: Abre el archivo en Notepad++ o VS Code")
        print("     y guardalo como 'UTF-8 sin BOM'")
        print("  -> O ejecuta: fix_bom(ruta) de este mismo script")
    else:
        print("[OK] Sin BOM")

    if b"\x00" in raw:
        pos = raw.index(b"\x00")
        print(f"\n[ERROR] El archivo contiene bytes nulos en posicion {pos}")
        print("  -> Esto causa SyntaxError al compilar el script")
        print("  -> El archivo puede estar corrupto o guardado en formato incorrecto")
    else:
        print("[OK] Sin bytes nulos")

    if b"\r\n" in raw:
        print("[INFO] Saltos de linea: CRLF (Windows)")
    elif b"\r" in raw:
        print("[WARN] Saltos de linea: CR (Mac clasico) - puede causar problemas")
    else:
        print("[OK] Saltos de linea: LF (Unix)")

    # 3. Verificar encoding
    contenido = None
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            contenido = raw.decode(enc)
            print(f"[OK] Decodificable como: {enc}")
            break
        except UnicodeDecodeError:
            print(f"[WARN] No decodificable como: {enc}")

    if contenido is None:
        print("[ERROR] No se pudo decodificar el archivo con ninguna codificacion comun")
        return

    # 4. Verificar caracteres invisibles problematicos
    problemas = []
    for i, ch in enumerate(contenido[:200]):  # primeros 200 chars
        if ord(ch) < 9 and ch != "\x00":
            problemas.append((i, repr(ch), ord(ch)))
        elif ord(ch) in (0xFEFF, 0x200B, 0x200C, 0x200D, 0xFFFE):
            problemas.append((i, repr(ch), ord(ch)))

    if problemas:
        print(f"\n[ERROR] Caracteres invisibles/problematicos encontrados:")
        for pos, rep, code in problemas:
            print(f"  -> Posicion {pos}: {rep} (U+{code:04X})")
    else:
        print("[OK] Sin caracteres invisibles problematicos")

    # 5. Intentar compilar como lo hace Rocketbot
    print(f"\n--- Prueba de compilacion ---")

    # Simular lo que hace Rocketbot: leer y exec como string
    try:
        compile(contenido, "<string>", "exec")
        print("[OK] El script compila correctamente")
    except SyntaxError as e:
        print(f"[ERROR] SyntaxError al compilar:")
        print(f"  -> Linea: {e.lineno}")
        print(f"  -> Offset: {e.offset}")
        print(f"  -> Texto: {e.text}")
        print(f"  -> Mensaje: {e.msg}")

        if e.lineno and e.lineno > 0:
            lineas = contenido.splitlines()
            if e.lineno <= len(lineas):
                print(f"\n  Linea problematica ({e.lineno}):")
                inicio = max(0, e.lineno - 3)
                fin = min(len(lineas), e.lineno + 2)
                for num in range(inicio, fin):
                    marcador = " >>>" if num == e.lineno - 1 else "    "
                    print(f"  {marcador} {num+1}: {lineas[num]}")

    # 6. Verificar primeras lineas
    print(f"\n--- Primeras 5 lineas del archivo ---")
    lineas = contenido.splitlines()
    for i, linea in enumerate(lineas[:5]):
        print(f"  {i+1}: {repr(linea)}")

    print(f"\n--- Resumen ---")
    print(f"Total lineas: {len(lineas)}")
    print(f"Codificacion detectada: {enc}")


def fix_bom(ruta):
    """Elimina el BOM de un archivo UTF-8."""
    with open(ruta, "rb") as f:
        raw = f.read()
    if raw[:3] == b"\xef\xbb\xbf":
        with open(ruta, "wb") as f:
            f.write(raw[3:])
        print(f"BOM eliminado de: {ruta}")
    else:
        print("El archivo no tiene BOM.")


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_SCRIPT
    diagnosticar(ruta)
