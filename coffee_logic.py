# This module provides functions to calculate coffee brewing instructions for a Chemex.
# It is designed to be used with PyScript in an HTML frontend.
# Key functions include calculating water and coffee amounts, and generating step-by-step instructions.

from numpy import ceil

# Assuming Element is globally available from PyScript for DOM manipulation
# from js import Element # This line would be needed if running outside PyScript with a bridge

def cups_of_coffee_desired(cups: int) -> float:
    """
    Calculates the total grams of water needed based on the number of cups desired.

    Args:
        cups: The number of coffee cups desired. Each cup is assumed to be 250g of water.

    Returns:
        The total grams of water needed.
    """
    grams_per_cup = 250  # Standard grams of water per cup
    grams_of_water_needed = cups * grams_per_cup
    return grams_of_water_needed

def chemex(coffee_grams: float, water_ratio: int) -> list[float]:
    """
    Calculates the specific amounts of coffee, bloom water, and pour water for a Chemex brew.

    Args:
        coffee_grams: The total grams of coffee beans to use.
        water_ratio: The desired ratio of water to coffee (e.g., 17 means 17g water per 1g coffee).

    Returns:
        A list containing:
        - coffee_grams (float): The input amount of coffee.
        - bloom_water (float): Grams of water for the bloom phase.
        - pour_water (float): Grams of water for the main pour.
        - total_water (float): Total grams of water to be used.

    Raises:
        Exception: If coffee_grams or water_ratio are non-positive.
        Exception: If the amount of coffee exceeds 70g.
        Exception: If the total water calculated exceeds 900g (overflow risk).
        Exception: If total water is not sufficient for the bloom phase.
    """
    if coffee_grams <= 0:
        raise Exception("Number of coffee grams must be positive.")
    if coffee_grams > 70:
        raise Exception("Too much coffee (max 70g). Please use a smaller amount.")
    if water_ratio <= 0:
        raise Exception("Water ratio must be a positive number.")

    total_water = coffee_grams * water_ratio
    if total_water > 900:
        raise Exception("Too much water (max 900g calculated), risk of overflow. Try a lower ratio or less coffee.")

    bloom_water = 70.0  # Standard grams of water for blooming

    if total_water <= bloom_water:
        raise Exception(f"Not enough water for the bloom phase (need > {bloom_water}g for {coffee_grams}g of coffee at 1:{water_ratio} ratio). Increase water or coffee amount.")

    pour_water = total_water - bloom_water
    return [coffee_grams, bloom_water, pour_water, total_water]

def brew(cups: int, water_ratio: int) -> list[float]:
    """
    Orchestrates the calculation of coffee brewing parameters.

    Args:
        cups: The desired number of coffee cups.
        water_ratio: The desired ratio of water to coffee.

    Returns:
        A list from the chemex function: [coffee_grams, bloom_water, pour_water, total_water].

    Raises:
        Exception: If cups or water_ratio are non-positive.
    """
    if cups <= 0:
        raise Exception("Number of cups must be a positive integer.")
    if water_ratio <= 0:
        raise Exception("Water ratio must be a positive integer.")

    grams_of_water_for_cups = cups_of_coffee_desired(cups)
    # Calculate coffee grams needed based on total water and desired ratio
    grams_of_coffee_needed = ceil(grams_of_water_for_cups / water_ratio)

    return chemex(grams_of_coffee_needed, water_ratio)

def main(*args, **kwargs) -> None:
    """
    Main function triggered by the "Brew" button in the HTML.
    It reads user inputs, calculates brewing instructions, and updates the webpage DOM.
    Handles errors by displaying messages on the webpage.
    """
    # DOM element references
    error_div = Element('error-message')
    output_div = Element('output') # Summary of the brew
    step1_div = Element('step1')
    step2_div = Element('step2')
    step3_div = Element('step3')

    # Clear previous messages from all relevant divs
    error_div.clear()
    output_div.clear()
    step1_div.clear()
    step2_div.clear()
    step3_div.clear()

    try:
        # Retrieve and validate inputs
        cups_input_str = Element('cups').value
        ratio_input_str = Element('ratio').value

        if not cups_input_str or not ratio_input_str:
            raise Exception("Please enter values for both cups and water ratio.")

        try:
            cups_of_coffee = int(cups_input_str)
            water_ratio = int(ratio_input_str)
        except ValueError:
            raise Exception("Cups and water ratio must be whole numbers.")

        if cups_of_coffee <= 0:
            raise Exception("Number of cups must be a positive number.")
        if water_ratio <= 0:
             raise Exception("Water ratio must be a positive number.")

        # Perform brewing calculations
        coffee_beans, bloom_water, pour_water, total_water = brew(cups_of_coffee, water_ratio)

        # Update DOM with summary and instructions
        output_div.write(f"""
        <h3>Summary</h3>
        <p>{cups_of_coffee} cup(s) of coffee with a bean to water ratio of 1:{water_ratio}.</p>
        <p>This will use <strong>{coffee_beans:.0f}g of coffee</strong> and <strong>{total_water:.0f}g of water</strong>.</p>
        """)

        step1_div.write(f"""
        <h4>Step 1: Preparation</h4>
        <ul>
            <li>Grind <strong>{coffee_beans:.0f}g</strong> of coffee beans to a medium-coarse consistency.</li>
            <li>Heat water to 197-204°F (92-96°C).</li>
        </ul>
        """)

        step2_div.write(f"""
        <h4>Step 2: Bloom</h4>
        <ul>
            <li>Place the Chemex filter in the brewer.</li>
            <li>Pour hot water to wet the filter thoroughly, then discard this water.</li>
            <li>Add the ground coffee to the filter, making a small divot in the center.</li>
            <li>Pour <strong>{bloom_water:.0f}g</strong> of hot water evenly over the grounds, ensuring all coffee is wet.</li>
            <li>Wait for 60 seconds for the coffee to "bloom" (release CO2).</li>
        </ul>
        """)

        step3_div.write(f"""
        <h4>Step 3: Brew</h4>
        <ul>
            <li>Slowly pour the remaining <strong>{pour_water:.0f}g</strong> of water in a circular or spiral motion.</li>
            <li>Avoid pouring directly down the center or onto the filter paper itself.</li>
            <li>Some suggest pouring the {pour_water:.0f}g in three phases of {pour_water/3:.0f}g each, allowing some drawdown in between.</li>
            <li>Once all water is added, allow the coffee to drip completely through. This may take several minutes.</li>
            <li>Remove the filter and enjoy your freshly brewed Chemex coffee!</li>
        </ul>
        """)

    except Exception as e:
        error_div.write(f"<strong>Error:</strong> {str(e)}")
        # Ensure instruction sections are cleared if an error occurs during processing
        output_div.clear()
        step1_div.clear()
        step2_div.clear()
        step3_div.clear()
