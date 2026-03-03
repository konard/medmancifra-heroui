import type {Field, Well, WellWithLatestRepair} from "./api";

import {Button} from "@heroui/react";
import React, {useState} from "react";

import {WellEditModal} from "./WellEditModal";

interface WellsTableProps {
  wells: WellWithLatestRepair[];
  fields: Field[];
  selectedWellId: string | null;
  onSelectWell: (wellId: string) => void;
  onUpdateWell: (id: string, data: Partial<Omit<Well, "id">>) => Promise<void>;
}

export function WellsTable({
  fields,
  onSelectWell,
  onUpdateWell,
  selectedWellId,
  wells,
}: WellsTableProps) {
  const [editingWell, setEditingWell] = useState<WellWithLatestRepair | null>(null);

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-border">
      <div className="flex items-center justify-between border-b border-border bg-surface-secondary px-4 py-3">
        <h2 className="text-sm font-semibold text-foreground">Скважины</h2>
        <span className="text-xs text-muted">{wells.length} записей</span>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 z-10 bg-surface-secondary">
            <tr>
              <th className="border-b border-border px-4 py-2 text-left font-medium text-muted">
                Месторождение
              </th>
              <th className="border-b border-border px-4 py-2 text-left font-medium text-muted">
                Куст
              </th>
              <th className="border-b border-border px-4 py-2 text-left font-medium text-muted">
                Скважина
              </th>
              <th className="border-b border-border px-4 py-2 text-left font-medium text-muted">
                Последний ремонт
              </th>
              <th className="border-b border-border px-4 py-2" />
            </tr>
          </thead>
          <tbody>
            {wells.map((well) => {
              const isSelected = well.id === selectedWellId;

              return (
                <tr
                  key={well.id}
                  className={`cursor-pointer border-b border-border transition-colors last:border-b-0 hover:bg-surface-secondary ${
                    isSelected ? "bg-accent-soft/20" : ""
                  }`}
                  onClick={() => onSelectWell(well.id)}
                >
                  <td className="px-4 py-2.5 text-foreground">{well.field?.name ?? "—"}</td>
                  <td className="px-4 py-2.5 text-foreground">{well.cluster}</td>
                  <td className="px-4 py-2.5 font-mono text-foreground">{well.wellNumber}</td>
                  <td className="px-4 py-2.5 text-muted">
                    {well.latestRepair ? (
                      <span className="text-xs">
                        {well.latestRepair.startDate}
                        {well.latestRepair.endDate === null && (
                          <span className="ml-1 rounded-full bg-warning-soft px-1.5 py-0.5 text-[10px] font-medium text-warning-soft-foreground">
                            В работе
                          </span>
                        )}
                      </span>
                    ) : (
                      <span className="text-xs">—</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5" onClick={(e) => e.stopPropagation()}>
                    <Button size="sm" variant="tertiary" onPress={() => setEditingWell(well)}>
                      Изменить
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {editingWell !== null && (
        <WellEditModal
          isOpen
          fields={fields}
          well={editingWell}
          onClose={() => setEditingWell(null)}
          onSave={onUpdateWell}
        />
      )}
    </div>
  );
}
