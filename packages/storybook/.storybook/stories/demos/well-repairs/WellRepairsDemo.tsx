import {Spinner} from "@heroui/react";
import React from "react";

import {RepairsTable} from "./RepairsTable";
import {useWellRepairs} from "./use-well-repairs";
import {WellsTable} from "./WellsTable";

export function WellRepairsDemo() {
  const {
    fields,
    handleUpdateRepair,
    handleUpdateWell,
    isLoading,
    repairTypes,
    repairsForSelectedWell,
    selectWell,
    selectedWellId,
    wells,
  } = useWellRepairs();

  const selectedWell = wells.find((w) => w.id === selectedWellId);

  if (isLoading) {
    return (
      <div className="flex h-[500px] items-center justify-center">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="flex h-[600px] gap-4 p-4">
      {/* Left: Wells table */}
      <div className="min-w-0 flex-1">
        <WellsTable
          fields={fields}
          selectedWellId={selectedWellId}
          wells={wells}
          onSelectWell={selectWell}
          onUpdateWell={handleUpdateWell}
        />
      </div>

      {/* Right: Repairs table for selected well */}
      <div className="min-w-0 flex-1">
        <RepairsTable
          repairs={repairsForSelectedWell}
          repairTypes={repairTypes}
          wellNumber={selectedWell?.wellNumber ?? ""}
          onUpdateRepair={handleUpdateRepair}
        />
      </div>
    </div>
  );
}
