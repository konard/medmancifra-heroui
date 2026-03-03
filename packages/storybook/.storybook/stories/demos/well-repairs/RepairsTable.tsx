import type {Repair, RepairType, RepairWithType} from "./api";

import {Button} from "@heroui/react";
import React, {useState} from "react";

import {RepairEditModal} from "./RepairEditModal";

interface RepairsTableProps {
  repairs: RepairWithType[];
  repairTypes: RepairType[];
  wellNumber: string;
  onUpdateRepair: (id: string, data: Partial<Omit<Repair, "id">>) => Promise<void>;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  try {
    return new Date(dateStr).toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function RepairsTable({
  onUpdateRepair,
  repairTypes,
  repairs,
  wellNumber,
}: RepairsTableProps) {
  const [editingRepair, setEditingRepair] = useState<RepairWithType | null>(null);

  if (repairs.length === 0) {
    return (
      <div className="flex h-full flex-col overflow-hidden rounded-xl border border-border">
        <div className="flex items-center border-b border-border bg-surface-secondary px-4 py-3">
          <h2 className="text-sm font-semibold text-foreground">
            Ремонты{wellNumber ? ` — скв. ${wellNumber}` : ""}
          </h2>
        </div>
        <div className="flex flex-1 items-center justify-center p-8 text-sm text-muted">
          Нет записей о ремонтах
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-border">
      <div className="flex items-center justify-between border-b border-border bg-surface-secondary px-4 py-3">
        <h2 className="text-sm font-semibold text-foreground">
          Ремонты{wellNumber ? ` — скв. ${wellNumber}` : ""}
        </h2>
        <span className="text-xs text-muted">{repairs.length} записей</span>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 z-10 bg-surface-secondary">
            <tr>
              <th className="border-b border-border px-4 py-2 text-left font-medium text-muted">
                Дата начала
              </th>
              <th className="border-b border-border px-4 py-2 text-left font-medium text-muted">
                Дата окончания
              </th>
              <th className="border-b border-border px-4 py-2 text-left font-medium text-muted">
                Код
              </th>
              <th className="border-b border-border px-4 py-2 text-left font-medium text-muted">
                Наименование
              </th>
              <th className="border-b border-border px-4 py-2" />
            </tr>
          </thead>
          <tbody>
            {repairs.map((repair) => {
              const isOngoing = repair.endDate === null;

              return (
                <tr
                  key={repair.id}
                  className={`border-b border-border last:border-b-0 ${
                    isOngoing ? "bg-warning-soft/10" : ""
                  }`}
                >
                  <td className="px-4 py-2.5 font-mono text-sm text-foreground">
                    {formatDate(repair.startDate)}
                  </td>
                  <td className="px-4 py-2.5">
                    {isOngoing ? (
                      <span className="inline-flex items-center gap-1.5">
                        <span className="size-2 animate-pulse rounded-full bg-warning" />
                        <span className="text-xs font-medium text-warning-foreground">
                          В работе
                        </span>
                      </span>
                    ) : (
                      <span className="font-mono text-sm text-foreground">
                        {formatDate(repair.endDate)}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="rounded-md bg-default px-1.5 py-0.5 font-mono text-xs font-medium text-foreground">
                      {repair.repairType?.code ?? "—"}
                    </span>
                  </td>
                  <td className="max-w-[180px] truncate px-4 py-2.5 text-foreground">
                    {repair.repairType?.name ?? "—"}
                  </td>
                  <td className="px-4 py-2.5">
                    <Button size="sm" variant="tertiary" onPress={() => setEditingRepair(repair)}>
                      Изменить
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {editingRepair !== null && (
        <RepairEditModal
          isOpen
          repair={editingRepair}
          repairTypes={repairTypes}
          onClose={() => setEditingRepair(null)}
          onSave={onUpdateRepair}
        />
      )}
    </div>
  );
}
