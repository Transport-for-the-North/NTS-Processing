### Organising NTS data and calculate mode split for business, commute and other trip purposes (car/rail/bus/walk), hb trips only ###


### Load libraries and import data ##############################################
require("tidyverse")
require("naniar")


# Import unclassified build
unclassified_build <- read_csv("Y:/NTS/tfn_unclassified_build.csv")

# Import new area_type classification of wards
new_area_types <- read_csv("Y:/NTS/new area type lookup/new_area_type.csv")

### Prepare dataset #############################################################


# Classify trip origin to get HB/NHB splits
hb <- c(23)
nhb <- c(1,2,3,4,5,6,7,8,9,
         10,11,12,13,14,15,
         16,17,18,19,20,21,22)


unclassified_build <- unclassified_build %>%
  mutate(trip_origin = case_when(
    TripPurpFrom_B01ID %in% hb ~ 'hb',
    TripPurpFrom_B01ID %in% nhb ~ 'nhb',
    TRUE ~ as.character(NA)
  ))


# Recode trip purposes as NTEM classification hb_purpose for HB trips
unclassified_build <- unclassified_build %>%
  mutate(hb_purpose = case_when(
    TripPurpTo_B01ID == 1 ~ '1', # Work
    TripPurpTo_B01ID == 2 ~ '2', # In course of work
    TripPurpTo_B01ID == 3 ~ '3', # Education
    TripPurpTo_B01ID == 4 ~ '4', # Food shopping
    TripPurpTo_B01ID == 5 ~ '4', # Non food shopping
    TripPurpTo_B01ID == 6 ~ '5', # Personal business medical
    TripPurpTo_B01ID == 7 ~ '5', # Personal business eat / drink
    TripPurpTo_B01ID == 8 ~ '5', # Personal business other
    TripPurpTo_B01ID == 9 ~ '6', # Eat / drink with friends
    TripPurpTo_B01ID == 10 ~ '7', # Visit friends
    TripPurpTo_B01ID == 11 ~ '6', # Other social
    TripPurpTo_B01ID == 12 ~ '6', # Entertain /  public activity
    TripPurpTo_B01ID == 13 ~ '6', # Sport: participate
    TripPurpTo_B01ID == 14 ~ '8', # Holiday: base
    TripPurpTo_B01ID == 15 ~ '8', # Day trip / just walk
    TripPurpTo_B01ID == 16 ~ '6', # Other non-escort
    TripPurpTo_B01ID == 17 ~ '99', # Escort home
    TripPurpTo_B01ID == 18 ~ '1', # Escort work
    TripPurpTo_B01ID == 19 ~ '2', # Escort in course of work
    TripPurpTo_B01ID == 20 ~ '3', # Escort education
    TripPurpTo_B01ID == 21 ~ '4', # Escort shopping / personal business
    TripPurpTo_B01ID == 22 ~ '7', # Other escort
    TripPurpTo_B01ID == 23 ~ '99', # Home
    TRUE ~ as.character('unclassified')
  ))


# Recode trip purposes as NTEM classification nhb_purpose for NHB trips
unclassified_build <- unclassified_build %>%
  mutate(nhb_purpose = case_when(
    TripPurpTo_B01ID == 1 ~ '12', # Work
    TripPurpTo_B01ID == 2 ~ '12', # In course of work
    TripPurpTo_B01ID == 3 ~ '13', # Education
    TripPurpTo_B01ID == 4 ~ '14', # Food shopping
    TripPurpTo_B01ID == 5 ~ '14', # Non food shopping
    TripPurpTo_B01ID == 6 ~ '15', # Personal business medical
    TripPurpTo_B01ID == 7 ~ '15', # Personal business eat / drink
    TripPurpTo_B01ID == 8 ~ '15', # Personal business other
    TripPurpTo_B01ID == 9 ~ '16', # Eat / drink with friends
    TripPurpTo_B01ID == 10 ~ '16', # Visit friends
    TripPurpTo_B01ID == 11 ~ '16', # Other social
    TripPurpTo_B01ID == 12 ~ '16', # Entertain /  public activity
    TripPurpTo_B01ID == 13 ~ '16', # Sport: participate
    TripPurpTo_B01ID == 14 ~ '18', # Holiday: base
    TripPurpTo_B01ID == 15 ~ '18', # Day trip / just walk
    TripPurpTo_B01ID == 16 ~ '16', # Other non-escort
    TripPurpTo_B01ID == 17 ~ '99', # Escort home
    TripPurpTo_B01ID == 18 ~ '12', # Escort work
    TripPurpTo_B01ID == 19 ~ '12', # Escort in course of work
    TripPurpTo_B01ID == 20 ~ '13', # Escort education
    TripPurpTo_B01ID == 21 ~ '14', # Escort shopping / personal business
    TripPurpTo_B01ID == 22 ~ '16', # Other escort
    TripPurpTo_B01ID == 23 ~ '99', # Home
    TRUE ~ as.character('unclassified')
  ))

