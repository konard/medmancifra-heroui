import type {Repair} from "./types";

import repairsData from "../mock/repairs.json";

// In-memory mutable store to simulate a REST backend
let repairsStore: Repair[] = [...(repairsData as Repair[])];

// Simulates async REST GET /repairs?wellId=:wellId
export async function fetchRepairsByWellId(wellId: string): Promise<Repair[]> {
  return Promise.resolve(repairsStore.filter((r) => r.wellId === wellId));
}

// Simulates async REST GET /repairs
export async function fetchAllRepairs(): Promise<Repair[]> {
  return Promise.resolve([...repairsStore]);
}

// Simulates async REST PUT /repairs/:id
export async function updateRepair(id: string, data: Partial<Omit<Repair, "id">>): Promise<Repair> {
  const existing = repairsStore.find((r) => r.id === id);

  if (!existing) throw new Error(`Repair with id "${id}" not found`);

  const updated: Repair = {...existing, ...data};

  repairsStore = repairsStore.map((r) => (r.id === id ? updated : r));

  return Promise.resolve(updated);
}
