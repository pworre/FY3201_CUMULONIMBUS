
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------

FILE_PATH = Path("data/01415_6th_january_2026.txt")

# Choose "pressure" or "height"
Y_AXIS = "pressure"



# ------------------------------------------------------------
# Read University of Wyoming sounding data
# ------------------------------------------------------------

with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the table header automatically
header_index = next(
    (
        i for i, line in enumerate(lines)
        if line.strip().startswith("PRES")
        and "HGHT" in line
        and "TEMP" in line
        and "DWPT" in line
    ),
    None,
)

if header_index is None:
    raise ValueError(
        "Could not find the PRES/HGHT/TEMP/DWPT header. "
        "Check the downloaded file format."
    )

columns = [
    "pressure", "height", "temperature", "dewpoint",
    "relative_humidity", "mixing_ratio", "wind_direction",
    "wind_speed", "potential_temperature",
    "equivalent_potential_temperature",
    "virtual_potential_temperature",
]

rows = []

# Skip the column header and units line
for line in lines[header_index + 2:]:
    fields = line.split()

    # The sounding table should contain 11 columns
    if len(fields) < 11:
        continue

    try:
        row = [float(value) for value in fields[:11]]
    except ValueError:
        continue

    rows.append(row)

data = pd.DataFrame(rows, columns=columns)

if data.empty:
    raise ValueError("No numerical sounding rows were found.")

# Remove missing or invalid measurements
data = data.dropna(
    subset=["pressure", "height", "temperature", "dewpoint"]
)

data = data[
    (data["pressure"] > 0)
    & (data["temperature"] > -150)
    & (data["dewpoint"] > -150)
]

data = data.sort_values("pressure", ascending=False)

print(data.head())
print(f"Number of valid levels: {len(data)}")



# ------------------------------------------------------------
# Plot the sounding
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(7, 9))

if Y_AXIS == "pressure":
    ax.plot(
        data["temperature"],
        data["pressure"],
        label="Air temperature",
        linewidth=2,
    )

    ax.plot(
        data["dewpoint"],
        data["pressure"],
        label="Dew-point temperature",
        linewidth=2,
    )

    ax.set_yscale("log")
    ax.invert_yaxis()
    ax.set_ylabel("Pressure (hPa)")

    ax.set_yticks(
        [1000, 925, 850, 700, 500, 400, 300, 200, 100]
    )
    ax.set_yticklabels(
        ["1000", "925", "850", "700", "500",
         "400", "300", "200", "100"]
    )

elif Y_AXIS == "height":
    data = data.sort_values("height")

    ax.plot(
        data["temperature"],
        data["height"] / 1000,
        label="Air temperature",
        linewidth=2,
    )

    ax.plot(
        data["dewpoint"],
        data["height"] / 1000,
        label="Dew-point temperature",
        linewidth=2,
    )

    ax.set_ylabel("Geopotential height (km)")

else:
    raise ValueError("Y_AXIS must be 'pressure' or 'height'.")

ax.set_xlabel("Temperature (°C)")
ax.set_title("Atmospheric Sounding: Stavanger/Sola\n"
             "6 January 2025, 12:00 UTC")

ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.tight_layout()

plt.savefig("sola_sounding.png", dpi=300, bbox_inches="tight")
plt.show()
