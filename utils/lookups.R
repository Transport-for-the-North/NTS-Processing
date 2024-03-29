match_columns <- function(x, df, lookup){
  
  ub_class <- class(df[[x]])
  
  ub_class <- paste0("as.", ub_class)
  
  match.fun(ub_class)(lookup[[x]])
  
}

join_lookup <- function(df, lookup_csv, keys, id,
                        filter_id = FALSE, 
                        filter_na = FALSE,
                        variable_expansion = FALSE,
                        lookup_dir = "D:/NTS/lookups/"){

  # Read in lookup csv
  lookup <- read_csv(str_c(lookup_dir, lookup_csv, ".csv"))
  
  lookup <- select(lookup, all_of(c(id, keys)))
  
  # Expand variable if required
  
  if(variable_expansion[1] != FALSE) {
    
    lookup <- reduce(variable_expansion, function(...) separate_rows(..., sep = "_"), .init = lookup)
    
  }
  
  # Convert to type in unclassified build
  lu_cols <- colnames(lookup)
  ub_cols <- colnames(df)
  
  common_cols <- lu_cols[lu_cols %in% ub_cols]
  
  lookup[common_cols] <- lapply(common_cols, match_columns, df, lookup)
  
  #lookup <- mutate_at(lookup, all_of(keys), as.double)
  
  # Merge df with lookup by keys
  df <- df %>%
    left_join(lookup, by = keys)
  
  # Any extra filters?
  if(filter_id != FALSE) {
    
    df <- df %>%
      filter(is.na(get(id)) | get(id) != filter_id)
    
  }
  
  if(filter_na != FALSE) {
    
    df <- df %>%
      filter(!is.na(get(id)))
    
  }
  
  return(df)
  
}

# New trip purpose definition - NN ---------------------------------------------
lu_direction <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "trip_direction---TripPurpFrom_B01ID--TripPurpTo_B01ID",
              keys = c("TripPurpFrom_B01ID","TripPurpTo_B01ID"),
              id = "trip_direction",
              variable_expansion = c("TripPurpFrom_B01ID","TripPurpTo_B01ID"))
  
}

lu_purpose <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "trip_purpose---MainMode_B11ID--TripPurpFrom_B01ID--TripPurpTo_B01ID",
              keys = c("MainMode_B11ID", "TripPurpFrom_B01ID", "TripPurpTo_B01ID"),
              id = "trip_purpose",
              variable_expansion = c("MainMode_B11ID", "TripPurpFrom_B01ID", "TripPurpTo_B01ID"))
  
}

lu_occupant <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "veh_occupant---MainMode_B11ID",
              keys = c("MainMode_B11ID"),
              id = "occupant",
              variable_expansion = c("MainMode_B11ID"))
  
}

# Trip Purposes ----------------------------------------------------------------

lu_trip_origin <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "trip_origin---TripPurpFrom_B01ID",
              keys = "TripPurpFrom_B01ID",
              id = "trip_origin",
              variable_expansion = "TripPurpFrom_B01ID")
  
}

lu_hb_purpose <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "hb_purpose---TripPurpTo_B01ID--MainMode_B11ID",
              keys = c("TripPurpTo_B01ID", "MainMode_B11ID"),
              id = "hb_purpose",
              variable_expansion = c("TripPurpTo_B01ID", "MainMode_B11ID"))
  
}

lu_nhb_purpose <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "nhb_purpose---TripPurpTo_B01ID",
              keys = "TripPurpTo_B01ID",
              id = "nhb_purpose",
              variable_expansion = "TripPurpTo_B01ID")
  
}

lu_nhb_purpose_hb_leg <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "nhb_purpose_hb_leg---TripPurpFrom_B01ID--MainMode_B11ID",
              keys = c("TripPurpFrom_B01ID", "MainMode_B11ID"),
              id = "nhb_purpose_hb_leg",
              variable_expansion = c("TripPurpFrom_B01ID", "MainMode_B11ID"))
  
}

# Other variables --------------------------------------------------------------

lu_gender <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "gender---Sex_B01ID--Age_B01ID",
              keys = c("Sex_B01ID",  "Age_B01ID"),
              id = "gender",
              variable_expansion = c("Sex_B01ID",  "Age_B01ID"))
  
}

lu_aws <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "aws--Age_B01ID---EcoStat_B01ID",
              keys = c("Age_B01ID", "EcoStat_B01ID"),
              id = "aws",
              filter_na = filter_na,
              variable_expansion = c("Age_B01ID", "EcoStat_B01ID"))
  
}

