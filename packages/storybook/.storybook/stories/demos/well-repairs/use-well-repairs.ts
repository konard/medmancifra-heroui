import type {Field, Repair, RepairType, RepairWithType, Well, WellWithLatestRepair} from "./api";

import {useCallback, useEffect, useMemo, useState} from "react";

import {
  fetchAllRepairs,
  fetchFields,
  fetchRepairTypes,
  fetchWells,
  updateRepair,
  updateWell,
} from "./api";

export interface WellRepairsState {
  wells: WellWithLatestRepair[];
  allRepairs: Repair[];
  fields: Field[];
  repairTypes: RepairType[];
  isLoading: boolean;
  selectedWellId: string | null;
  selectWell: (wellId: string | null) => void;
  repairsForSelectedWell: RepairWithType[];
  handleUpdateWell: (id: string, data: Partial<Omit<Well, "id">>) => Promise<void>;
  handleUpdateRepair: (id: string, data: Partial<Omit<Repair, "id">>) => Promise<void>;
}

/** Builds an enriched list of wells sorted by most-recent repair start date (desc) */
function buildEnrichedWells(
  wells: Well[],
  repairs: Repair[],
  fields: Field[],
  repairTypes: RepairType[],
): WellWithLatestRepair[] {
  const repairsByWell = new Map<string, Repair[]>();

  for (const repair of repairs) {
    const list = repairsByWell.get(repair.wellId) ?? [];

    list.push(repair);
    repairsByWell.set(repair.wellId, list);
  }

  const enriched = wells.map((well): WellWithLatestRepair => {
    const wellRepairs = repairsByWell.get(well.id) ?? [];
    const sorted = [...wellRepairs].sort((a, b) =>
      (b.startDate ?? "").localeCompare(a.startDate ?? ""),
    );
    const latest = sorted[0];
    const latestRepair: RepairWithType | undefined = latest
      ? {...latest, repairType: repairTypes.find((rt) => rt.id === latest.repairTypeId)}
      : undefined;

    return {
      ...well,
      field: fields.find((f) => f.id === well.fieldId),
      latestRepair,
    };
  });

  // Sort wells by the start date of their latest repair, descending
  return enriched.sort((a, b) => {
    const dateA = a.latestRepair?.startDate ?? "";
    const dateB = b.latestRepair?.startDate ?? "";

    return dateB.localeCompare(dateA);
  });
}

export function useWellRepairs(): WellRepairsState {
  const [wells, setWells] = useState<Well[]>([]);
  const [allRepairs, setAllRepairs] = useState<Repair[]>([]);
  const [fields, setFields] = useState<Field[]>([]);
  const [repairTypes, setRepairTypes] = useState<RepairType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedWellId, setSelectedWellId] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchWells(), fetchAllRepairs(), fetchFields(), fetchRepairTypes()])
      .then(([w, r, f, rt]) => {
        setWells(w);
        setAllRepairs(r);
        setFields(f);
        setRepairTypes(rt);
        const first = w[0];

        if (first) setSelectedWellId(first.id);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const enrichedWells = useMemo(
    () => buildEnrichedWells(wells, allRepairs, fields, repairTypes),
    [wells, allRepairs, fields, repairTypes],
  );

  const repairsForSelectedWell = useMemo<RepairWithType[]>(() => {
    if (!selectedWellId) return [];

    const sorted = allRepairs
      .filter((r) => r.wellId === selectedWellId)
      .sort((a, b) => (b.startDate ?? "").localeCompare(a.startDate ?? ""));

    return sorted.map((r) => ({
      ...r,
      repairType: repairTypes.find((rt) => rt.id === r.repairTypeId),
    }));
  }, [selectedWellId, allRepairs, repairTypes]);

  const handleUpdateWell = useCallback(async (id: string, data: Partial<Omit<Well, "id">>) => {
    const updated = await updateWell(id, data);

    setWells((prev) => prev.map((w) => (w.id === id ? updated : w)));
  }, []);

  const handleUpdateRepair = useCallback(async (id: string, data: Partial<Omit<Repair, "id">>) => {
    const updated = await updateRepair(id, data);

    setAllRepairs((prev) => prev.map((r) => (r.id === id ? updated : r)));
  }, []);

  return {
    allRepairs,
    fields,
    handleUpdateRepair,
    handleUpdateWell,
    isLoading,
    repairTypes,
    repairsForSelectedWell,
    selectWell: setSelectedWellId,
    selectedWellId,
    wells: enrichedWells,
  };
}
