import type {Field, Well} from "./api";

import {Button, Input, Label, ListBox, Modal, Select, TextField} from "@heroui/react";
import React, {useState} from "react";

interface WellEditModalProps {
  well: Well;
  fields: Field[];
  isOpen: boolean;
  onClose: () => void;
  onSave: (id: string, data: Partial<Omit<Well, "id">>) => Promise<void>;
}

export function WellEditModal({fields, isOpen, onClose, onSave, well}: WellEditModalProps) {
  const [fieldId, setFieldId] = useState(well.fieldId);
  const [cluster, setCluster] = useState(well.cluster);
  const [wellNumber, setWellNumber] = useState(well.wellNumber);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(well.id, {cluster, fieldId, wellNumber});
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal.Backdrop isOpen={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Modal.Container>
        <Modal.Dialog className="sm:max-w-[400px]">
          <Modal.CloseTrigger />
          <Modal.Header>
            <Modal.Heading>Редактирование скважины</Modal.Heading>
          </Modal.Header>
          <Modal.Body className="flex flex-col gap-4 p-6">
            <Select
              isRequired
              className="w-full"
              placeholder="Выберите месторождение"
              selectedKey={fieldId}
              onSelectionChange={(key) => setFieldId(key as string)}
            >
              <Label>Месторождение</Label>
              <Select.Trigger>
                <Select.Value />
                <Select.Indicator />
              </Select.Trigger>
              <Select.Popover>
                <ListBox>
                  {fields.map((f) => (
                    <ListBox.Item key={f.id} id={f.id} textValue={f.name}>
                      {f.name}
                      <ListBox.ItemIndicator />
                    </ListBox.Item>
                  ))}
                </ListBox>
              </Select.Popover>
            </Select>

            <TextField className="w-full" value={cluster} onChange={setCluster}>
              <Label>Куст</Label>
              <Input placeholder="Номер куста" />
            </TextField>

            <TextField className="w-full" value={wellNumber} onChange={setWellNumber}>
              <Label>Скважина</Label>
              <Input placeholder="Номер скважины" />
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
