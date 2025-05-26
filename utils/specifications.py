"""
Common specifications to scrape for Porsche models
"""

# Basic performance specifications
PERFORMANCE_SPECS = [
    "horsepower",
    "0-60 mph",
    "top speed",
    "torque",
    "acceleration",
]

# Engine specifications
ENGINE_SPECS = [
    "engine type",
    "displacement",
    "cylinders",
    "bore",
    "stroke",
    "compression ratio",
    "fuel type",
    "fuel tank capacity",
    "Max. engine power",
    "Max. power per liter"
]

# Dimensions and weight
DIMENSION_SPECS = [
    "length",
    "width",
    "height",
    "wheelbase",
    "weight",
    "curb weight",
    "cargo volume",
    "turning circle",
    "ground clearance"
]

# Transmission and drivetrain
TRANSMISSION_SPECS = [
    "transmission",
    "differential"
]

# Fuel economy
FUEL_SPECS = [
    "fuel economy",
]

# Price and warranty
PRICE_SPECS = [
    "price",
    "warranty",
    "service"
]

# All specifications combined
ALL_SPECS = (
    PERFORMANCE_SPECS +
    ENGINE_SPECS +
    DIMENSION_SPECS +
    TRANSMISSION_SPECS +
    FUEL_SPECS +
    PRICE_SPECS
) 