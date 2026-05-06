"""
Script para corregir problemas comunes que causan:
  SyntaxError: invalid syntax (<string>, line 0)
en Rocketbot execpython.

Uso:
  python fix_execpython.py "C:\ruta\FechaConGasto.py"
"""

import sys
import os
import shutil


def fix_script(ruta):
    if not os.path.exists(ruta):
        print(f"[ERROR] No existe: {ruta}")
        return False

    # Backup
    backup = ruta + ".bak"
    shutil.copy2(ruta, backup)
    print(f"Backup creado: {backup}")

    with open(ruta, "rb") as f:
        raw = f.read()

    cambios = []

    # 1. Eliminar BOM
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
        cambios.append("BOM UTF-8 eliminado")

    # 2. Eliminar bytes nulos
    if b"\x00" in raw:
        raw = raw.replace(b"\x00", b"")
        cambios.append("Bytes nulos eliminados")

    # 3. Normalizar saltos de linea a CRLF (Windows/Rocketbot)
    raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n").replace(b"\n", b"\r\n")
    cambios.append("Saltos de linea normalizados a CRLF")

    # 4. Eliminar caracteres invisibles Unicode problematicos
    try:
        texto = raw.decode("utf-8")
    except UnicodeDecodeError:
        texto = raw.decode("latin-1")

    chars_problematicos = ["\ufeff", "\u200b", "\u200c", "\u200d", "\ufffe"]
    for ch in chars_problematicos:
        if ch in texto:
            texto = texto.replace(ch, "")
            cambios.append(f"Caracter U+{ord(ch):04X} eliminado")

    # 5. Asegurar nueva linea al final
    if not texto.endswith("\n") and not texto.endswith("\r\n"):
        texto += "\r\n"
        cambios.append("Nueva linea final agregada")

    # Guardar como UTF-8 sin BOM
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(texto)

    if cambios:
        print("Correcciones aplicadas:")
        for c in cambios:
            print(f"  - {c}")
    else:
        print("No se encontraron problemas de encoding.")

    # Verificar compilacion
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    try:
        compile(contenido, "<string>", "exec")
        print("\n[OK] El script corregido compila correctamente")
        return True
    except SyntaxError as e:
        print(f"\n[ERROR] El script aun tiene errores de sintaxis:")
        print(f"  Linea {e.lineno}: {e.msg}")
        if e.text:
            print(f"  Texto: {e.text.strip()}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python fix_execpython.py <ruta_al_script.py>")
        sys.exit(1)
    fix_script(sys.argv[1])
