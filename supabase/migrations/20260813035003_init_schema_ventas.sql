-- Schema relacional de ventas online 2021 (práctica SOG2).
-- RLS activo: el análisis usa DATABASE_URL (rol postgres, bypass RLS).
-- anon/authenticated no ven filas salvo que se añadan policies.

create table public.catalogo_genero (
  codigo smallint primary key,
  nombre text not null unique
);

create table public.catalogo_metodo_pago (
  codigo smallint primary key,
  nombre text not null unique
);

create table public.catalogo_navegador (
  codigo smallint primary key,
  nombre text not null unique
);

create table public.clientes (
  id_cliente integer primary key,
  edad smallint not null check (edad >= 0),
  genero_id smallint not null references public.catalogo_genero (codigo),
  venta_total numeric(12, 2) not null check (venta_total >= 0),
  n_compras integer not null check (n_compras >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.compras (
  id bigint generated always as identity primary key,
  id_cliente integer not null references public.clientes (id_cliente),
  fecha_compra date not null,
  monto_compra numeric(12, 3) not null check (monto_compra >= 0),
  metodo_pago_id smallint not null references public.catalogo_metodo_pago (codigo),
  tiempo integer not null check (tiempo >= 0),
  navegador_id smallint not null references public.catalogo_navegador (codigo),
  boletin boolean not null,
  vale boolean not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_clientes_genero on public.clientes (genero_id);
create index idx_compras_cliente on public.compras (id_cliente);
create index idx_compras_fecha on public.compras (fecha_compra);
create index idx_compras_metodo on public.compras (metodo_pago_id);
create index idx_compras_navegador on public.compras (navegador_id);

insert into public.catalogo_genero (codigo, nombre) values
  (0, 'Masculino'),
  (1, 'Femenino');

insert into public.catalogo_metodo_pago (codigo, nombre) values
  (0, 'Efectivo'),
  (1, 'Tarjeta de Credito'),
  (2, 'Tarjeta de Debito');

insert into public.catalogo_navegador (codigo, nombre) values
  (0, 'Tienda Fisica'),
  (1, 'Navegador 1'),
  (2, 'Navegador 2'),
  (3, 'Navegador 3'),
  (4, 'Navegador 4');

alter table public.catalogo_genero enable row level security;
alter table public.catalogo_metodo_pago enable row level security;
alter table public.catalogo_navegador enable row level security;
alter table public.clientes enable row level security;
alter table public.compras enable row level security;
