# Solucion: SyntaxError invalid syntax (line 0) en Rocketbot execpython

## Error reportado

```
2026-04-08 08:33:53.995814 - ERROR - EXCEPTION IN (<string> script, L_135 ""):
SyntaxError: invalid syntax (<string>, line 0)
```

## Analisis de la causa raiz

El error ocurre en **linea 0**, lo cual es clave: Python numera lineas desde 1.
Un error en "linea 0" significa que el problema esta **antes de que Python lea
la primera linea de codigo**, es decir, en la carga/compilacion del archivo.

Rocketbot `execpython` funciona asi internamente:
1. Lee el contenido del archivo `.py` como string
2. Ejecuta `exec(contenido)` o `compile(contenido, '<string>', 'exec')`
3. Si el string tiene problemas de encoding, falla en linea 0

## Causas probables (ordenadas por probabilidad)

### 1. BOM (Byte Order Mark) en el archivo - MAS PROBABLE

Si el archivo `FechaConGasto.py` fue creado/editado con un editor que guarda
UTF-8 con BOM (como Notepad de Windows), los 3 bytes invisibles `EF BB BF` al
inicio del archivo causan exactamente este error.

**Como verificar:**
```cmd
:: En PowerShell
format-hex FechaConGasto.py | Select-Object -First 1
:: Si la primera linea muestra EF BB BF, tiene BOM
```

**Solucion:**
- Abrir en **Notepad++** > Menu Encoding > "Encode in UTF-8" (sin BOM) > Guardar
- O abrir en **VS Code** > Click en "UTF-8 with BOM" (esquina inferior derecha) > "Save with Encoding" > "UTF-8"
- O ejecutar el script `fix_execpython.py` incluido en este repositorio

### 2. Ruta mal construida (falta separador)

Si `{vGblStrRutaPython}` = `C:\Scripts` (sin `\` al final), la ruta resulta:
```
C:\ScriptsFechaConGasto.py   <-- MAL, archivo no encontrado
```

Rocketbot puede pasar un string vacio a exec(), generando el error en linea 0.

**Solucion en Rocketbot:**
```
# Opcion A: Asegurar que la variable termina en \
{vGblStrRutaPython} = C:\Scripts\

# Opcion B: Usar os.path.join en la asignacion
# En un execpython previo:
import os
ruta = os.path.join("{vGblStrRutaPython}", "FechaConGasto.py")

# Opcion C: Concatenar con separador explicito
{vGblStrRutaPython}\FechaConGasto.py
```

**Como verificar:**
Agrega un paso `execpython` ANTES del que falla con este codigo:
```python
ruta = r"{vGblStrRutaPython}FechaConGasto.py"
print(f"Ruta completa: {ruta}")
print(f"Existe: {__import__('os').path.exists(ruta)}")
```
Revisa el log de Rocketbot para ver el print.

### 3. Caracteres invisibles o encoding incorrecto

El archivo puede contener:
- Caracteres Unicode invisibles (U+200B zero-width space, etc.)
- Bytes nulos (`\x00`) por guardar en formato incorrecto
- Encoding mixto (parte UTF-8, parte Latin-1)

**Solucion:** Ejecutar `fix_execpython.py` que limpia todos estos problemas.

### 4. Contenido del script con sintaxis invalida

Aunque menos probable dado que el error es en linea 0, verificar:
- Que no haya caracteres especiales copiados de Word/PDF (comillas tipograficas `""` en vez de `""`)
- Que los indentados sean consistentes (no mezclar tabs y espacios)

**Comillas tipograficas problematicas:**
```python
# MAL (copiado de Word/PDF)
texto = "hola"   # <- comillas tipograficas, causan SyntaxError

# BIEN
texto = "hola"    # <- comillas rectas ASCII
```

## Pasos de solucion recomendados

### Paso 1: Ejecutar diagnostico
```cmd
python diagnostico_execpython.py "C:\tu\ruta\FechaConGasto.py"
```
Esto identifica el problema exacto.

### Paso 2: Aplicar correccion automatica
```cmd
python fix_execpython.py "C:\tu\ruta\FechaConGasto.py"
```
Esto crea un backup (.bak) y corrige BOM, bytes nulos y encoding.

### Paso 3: Verificar la ruta en Rocketbot
Agrega este bloque `execpython` ANTES del paso que falla:
```python
import os
ruta = r"{vGblStrRutaPython}" + "FechaConGasto.py"
if not os.path.isfile(ruta):
    raise FileNotFoundError(f"Script no encontrado: {ruta}")
with open(ruta, "rb") as f:
    primeros = f.read(3)
if primeros == b"\xef\xbb\xbf":
    raise ValueError("El archivo tiene BOM UTF-8. Guardar sin BOM.")
print(f"OK: {ruta} ({os.path.getsize(ruta)} bytes)")
```

### Paso 4: Si nada funciona - bypass exec de Rocketbot
Como alternativa, usa `execpython` con subprocess en lugar de depender del
mecanismo interno de Rocketbot:
```python
import subprocess
import sys
resultado = subprocess.run(
    [sys.executable, r"{vGblStrRutaPython}FechaConGasto.py"],
    capture_output=True, text=True
)
if resultado.returncode != 0:
    print(f"STDERR: {resultado.stderr}")
    raise RuntimeError(f"Script fallo con codigo {resultado.returncode}")
print(resultado.stdout)
```
Esto ejecuta el script como proceso separado, evitando el `exec()` interno de
Rocketbot que es sensible a problemas de encoding.

## Depuracion general de execpython en Rocketbot

1. **Revisar logs completos**: El log de Rocketbot esta en
   `C:\Users\<usuario>\AppData\Local\Rocketbot\logs\`

2. **Probar el script aislado**: Ejecuta desde cmd:
   ```cmd
   python "C:\ruta\completa\FechaConGasto.py"
   ```
   Si funciona aislado pero falla en Rocketbot, el problema es de
   encoding/BOM/ruta.

3. **Agregar try-except en execpython**:
   ```python
   try:
       ruta = r"{vGblStrRutaPython}FechaConGasto.py"
       with open(ruta, encoding="utf-8-sig") as f:
           codigo = f.read()
       exec(compile(codigo, ruta, "exec"))
   except Exception as e:
       print(f"Error tipo: {type(e).__name__}")
       print(f"Detalle: {e}")
       import traceback
       traceback.print_exc()
   ```
   Nota: `utf-8-sig` maneja automaticamente el BOM.

4. **Variable de ruta**: Verifica en Rocketbot con un `setVar` + print:
   ```
   Paso 1: setVar > vDebug = {vGblStrRutaPython}
   Paso 2: execpython > print("{vDebug}")
   ```
