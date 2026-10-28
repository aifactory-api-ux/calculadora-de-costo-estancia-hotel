# hotel-booking

Librería Python para calcular el costo de una estadía de hotel de forma determinista:
cuenta las noches, aplica la tarifa de cada noche —con recargo de fin de semana— y
devuelve el total con la tasa turística y el descuento por estadías largas.

Solo usa la biblioteca estándar (`datetime`, `decimal`): no tiene servidor, ni
interfaz, ni dependencias de terceros.

## Instalación

Como dependencia en el entorno donde corren los scripts:

```bash
pip install .
```

## Uso

```python
from booking import nights, nightly_rate, stay_total
```

### API

| Función | Firma | Resultado |
| --- | --- | --- |
| `nights` | `nights(check_in: date, check_out: date) -> int` | Cantidad de noches de la estadía. |
| `nightly_rate` | `nightly_rate(day: date, room: str) -> Decimal` | Tarifa de la noche que comienza en `day`. |
| `stay_total` | `stay_total(check_in: date, check_out: date, room: str, guests: int) -> Decimal` | Costo total de la estadía. |

Errores:

- `nights`
  - `TypeError`: `check_in` o `check_out` no son instancias de `datetime.date`
    (un `datetime.datetime` también se rechaza, aunque sea subclase de `date`).
  - `ValueError`: `check_out` no es posterior a `check_in`, o la estadía supera
    las 30 noches.
- `nightly_rate`
  - `TypeError`: `day` no es una instancia de `datetime.date`.
  - `ValueError`: el tipo de habitación no es conocido.
- `stay_total`
  - `TypeError`: alguna fecha no es una instancia de `datetime.date`, o `guests`
    no es un `int` (un `bool` se rechaza).
  - `ValueError`: el rango de fechas no es válido, el tipo de habitación no es
    conocido, o `guests` está fuera del rango `1..capacidad` de la habitación.

## Tarifas y capacidades

| Habitación | Tarifa base por noche | Capacidad |
| --- | --- | --- |
| `single` | 50.00 | 1 huésped |
| `double` | 80.00 | 2 huéspedes |
| `suite` | 150.00 | 4 huéspedes |

Reglas de precio:

- Las noches que **comienzan** en viernes o sábado llevan un recargo del 25%.
- La tasa turística es de 2.50 por huésped y por noche.
- Las estadías de **7 noches o más** reciben un 10% de descuento sobre el
  subtotal de habitación, nunca sobre la tasa turística.
- Todos los importes se redondean a 2 decimales con `ROUND_HALF_UP`.

## Ejemplo

Del 2026-01-02 (viernes) al 2026-01-04, habitación `double` y 2 huéspedes:

```python
from datetime import date

from booking import stay_total

stay_total(date(2026, 1, 2), date(2026, 1, 4), "double", 2)
# Decimal('210.00')
```

El total es `100.00` de la noche del viernes, `100.00` de la noche del sábado y
`10.00` de tasa turística: `210.00`.

## Pruebas

```bash
pip install pytest
python -m pytest
```

La suite se ejecuta desde la raíz del repositorio sin instalar el paquete: la
configuración de pytest agrega `src` al `sys.path`.

## Contenedores

El repositorio incluye un `Dockerfile` y un `docker-compose.yml` en la raíz. Como
la librería no tiene servidor, el comando por defecto de la imagen ejecuta la
suite de pruebas:

```bash
docker compose up --build
```

El contenedor no expone puertos ni monta volúmenes: corre la suite y termina con
el código de salida de `pytest`.
