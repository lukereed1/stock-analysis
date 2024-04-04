from util import convert_from_mil_to_bil


def discounted_cash_flow_analysis(growth_rate, ttm_fcf, margin_of_safety, terminal_multiplier):
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
    intrinsic_value = round(sum(discounted_values) + terminal_value_discounted, 2)
    intrinsic_value_mos_applied = round(intrinsic_value - (margin_of_safety / 100) * intrinsic_value, 2)
    print(f"Intrinsic Value without MOS Applied: {convert_from_mil_to_bil(intrinsic_value)}B")
    print(f"Intrinsic Value with MOS Applied: {convert_from_mil_to_bil(intrinsic_value_mos_applied)}B")


def get_sticker_price(growth_rate, ttm_eps, margin_of_safety, future_pe):
    future_eps = ttm_eps * (1 + (growth_rate / 100)) ** 10
    future_value = future_eps * future_pe
    current_price = round(future_value / 1.15 ** 10, 2)
    current_price_with_mos = round(current_price - (margin_of_safety / 100) * current_price, 2)
    print(f"Current sticker price without MOS Applied: {current_price}")
    print(f"Current sticker price with MOS Applied: {current_price_with_mos}")