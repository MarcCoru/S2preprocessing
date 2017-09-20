CREATE TABLE public.labelmap
(
  name text,
  label text,
  id integer NOT NULL DEFAULT nextval('labelmap_id_seq'::regclass),
  doystart integer,
  doyend integer,
  labelid integer,
  CONSTRAINT id PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.labelmap
  OWNER TO russwurm;
