"""Cálculo del costo de estadías de hotel.

Punto de entrada de la librería: `nights` cuenta las noches de una estadía a
partir de las fechas de check-in y check-out, `nightly_rate` calcula la tarifa
de una noche según el tipo de habitación y `stay_total` determina el costo
total de la estadía con la tasa turística y el descuento por estadías largas.
"""

from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

MAX_STAY_NIGHTS = 30

#: Tarifa base por noche y tipo de habitación.
BASE_RATES: dict[str, Decimal] = {
    "single": Decimal("50.00"),
    "double": Decimal("80.00"),
    "suite": Decimal("150.00"),
}

#: Cantidad máxima de huéspedes por tipo de habitación.
ROOM_CAPACITY: dict[str, int] = {
    "single": 1,
    "double": 2,
    "suite": 4,
}

#: Recargo aplicado a las noches que comienzan en viernes o sábado.
WEEKEND_SURCHARGE = Decimal("0.25")

#: Tasa turística por huésped y por noche.
TOURIST_TAX_PER_GUEST_NIGHT = Decimal("2.50")

#: Descuento aplicado al subtotal de habitación en estadías largas.
LONG_STAY_DISCOUNT = Decimal("0.10")

#: Mínimo de noches para que la estadía obtenga el descuento.
LONG_STAY_MIN_NIGHTS = 7

#: Días de la semana según `date.weekday()`, donde el lunes es 0.
FRIDAY = 4
SATURDAY = 5


def _require_date(value: object, name: str) -> None:
    """Comprueba que el valor sea una fecha simple, no un `datetime`.

    Args:
        value: Valor a validar.
        name: Nombre del argumento, usado en el mensaje de error.

    Raises:
        TypeError: Si el valor no es una instancia de `datetime.date`.
    """
    if isinstance(value, datetime) or not isinstance(value, date):
        raise TypeError(
            f"{name} debe ser una instancia de datetime.date, "
            f"no {type(value).__name__}"
        )


def _money(value: Decimal) -> Decimal:
    """Redondea un importe a dos decimales con `ROUND_HALF_UP`."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _rate_for_room(room: str) -> Decimal:
    """Devuelve la tarifa base de un tipo de habitación.

    Args:
        room: Tipo de habitación.

    Returns:
        La tarifa base por noche.

    Raises:
        ValueError: Si el tipo de habitación no es conocido.
    """
    try:
        return BASE_RATES[room]
    except (KeyError, TypeError):
        raise ValueError(f"Habitación desconocida: {room!r}") from None


def _capacity_for_room(room: str) -> int:
    """Devuelve la capacidad de huéspedes de un tipo de habitación.

    Args:
        room: Tipo de habitación.

    Returns:
        La cantidad máxima de huéspedes admitidos.

    Raises:
        ValueError: Si el tipo de habitación no es conocido.
    """
    try:
        return ROOM_CAPACITY[room]
    except (KeyError, TypeError):
        raise ValueError(f"Habitación desconocida: {room!r}") from None


def _require_guests(guests: object) -> None:
    """Comprueba que la cantidad de huéspedes sea un entero.

    Args:
        guests: Valor a validar.

    Raises:
        TypeError: Si el valor no es un `int`. Los booleanos se rechazan
            porque en Python son subclase de `int`.
    """
    if isinstance(guests, bool) or not isinstance(guests, int):
        raise TypeError(
            f"guests debe ser un int, no {type(guests).__name__}"
        )


def _night_sequence(check_in: date, check_out: date) -> list[date]:
    """Devuelve las fechas de inicio de cada noche de la estadía.

    Args:
        check_in: Fecha de check-in.
        check_out: Fecha de check-out, posterior a `check_in`.

    Returns:
        Las fechas desde `check_in` hasta el día anterior a `check_out`.
    """
    return [
        check_in + timedelta(days=offset)
        for offset in range((check_out - check_in).days)
    ]


def nights(check_in: date, check_out: date) -> int:
    """Cuenta las noches de una estadía.

    Cuenta cada noche que comienza entre `check_in` y el día anterior a
    `check_out`.

    Args:
        check_in: Fecha de check-in.
        check_out: Fecha de check-out, posterior a `check_in`.

    Returns:
        La cantidad de noches de la estadía.

    Raises:
        TypeError: Si alguna de las fechas no es una instancia de
            `datetime.date`.
        ValueError: Si `check_out` no es posterior a `check_in` o si la
            estadía supera las 30 noches.
    """
    _require_date(check_in, "check_in")
    _require_date(check_out, "check_out")

    if check_out <= check_in:
        raise ValueError("check_out debe ser posterior a check_in")

    total_nights = (check_out - check_in).days
    if total_nights > MAX_STAY_NIGHTS:
        raise ValueError(
            f"La estadía no puede superar las {MAX_STAY_NIGHTS} noches"
        )

    return total_nights


def nightly_rate(day: date, room: str) -> Decimal:
    """Calcula la tarifa de la noche que comienza en `day`.

    Las noches que comienzan en viernes o sábado llevan un recargo del 25%
    sobre la tarifa base del tipo de habitación.

    Args:
        day: Fecha en la que comienza la noche.
        room: Tipo de habitación: `single`, `double` o `suite`.

    Returns:
        La tarifa de la noche, redondeada a dos decimales con
        `ROUND_HALF_UP`.

    Raises:
        TypeError: Si `day` no es una instancia de `datetime.date`.
        ValueError: Si el tipo de habitación no es conocido.
    """
    _require_date(day, "day")
    rate = _rate_for_room(room)

    if day.weekday() in (FRIDAY, SATURDAY):
        rate = rate * (Decimal("1") + WEEKEND_SURCHARGE)

    return _money(rate)


def stay_total(check_in: date, check_out: date, room: str, guests: int) -> Decimal:
    """Calcula el costo total de una estadía.

    Suma la tarifa de cada noche de la estadía — desde `check_in` hasta el día
    anterior a `check_out` — y agrega la tasa turística de `2.50` por huésped
    y por noche. Las estadías de 7 noches o más reciben un 10% de descuento
    sobre el subtotal de habitación, nunca sobre la tasa turística.

    Args:
        check_in: Fecha de check-in.
        check_out: Fecha de check-out, posterior a `check_in`.
        room: Tipo de habitación: `single`, `double` o `suite`.
        guests: Cantidad de huéspedes, entre 1 y la capacidad de la habitación.

    Returns:
        El costo total de la estadía, redondeado a dos decimales con
        `ROUND_HALF_UP`.

    Raises:
        TypeError: Si alguna fecha no es una instancia de `datetime.date` o si
            `guests` no es un `int`.
        ValueError: Si el rango de fechas no es válido, si el tipo de
            habitación no es conocido o si la cantidad de huéspedes excede la
            capacidad de la habitación.
    """
    total_nights = nights(check_in, check_out)
    _require_guests(guests)
    capacity = _capacity_for_room(room)

    if not 1 <= guests <= capacity:
        raise ValueError(
            f"guests debe estar entre 1 y {capacity} para una habitación {room!r}"
        )

    room_subtotal = sum(
        (nightly_rate(day, room) for day in _night_sequence(check_in, check_out)),
        Decimal("0.00"),
    )
    if total_nights >= LONG_STAY_MIN_NIGHTS:
        room_subtotal = room_subtotal * (Decimal("1") - LONG_STAY_DISCOUNT)

    tourist_tax = TOURIST_TAX_PER_GUEST_NIGHT * guests * total_nights

    return _money(room_subtotal + tourist_tax)
