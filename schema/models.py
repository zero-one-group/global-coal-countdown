from enum import Enum
from typing import Dict, List, Literal, Union

from pydantic import (
    BaseModel,
    Extra,
    HttpUrl,
    Field,
    StrictInt,
    StrictFloat,
    StrictStr
)

from schema.enum_key_values import COUNTRY_KEY_VALUES, ISO_KEY_VALUES
from schema.validation import (
    american_date,
    length_constraint,
    min_length,
    non_negative,
    percentage_string,
    require_dict_keys,
    sorted_by_capacity,
    unique_elements,
    valid_bounds,
    valid_long_lat,
    valid_year,
    validate
)

# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------
CountryEnum = Enum('CountryEnum', COUNTRY_KEY_VALUES)
IsoEnum = Enum('IsoEnum', ISO_KEY_VALUES)


class GlobalTotals(BaseModel, extra=Extra.forbid):
    total_number: StrictInt = Field(..., description='BBG1')
    total_number_net_change: StrictStr = Field(..., description='BBG2')
    total_capacity_mw: StrictInt = Field(..., description='BBG3')
    total_capacity_mw_net_change: StrictStr = Field(..., description='BBG4')

    _non_negative = validate(
        non_negative,
        'total_capacity_mw',
        'total_number'
    )
    _percentage_string = validate(
        percentage_string,
        'total_capacity_mw_net_change',
        'total_number_net_change'
    )


class CountryRankingsByStatus(BaseModel, extra=Extra.forbid):
    class RankedCountry(BaseModel, extra=Extra.forbid):
        country: CountryEnum
        capacity_mw: StrictInt
        _non_negative = validate(non_negative, 'capacity_mw')

    operational: List[RankedCountry] = Field(..., description='BBG5')
    construction: List[RankedCountry] = Field(..., description='BBG6')
    planned: List[RankedCountry] = Field(..., description='BBG7')
    cancelled: List[RankedCountry] = Field(..., description='BBG7')
    halted: List[RankedCountry] = Field(..., description='BBG8')
    retired: List[RankedCountry] = Field(..., description='BBG9')

    _length_of_ten = validate(
        length_constraint(10),
        'operational',
        'construction',
        'planned',
        'cancelled',
        'halted',
        'retired',
    )
    _sorted_by_capacity = validate(
        sorted_by_capacity,
        'operational',
        'construction',
        'planned',
        'cancelled',
        'halted',
        'retired',
    )
    _unique_countries = validate(
        unique_elements(lambda model: model.country),
        'operational',
        'construction',
        'planned',
        'cancelled',
        'halted',
        'retired',
    )


class CoalPlantsByStatus(BaseModel, extra=Extra.forbid):
    operational: StrictInt
    construction: StrictInt
    planned: StrictInt
    cancelled: StrictInt
    halted: StrictInt
    retired: StrictInt

    _non_negative = validate(
        non_negative,
        'operational',
        'construction',
        'planned',
        'cancelled',
        'halted',
        'retired',
    )


class EmissionPathwayPoint(BaseModel, extra=Extra.forbid):
    current: StrictFloat
    no_action: StrictFloat
    target_1_5_deg: StrictFloat
    target_2_deg: StrictFloat
    year: StrictInt

    _non_negative = validate(
        non_negative,
        'current',
        'no_action',
        'target_1_5_deg',
        'target_2_deg',
    )

    _valid_year = validate(valid_year, 'year')


class CapacitySnapshot(BaseModel, extra=Extra.forbid):
    year: StrictInt
    operational: StrictInt
    construction: StrictInt
    planned: StrictInt
    cancelled: StrictInt
    halted: StrictInt
    retired: StrictInt
    expected_retirements_by_2030: StrictInt

    _valid_year = validate(valid_year, 'year')
    _non_negative = validate(
        non_negative,
        'operational',
        'construction',
        'planned',
        'cancelled',
        'halted',
        'retired',
        'expected_retirements_by_2030'
    )


class RegionalCapacityChanges(BaseModel, extra=Extra.forbid):
    oecd_and_eu: List[CapacitySnapshot]
    china: List[CapacitySnapshot]
    non_oecd_no_china: List[CapacitySnapshot]

    _unique_years = validate(
        unique_elements(lambda model: model.year),
        'oecd_and_eu',
        'china',
        'non_oecd_no_china'
    )


