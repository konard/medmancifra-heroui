import type {Repair, RepairType} from "./api";

import {Button, Input, Label, ListBox, Modal, Select, TextField} from "@heroui/react";
import React, {useState} from "react";

interface RepairEditModalProps {
  repair: Repair;
  repairTypes: RepairType[];
  isOpen: boolean;
  onClose: () => void;
  onSave: (id: string, data: Partial<Omit<Repair, "id">>) => Promise<void>;
}

export function RepairEditModal({
  isOpen,
  onClose,
  onSave,
  repair,
  repairTypes,
}: RepairEditModalProps) {
  const [repairTypeId, setRepairTypeId] = useState(repair.repairTypeId);
  const [startDate, setStartDate] = useState(repair.startDate ?? "");
  const [endDate, setEndDate] = useState(repair.endDate ?? "");
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(repair.id, {
        endDate: endDate.trim() === "" ? null : endDate,
        repairTypeId,
        startDate,
      });
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal.Backdrop isOpen={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Modal.Container>
        <Modal.Dialog className="sm:max-w-[420px]">
          <Modal.CloseTrigger />
          <Modal.Header>
            <Modal.Heading>Редактирование ремонта</Modal.Heading>
          </Modal.Header>
          <Modal.Body className="flex flex-col gap-4 p-6">
            <Select
              isRequired
              className="w-full"
              placeholder="Выберите тип ремонта"
              selectedKey={repairTypeId}
              onSelectionChange={(key) => setRepairTypeId(key as string)}
            >
              <Label>Код / Наименование ремонта</Label>
              <Select.Trigger>
                <Select.Value />
                <Select.Indicator />
              </Select.Trigger>
              <Select.Popover>
                <ListBox>
                  {repairTypes.map((rt) => (
                    <ListBox.Item key={rt.id} id={rt.id} textValue={`${rt.code} — ${rt.name}`}>
                      <span className="font-mono font-medium">{rt.code}</span>
                      <span className="ml-2 text-muted">{rt.name}</span>
                      <ListBox.ItemIndicator />
                    </ListBox.Item>
                  ))}
                </ListBox>
              </Select.Popover>
            </Select>

            <TextField className="w-full" value={startDate} onChange={setStartDate}>
              <Label>Дата начала</Label>
              <Input placeholder="ГГГГ-ММ-ДД" type="date" />
            </TextField>

            <TextField className="w-full" value={endDate} onChange={setEndDate}>
              <Label>Дата окончания (оставьте пустым, если ремонт продолжается)</Label>
              <Input placeholder="ГГГГ-ММ-ДД" type="date" />
            </TextField>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onPress={onClose}>
              Отмена
            </Button>
            <Button isDisabled={isSaving} onPress={handleSave}>
              {isSaving ? "Сохранение..." : "Сохранить"}
            </Button>
          </Modal.Footer>
        </Modal.Dialog>
      </Modal.Container>
    </Modal.Backdrop>
  );
}
