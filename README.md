## Bloomberg Global Coal Countdown

![](https://bloombergcoalcountdown.com/_next/static/images/big-black-logo-46b32763924ec161ae53ca88b2c25517.webp)

This is the accompanying repository for the **[Bloomberg Global Coal Countdown](https://bloombergcoalcountdown.com/) (BGCC)** website.

<ul>
  <li><a href="#data-sources">Data Sources</a></li>
  <li><a href="#dashboard-data">Dashboard Data</a></li>
  <li><a href="#schema-and-validation">Schema and Validation</a></li>
  <li><a href="#license">License</a></li>
<ul>

## Data Sources

The data presented on the BGCC website comes from the following sources:

1. [Global Energy Monitor's (GEM)](https://globalenergymonitor.org/) [Global Coal Plant Tracker (GCPT)](https://globalenergymonitor.org/projects/global-coal-plant-tracker/) and the accompanying GCPT status changes since 2015. GEM's GCPT dataset provides unit-level data and it is the basis for all calculations related to coal-plant capacity, status, technology and age.
2. Country-level coal phaseout strategies, country-level expected retirements and global emission pathways from [University of Maryland's (UMD)](https://www.umd.edu/) [Center for Global Sustainability (CGS)](https://cgs.umd.edu/). Datasets from UMD are outputs from published research, and are therefore mostly served as is with very few modifications for aesthetic purposes such as smooth interpolation.
3. [Ember](https://ember-climate.org/)'s [Global Electricity Review 2021](https://ember-climate.org/project/global-electricity-review-2021/) data. Ember's dataset provides panel data over three dimensions, namely area (such as country and regions), year and variable (such as energy sources). It is used as the basis for all calculations related to energy mixes and trends.
4. In the Headlines content is scraped from [CoalWire](https://endcoal.org/category/coalwire/), published by [GEM](https://globalenergymonitor.org/). A CoalWire issue consists of multiple articles, news and analysis pieces, which are individually presented on the BGCC site.
5. Research and analysis pieces as curated by [Bloomberg Philanthropies](https://www.bloomberg.org/).
6. [Gapminder data, HYDE, and UN Population Division (2019) estimates](https://www.gapminder.org/data/documentation/gd003/) as presented by [Our World in Data's (OWD)](https://ourworldindata.org/) [world population data since 1800](https://ourworldindata.org/grapher/population). This dataset is used for per-capita calculations with simple extrapolations for 2020.
8. [Natural Earth Data](https://www.naturalearthdata.com/)'s [country vectors](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/) as presented by [Graydon Hoare](https://gist.github.com/graydon/11198540) with our own manual modifications for aesthetic reasons in order to make the interactive map appear more presentable.
9. Country commitments to phasing out coal as well as no new coal are based on research from [UMD](https://www.umd.edu/) [CGS](https://cgs.umd.edu/) and the [Powering Past Coal Alliance (PPCA)](https://www.poweringpastcoal.org/).
10. Expected retirements by 2030 of each country are collected and maintained by [PPCA](https://www.poweringpastcoal.org/).

The countries’ political affiliations such as EU27+1, G20, G7, OECD and PPCA are taken as of July 2021. We have decided to include the United Kingdom into the EU27+1 list in order to maintain comparability with other EU figures that have been reported in the past.

## Dashboard Data

The resulting datasets are available for download as part of a release attached to the repository - see [Releases](https://github.com/zero-one-group/global-coal-countdown/releases).

The following JSONs correspond to a page on the BGCC website:

* `coal_capacity_landscape.json`
* `coal_power_generation.json`
* `country_main.json`
* `homepage.json`
* `newsfeed.json`

The following JSONs are utility lookup datasets:
* `country_coal_status.json`
* `country_iso_lookup.json`
* `iso_country_lookup.json`
* `website_texts.json`

The `mapbox.json` data is uploaded one [feature](https://docs.mapbox.com/api/maps/datasets/#the-feature-object) at a time to [Mapbox](https://www.mapbox.com/) using the [Mapbox API](https://docs.mapbox.com/api/overview/). The `country_bounding_boxes.json` is used to center the map view on the selected country.

## Schema and Validation

Each JSON file is accompanied by a [Pydantic model](https://pydantic-docs.helpmanual.io/), which is used as a schema documentation and runtime validation. The Pydantic models can be found in `schema/models.py`. The source code references two other files, namely `schema/validation.py` and `schema/enum_key_value_pairs.py`, which contain custom validators and valid country names and the corresponding ISO 3166-1 alpha-2 country codes.

In the `docker` directory, we make available a `Dockerfile` and a `requirements.txt` to build an ephemeral Docker container, which we used to generate the data at the time writing.

## License

As the datasets are built upon the GEM's GCPT dataset, the BGCC datasets are also licensed under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) license. Therefore, it is allowed to copy and redistribute, as well as to build upon the datasets for any purpose including for commercial purposes. If you do build upon the datasets, you must distribute it under the same license.