class HomePageData(BaseModel, extra=Extra.forbid):
    global_totals: GlobalTotals
    country_rankings_by_status: CountryRankingsByStatus
    coal_plants_by_status: CoalPlantsByStatus = Field(..., description='BBG10')
    emission_pathways: List[EmissionPathwayPoint] = Field(..., description='BBG13')
    regional_capacity_changes: RegionalCapacityChanges = Field(..., description='BBG15')

    _unique_years = validate(
        unique_elements(lambda model: model.year),
        'emission_pathways',
    )


# ---------------------------------------------------------------------------
# Country Main
# ---------------------------------------------------------------------------
class CapacityTimeSeriesPoint(BaseModel, extra=Extra.forbid):
    year: StrictInt = Field(..., description='BBG25 & BBG27')
    capacity: StrictInt = Field(..., description='BBG25 & BBG27')
    net_change: StrictStr = Field(..., description='BBG26')

    _valid_year = validate(valid_year, 'year')
    _non_negative = validate(non_negative, 'capacity')
    _percentage_string = validate(percentage_string, 'net_change')


class NewCoalEnum(str, Enum):
    na = 'N/A'
    cancelled_coal = 'cancelled_coal'
    commited_to_no_new_coal = 'committed_to_no_new_coal'
    part_of_no_new_coal_power_compact = 'part_of_no_new_coal_power_compact'
    constructing_new_coal = 'constructing_new_coal'
    planning_new_coal = 'planning_new_coal'


class PhaseOutEnum(str, Enum):
    na = 'N/A'
    coal_free = 'coal_free'
    phase_out_by_2030 = 'phase_out_by_2030'
    phase_out_by_2040 = 'phase_out_by_2040'
    phase_out_in_consideration = 'phase_out_in_consideration'


class CountryMainStatuses(BaseModel, extra=Extra.forbid):
    phase_out: PhaseOutEnum
    new_coal: NewCoalEnum
    ppca_member: bool


class SingleCountryMainData(BaseModel, extra=Extra.forbid):
    capacity_time_series: List[CapacityTimeSeriesPoint] = (
        Field(..., description='BBG27')
    )
    capacity_trends: List[CapacitySnapshot] = (
        Field(..., description='BBG16')
    )
    statuses: CountryMainStatuses

    _require_regional_country_trend_keys = validate(
        min_length(1),
        'capacity_trends',
        'capacity_time_series'
    )
    _unique_years = validate(
        unique_elements(lambda model: model.year),
        'capacity_time_series',
        'capacity_trends',
    )


class CountryMainData(BaseModel, extra=Extra.forbid):
    countries: Dict[IsoEnum, SingleCountryMainData]

    _require_regional_country_trend_keys = validate(
        require_dict_keys([IsoEnum['us'], IsoEnum['in']]),
        'countries'
    )


# ---------------------------------------------------------------------------
# Coal Capacity Landscape
# ---------------------------------------------------------------------------
class CoalCapacityRankings(BaseModel, extra=Extra.forbid):
    operational: StrictInt = Field(..., description='BBG21')
    new_coal_risk: StrictInt = Field(..., description='BBG22')

    _non_negative = validate(non_negative, 'operational', 'new_coal_risk')


class CurrentCapacity(BaseModel, extra=Extra.forbid):
    capacity: StrictInt = Field(..., description='BBG25')
    capacity_net_change: StrictStr = Field(..., description='BBG26')

    _non_negative = validate(non_negative, 'capacity')
    _percentage_string = validate(percentage_string, 'capacity_net_change')


class CapacityByStatus(BaseModel, extra=Extra.forbid):
    operational: StrictInt
    construction: StrictInt
    planned: StrictInt
    cancelled: StrictInt
    halted: StrictInt
    retired: StrictInt

    _non_negative = validate(
        non_negative,
        'operational',
        'construction',
        'planned',
        'cancelled',
        'halted',
        'retired',
    )


class CapacityByTechnology(BaseModel, extra=Extra.forbid):
    subcritical: StrictInt
    supercritical: StrictInt
    ultra_supercritical: StrictInt
    other: StrictInt
    unknown: StrictInt

    _non_negative = validate(
        non_negative,
        'subcritical',
        'supercritical',
        'ultra_supercritical',
        'other',
        'unknown'
    )