# Drop hb_purpose = 99 - Return leg for hb trips
unclassified_build <- subset(unclassified_build, hb_purpose != '99')

# Pick a final purpose depending on purpose from
unclassified_build <- unclassified_build %>%
  mutate(trip_purpose = case_when(
    trip_origin == 'hb' ~ hb_purpose,
    trip_origin == 'nhb' ~ nhb_purpose,
    TRUE ~ as.character('unclassified')
  ))

# drop 'unclassified' hb_purpose as cannot be used in regression by trip_purpose
unclassified_build <- subset(unclassified_build, trip_purpose != 'unclassified')


# Recode gender(Sex_B01ID) as gender(Male or Female)
unclassified_build <- unclassified_build %>%
  mutate(gender = case_when(
    Sex_B01ID == 1 ~ 'Male',
    Sex_B01ID == 2 ~ 'Female',
    TRUE ~ as.character(Sex_B01ID)
  ))


# Combine Age and work status to age_workstatus (excluding 75+ AND pte/fte/stu as insignificant N (<0.2% combined))
unclassified_build <- unclassified_build %>%
  mutate(age_work_status = case_when(
    Age_B01ID %in% c(1,2,3,4,5) ~ '0-16_child',
    Age_B01ID %in% c(6,7,8,9,10,11,12,13,14,15,16,17,18) & EcoStat_B01ID %in% c(1,2) ~ '16-74_fte',
    Age_B01ID %in% c(6,7,8,9,10,11,12,13,14,15,16,17,18) & EcoStat_B01ID %in% c(3,4) ~ '16-74_pte',
    Age_B01ID %in% c(6,7,8,9,10,11,12,13,14,15,16,17,18) & EcoStat_B01ID == 7 ~ '16-74_stu',
    Age_B01ID %in% c(6,7,8,9,10,11,12,13,14,15,16,17,18) & EcoStat_B01ID %in% c(5,6,8,9,10,11) ~ '16-74_unm',
    Age_B01ID %in% c(19,20,21) & EcoStat_B01ID %in% c(5,6,8,9,10,11) ~ '75+_retired',
    TRUE ~ as.character('unclassified')
  )) %>% subset(age_work_status != 'unclassified')



# Recode number of cars(NumCarVan_B02ID) as cars
unclassified_build <- unclassified_build %>%
  mutate(cars = case_when(
    NumCarVan_B02ID == 1 ~ '0',
    NumCarVan_B02ID == 2 ~ '1',
    NumCarVan_B02ID == 3 ~ '2+',
    TRUE ~ as.character(NumCarVan_B02ID)
  ))

# Recode number of adults in household(HHoldNumAdults) as hh_adults
unclassified_build <- unclassified_build %>%
  mutate(hh_adults = case_when(
    HHoldNumAdults == 1 ~ '1', # 1 Adult
    HHoldNumAdults == 2 ~ '2', # 2 Adults
    HHoldNumAdults >= 3 ~ '3+', # 3+ Adults
    TRUE ~ as.character(HHoldNumAdults)
  ))


