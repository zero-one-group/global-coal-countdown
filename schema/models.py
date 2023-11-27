from enum import Enum
from typing import Annotated, Dict, List, Literal

from pydantic import (AfterValidator, BaseModel, ConfigDict, Field, HttpUrl,
                      RootModel, StrictFloat, StrictInt, StrictStr,
                      model_validator)

from schema.enum import COUNTRY_KEY_VALUES, ISO_KEY_VALUES
from schema.validators import (is_american_date, is_greater_than_min_length,
                               is_len, is_percentage_string, is_positive,
                               is_required_keys_exist, is_sorted_by_capacity,
                               is_unique, is_valid_article_id, is_valid_bounds,
                               is_valid_long_lat, is_valid_year)

# NOTE: Type
StrictPosInt = Annotated[StrictInt, AfterValidator(is_positive)]
StrictPosFloat = Annotated[StrictFloat, AfterValidator(is_positive)]
Year = Annotated[StrictInt, AfterValidator(is_valid_year)]


# NOTE: Enum
CountryEnum = Enum("CountryEnum", COUNTRY_KEY_VALUES)
IsoEnum = Enum("IsoEnum", ISO_KEY_VALUES)


# NOTE: Website Texts
class AnalysisRegionEnum(str, Enum):
    north_america = "north_america"
    south_america = "south_america"
    caribbean = "caribbean"
    europe = "europe"
    africa = "africa"
    middle_east = "middle_east"
    central_asia = "central_asia"
    india = "india"
    china = "china"
    indo_pacific = "indo_pacific"
    global_ = "global"


class Analysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: StrictStr
    timestamp: StrictPosInt
    link: HttpUrl
    summary: StrictStr
    title: StrictStr
    countries: List[IsoEnum]
    region: AnalysisRegionEnum

    @model_validator(mode="after")
    def check_american_date(self):
        is_american_date(self.date)


class FootNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: StrictStr
    link: HttpUrl | Literal["N/A"]


class CountryTexts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country_overview: List[StrictStr]
    coal_overview: List[StrictStr]
    electricity_overview: List[StrictStr]
    footnotes: List[FootNote]

    @model_validator(mode="after")
    def check_min_length(self):
        args = [self.country_overview, self.coal_overview, self.electricity_overview]
        for arg in args:
            is_greater_than_min_length(1, arg)


class WebsiteTextsData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis: List[Analysis]
    countries: Dict[IsoEnum, CountryTexts]

    @model_validator(mode="after")
    def check_countries_keys(self):
        is_required_keys_exist([IsoEnum["id"]], self.countries)


# NOTE: Mapbox
class CoalTypeEnum(str, Enum):  # Is this a good enum?
    anthracite = "Anthracite"
    biomass_bituminous = "Biomass & Bituminous"
    bituminous = "Bituminous"
    bituminous_anthracite = "Bituminous & Anthracite"
    lignite = "Lignite"
    lignite_bituminous = "Lignite & Bituminous"
    lignite_sub_bituminous = "Lignite & Sub-Bituminous"
    sub_bituminous = "Sub-Bituminous"
    sub_bituminous_bituminous = "Sub-Bituminous & Bituminous"
    waste_coal = "Waste Coal"
    unknown = "Unknown"


class StatusEnum(str, Enum):
    retired = "Retired"
    construction = "Construction"
    halted = "Halted"
    planned = "Planned"
    cancelled = "Cancelled"
    operational = "Operational"


class CompleteTechEnum(str, Enum):
    integrated_gasification_combined_cycle = "Integrated Gasification Combined Cycle"
    integrated_gasification_combined_cycle_wccs = (
        "Integrated Gasification Combined " "Cycle with Carbon Capture & Storage"
    )
    subcritical = "Subcritical"
    subcritical_with_carbon_capture_storage = (
        "Subcritical with Carbon " "Capture & Storage"
    )
    subcritical_with_circulating_fluidized_bed = (
        "Subcritical with " "Circulating Fluidized Bed"
    )
    supercritical = "Supercritical"
    supercritical_with_carbon_capture_storage = (
        "Supercritical with " "Carbon Capture & Storage"
    )
    ultra_supercritical = "Ultra-Supercritical"
    unknown = "Unknown"
    unknown_with_carbon_capture_storage = "Unknown with Carbon Capture & Storage"


class MapboxGeometry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    coordinates: List[float]
    type: Literal["Point"]

    @model_validator(mode="after")
    def valid_coord(self):
        is_valid_long_lat(self.coordinates)


