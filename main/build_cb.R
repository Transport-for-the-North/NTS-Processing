define_nts_audit_params <- function(nts_dat){

  # Include more variable to check. i.e. trip purpose, age_work_status
  
  nts_dat %>%
    count(SurveyYear)
  
}

cb_preprocess <- function(ub, cb_version){
  
  # Post codes
  ub <- ub %>% 
    mutate(PSUPSect = str_replace(PSUPSect, "^(.*\\s.).*", "\\1"),
           PSUPSect = str_replace_all(PSUPSect, " ", "")) 
    
  ub %>% 
    rename(ns = NSSec_B03ID) %>%
    mutate(ns = ifelse(ns == -9, 6, ns)) %>% 
    group_by(HouseholdID) %>%
    mutate(ns = min(ns)) %>%
    ungroup() %>%
    mutate(ns = ifelse(ns == 6, 5, ns))
  
}

build_cb <- function(user,
                     drive,
                     version_in,
                     version_out,
                     build_type = "",
                     save_processed = FALSE){
  
  library_list <- c("dplyr",
                    "stringr",
                    "readr",
                    "tidyr",
                    "purrr")
  
  library_c(library_list)
  
  # Directories -------------------------------------------------------------
   
  # Imports
  y_dir <- "Y:/NTS/"
  c_dir <- str_c("C:/Users/", user, "/Documents/NTS_C/")
  nts_dir <- ifelse(drive == "Y", y_dir, c_dir)
  
  ub_dir <- str_c(nts_dir, "unclassified builds/ub_", version_in, ".csv")
  
  # Exports
  export_dir <- str_c(nts_dir, "classified builds/")
  dir.create(export_dir, showWarnings = FALSE)
  
  out_cb_dir <- str_c(export_dir, "cb_", version_out, ".csv")
  out_hb_tr_dir <- str_c(export_dir, "cb_hb_tr_", version_out, ".csv")
  out_hb_weights_dir <- str_c(nts_dir, "import/hb_trip_rates/hb_response_weights_", version_out, ".csv")
  
  # Unclassified build
  ub <- read_csv(ub_dir)
  
  # Audit 1
  nts_audit <- define_nts_audit_params(ub)
  
  # Pre-processing ----------------------------------------------------------
  
  # All non-lookup pre processing
  ub <- cb_preprocess(ub, version)
   
  # Classify Purposes -------------------------------------------------------
  
  # Remove Just-Walk trips 17, Other non-escort, and other escort 
  ub <- ub %>%
    filter(TripPurpose_B01ID != 17,
           !TripPurpTo_B01ID %in% c(16,22))
  
  # Remove trips which are home to 'escort home' and 'escort home' to home
  ub <- ub %>%
    filter(!(TripPurpFrom_B01ID == 23 & TripPurpTo_B01ID == 17), # 11,438 records
           !(TripPurpFrom_B01ID == 17 & TripPurpTo_B01ID == 23)) # 24,810 records
  
  # Define trip purposes
  ub <- ub %>%
    lu_trip_origin() %>%
    lu_hb_purpose() %>%
    lu_nhb_purpose() %>% 
    lu_nhb_purpose_hb_leg() %>%
    mutate(p = ifelse(trip_origin == "hb", hb_purpose, nhb_purpose))
  
  # Classify Other variables ------------------------------------------------
  
  cb <- ub %>%
    lu_gender() %>%
    lu_aws() %>%
    lu_hh_type() %>%
    lu_main_mode() %>%
    lu_start_time() %>%
    lu_end_time() %>%
    lu_sw_weight() %>% 
    lu_is_north() %>% 
    lu_soc() %>%
    lu_tfn_at() %>% 
    lu_tt()
  
  if(version_out == "ntem"){
    
    cb <- cb %>% 
      lu_ntem_at() %>%
      lu_ntem_aws() %>% 
      lu_ntem_main_mode()
    
  }
  
  if(save_processed) write_csv(cb, out_cb_dir)
  
  if(build_type == "hb_trip_rates"){
    
    if(version_out == "tfn"){
      
      grouping_vars <- c("IndividualID", "p", "SurveyYear", "aws", "gender",
                         "hh_type", "soc", "ns", "tfn_at")
      
      grouping_vars <- colnames(cb)[colnames(cb) %in% grouping_vars]
      
    } else if (version_out == "ntem"){
      
      grouping_vars <- c("IndividualID", "p", "SurveyYear", "aws", "gender",
                         "hh_type", "ntem_at")
      
      grouping_vars <- colnames(cb)[colnames(cb) %in% grouping_vars]
      
    }
    
    # Remove Air trips
    cb <- filter(cb, main_mode != 8)
    
    if(version_out == "ntem"){
      
      cb <- filter(cb, SurveyYear %in% 2002:2012)
      
    }
    
    # Weight trips by short walk and calculate weekly trips
    weighted_trips <- cb %>%
      filter(p %in% 1:8,
             W1 == 1) %>%
      group_by_at(grouping_vars) %>%
      summarise(weekly_trips = sum(JJXSC)) %>%
      ungroup()
    
    grouping_vars <- str_subset(grouping_vars, "^p$", negate = TRUE)
    #grouping_vars <- c(grouping_vars, "W2")
    
    # Every individual must have an observation for each trip purpose
    hb_trip_rates_out <- weighted_trips %>%
      complete(nesting(!!!dplyr::syms(grouping_vars)),
               p = 1:8,
               fill = list(weekly_trips = 0))
    
    write_csv(hb_trip_rates_out, out_hb_tr_dir)
    
    response_weights <- cb %>% 
      filter(p %in% 1:8,
             W1 == 1) %>%
      select(IndividualID, p, SurveyYear, W5xHH, JJXSC) %>% 
      mutate(trips = 1) %>% 
      complete(nesting(IndividualID, SurveyYear),
               p = 1:8,
               fill = list(W5xHH = 0, trips = 0, JJXSC = 0)) %>% 
      group_by(p, SurveyYear) %>% 
      summarise(r_weights = sum(W5xHH*JJXSC)/sum(trips*JJXSC),
                count = sum(trips)) %>% 
      ungroup()
      
    write_csv(response_weights, out_hb_weights_dir)
    
  }
  
}