lu_hh_type <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "hh_type--HHoldNumAdults---NumCarVan",
              keys = c("HHoldNumAdults", "NumCarVan"),
              id = "hh_type",
              variable_expansion = c("HHoldNumAdults", "NumCarVan"), #NumCarVan originally
              filter_na = filter_na)

}

lu_tt <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "tfn_tt--ntem_tt---aws--gender--hh_type--ns--soc",
              keys = c("aws", "gender", "hh_type", "ns", "soc"),
              id = c("tfn_tt", "ntem_tt"))
}

lu_tfn_tt <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "traveller_type---age_work_status--gender--hh_type--soc--ns",
              keys = c("age_work_status", "gender", "hh_type", "soc", "ns"),
              id = c("tfn_traveller_type", "ntem_traveller_type"))
}

lu_ntem_tt <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "ntem_tt---aws--gender--hh_type",
              keys = c("aws", "gender", "hh_type"),
              id = "ntem_tt")
}

lu_soc <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "soc---XSOC2000_B02ID--Age_B01ID--EcoStat_B01ID",
              keys = c("XSOC2000_B02ID", "Age_B01ID", "EcoStat_B01ID"),
              id = "soc",
              variable_expansion = c("XSOC2000_B02ID", "Age_B01ID", "EcoStat_B01ID"),
              filter_na = filter_na)
  
}

lu_main_mode <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "main_mode---MainMode_B11ID",
              keys = "MainMode_B11ID",
              id = "main_mode",
              variable_expansion = "MainMode_B11ID",
              filter_na = filter_na)
  
}

lu_stage_mode <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "stage_mode---StageMode_B11ID",
              keys = "StageMode_B11ID",
              id = "stage_mode",
              variable_expansion = "StageMode_B11ID",
              filter_na = filter_na)
  
}

lu_start_time <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "start_time---TravelWeekDay_B01ID--TripStart_B01ID",
              keys = c("TravelWeekDay_B01ID", "TripStart_B01ID"),
              id = "start_time",
              variable_expansion = c("TravelWeekDay_B01ID", "TripStart_B01ID"),
              filter_na = filter_na)
  
}

lu_end_time<- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "end_time---TravelWeekDay_B01ID--TripEnd_B01ID",
              keys = c("TravelWeekDay_B01ID","TripEnd_B01ID"),
              id = "end_time",
              variable_expansion = c("TravelWeekDay_B01ID", "TripEnd_B01ID"),
              filter_na = filter_na)
  
}

lu_tfn_at <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "tfn_at---PSUPSect",
              keys = "PSUPSect",
              id = "tfn_at",
              filter_na = filter_na)
  
}

lu_sw_weight <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "sw_weight---TripDisIncSW_B01ID--MainMode_B04ID",
              keys = c("TripDisIncSW_B01ID","MainMode_B04ID"),
              id = "sw_weight",
              variable_expansion = c("TripDisIncSW_B01ID","MainMode_B04ID"))
  
}

lu_is_north <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "is_north---HHoldOSLAUA_B01ID",
              keys = "HHoldOSLAUA_B01ID",
              id = "is_north")
  
}

lu_ntem_at <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "ntem_at---PSUAreaType2_B01ID",
              keys = "PSUAreaType2_B01ID",
              id = "ntem_at",
              variable_expansion = "PSUAreaType2_B01ID")
  
}

lu_ntem_aws <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "ntem_aws--Age_B01ID---EcoStat_B01ID",
              keys = c("Age_B01ID", "EcoStat_B01ID"),
              id = "ntem_aws",
              filter_na = filter_na,
              variable_expansion = c("Age_B01ID", "EcoStat_B01ID"))
  
}

lu_ntem_main_mode <- function(df, filter_na = TRUE){
  
  join_lookup(df = df,
              lookup_csv = "ntem_main_mode---MainMode_B11ID",
              keys = "MainMode_B11ID",
              id = "ntem_main_mode",
              variable_expansion = "MainMode_B11ID",
              filter_na = filter_na)
  
}

lu_agg_gor_from <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "agg_gor_from---TripOrigGOR_B02ID",
              keys = "TripOrigGOR_B02ID",
              id = "agg_gor_from",
              variable_expansion = "TripOrigGOR_B02ID")
  
}

lu_agg_gor_to <- function(df){
  
  join_lookup(df = df,
              lookup_csv = "agg_gor_to---TripDestGOR_B02ID",
              keys = "TripDestGOR_B02ID",
              id = "agg_gor_to",
              variable_expansion = "TripDestGOR_B02ID")
  
}