class HistoricalCapacityByStatus(BaseModel, extra=Extra.forbid):
    year: StrictInt
    operational: StrictInt
    construction: StrictInt
    planned: StrictInt
    cancelled: StrictInt
    halted: StrictInt
    retired: StrictInt
    expected_retirements_by_2030: StrictInt

    _valid_year = validate(valid_year, 'year')
    _non_negative = validate(
        non_negative,
        'operational',
        'construction',
        'planned',
        'cancelled',
        'halted',
        'retired',
        'expected_retirements_by_2030'
    )


class TechEnum(str, Enum):
    subcritical = 'subcritical'
    supercritical = 'supercritical'
    ultra_supercritical = 'ultra_supercritical'
    other = 'other'
    unknown = 'unknown'


class PlantSwarmPoint(BaseModel, extra=Extra.forbid):
    id: TechEnum
    unit_id: StrictStr
    year: StrictInt
    capacity_mw_sqrt: StrictFloat

    _non_negative = validate(non_negative, 'capacity_mw_sqrt', 'year')


class CountryCoalCapacityLandscape(BaseModel, extra=Extra.forbid):
    statuses: CountryMainStatuses
    rankings: CoalCapacityRankings
    current_capacity: CurrentCapacity
    capacity_by_status: CapacityByStatus = (
        Field(..., description='BBG28')
    )
    capacity_by_technology: CapacityByTechnology = (
        Field(..., description='BBG23')
    )
    historical_capacities: List[HistoricalCapacityByStatus] = (
        Field(..., description='BBG29')
    )
    plant_swarm: List[PlantSwarmPoint] = (
        Field(..., description='BBG30')
    )

    _min_length = validate(min_length(1), 'historical_capacities')
    _unique_years = validate(
        unique_elements(lambda model: model.year),
        'historical_capacities',
    )
    _unique_unit_id = validate(
        unique_elements(lambda model: model.unit_id),
        'plant_swarm'
    )


class CoalCapacityLandscapeData(BaseModel, extra=Extra.forbid):
    countries: Dict[IsoEnum, CountryCoalCapacityLandscape]

    _require_regional_capacity_change_keys = validate(
        require_dict_keys([IsoEnum['cn']]),
        'countries'
    )


# ---------------------------------------------------------------------------
# Coal Power Generation
# ---------------------------------------------------------------------------
class EnergyMix(BaseModel, extra=Extra.forbid):
    bioenergy: StrictInt
    coal: StrictInt
    gas: StrictInt
    hydro: StrictInt
    nuclear: StrictInt
    other_fossil: StrictInt
    other_renewables: StrictInt
    wind: StrictInt
    solar: StrictInt

    _non_negative = validate(
        non_negative,
        'bioenergy',
        'coal',
        'gas',
        'hydro',
        'nuclear',
        'other_fossil',
        'other_renewables',
        'solar',
        'wind',
    )


class ElectricityDemand(BaseModel, extra=Extra.forbid):
    year: StrictInt
    demand: StrictFloat

    _non_negative = validate(non_negative, 'demand')
    _valid_year = validate(valid_year, 'year')


class ElectricityDemandChange(BaseModel, extra=Extra.forbid):
    year: StrictInt
    demand: StrictFloat

    _valid_year = validate(valid_year, 'year')


class ElectricityGeneration(BaseModel, extra=Extra.forbid):
    year: StrictInt
    bioenergy: StrictInt
    coal: StrictInt
    gas: StrictInt
    hydro: StrictInt
    nuclear: StrictInt
    other_fossil: StrictInt
    other_renewables: StrictInt
    wind: StrictInt
    solar: StrictInt

    _valid_year = validate(valid_year, 'year')
    _non_negative = validate(
        non_negative,
        'bioenergy',
        'coal',
        'gas',
        'hydro',
        'nuclear',
        'other_fossil',
        'other_renewables',
        'solar',
        'wind',
    )


class GenerationChange(BaseModel, extra=Extra.forbid):
    year: StrictInt
    bioenergy: StrictInt
    coal: StrictInt
    gas: StrictInt
    hydro: StrictInt
    nuclear: StrictInt
    other_fossil: StrictInt
    other_renewables: StrictInt
    wind: StrictInt
    solar: StrictInt

    _valid_year = validate(valid_year, 'year')


