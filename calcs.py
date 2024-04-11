def dcfa_calc(growth_rate, ttm_fcf, margin_of_safety, terminal_multiplier):
    yearly_fcf_growth = []
    fcf = ttm_fcf
    for i in range(10):
        fcf = fcf * (1 + (growth_rate / 100))
        yearly_fcf_growth.append(round(fcf, 2))

    discounted_values = []
    j = 1
    for i in range(10):
        discounted_value = yearly_fcf_growth[i] / 1.15 ** j
        discounted_values.append(round(discounted_value, 2))
        j += 1

    terminal_value = yearly_fcf_growth[9] * terminal_multiplier
    terminal_value_discounted = terminal_value / 1.15 ** 10
    intrinsic_value = int(sum(discounted_values) + terminal_value_discounted)
    intrinsic_value_mos_applied = int(intrinsic_value - (margin_of_safety / 100) * intrinsic_value)
    print(f"Intrinsic Value without MOS Applied: {intrinsic_value}")
    print(f"Intrinsic Value with MOS Applied: {intrinsic_value_mos_applied}")

    return intrinsic_value, intrinsic_value_mos_applied


def get_sticker_price(growth_rate, ttm_eps, margin_of_safety, future_pe):
    future_eps = ttm_eps * (1 + (growth_rate / 100)) ** 10
    future_value = future_eps * future_pe
    current_price = int(future_value / 1.15 ** 10, 2)
    current_price_with_mos = int(current_price - (margin_of_safety / 100) * current_price, 2)
    print(f"Current sticker price without MOS Applied: {current_price}")
    print(f"Current sticker price with MOS Applied: {current_price_with_mos}")


def calculate_growth_rate(time_frame_in_years, start_amount, end_amount):
    if start_amount < 0:
        start_amount = 1
    growth_rate = (end_amount / start_amount) ** (1 / time_frame_in_years) - 1
    if isinstance(growth_rate, complex):
        return "N/A"
    growth_rate = round(growth_rate * 100, 2)
    return growth_rate


def add_commas_to_num(value):
    return format(value, ",")

