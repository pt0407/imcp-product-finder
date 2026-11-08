# Digital shelf audit: Pan's Mushroom Jerky — Texas store locator

- **Method:** `digital_shelf_audit` — queried the brand's own public store-locator API
  (`pans-store-locator.netlify.app/.netlify/functions/nearby`, embedded at
  mushroomjerky.com/pages/store-locator) from 12 Texas metro coordinates. Each query returns
  the nearest ~20 retail locations carrying Pan's.
- **Date:** 2026-11-07
- **n:** 12 metro queries → 240 store records → **159 unique stores** after dedup by name+city.
- **Queries:** Houston, Dallas, Austin, San Antonio, Fort Worth, El Paso, Corpus Christi,
  Lubbock, Waco, Amarillo, Brownsville, Tyler.

## Results

| Banner | Unique stores found | Notes |
|---|---|---|
| H-E-B | 76 | All in Texas — H-E-B is Pan's only big-box banner in these queries |
| H-E-B Central Market | 4 | Houston/Austin/San Antonio premium format |
| CVS | 36 | National convenience banner |
| DoorDash dark stores | 19 | Delivery-only locations, not physical retail |
| Other (herb markets, Whole Foods, indie) | 22 | Sprouts-type independents |

## Geography (H-E-B records by metro region)

| Region | H-E-B doors found |
|---|---|
| San Antonio + Central TX (Waco/Killeen/Georgetown) | ~31 |
| Austin | 12 |
| Houston | 9 |
| Rio Grande Valley (Brownsville/Laredo) | 8 |
| West TX (El Paso/Lubbock/Midland/Odessa) | 5 |
| Gulf Coast (Corpus Christi) | ~4 |
| **DFW (Dallas + Fort Worth)** | **3** |
| East TX (Tyler) | 1 |

## Findings for the deck

1. **H-E-B is the whole Texas game** — 80 of 159 unique stores (50%) are H-E-B banners, and
   every one is in Texas. Pan's Texas retail strategy *is* an H-E-B strategy.
2. **DFW is nearly empty** — only 3 H-E-B doors within ~20 miles of Dallas/Fort Worth
   (nearest: Burleson). H-E-B has minimal DFW presence, so a Dallas-based team should run
   demos in Houston/Austin/San Antonio (~3–3.5h) or treat DFW as a later expansion market.
3. **Density is south/central** — San Antonio, Austin, Houston, Corpus Christi, Waco,
   Rio Grande Valley are the deep markets.
4. **DoorDash dark stores already cover online convenience** — the gap is physical retail
   trial, which supports the demo-day strategy.

## Limitations

- "Nearest 20" per query undercounts total doors (2,500+ claimed nationally); treat counts as
  a density map, not a census.
- Queries used city-center coordinates; suburban coverage is approximate.
- Store names come from the locator's own data; banner classification is keyword-based.