class ElectricityGenerationRatio(BaseModel, extra=Extra.forbid):
    year: StrictInt
    bioenergy: StrictFloat
    coal: StrictFloat
    gas: StrictFloat
    hydro: StrictFloat
    nuclear: StrictFloat
    other_fossil: StrictFloat
    other_renewables: StrictFloat
    wind: StrictFloat
    solar: StrictFloat

    _valid_year = validate(valid_year, 'year')
    _non_negative = validate(
        non_negative,
        'bioenergy',
        'coal',
        'gas',
        'hydro',
        'nuclear',
        'other_fossil',
        'other_renewables',
        'solar',
        'wind',
    )


class ProgressRatios(BaseModel, extra=Extra.forbid):
    year_2010: StrictFloat
    now: StrictFloat


class ProgressComparisons(BaseModel, extra=Extra.forbid):
    clean_energy: ProgressRatios = Field(..., description='BBG44')
    phase_out: ProgressRatios = Field(..., description='BBG45')


class CountryCoalPowerGeneration(BaseModel, extra=Extra.forbid):
    progress: ProgressComparisons
    energy_mix: EnergyMix = Field(..., description='BBG31')
    electricity_demand_per_capita: List[ElectricityDemand] = (
        Field(..., description='BBG33')
    )
    electricity_generation_by_fuel: List[ElectricityGeneration] = (
        Field(..., description='BBG34')
    )
    cumulative_generation_changes: List[GenerationChange] = (
        Field(..., description='BBG35')
    )
    cumulative_demand_changes: List[ElectricityDemandChange] = (
        Field(..., description='BBG35')
    )
    electricity_generation_ratios: List[ElectricityGenerationRatio] = (
        Field(..., description='BBG36')
    )

    _min_length = validate(
        min_length(1),
        'electricity_demand_per_capita',
        'electricity_generation_by_fuel',
        'cumulative_generation_changes',
        'cumulative_demand_changes',
        'electricity_generation_ratios'
    )
    _unique_years = validate(
        unique_elements(lambda model: model.year),
        'electricity_demand_per_capita',
        'electricity_generation_by_fuel',
        'cumulative_generation_changes',
        'cumulative_demand_changes',
        'electricity_generation_ratios'
    )


class WorldCoalPowerGeneration(BaseModel, extra=Extra.forbid):
    progress: ProgressComparisons
    energy_mix: EnergyMix = Field(..., description='BBG32')
    electricity_demand_per_capita: List[ElectricityDemand] = (
        Field(..., description='BBG33')
    )

    _min_length = validate(min_length(1), 'electricity_demand_per_capita')
    _unique_years = validate(
        unique_elements(lambda model: model.year),
        'electricity_demand_per_capita'
    )


class RegionalEnum(str, Enum):
    china = 'china'
    non_oecd_no_china = 'non_oecd_no_china'
    oecd_and_eu = 'oecd_and_eu'


class RegionalPowerGeneration(BaseModel, extra=Extra.forbid):
    progress: Dict[RegionalEnum, ProgressComparisons]


class CoalPowerGenerationData(BaseModel, extra=Extra.forbid):
    world: WorldCoalPowerGeneration
    regions: RegionalPowerGeneration
    countries: Dict[IsoEnum, CountryCoalPowerGeneration]

    _require_regional_capacity_change_keys = validate(
        require_dict_keys([IsoEnum['cn']]),
        'countries'
    )


# ---------------------------------------------------------------------------
# Mapbox
# ---------------------------------------------------------------------------
class MapboxGeometry(BaseModel, extra=Extra.forbid):
    coordinates: List[StrictFloat]
    type: Literal['Point']

    _valid_long_lat = validate(valid_long_lat, 'coordinates')


class CoalTypeEnum(str, Enum):  # Is this a good enum?
    anthracite = 'Anthracite'
    biomass_bituminous = 'Biomass & Bituminous'
    bituminous = 'Bituminous'
    bituminous_anthracite = 'Bituminous & Anthracite'
    lignite = 'Lignite'
    lignite_bituminous = 'Lignite & Bituminous'
    lignite_sub_bituminous = 'Lignite & Sub-Bituminous'
    sub_bituminous = 'Sub-Bituminous'
    sub_bituminous_bituminous = 'Sub-Bituminous & Bituminous'
    unknown = 'Unknown'


