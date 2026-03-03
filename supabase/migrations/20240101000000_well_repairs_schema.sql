-- Migration: Well Repairs schema
-- Creates tables for the Well Repairs management system.
-- Run via Supabase dashboard SQL editor or supabase db push.

-- Fields (oil field locations)
create table if not exists fields (
  id text primary key,
  name text not null
);

-- Repair types (reference data)
create table if not exists repair_types (
  id text primary key,
  code text not null unique,
  name text not null
);

-- Wells
create table if not exists wells (
  id text primary key,
  field_id text not null references fields(id),
  cluster text not null,
  well_number text not null
);

-- Repairs
create table if not exists repairs (
  id text primary key,
  well_id text not null references wells(id),
  start_date date not null,
  end_date date,
  repair_type_id text not null references repair_types(id)
);

-- Seed: Fields
insert into fields (id, name) values
  ('field-1', 'Самотлорское'),
  ('field-2', 'Приобское'),
  ('field-3', 'Сугмутское'),
  ('field-4', 'Урьевское'),
  ('field-5', 'Мамонтовское'),
  ('field-6', 'Федоровское'),
  ('field-7', 'Ватьеганское')
on conflict (id) do nothing;

-- Seed: Repair types
insert into repair_types (id, code, name) values
  ('rt-1', 'КРС-1', 'Капитальный ремонт скважины №1'),
  ('rt-2', 'КРС-2', 'Капитальный ремонт скважины №2'),
  ('rt-3', 'ПРС-1', 'Подземный ремонт скважины №1'),
  ('rt-4', 'ПРС-2', 'Подземный ремонт скважины №2'),
  ('rt-5', 'ГРП',   'Гидроразрыв пласта'),
  ('rt-6', 'ОПЗ',   'Обработка призабойной зоны'),
  ('rt-7', 'РИР',   'Ремонтно-изоляционные работы'),
  ('rt-8', 'ВРП',   'Воздействие на пласт')
on conflict (id) do nothing;

-- Seed: Wells
insert into wells (id, field_id, cluster, well_number) values
  ('w-1', 'field-1', 'К-101', '1001'),
  ('w-2', 'field-1', 'К-101', '1002'),
  ('w-3', 'field-1', 'К-102', '1003'),
  ('w-4', 'field-2', 'К-201', '2001'),
  ('w-5', 'field-2', 'К-201', '2002'),
  ('w-6', 'field-3', 'К-301', '3001'),
  ('w-7', 'field-4', 'К-401', '4001'),
  ('w-8', 'field-5', 'К-501', '5001')
on conflict (id) do nothing;

-- Seed: Repairs
insert into repairs (id, well_id, start_date, end_date, repair_type_id) values
  ('r-1',  'w-1', '2024-11-15', '2024-12-01', 'rt-1'),
  ('r-2',  'w-1', '2025-01-10', null,          'rt-3'),
  ('r-3',  'w-2', '2024-10-05', '2024-10-20', 'rt-5'),
  ('r-4',  'w-2', '2025-02-01', null,          'rt-2'),
  ('r-5',  'w-3', '2024-09-12', '2024-09-30', 'rt-6'),
  ('r-6',  'w-4', '2024-12-20', '2025-01-05', 'rt-7'),
  ('r-7',  'w-4', '2025-03-01', null,          'rt-4'),
  ('r-8',  'w-5', '2024-08-15', '2024-08-28', 'rt-8'),
  ('r-9',  'w-6', '2025-01-20', null,          'rt-1'),
  ('r-10', 'w-7', '2024-11-01', '2024-11-15', 'rt-3'),
  ('r-11', 'w-8', '2025-02-15', null,          'rt-5')
on conflict (id) do nothing;