# Adapt number of cars available to NTEM methodology
unclassified_build <- unclassified_build %>%
  mutate(cars = case_when(
    HHoldNumAdults == 1 & cars == '1' ~ '1+',
    HHoldNumAdults == 1 & cars == '2+' ~ '1+',
    TRUE ~ as.character(cars)
  ))

# Drop cars = -8
unclassified_build <- subset(unclassified_build, cars != -8)


# Recode area type (HHoldAreaType1_B01ID) as NTEM area classification area_type
unclassified_build <- unclassified_build %>%
  mutate(area_type = case_when(
    HHoldAreaType1_B01ID == 1 ~ '1',
    HHoldAreaType1_B01ID == 2 ~ '2',
    HHoldAreaType1_B01ID == 3 ~ '3',
    HHoldAreaType1_B01ID == 4 ~ '3',
    HHoldAreaType1_B01ID == 5 ~ '3',
    HHoldAreaType1_B01ID == 6 ~ '3',
    HHoldAreaType1_B01ID == 7 ~ '3',
    HHoldAreaType1_B01ID == 8 ~ '3',
    HHoldAreaType1_B01ID == 9 ~ '4',
    HHoldAreaType1_B01ID == 10 ~ '5',
    HHoldAreaType1_B01ID == 11 ~ '6',
    HHoldAreaType1_B01ID == 12 ~ '6',
    HHoldAreaType1_B01ID == 13 ~ '7',
    HHoldAreaType1_B01ID == 14 ~ '7',
    HHoldAreaType1_B01ID == 15 ~ '8',
    TRUE ~ as.character(HHoldAreaType1_B01ID)
  ))


# Drop area_type = -8
unclassified_build <- subset(unclassified_build, area_type != -8)


# Convert SOC Types(XSOC2000_B02ID) as soc_stat
unclassified_build <- unclassified_build %>%
  mutate(soc_cat = case_when(
    XSOC2000_B02ID == 1 ~ '1', # 1	Managers and senior officials
    XSOC2000_B02ID == 2 ~ '1', # 2	Professional occupations
    XSOC2000_B02ID == 3 ~ '1', # 3	Associate professional and technical occupations
    XSOC2000_B02ID == 4 ~ '2', # 4	Administrative and secretarial occupations
    XSOC2000_B02ID == 5 ~ '2', # 5	Skilled trades occupations
    XSOC2000_B02ID == 6 ~ '2', # 6	Personal service occupations
    XSOC2000_B02ID == 7 ~ '2', # 7	Sales and customer service occupations
    XSOC2000_B02ID == 8 ~ '3', # 8	Process, plant and machine operatives
    XSOC2000_B02ID == 9 ~ '3', # 9	Elementary occupations
    TRUE ~ as.character(XSOC2000_B02ID)
  ))


# NS-Sec already in correct classification, rename for legibility
unclassified_build <- unclassified_build %>%
  rename(ns_sec = NSSec_B03ID)


# recode main mode(MainMode_B04ID) as main_mode
unclassified_build <- unclassified_build %>%
  mutate(main_mode = case_when(
    MainMode_B04ID == 1 ~ '1', # Walk
    MainMode_B04ID == 2 ~ '2', # Bicycle
    MainMode_B04ID == 3 ~ '3', # Car/van driver
    MainMode_B04ID == 4 ~ '3', # Car/van passenger
    MainMode_B04ID == 5 ~ '3', # Motorcycle
    MainMode_B04ID == 6 ~ '3', # Other private transport
    MainMode_B04ID == 7 ~ '5', # Bus in London
    MainMode_B04ID == 8 ~ '5', # Other local bus
    MainMode_B04ID == 9 ~ '5', # Non-local bus
    MainMode_B04ID == 10 ~ '99', # London Underground - leave for now
    MainMode_B04ID == 11 ~ '6', # Surface rail
    MainMode_B04ID == 12 ~ '3', # Taxi/minicab ie. a car
    MainMode_B04ID == 13 ~ '5', # Other public transport ie. small bus or light rail.
    TRUE ~ as.character(MainMode_B04ID)
  ))

# Drop main_mode = 99 - London Underground as not modelled
unclassified_build <- subset(unclassified_build, main_mode != '99')