class StatusEnum(str, Enum):
    retired = 'Retired'
    construction = 'Construction'
    halted = 'Halted'
    planned = 'Planned'
    cancelled = 'Cancelled'
    operational = 'Operational'


class CompleteTechEnum(str, Enum):
    integrated_gasification_combined_cycle = 'Integrated Gasification Combined Cycle'
    integrated_gasification_combined_cycle_wccs = 'Integrated Gasification Combined ' \
                                                  'Cycle with Carbon Capture & Storage'
    subcritical = 'Subcritical'
    subcritical_with_carbon_capture_storage = 'Subcritical with Carbon ' \
                                              'Capture & Storage'
    subcritical_with_circulating_fluidized_bed = 'Subcritical with ' \
                                                 'Circulating Fluidized Bed'
    supercritical = 'Supercritical'
    supercritical_with_carbon_capture_storage = 'Supercritical with ' \
                                                'Carbon Capture & Storage'
    ultra_supercritical = 'Ultra-Supercritical'
    unknown = 'Unknown'
    unknown_with_carbon_capture_storage = 'Unknown with Carbon Capture & Storage'


class MapboxProperties(BaseModel, extra=Extra.forbid):
    age: Union[Literal['N/A'], StrictInt]
    capacity_mw: StrictInt
    coal_type: CoalTypeEnum
    country: CountryEnum
    emission_factor_kg_co2_per_tj: StrictInt
    plant_name: StrictStr
    status: StatusEnum
    technology: CompleteTechEnum
    thermal_efficiency: StrictFloat
    unit_id: StrictInt
    unit_name: StrictStr

    _non_negative = validate(
        non_negative,
        'capacity_mw',
        'emission_factor_kg_co2_per_tj',
        'thermal_efficiency',
        'unit_id'
    )


class MapboxFeature(BaseModel, extra=Extra.forbid):
    geometry: MapboxGeometry
    id: StrictStr
    properties: MapboxProperties
    type: Literal['Feature']


class MapboxData(BaseModel, extra=Extra.forbid):
    features: List[MapboxFeature]
    type: Literal['FeatureCollection']

    _unique_id = validate(
        unique_elements(lambda model: model.id),
        'features'
    )


# ---------------------------------------------------------------------------
# Country Bounding Boxes
# ---------------------------------------------------------------------------
class CountryBoundingBox(BaseModel, extra=Extra.forbid):
    iso: StrictStr  # Should this be enum also?
    name: CountryEnum
    bounds: List[StrictFloat]

    _iso_length = validate(length_constraint(2), 'iso')
    _valid_bounds = validate(valid_bounds, 'bounds')


class CountryBoundingBoxesData(BaseModel, extra=Extra.forbid):
    countries: Dict[IsoEnum, CountryBoundingBox] = Field(..., description='BBG46')

    _require_countries_keys = validate(
        require_dict_keys([IsoEnum['us'], IsoEnum['in']]),
        'countries'
    )


# ---------------------------------------------------------------------------
# Country Coal Status Data
# ---------------------------------------------------------------------------
class PhaseOutStatuses(BaseModel, extra=Extra.forbid):
    no_coal: List[IsoEnum]
    phase_out_in_consideration: List[IsoEnum]
    phase_out_by_2030: List[IsoEnum]
    phase_out_by_2040: List[IsoEnum]
    coal_free: List[IsoEnum]
    ppca_member: List[IsoEnum]

    _min_length = validate(
        min_length(1),
        'no_coal',
        'phase_out_in_consideration',
        'phase_out_by_2030',
        'phase_out_by_2040',
        'coal_free',
        'ppca_member',
    )
    _unique_isos = validate(
        unique_elements(str),
        'no_coal',
        'phase_out_in_consideration',
        'phase_out_by_2030',
        'phase_out_by_2040',
        'coal_free',
        'ppca_member',
    )


