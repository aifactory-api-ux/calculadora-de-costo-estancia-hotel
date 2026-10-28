"""Pruebas del conteo de noches, de la validación de fechas, de la tarifa nocturna
y del costo total de una estadía."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from booking import nights, nightly_rate, stay_total


def test_counts_a_single_night():
    assert nights(date(2026, 1, 5), date(2026, 1, 6)) == 1


def test_counts_two_nights():
    assert nights(date(2026, 1, 2), date(2026, 1, 4)) == 2


def test_counts_a_stay_spanning_a_month_boundary():
    assert nights(date(2026, 1, 30), date(2026, 2, 2)) == 3


@pytest.mark.parametrize("invalid", ["2026-01-02", None, 20260102])
def test_rejects_a_check_in_that_is_not_a_date(invalid):
    with pytest.raises(TypeError):
        nights(invalid, date(2026, 1, 4))


@pytest.mark.parametrize("invalid", ["2026-01-04", None, 20260104])
def test_rejects_a_check_out_that_is_not_a_date(invalid):
    with pytest.raises(TypeError):
        nights(date(2026, 1, 2), invalid)


def test_rejects_a_check_in_that_is_a_datetime():
    with pytest.raises(TypeError):
        nights(datetime(2026, 1, 2, 10, 30), date(2026, 1, 4))


def test_rejects_a_check_out_that_is_a_datetime():
    with pytest.raises(TypeError):
        nights(date(2026, 1, 2), datetime(2026, 1, 4, 18, 0))


def test_type_error_names_the_invalid_argument():
    with pytest.raises(TypeError, match="check_in"):
        nights("2026-01-02", date(2026, 1, 4))


def test_rejects_a_same_day_check_out():
    with pytest.raises(ValueError):
        nights(date(2026, 1, 2), date(2026, 1, 2))


def test_rejects_a_check_out_before_the_check_in():
    with pytest.raises(ValueError):
        nights(date(2026, 1, 4), date(2026, 1, 2))


def test_accepts_a_stay_of_thirty_nights():
    assert nights(date(2026, 1, 1), date(2026, 1, 31)) == 30


def test_rejects_a_stay_of_thirty_one_nights():
    with pytest.raises(ValueError):
        nights(date(2026, 1, 1), date(2026, 2, 1))


def test_base_rate_of_a_single_room():
    assert nightly_rate(date(2026, 1, 5), "single") == Decimal("50.00")


def test_base_rate_of_a_double_room():
    assert nightly_rate(date(2026, 1, 5), "double") == Decimal("80.00")


def test_base_rate_of_a_suite():
    assert nightly_rate(date(2026, 1, 5), "suite") == Decimal("150.00")


def test_friday_night_carries_the_surcharge():
    assert nightly_rate(date(2026, 1, 2), "double") == Decimal("100.00")


def test_saturday_night_carries_the_surcharge():
    assert nightly_rate(date(2026, 1, 3), "single") == Decimal("62.50")


def test_sunday_night_has_no_surcharge():
    assert nightly_rate(date(2026, 1, 4), "suite") == Decimal("150.00")


def test_monday_night_has_no_surcharge():
    assert nightly_rate(date(2026, 1, 5), "double") == Decimal("80.00")


def test_surcharged_rate_is_quantized_to_two_decimal_places():
    rate = nightly_rate(date(2026, 1, 2), "suite")

    assert rate == Decimal("187.50")
    assert rate.as_tuple().exponent == -2


def test_base_rate_carries_two_decimal_places():
    assert nightly_rate(date(2026, 1, 5), "double").as_tuple().exponent == -2


@pytest.mark.parametrize("room", ["deluxe", "", "Double", "SINGLE", None, 42])
def test_rejects_an_unknown_room(room):
    with pytest.raises(ValueError):
        nightly_rate(date(2026, 1, 5), room)


def test_rejects_a_day_that_is_not_a_date():
    with pytest.raises(TypeError):
        nightly_rate("2026-01-05", "double")


def test_rejects_a_day_that_is_a_datetime():
    with pytest.raises(TypeError):
        nightly_rate(datetime(2026, 1, 5, 10, 30), "double")


def test_total_of_the_worked_example():
    assert stay_total(date(2026, 1, 2), date(2026, 1, 4), "double", 2) == Decimal(
        "210.00"
    )


def test_total_of_a_single_night_includes_the_tourist_tax():
    assert stay_total(date(2026, 1, 5), date(2026, 1, 6), "single", 1) == Decimal(
        "52.50"
    )


def test_tourist_tax_scales_with_the_number_of_guests():
    one_guest = stay_total(date(2026, 1, 5), date(2026, 1, 6), "double", 1)
    two_guests = stay_total(date(2026, 1, 5), date(2026, 1, 6), "double", 2)

    assert one_guest == Decimal("82.50")
    assert two_guests == Decimal("85.00")


def test_tourist_tax_is_charged_per_guest_and_night():
    room_subtotal = sum(
        (
            nightly_rate(date(2026, 1, 5) + timedelta(days=offset), "double")
            for offset in range(2)
        ),
        Decimal("0.00"),
    )
    total = stay_total(date(2026, 1, 5), date(2026, 1, 7), "double", 2)

    assert room_subtotal == Decimal("160.00")
    assert total - room_subtotal == Decimal("10.00")


def test_a_seven_night_stay_gets_the_discount():
    assert stay_total(date(2026, 1, 5), date(2026, 1, 12), "double", 2) == Decimal(
        "575.00"
    )


def test_a_six_night_stay_does_not_get_the_discount():
    assert stay_total(date(2026, 1, 5), date(2026, 1, 11), "double", 2) == Decimal(
        "550.00"
    )


def test_the_discount_leaves_the_tourist_tax_untouched():
    room_subtotal = sum(
        (
            nightly_rate(date(2026, 1, 5) + timedelta(days=offset), "double")
            for offset in range(7)
        ),
        Decimal("0.00"),
    )
    tourist_tax = Decimal("2.50") * 2 * 7

    total = stay_total(date(2026, 1, 5), date(2026, 1, 12), "double", 2)

    assert room_subtotal == Decimal("600.00")
    assert total == room_subtotal * Decimal("0.9") + tourist_tax
    assert total != (room_subtotal + tourist_tax) * Decimal("0.9")


def test_total_accepts_a_guest_count_equal_to_the_capacity():
    assert stay_total(date(2026, 1, 5), date(2026, 1, 6), "suite", 4) == Decimal(
        "160.00"
    )


def test_total_rejects_a_fractional_guest_count():
    with pytest.raises(TypeError):
        stay_total(date(2026, 1, 5), date(2026, 1, 6), "double", 2.5)


def test_total_rejects_a_boolean_guest_count():
    with pytest.raises(TypeError):
        stay_total(date(2026, 1, 5), date(2026, 1, 6), "double", True)


def test_total_rejects_a_guest_count_that_is_not_an_integer():
    with pytest.raises(TypeError):
        stay_total(date(2026, 1, 5), date(2026, 1, 6), "double", "2")


def test_total_rejects_zero_guests():
    with pytest.raises(ValueError):
        stay_total(date(2026, 1, 5), date(2026, 1, 6), "double", 0)


def test_total_rejects_more_guests_than_the_room_holds():
    with pytest.raises(ValueError):
        stay_total(date(2026, 1, 5), date(2026, 1, 6), "single", 2)


@pytest.mark.parametrize("room", ["deluxe", "", "Double", "SINGLE", None, 42])
def test_total_rejects_an_unknown_room(room):
    with pytest.raises(ValueError):
        stay_total(date(2026, 1, 5), date(2026, 1, 6), room, 1)


def test_total_rejects_a_same_day_check_out():
    with pytest.raises(ValueError):
        stay_total(date(2026, 1, 2), date(2026, 1, 2), "double", 2)


def test_total_rejects_a_stay_longer_than_thirty_nights():
    with pytest.raises(ValueError):
        stay_total(date(2026, 1, 1), date(2026, 2, 1), "double", 2)


def test_total_rejects_a_check_in_that_is_not_a_date():
    with pytest.raises(TypeError):
        stay_total("2026-01-02", date(2026, 1, 4), "double", 2)


def test_total_rejects_a_check_in_that_is_a_datetime():
    with pytest.raises(TypeError):
        stay_total(datetime(2026, 1, 2, 10, 30), date(2026, 1, 4), "double", 2)


def test_total_carries_two_decimal_places():
    total = stay_total(date(2026, 1, 2), date(2026, 1, 4), "double", 2)

    assert total == Decimal("210.00")
    assert total.as_tuple().exponent == -2