class MapboxProperties(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: Literal["N/A"] | StrictInt
    capacity_mw: StrictPosInt
    coal_type: CoalTypeEnum
    country: CountryEnum
    emission_factor_kg_co2_per_tj: StrictPosInt
    plant_name: StrictStr
    status: StatusEnum
    technology: CompleteTechEnum
    thermal_efficiency: StrictPosFloat
    unit_id: StrictPosInt
    unit_name: StrictStr


class MapboxFeature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    geometry: MapboxGeometry
    id: StrictStr
    properties: MapboxProperties
    type: Literal["Feature"]


class MapboxData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    features: List[MapboxFeature]
    type: Literal["FeatureCollection"]

    @model_validator(mode="after")
    def check_unique_feature_id(self):
        is_unique(self.features, lambda feature: feature.id)


# NOTE: News Feed
class NewsFeedItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: StrictStr
    title: StrictStr
    summary: StrictStr
    links: List[HttpUrl]
    timestamp: StrictInt

    @model_validator(mode="after")
    def check_validation(self):
        _unique_links = is_unique(self.links, str)
        _date_is_american = is_american_date(self.date)
        _links_gt_1 = is_greater_than_min_length(1, self.links)
        return _unique_links, _date_is_american, _links_gt_1


class RegionEnum(str, Enum):
    africa = "Africa"
    americas = "Americas"
    asia = "Asia"
    europe = "Europe"
    oceania = "Oceania"


ArticleID = Annotated[str, AfterValidator(is_valid_article_id)]


class CountryNewsFeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region: RegionEnum
    national_article_ids: List[ArticleID]
    regional_article_ids: List[ArticleID]
    global_article_ids: List[ArticleID]

    @model_validator(mode="after")
    def check_unique_args(self):
        args = [
            self.national_article_ids,
            self.regional_article_ids,
            self.global_article_ids,
        ]
        for arg in args:
            is_unique(arg, str)


class NewsFeedData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recent_news_article_ids: List[ArticleID]
    countries: Dict[IsoEnum, CountryNewsFeed]
    articles: Dict[ArticleID, NewsFeedItem]
    latest_issue: StrictInt
    latest_date: StrictStr

    @model_validator(mode="after")
    def check_validation(self):
        _unique_article_ids = is_unique(self.recent_news_article_ids, str)
        _recent_news_gt_5 = is_greater_than_min_length(5, self.recent_news_article_ids)
        _latest_date_is_american = is_american_date(self.latest_date)
        _article_gt_1 = is_greater_than_min_length(1, self.articles)
        _id_in_countries = is_required_keys_exist([IsoEnum["id"]], self.countries)
        return (
            _unique_article_ids,
            _recent_news_gt_5,
            _latest_date_is_american,
            _article_gt_1,
            _id_in_countries,
        )


# NOTE: Country Bounding Boxes
class CountryBoundingBox(BaseModel):
    model_config = ConfigDict(extra="forbid")

    iso: StrictStr  # Should this be enum also?
    name: CountryEnum
    bounds: List[StrictFloat]

    @model_validator(mode="after")
    def check_validation(self):
        _iso_length = is_len(self.iso, 2)
        _valid_bounds = is_valid_bounds(self.bounds)
        return _iso_length, _valid_bounds


class CountryBoundingBoxesData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    countries: Dict[IsoEnum, CountryBoundingBox] = Field(..., description="BBG46")

    @model_validator(mode="after")
    def check_validation(self):
        _us_in_in_countries = is_required_keys_exist(
            [IsoEnum["us"], IsoEnum["in"]], self.countries
        )
        return _us_in_in_countries


# NOTE: Homepage Data


class GlobalTotals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_number: StrictPosInt = Field(..., description="BBG1")
    total_number_net_change: StrictStr = Field(..., description="BBG2")
    total_capacity_mw: StrictPosInt = Field(..., description="BBG3")
    total_capacity_mw_net_change: StrictStr = Field(..., description="BBG4")

    @model_validator(mode="after")
    def check_validation(self):
        vars = [self.total_capacity_mw_net_change, self.total_number_net_change]
        for var in vars:
            _percentage_string = is_percentage_string(var)
        return _percentage_string


class CountryRankingsByStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class RankedCountry(BaseModel):
        model_config = ConfigDict(extra="forbid")
        country: CountryEnum
        capacity_mw: StrictPosInt

    operational: List[RankedCountry] = Field(..., description="BBG5")
    construction: List[RankedCountry] = Field(..., description="BBG6")
    planned: List[RankedCountry] = Field(..., description="BBG7")
    cancelled: List[RankedCountry] = Field(..., description="BBG7")
    halted: List[RankedCountry] = Field(..., description="BBG8")
    retired: List[RankedCountry] = Field(..., description="BBG9")

    @model_validator(mode="after")
    def check_validation(self):
        vars = [
            self.operational,
            self.construction,
            self.construction,
            self.planned,
            self.cancelled,
            self.halted,
            self.retired,
        ]
        for var in vars:
            _length_of_ten = is_len(var, 10)
            _sorted_by_capacity = is_sorted_by_capacity(var)
            _unique_countries = is_unique(var, lambda model: model.country)
        return _length_of_ten, _sorted_by_capacity, _unique_countries


class CoalPlantsByStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operational: StrictPosInt
    construction: StrictPosInt
    planned: StrictPosInt
    cancelled: StrictPosInt
    halted: StrictPosInt
    retired: StrictPosInt


class EmissionPathwayPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current: StrictPosFloat
    no_action: StrictPosFloat
    target_1_5_deg: StrictPosFloat
    target_2_deg: StrictPosFloat
    year: Year


class CapacitySnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: Year
    operational: StrictPosInt
    construction: StrictPosInt
    planned: StrictPosInt
    cancelled: StrictPosInt
    halted: StrictPosInt
    retired: StrictPosInt
    expected_retirements_by_2030: StrictPosInt


class RegionalCapacityChanges(BaseModel):
    model_config = ConfigDict(extra="forbid")

    oecd_and_eu: List[CapacitySnapshot]
    china: List[CapacitySnapshot]
    non_oecd_no_china: List[CapacitySnapshot]

    @model_validator(mode="after")
    def check_validation(self):
        vars = [self.oecd_and_eu, self.china, self.non_oecd_no_china]
        for var in vars:
            _unique_years = is_unique(var, lambda model: model.year)
        return _unique_years


class HomePageData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    global_totals: GlobalTotals
    country_rankings_by_status: CountryRankingsByStatus
    coal_plants_by_status: CoalPlantsByStatus = Field(..., description="BBG10")
    emission_pathways: List[EmissionPathwayPoint] = Field(..., description="BBG13")
    regional_capacity_changes: RegionalCapacityChanges = Field(..., description="BBG15")

    @model_validator(mode="after")
    def check_validation(self):
        _unique_years = is_unique(self.emission_pathways, lambda model: model.year)
        return _unique_years


# NOTE: Coal Status Data


class PhaseOutStatuses(BaseModel):
    model_config = ConfigDict(extra="forbid")

    no_coal: List[IsoEnum]
    phase_out_in_consideration: List[IsoEnum]
    phase_out_by_2030: List[IsoEnum]
    phase_out_by_2040: List[IsoEnum]
    coal_free: List[IsoEnum]
    ppca_member: List[IsoEnum]

    @model_validator(mode="after")
    def check_validation(self):
        vars = [
            self.no_coal,
            self.phase_out_in_consideration,
            self.phase_out_by_2030,
            self.phase_out_by_2040,
            self.coal_free,
            self.ppca_member,
        ]
        for var in vars:
            _min_length = is_greater_than_min_length(1, var)
            _unique_isos = is_unique(var, str)
        return _min_length, _unique_isos


class NewCoalStatuses(BaseModel):
    model_config = ConfigDict(extra="forbid")

    constructing_new_coal: List[IsoEnum]
    planning_new_coal: List[IsoEnum]
    committed_to_no_new_coal: List[IsoEnum]
    part_of_no_new_coal_power_compact: List[IsoEnum]
    cancelled_coal: List[IsoEnum]

    @model_validator(mode="after")
    def check_validation(self):
        vars = [
            self.constructing_new_coal,
            self.planning_new_coal,
            self.committed_to_no_new_coal,
            self.cancelled_coal,
        ]
        for var in vars:
            _min_length = is_greater_than_min_length(1, var)
            _unique_isos = is_unique(var, str)
        return _min_length, _unique_isos


class CountryCoalStatusData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phase_out: PhaseOutStatuses = Field(..., description="BBG12a")
    new_coal: NewCoalStatuses = Field(..., description="BBG12b")


# NOTE: Country Main


class CapacityTimeSeriesPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: StrictInt = Field(..., description="BBG25 & BBG27")
    capacity: StrictPosInt = Field(..., description="BBG25 & BBG27")
    net_change: StrictStr = Field(..., description="BBG26")

    @model_validator(mode="before")
    @classmethod
    def check_validation(cls, data):
        is_valid_year(data["year"])
        is_percentage_string(data["net_change"])
        return data


class NewCoalEnum(str, Enum):
    na = "N/A"
    cancelled_coal = "cancelled_coal"
    commited_to_no_new_coal = "committed_to_no_new_coal"
    part_of_no_new_coal_power_compact = "part_of_no_new_coal_power_compact"
    constructing_new_coal = "constructing_new_coal"
    planning_new_coal = "planning_new_coal"


class PhaseOutEnum(str, Enum):
    na = "N/A"
    coal_free = "coal_free"
    phase_out_by_2030 = "phase_out_by_2030"
    phase_out_by_2040 = "phase_out_by_2040"
    phase_out_in_consideration = "phase_out_in_consideration"


class CountryMainStatuses(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phase_out: PhaseOutEnum
    new_coal: NewCoalEnum
    ppca_member: bool


class SingleCountryMainData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    capacity_time_series: List[CapacityTimeSeriesPoint] = Field(
        ..., description="BBG27"
    )
    capacity_trends: List[CapacitySnapshot] = Field(..., description="BBG16")
    statuses: CountryMainStatuses

    @model_validator(mode="after")
    def check_validation(self):
        vars = [self.capacity_time_series, self.capacity_trends]
        for var in vars:
            _unique_years = is_unique(var, lambda model: model.year)
            _var_min_length = is_greater_than_min_length(1, var)
        return _var_min_length, _unique_years


class CountryMainData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    countries: Dict[IsoEnum, SingleCountryMainData]

    @model_validator(mode="after")
    def check_validation(self):
        _require_regional_country_trend_keys = is_required_keys_exist(
            [IsoEnum["us"], IsoEnum["in"]], self.countries
        )

        # NOTE: Coal Capacity Landscape
        return _require_regional_country_trend_keys


class CoalCapacityRankings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operational: StrictPosInt = Field(..., description="BBG21")
    new_coal_risk: StrictPosInt = Field(..., description="BBG22")


class CurrentCapacity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    capacity: StrictPosInt = Field(..., description="BBG25")
    capacity_net_change: StrictStr = Field(..., description="BBG26")

    @model_validator(mode="after")
    def check_validation(self):
        is_percentage_string(self.capacity_net_change)


class CapacityByStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operational: StrictPosInt
    construction: StrictPosInt
    planned: StrictPosInt
    cancelled: StrictPosInt
    halted: StrictPosInt
    retired: StrictPosInt


class CapacityByTechnology(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subcritical: StrictPosInt
    supercritical: StrictPosInt
    ultra_supercritical: StrictPosInt
    other: StrictPosInt
    unknown: StrictPosInt


class HistoricalCapacityByStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: Year
    operational: StrictPosInt
    construction: StrictPosInt
    planned: StrictPosInt
    cancelled: StrictPosInt
    halted: StrictPosInt
    retired: StrictPosInt
    expected_retirements_by_2030: StrictPosInt


class TechEnum(str, Enum):
    subcritical = "subcritical"
    supercritical = "supercritical"
    ultra_supercritical = "ultra_supercritical"
    other = "other"
    unknown = "unknown"


class PlantSwarmPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # NOTE:
    # year use StrictInt rather than Year type due to
    # plant swarm year is out of the validated year
    id: TechEnum
    unit_id: StrictStr
    year: StrictInt
    capacity_mw_sqrt: StrictPosFloat


class CountryCoalCapacityLandscape(BaseModel):
    model_config = ConfigDict(extra="forbid")

    statuses: CountryMainStatuses
    rankings: CoalCapacityRankings
    current_capacity: CurrentCapacity
    capacity_by_status: CapacityByStatus = Field(..., description="BBG28")
    capacity_by_technology: CapacityByTechnology = Field(..., description="BBG23")
    historical_capacities: List[HistoricalCapacityByStatus] = Field(
        ..., description="BBG29"
    )
    plant_swarm: List[PlantSwarmPoint] = Field(..., description="BBG30")

    @model_validator(mode="after")
    def check_validation(self):
        is_greater_than_min_length(1, self.historical_capacities)
        is_unique(self.historical_capacities, lambda model: model.year)
        is_unique(self.plant_swarm, lambda model: model.unit_id)


class CoalCapacityLandscapeData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    countries: Dict[IsoEnum, CountryCoalCapacityLandscape]

    @model_validator(mode="after")
    def check_validation(self):
        is_required_keys_exist([IsoEnum["cn"]], self.countries)


# NOTE: Coal Power Generation


class EnergyMix(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bioenergy: StrictPosInt
    coal: StrictPosInt
    gas: StrictPosInt
    hydro: StrictPosInt
    nuclear: StrictPosInt
    other_fossil: StrictPosInt
    other_renewables: StrictPosInt
    wind: StrictPosInt
    solar: StrictPosInt


class ElectricityDemand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: Year
    demand: StrictPosFloat


class ElectricityDemandChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: Year
    demand: StrictFloat


class ElectricityGeneration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: Year
    bioenergy: StrictPosInt
    coal: StrictPosInt
    gas: StrictPosInt
    hydro: StrictPosInt
    nuclear: StrictPosInt
    other_fossil: StrictPosInt
    other_renewables: StrictPosInt
    wind: StrictPosInt
    solar: StrictPosInt


class GenerationChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: Year
    bioenergy: StrictInt
    coal: StrictInt
    gas: StrictInt
    hydro: StrictInt
    nuclear: StrictInt
    other_fossil: StrictInt
    other_renewables: StrictInt
    wind: StrictInt
    solar: StrictInt


class ElectricityGenerationRatio(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: Year
    bioenergy: StrictPosFloat
    coal: StrictPosFloat
    gas: StrictPosFloat
    hydro: StrictPosFloat
    nuclear: StrictPosFloat
    other_fossil: StrictPosFloat
    other_renewables: StrictPosFloat
    wind: StrictPosFloat
    solar: StrictPosFloat


class ProgressRatios(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year_2010: StrictFloat
    now: StrictFloat


class ProgressComparisons(BaseModel):
    model_config = ConfigDict(extra="forbid")

    clean_energy: ProgressRatios = Field(..., description="BBG44")
    phase_out: ProgressRatios = Field(..., description="BBG45")


class CountryCoalPowerGeneration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    progress: ProgressComparisons
    energy_mix: EnergyMix = Field(..., description="BBG31")
    electricity_demand_per_capita: List[ElectricityDemand] = Field(
        ..., description="BBG33"
    )
    electricity_generation_by_fuel: List[ElectricityGeneration] = Field(
        ..., description="BBG34"
    )
    cumulative_generation_changes: List[GenerationChange] = Field(
        ..., description="BBG35"
    )
    cumulative_demand_changes: List[ElectricityDemandChange] = Field(
        ..., description="BBG35"
    )
    electricity_generation_ratios: List[ElectricityGenerationRatio] = Field(
        ..., description="BBG36"
    )

    @model_validator(mode="after")
    def check_validation(self):
        vars = [
            self.electricity_generation_ratios,
            self.electricity_generation_by_fuel,
            self.electricity_demand_per_capita,
            self.cumulative_demand_changes,
            self.cumulative_generation_changes,
        ]
        for var in vars:
            is_greater_than_min_length(1, var)
            is_unique(var, lambda model: model.year)


class WorldCoalPowerGeneration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    progress: ProgressComparisons
    energy_mix: EnergyMix = Field(..., description="BBG32")
    electricity_demand_per_capita: List[ElectricityDemand] = Field(
        ..., description="BBG33"
    )

    @model_validator(mode="after")
    def check_validation(self):
        is_greater_than_min_length(1, self.electricity_demand_per_capita)
        is_unique(self.electricity_demand_per_capita, lambda model: model.year)


class RegionalEnum(str, Enum):
    china = "china"
    non_oecd_no_china = "non_oecd_no_china"
    oecd_and_eu = "oecd_and_eu"


class RegionalPowerGeneration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    progress: Dict[RegionalEnum, ProgressComparisons]


class CoalPowerGenerationData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    world: WorldCoalPowerGeneration
    regions: RegionalPowerGeneration
    countries: Dict[IsoEnum, CountryCoalPowerGeneration]

    @model_validator(mode="after")
    def check_validation(self):
        is_required_keys_exist([IsoEnum["cn"]], self.countries)


# NOTE: Lookup


class IsoCountryData(RootModel):
    root: Dict[IsoEnum, CountryEnum]


class CountryIsoData(RootModel):
    root: Dict[CountryEnum, IsoEnum]