class NewCoalStatuses(BaseModel, extra=Extra.forbid):
    constructing_new_coal: List[IsoEnum]
    planning_new_coal: List[IsoEnum]
    committed_to_no_new_coal: List[IsoEnum]
    part_of_no_new_coal_power_compact: List[IsoEnum]
    cancelled_coal: List[IsoEnum]

    _min_length = validate(
        min_length(1),
        'constructing_new_coal',
        'planning_new_coal',
        'committed_to_no_new_coal',
        'cancelled_coal'
    )
    _unique_isos = validate(
        unique_elements(str),
        'constructing_new_coal',
        'planning_new_coal',
        'committed_to_no_new_coal',
        'cancelled_coal'
    )


class CountryCoalStatusData(BaseModel, extra=Extra.forbid):
    phase_out: PhaseOutStatuses = Field(..., description='BBG12a')
    new_coal: NewCoalStatuses = Field(..., description='BBG12b')


# ---------------------------------------------------------------------------
# Newsfeed
# ---------------------------------------------------------------------------
class NewsFeedItem(BaseModel, extra=Extra.forbid):
    date: StrictStr
    title: StrictStr
    summary: StrictStr
    links: List[HttpUrl]
    timestamp: StrictInt

    _min_length = validate(min_length(1), 'links')
    _is_american_date = validate(american_date, 'date')
    _unique_links = validate(unique_elements(str), 'links')


class RegionEnum(str, Enum):
    africa_and_middle_east = 'Africa and Middle East'
    australia_nz = 'Australia/NZ'
    canada_us = 'Canada/US'
    east_asia = 'East Asia'
    eu27 = 'EU27'
    eurasia = 'Eurasia'
    latin_america = 'Latin America'
    non_eu_europe = 'non-EU Europe'
    se_asia = 'SE Asia'
    south_asia = 'South Asia'


class ArticleID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise TypeError('string required')
        if 'coalwire' not in value.lower():
            raise ValueError('ArticleID does not have the required format.')
        return cls(value)


class CountryNewsFeed(BaseModel, extra=Extra.forbid):
    region: RegionEnum
    national_article_ids: List[ArticleID]
    regional_article_ids: List[ArticleID]
    global_article_ids: List[ArticleID]
    news_article_ids: List[ArticleID]

    _unique_article_ids = validate(
        unique_elements(str),
        'national_article_ids',
        'regional_article_ids',
        'global_article_ids',
        'news_article_ids'
    )


class NewsFeedData(BaseModel, extra=Extra.forbid):
    news_article_ids: List[ArticleID]
    countries: Dict[IsoEnum, CountryNewsFeed]
    articles: Dict[ArticleID, NewsFeedItem]
    latest_issue: StrictInt
    latest_date: StrictStr

    _min_length = validate(min_length(1), 'articles')
    _require_countries_keys = validate(require_dict_keys([IsoEnum['id']]), 'countries')
    _is_american_date = validate(american_date, 'latest_date')
    _unique_article_ids = validate(unique_elements(str), 'news_article_ids')


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------
class IsoCountryData(BaseModel, extra=Extra.forbid):
    __root__: Dict[IsoEnum, CountryEnum]


class CountryIsoData(BaseModel, extra=Extra.forbid):
    __root__: Dict[CountryEnum, IsoEnum]


# ---------------------------------------------------------------------------
# Website Text
# ---------------------------------------------------------------------------
class Analysis(BaseModel, extra=Extra.forbid):
    date: StrictStr
    timestamp: StrictInt
    link: HttpUrl
    summary: StrictStr
    title: StrictStr

    _is_american_date = validate(american_date, 'date')
    _non_negative = validate(non_negative, 'timestamp')


class FootNote(BaseModel, extra=Extra.forbid):
    text: StrictStr
    link: Union[HttpUrl, Literal['N/A']]


class CountryTexts(BaseModel, extra=Extra.forbid):
    country_overview: List[StrictStr]
    coal_overview: List[StrictStr]
    electricity_overview: List[StrictStr]
    footnotes: List[FootNote]

    _min_length = validate(
        min_length(1),
        'country_overview',
        'coal_overview',
        'electricity_overview'
    )


class WebsiteTextsData(BaseModel, extra=Extra.forbid):
    analysis: List[Analysis]
    countries: Dict[IsoEnum, CountryTexts]

    _require_countries_keys = validate(
        require_dict_keys([IsoEnum['id']]),
        'countries'
    )