# Set time period params
am_peak <- c(8,9,10)
inter_peak <- c(11,12,13,14,15,16)
pm_peak <- c(17,18,19)
off_peak <- c(1,2,3,4,5,6,7,20,21,22,23,24)


# Create start time based on day(TravDay) and time period(TripTravTime)
unclassified_build <- unclassified_build %>%
  mutate(start_time = case_when(
    TravDay %in% c(1,2,3,4,5) & TripStart_B01ID %in% am_peak ~ '1', # Weekday AM peak
    TravDay %in% c(1,2,3,4,5) & TripStart_B01ID %in% inter_peak ~ '2', # Weekday IP peak
    TravDay %in% c(1,2,3,4,5) & TripStart_B01ID %in% pm_peak ~ '3', # Weekday PM peak
    TravDay %in% c(1,2,3,4,5) & TripStart_B01ID %in% off_peak ~ '4', # Offpeak
    TravDay %in% c(6) ~ '5', # Saturday
    TravDay %in% c(7) ~ '6', # Sunday
    TRUE ~ as.character('unclassified')
  ))


# # Create end time based on day(TravDay) and time period(TripTravTime)
# unclassified_build <- unclassified_build %>%
#   mutate(end_time = case_when(
#     TravDay %in% c(1,2,3,4,5) & TripEnd_B01ID %in% am_peak ~ '1', # Weekday AM peak
#     TravDay %in% c(1,2,3,4,5) & TripEnd_B01ID %in% inter_peak ~ '2', # Weekday IP peak
#     TravDay %in% c(1,2,3,4,5) & TripEnd_B01ID %in% pm_peak ~ '3', # Weekday PM peak
#     TravDay %in% c(1,2,3,4,5) & TripEnd_B01ID %in% off_peak ~ '4', # Offpeak
#     TravDay %in% c(6) ~ '5', # Saturday
#     TravDay %in% c(7) ~ '6', # Sunday
#     TRUE ~ as.character('unclassified')
#   ))


# Drop unclassified time_period - apply only for time_period regression?
unclassified_build <- subset(unclassified_build, start_time != 'unclassified' & end_time != 'unclassified')


# Add new area_type
unclassified_build <- unclassified_build %>% left_join(new_area_types, by = c("HHoldOSWard_B01ID" = "uk_ward_zones"))


# Transform catgeorical variables to factors
facts <- c("hb_purpose", "age_work_status", "gender", "hh_adults", "cars", "area_type", "new_area_type", "soc_cat", "ns_sec", "main_mode", "start_time")
unclassified_build <- unclassified_build %>% mutate_at(facts, funs(factor))


#### Analysis to remove incomplete surveys for prior years. ####

# Get unq household by year
unq_household <- unclassified_build %>%
  select(SurveyYear, HouseholdID, OutCom_B02ID) %>%
  distinct()

household_individual_count <- unclassified_build %>%
  filter(!is.na(IndividualID)) %>%
  select(SurveyYear, HouseholdID, IndividualID) %>%
  distinct() %>%
  group_by(SurveyYear, HouseholdID) %>%
  count() %>%
  rename(individuals = n)

household_trip_count <- unclassified_build %>%
  filter(!is.na(TripID)) %>%
  select(SurveyYear, HouseholdID, TripID) %>%
  distinct() %>%
  group_by(SurveyYear, HouseholdID) %>%
  count() %>%
  rename(trips = n)

household_days_count <- unclassified_build %>%
  filter(!is.na(TripID)) %>%
  select(SurveyYear, HouseholdID, TravDay) %>%
  distinct() %>%
  group_by(SurveyYear, HouseholdID) %>%
  count() %>%
  rename(days = n)

household_trip_distance <- unclassified_build %>%
  filter(!is.na(TripDisIncSW)) %>%
  select(SurveyYear, HouseholdID, TripDisIncSW) %>%
  distinct() %>%
  group_by(SurveyYear, HouseholdID) %>%
  count() %>%
  rename(logged_distance = n)

