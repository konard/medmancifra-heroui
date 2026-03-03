import type {Meta} from "@storybook/react-vite";

import React from "react";

import {WellRepairsDemo} from "./demos/well-repairs/WellRepairsDemo";

const meta: Meta = {
  parameters: {
    layout: "fullscreen",
  },
  title: "Well Repairs Demo",
};

export default meta;

export const Default = () => {
  return <WellRepairsDemo />;
};

Default.parameters = {
  docs: {
    description: {
      story:
        "Управление скважинами и ремонтами: таблица скважин слева, список ремонтов по выбранной скважине справа. Редактирование данных через модальное окно.",
    },
  },
};
