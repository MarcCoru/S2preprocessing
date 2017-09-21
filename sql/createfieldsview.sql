 SELECT m.labelid,
    m.label,
    m.doystart,
    m.doyend,
    o.geom
   FROM labelmap m,
    osm o
  WHERE o.fclass::text = m.name AND NOT m.label = ''::text
UNION ALL
 SELECT m.labelid,
    m.label,
    m.doystart,
    m.doyend,
    f.geom
   FROM labelmap m,
    fieldsstmelf f
  WHERE f.nutzung::text = m.name AND NOT m.label = ''::text;
