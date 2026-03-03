import type {Field} from "./types";

import fieldsData from "../mock/fields.json";

// Simulates async REST call for fields (drill site locations)
export async function fetchFields(): Promise<Field[]> {
  return Promise.resolve(fieldsData as Field[]);
}

export async function updateField(id: string, data: Partial<Omit<Field, "id">>): Promise<Field> {
  const field = fieldsData.find((f) => f.id === id);

  if (!field) throw new Error(`Field with id "${id}" not found`);

  return Promise.resolve({...field, ...data} as Field);
}
