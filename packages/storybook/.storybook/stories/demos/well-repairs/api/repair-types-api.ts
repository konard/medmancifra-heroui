import type {RepairType} from "./types";

import repairTypesData from "../mock/repair-types.json";

// Simulates async REST call for repair type reference data
export async function fetchRepairTypes(): Promise<RepairType[]> {
  return Promise.resolve(repairTypesData as RepairType[]);
}
