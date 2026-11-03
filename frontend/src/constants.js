// src/constants.js
// All categorical values sourced directly from filtered_data.csv
// and the trained preprocessor categories.

export const CITIES = [
  { value: 'mumbai',         label: 'Mumbai' },
  { value: 'western mumbai', label: 'Western Mumbai' },
  { value: 'central mumbai', label: 'Central Mumbai' },
  { value: 'mumbai south',   label: 'Mumbai South' },
]

export const PROPERTY_TYPES = [
  { value: 'apartment',         label: 'Apartment' },
  { value: 'independent floor', label: 'Independent Floor' },
  { value: 'independent house', label: 'Independent House' },
  { value: 'villa',             label: 'Villa' },
  // 'studio apartment' exists in property catalog but not in
  // property_type_pref OHE categories — omit from pref dropdown
]

export const FURNISHED_OPTIONS = [
  { value: 'unfurnished',    label: 'Unfurnished' },
  { value: 'semi-furnished', label: 'Semi-Furnished' },
  { value: 'furnished',      label: 'Furnished' },
]

// Top localities by frequency (305 total; showing top 60 for usability)
export const LOCALITIES = [
  'thane','mira road','kandivali','kharghar','andheri','dombivali',
  'panvel','chembur','borivali','kalyan','mulund','malad','goregaon',
  'kanjurmarg','ghatkopar','vikhroli','powai','ambernath','virar','vasai',
  'taloja','ulwe','wadala','sion','naigaon','bhandup','bandra','jogeshwari',
  'kurla','byculla','dahisar','airoli','ghansoli','belapur','khopoli',
  'vile parle','santacruz','andheri west','andheri east','juhu','marol',
  'manpada','balkum','ambivali','badlapur','navi mumbai','nerul','vashi',
  'kopar khairane','turbhe','ghatakopar','diva','titwala','mumbai central',
  'lower parel','prabhadevi','dadar','matunga','worli',
].map(v => ({ value: v, label: v.replace(/\b\w/g, c => c.toUpperCase()) }))

export const DEFAULT_PREFS = {
  budget_max:          15000000,
  min_area:            900,
  max_area:            1400,
  bedroom_pref:        3,
  bathroom_pref:       2,
  balcony_pref:        1,
  max_age:             10,
  locality_pref:       'mira road',
  city_pref:           'mumbai',
  property_type_pref:  'apartment',
  furnished_pref:      'unfurnished',
}
