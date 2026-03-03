// Domain types for the Well Repairs management system

export interface Field {
  id: string;
  name: string;
}

export interface RepairType {
  id: string;
  code: string;
  name: string;
}

export interface Well {
  id: string;
  fieldId: string;
  cluster: string;
  wellNumber: string;
}

export interface Repair {
  id: string;
  wellId: string;
  startDate: string; // ISO date string YYYY-MM-DD
  endDate: string | null; // null means repair is ongoing
  repairTypeId: string;
}

// Enriched view types for display

export interface WellWithLatestRepair extends Well {
  field?: Field;
  latestRepair?: RepairWithType;
}

export interface RepairWithType extends Repair {
  repairType?: RepairType;
}
