import type {Well} from "./types";

import wellsData from "../mock/wells.json";

// In-memory mutable store to simulate a REST backend
let wellsStore: Well[] = [...(wellsData as Well[])];

// Simulates async REST GET /wells
export async function fetchWells(): Promise<Well[]> {
  return Promise.resolve([...wellsStore]);
}

// Simulates async REST PUT /wells/:id
export async function updateWell(id: string, data: Partial<Omit<Well, "id">>): Promise<Well> {
  const existing = wellsStore.find((w) => w.id === id);

  if (!existing) throw new Error(`Well with id "${id}" not found`);

  const updated: Well = {...existing, ...data};

  wellsStore = wellsStore.map((w) => (w.id === id ? updated : w));

  return Promise.resolve(updated);
}
