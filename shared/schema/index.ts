/**
 * Schema index file
 * 
 * This file exports all database schema definitions from individual files,
 * making them available as a single importable namespace.
 */

// Import and export tax district related schemas
import { 
  taxDistricts, 
  districtConfigurations,
  taxDistrictsRelations,
  districtConfigurationsRelations
} from './taxDistricts';
export { 
  taxDistricts, 
  districtConfigurations,
  taxDistrictsRelations,
  districtConfigurationsRelations 
};

// Import and export tax code related schemas
import { 
  taxCodes, 
  taxCodeHistoricalRates, 
  taxCodeToTaxDistrict,
  taxCodesRelations,
  taxCodeHistoricalRatesRelations,
  taxCodeToTaxDistrictRelations
} from './taxCodes';
export { 
  taxCodes, 
  taxCodeHistoricalRates, 
  taxCodeToTaxDistrict,
  taxCodesRelations,
  taxCodeHistoricalRatesRelations,
  taxCodeToTaxDistrictRelations
};

// Import and export property related schemas
import { 
  properties, 
  propertyAssessments, 
  propertyDetails,
  propertiesRelations,
  propertyAssessmentsRelations,
  propertyDetailsRelations
} from './properties';
export { 
  properties, 
  propertyAssessments, 
  propertyDetails,
  propertiesRelations,
  propertyAssessmentsRelations,
  propertyDetailsRelations
};

// Import and export user related schemas
import { users, userRoles, usersRelations, userRolesRelations } from './users';
export { users, userRoles, usersRelations, userRolesRelations };

// Import and export levy related schemas
import { 
  levies,
  levyScenarios, 
  levyScenarioResults,
  leviesRelations,
  levyScenariosRelations,
  levyScenarioResultsRelations
} from './levies';
export { 
  levies,
  levyScenarios, 
  levyScenarioResults,
  leviesRelations,
  levyScenariosRelations,
  levyScenarioResultsRelations
};

// Import and export log related schemas
import { 
  importLogs, 
  userActionLogs, 
  levyOverrideLogs,
  importLogsRelations,
  userActionLogsRelations,
  levyOverrideLogsRelations
} from './logs';
export { 
  importLogs, 
  userActionLogs, 
  levyOverrideLogs,
  importLogsRelations,
  userActionLogsRelations,
  levyOverrideLogsRelations
};

// Import and export API call logs
import { 
  apiCallLogs,
  apiCallLogsRelations
} from './apiLogs';
export { 
  apiCallLogs,
  apiCallLogsRelations
};