household_trip_time <- unclassified_build %>%
  filter(!is.na(TripTravTime)) %>%
  select(SurveyYear, HouseholdID, TripTravTime) %>%
  distinct() %>%
  group_by(SurveyYear, HouseholdID) %>%
  count() %>%
  rename(logged_time = n)

unq_household <- unq_household %>%
  left_join(household_individual_count) %>%
  left_join(household_trip_count) %>%
  left_join(household_days_count) %>%
  left_join(household_trip_distance) %>%
  left_join(household_trip_time) %>%
  mutate(individuals = replace_na(individuals, 0)) %>%
  mutate(trips = replace_na(trips, 0)) %>%
  mutate(days = replace_na(days, 0)) %>%
  mutate(logged_distance = replace_na(logged_distance, 0)) %>%
  mutate(logged_time = replace_na(logged_time, 0))


# Remove households with no trips and with n/a for cars to produce usable dataset nts_completed

usable_households <- unq_household %>%
  filter(trips > 0) %>%
  select(SurveyYear, HouseholdID)

nts_completed <- usable_households %>%
  left_join(unclassified_build) %>%
  filter(cars!='-8')

# Calculate weighted trips
nts_completed <- nts_completed %>%
  mutate(weighted_trip = W1 * W5xHh * W2)


#### Recode main mode, calculat mode share for trip purposes and export ####

# Recode main mode(MainMode_B04ID) as main_mode (car/bus/rail/walk, small bus & light rail = bus)
nts_completed <- nts_completed %>%
  mutate(main_mode = case_when(
    MainMode_B04ID == 1 ~ 'walk', # Walk
    MainMode_B04ID == 3 ~ 'car', # Car/van driver
    MainMode_B04ID == 4 ~ 'car', # Car/van passenger
    MainMode_B04ID == 5 ~ 'car', # Motorcycle
    MainMode_B04ID == 6 ~ 'car', # Other private transport
    MainMode_B04ID == 7 ~ 'bus', # Bus in London
    MainMode_B04ID == 8 ~ 'bus', # Other local bus
    MainMode_B04ID == 9 ~ 'bus', # Non-local bus
    MainMode_B04ID == 11 ~ 'rail', # Surface rail
    MainMode_B04ID == 12 ~ 'car', # Taxi/minicab ie. a car
    MainMode_B04ID == 13 ~ 'bus', # Other public transport ie. small bus or light rail.
    TRUE ~ as.character('unclassified')
  ))

# Drop modes that are not modelled = cycling, tube
nts_completed <- subset(nts_completed, main_mode != 'unclassified')


# Recode trip purposes as commute/business/other
mode_share <- nts_completed %>% mutate(purpose = case_when(
    hb_purpose == 1  ~ '1', # Commute trips
    hb_purpose == 2  ~ '2', # Business trips
    hb_purpose %in% c(3,4,5,6,7,8) ~ '3', # Other trips
    TRUE ~ as.character('unclassified')
  ))

# calculate mode share for purposes
mode_share_1 <- mode_share %>%
  filter(purpose == '1' | purpose == '2') %>%
  filter(soc_cat != -8 & soc_cat != -9  ) %>%
  select(purpose, soc_cat, main_mode, weighted_trip) %>%
  group_by(purpose, soc_cat, main_mode) %>%
  summarise(weighted_group_trips = sum(weighted_trip, na.rm = TRUE)) %>% 
  mutate(share = weighted_group_trips/sum(weighted_group_trips))

mode_share_2 <- mode_share %>%
  filter(purpose == '3') %>%
  filter(ns_sec != -9) %>%
  select(purpose, ns_sec, main_mode,weighted_trip) %>%
  group_by(purpose, ns_sec, main_mode) %>%
  summarise(weighted_group_trips = sum(weighted_trip, na.rm = TRUE)) %>%
  mutate(share = weighted_group_trips/sum(weighted_group_trips))

# Combine and export
mode_share <- bind_rows(mode_share_1, mode_share_2)
mode_share %>% write_csv("Y:/NTS/mode_time_splits/aggregate_mode_share_hb_only.csv")

