from typing import List, TYPE_CHECKING
import json

from arkparse.api.player_api import PlayerApi

from .dino_id import DinoId
from .dino import Dino
from .tamed_dino import TamedDino
if TYPE_CHECKING:
    from arkparse.api import DinoApi
from arkparse.parsing.struct.ark_dino_ancestor_entry import ArkDinoAncestor, ArkDinoAncestorEntry

class PedigreeEntry:
    is_deceased: bool = False
    is_original: bool = False
    id_: DinoId
    is_female: bool = False
    dino: Dino = None
    father: "PedigreeEntry" = None
    mother: "PedigreeEntry" = None
    generation: int = 0
    mutations: int = 0
    mixed_mutations: bool = False
    owner_id: str = None
    owner_name: str = None

    def __eq__(self, value):
        if not isinstance(value, PedigreeEntry):
            return False
        return self.id_ == value.id_
    
    def __hash__(self):
        return hash(self.id_)

    def __get_index_in_source_tree(self, source_tree: List[ArkDinoAncestorEntry]) -> int:
        for i, entry in enumerate(source_tree):
            if self.is_female and entry.female.id_ == self.id_:
                return i
            elif not self.is_female and entry.male.id_ == self.id_:
                return i
        return None
    
    def __get_generation(self) -> int:
        gen_patrilineal = 0
        gen_matrilineal = 0
        if self.father is not None:
            gen_patrilineal = self.father.__get_generation() + 1
        if self.mother is not None:
            gen_matrilineal = self.mother.__get_generation() + 1
        return max(gen_patrilineal, gen_matrilineal)
    
    def __get_mutations(self) -> int:
        if self.dino is not None:
            return self.dino.stats.get_total_mutations()
        else:
            mutations_patrilineal = 0
            mutations_matrilineal = 0
            if self.father is not None:
                mutations_patrilineal = self.father.__get_mutations()
            if self.mother is not None:
                mutations_matrilineal = self.mother.__get_mutations()

            if mutations_matrilineal > 0 and mutations_patrilineal > 0:
                self.mixed_mutations = True

            return mutations_patrilineal + mutations_matrilineal

    def __init__(self, dino_id: DinoId, is_female: bool, api: "DinoApi", pedigree: "Pedigree", source_tree: List[ArkDinoAncestorEntry] = None):
        self.api = api
        self.id_ = dino_id

        if self.id_.id1 == 0 and self.id_.id2 == 0:
            return

        if self.id_ in pedigree.dino_id_map:
            return
            raise ValueError(f"Dino with ID {dino_id} already exists in pedigree")

        self.is_female = is_female
        self.dino = api.get_by_id(dino_id)
        if self.dino is None:
            self.is_deceased = True

            if source_tree is None:
                raise ValueError("source_tree must be provided for deceased dinos")
            
            index = self.__get_index_in_source_tree(source_tree)
            if index is None:
                raise ValueError(f"Dino with ID {dino_id} not found in source tree")
            
            if index > 0:
                parents: ArkDinoAncestorEntry = source_tree[index - 1]
                if parents.male.id_ in pedigree.dino_id_map:
                    self.father = pedigree.dino_id_map[parents.male.id_]
                else:
                    self.father = PedigreeEntry(parents.male.id_, False, api, pedigree, source_tree)

                if parents.female.id_ in pedigree.dino_id_map:
                    self.mother = pedigree.dino_id_map[parents.female.id_]
                else:
                    self.mother = PedigreeEntry(parents.female.id_, True, api, pedigree, source_tree)
        else:
            self.is_deceased = self.dino.is_dead
            if isinstance(self.dino, TamedDino):
                self.owner_id = self.dino.owner.target_team
            else:
                raise ValueError("PedigreeEntry can only be created from TamedDino instances")
        
            ancestors_female: List[ArkDinoAncestorEntry] = self.dino.object.get_property_value("DinoAncestors", [])
            ancestors_male: List[ArkDinoAncestorEntry] = self.dino.object.get_property_value("DinoAncestorsMale", [])
            mother_source_tree = None
            father_source_tree = None
            mother_id = None
            father_id = None

            if len(ancestors_female) != 0:
                mother_source_tree = ancestors_female
                mother_id = ancestors_female[-1].female.id_
            elif len(ancestors_male) != 0:
                mother_source_tree = [ancestors_male[-1]]
                mother_id = ancestors_male[-1].female.id_

            if len(ancestors_male) != 0:
                father_source_tree = ancestors_male
                father_id = ancestors_male[-1].male.id_
            elif len(ancestors_female) != 0:
                father_source_tree = [ancestors_female[-1]]
                father_id = ancestors_female[-1].male.id_

            if mother_id is not None:
                if mother_id in pedigree.dino_id_map:
                    self.mother = pedigree.dino_id_map[mother_id]
                else:
                    self.mother = PedigreeEntry(mother_id, True, api, pedigree, mother_source_tree)
            if father_id is not None:
                if father_id in pedigree.dino_id_map:
                    self.father = pedigree.dino_id_map[father_id]
                else:
                    self.father = PedigreeEntry(father_id, False, api, pedigree, father_source_tree)
        
        self.is_original = self.father is None and self.mother is None
        self.generation = self.__get_generation()
        self.mutations = self.__get_mutations()

        pedigree.entries.add(self)
        pedigree.dino_id_map[self.id_] = self

        if self.is_original:
            pedigree.number_of_originals += 1
            pedigree.top_entries.add(self)

        if self.is_deceased:
            pedigree.number_of_deceased += 1
        else:
            pedigree.number_of_living += 1

        pedigree.number_of_generations = max(pedigree.number_of_generations, self.generation)
        pedigree.max_mutations = max(pedigree.max_mutations, self.mutations)
        pedigree.number_of_dinos += 1      

        print(self)

    def __str__(self):
        return f"PedigreeEntry:(id_={self.id_}, is_female={self.is_female}, generation={self.generation}, mutations={self.mutations})"


class Pedigree:
    entries: set[PedigreeEntry]
    top_entries: set[PedigreeEntry]
    bottom_entries: set[PedigreeEntry]
    dino_id_map: dict[DinoId, PedigreeEntry]

    number_of_dinos: int
    number_of_originals: int
    number_of_deceased: int
    number_of_living: int
    number_of_generations: int 

    mixed_ownership: bool
    max_mutations: int
    dino_type: str
    owner: str

    _api: "DinoApi"
    _player_api: PlayerApi

    def __init__(self, dino: Dino, api: "DinoApi", player_api: PlayerApi = None):
        self.entries: set[PedigreeEntry] = set()
        self.top_entries: set[PedigreeEntry] = set()
        self.bottom_entries: set[PedigreeEntry] = set()
        self.dino_id_map: dict[DinoId, PedigreeEntry] = {}
        self.number_of_dinos = 0
        self.number_of_originals = 0
        self.number_of_deceased = 0
        self.number_of_living = 0
        self.number_of_generations = 0
        self.mixed_ownership = False
        self.max_mutations = 0
        self._api = api
        self._player_api = player_api
        self.dino_type = dino.get_short_name()
        PedigreeEntry(dino.id_, dino.is_female, api, self)
        self.__update_bottom_entries()
        self.__parse_owners()

    def __parse_owners(self):
        if self._player_api is None:
            return
        owners = set()
        for entry in self.entries:
            if entry.owner_id is not None:
                owner_verbose = self._player_api.get_tribe(entry.owner_id)
                entry.owner_name = owner_verbose.name if owner_verbose is not None else None
                owners.add(entry.owner_id)
        self.mixed_ownership = len(owners) > 1

    def __update_bottom_entries(self):
        self.bottom_entries = set()
        for entry in self.entries:
            if entry.generation == self.number_of_generations:
                self.bottom_entries.add(entry)

    def add_new_dino(self, dino: Dino) -> PedigreeEntry:
        if dino.id_ in self.dino_id_map:
            raise ValueError(f"Dino with ID {dino.id_} already exists in pedigree")
        PedigreeEntry(dino.id_, dino.is_female, self._api, self)
        self.__update_bottom_entries()
        self.__parse_owners()

    def has_ancestors_in_pedigree(self, dino: TamedDino) -> bool:
        for ancestor in dino.ancestor_ids:
            if ancestor in self.dino_id_map:
                return True
        return False

    def visualize_as_html(self, out_path: str, title: str | None = None) -> None:
        """
        Create a self-contained HTML file rendering the pedigree as an interactive SVG.
        No Python f-strings are used; JS template literals remain intact.
        """
        # ---- Collect graph data (nodes + edges) ---------------------------------
        def safe_name(d: Dino | None) -> str:
            if d is None:
                return "Unknown"
            for attr in ("name", "Name", "tamed_name"):
                if hasattr(d, attr) and getattr(d, attr):
                    return str(getattr(d, attr))
            return "Unknown"

        def safe_species(d: Dino | None) -> str:
            for attr in ("class_name", "bp_path", "species", "dino_class"):
                if d is not None and hasattr(d, attr) and getattr(d, attr):
                    return str(getattr(d, attr))
            return ""

        nodes = []
        edges = []
        gen_groups: dict[int, list[dict]] = {}

        for e in self.entries:
            nid = str(e.id_)
            node = {
                "id": nid,
                "label": safe_name(e.dino) or nid,
                "species": safe_species(e.dino),
                "sex": "F" if e.is_female else "M",
                "generation": int(e.generation),
                "deceased": bool(e.is_deceased),
                "original": bool(e.is_original),
                "mutations": int(e.mutations),
                "owner": e.owner_name if e.owner_name is not None else (e.owner_id if e.owner_id is not None else "Unknown"),
            }
            nodes.append(node)
            gen_groups.setdefault(e.generation, []).append(node)

            if e.father is not None:
                edges.append({"source": str(e.father.id_), "target": nid, "relation": "father"})
            if e.mother is not None:
                edges.append({"source": str(e.mother.id_), "target": nid, "relation": "mother"})

        # Deterministic order within each generation
        for g in gen_groups.values():
            g.sort(key=lambda n: (n["label"].lower(), n["id"]))

        # Layout params
        col_gap = 280
        row_gap = 140
        node_w = 210
        node_h = 72
        margin = 80

        # Compute positions
        positions = {}
        max_rows = 1
        for gen in range(0, max(self.number_of_generations, 0) + 1):
            col = gen_groups.get(gen, [])
            max_rows = max(max_rows, len(col) if col else 1)
            for idx, n in enumerate(col):
                x = margin + gen * col_gap
                y = margin + idx * row_gap
                positions[n["id"]] = {"x": x, "y": y}

        width = margin * 2 + (max(0, self.number_of_generations) + 1) * col_gap
        height = margin * 2 + max_rows * row_gap

        data = {
            "title": title or "Pedigree",
            "nodes": nodes,
            "edges": edges,
            "positions": positions,
            "layout": {"node_w": node_w, "node_h": node_h, "width": width, "height": height},
            "stats": {
                "dinos": self.number_of_dinos,
                "originals": self.number_of_originals,
                "living": self.number_of_living,
                "deceased": self.number_of_deceased,
                "generations": self.number_of_generations,
                "max_mutations": self.max_mutations,
                "mixed_ownership": bool(self.mixed_ownership),
            },
        }

        # ---- HTML template with placeholders (no f-strings) ---------------------
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>__TITLE__</title>
<style>
  :root {
    --bg: #0b0f14;
    --panel: #0f1520;
    --ink: #e6edf3;
    --muted: #98a6b3;
    --grid: #1a2430;
    --male: #3b82f6;
    --female: #ec4899;
    --deceased: #64748b;
    --alive: #22c55e;
    --original: #f59e0b;
    --edge: #8ea0b3;
    --edge-mother: #ec4899;
    --edge-father: #3b82f6;
    --badge-bg: rgba(255,255,255,0.08);
  }

  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; height:100%; background:var(--bg); color:var(--ink); font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol'; }
  .app { display:flex; flex-direction:column; height:100%; }
  header {
    padding: 16px 20px; border-bottom: 1px solid #1b2838; background: linear-gradient(180deg, #0f1520, #0c121a);
    display:flex; align-items:center; gap:16px; position:sticky; top:0; z-index:10;
  }
  header h1 { margin:0; font-size:18px; font-weight:600; letter-spacing:0.2px; }
  .stats { display:flex; gap:16px; flex-wrap:wrap; color:var(--muted); font-size:12px; }
  .chip { padding:6px 10px; border:1px solid #243141; border-radius:999px; background:rgba(255,255,255,0.03); }
  .canvas-wrap { position:relative; flex:1; overflow:hidden; }
  svg { width:100%; height:100%; background:
        linear-gradient(var(--grid) 1px, transparent 1px) 0 0/ 100% 64px,
        linear-gradient(90deg, var(--grid) 1px, transparent 1px) 0 0/ 64px 100%,
        radial-gradient(600px 600px at 30% 20%, rgba(80,140,255,0.08), transparent 60%); }
  .legend {
    position:absolute; right:16px; top:16px; background:var(--panel); border:1px solid #223044;
    border-radius:12px; padding:10px 12px; font-size:12px; color:var(--muted);
    backdrop-filter: blur(6px);
  }
  .legend .row { display:flex; align-items:center; gap:8px; margin:6px 0; }
  .swatch { width:14px; height:14px; border-radius:4px; }
  .node { cursor: pointer; }
  .node rect {
    rx:14; ry:14; fill: #162130; stroke:#26435e; stroke-width:1.25;
    filter: drop-shadow(0 6px 10px rgba(0,0,0,0.35));
  }
  .node.female rect { stroke: var(--female); }
  .node.male rect { stroke: var(--male); }
  .node.deceased rect { opacity:0.7; stroke: var(--deceased); }
  .node .label { font-size:13px; font-weight:600; fill:var(--ink); }
  .node .sub { font-size:11px; fill: var(--muted); }
  .badge { font-size:10px; font-weight:600; fill: var(--ink); }
  .badge-bg { fill: var(--badge-bg); stroke: #2a3a52; stroke-width: 1; rx: 8; ry: 8; }
  .edge { fill:none; stroke:var(--edge); stroke-width:1.5; marker-end:url(#arrow); opacity:0.9; }
  .edge.mother { stroke: var(--edge-mother); }
  .edge.father { stroke: var(--edge-father); }
  .highlight-node rect { stroke-width:2.5 !important; }
  .highlight-edge { stroke-width:3 !important; opacity:1 !important; }
  .tooltip {
    position:absolute; pointer-events:none; background:#0c121a; color:#e6edf3; border:1px solid #223044;
    padding:8px 10px; border-radius:10px; font-size:12px; display:none; z-index:10;
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
  }
</style>
</head>
<body>
<div class="app">
  <header>
    <h1>__TITLE__</h1>
    <div class="stats">
      <div class="chip">Dinos: <span id="stat-dinos"></span></div>
      <div class="chip">Generations: <span id="stat-gens"></span></div>
      <div class="chip">Living: <span id="stat-living"></span></div>
      <div class="chip">Deceased: <span id="stat-deceased"></span></div>
      <div class="chip">Originals: <span id="stat-originals"></span></div>
      <div class="chip">Max Mutations: <span id="stat-maxmut"></span></div>
    </div>
  </header>
  <div class="canvas-wrap">
    <div class="legend">
      <div class="row"><span class="swatch" style="background:var(--male)"></span> Male</div>
      <div class="row"><span class="swatch" style="background:var(--female)"></span> Female</div>
      <div class="row"><span class="swatch" style="background:var(--deceased)"></span> Deceased</div>
      <div class="row"><span class="swatch" style="background:var(--original)"></span> Original</div>
    </div>
    <div id="tooltip" class="tooltip"></div>
    <svg id="stage" viewBox="0 0 __WIDTH__ __HEIGHT__" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"></path>
        </marker>
      </defs>
      <g id="viewport"></g>
    </svg>
  </div>
</div>

<script>
  const DATA = __DATA__;
  const NODE_W = DATA.layout.node_w, NODE_H = DATA.layout.node_h;

  document.getElementById('stat-dinos').textContent = DATA.stats.dinos;
  document.getElementById('stat-gens').textContent = DATA.stats.generations;
  document.getElementById('stat-living').textContent = DATA.stats.living;
  document.getElementById('stat-deceased').textContent = DATA.stats.deceased;
  document.getElementById('stat-originals').textContent = DATA.stats.originals;
  document.getElementById('stat-maxmut').textContent = DATA.stats.max_mutations;

  const svg = document.getElementById('stage');
  const vp = document.getElementById('viewport');
  const tooltip = document.getElementById('tooltip');

  // Helpers to compute edge geometry from stored positions
  const pos = DATA.positions;
  function midRight(n) { return [pos[n].x + NODE_W, pos[n].y + NODE_H/2]; }
  function midLeft(n)  { return [pos[n].x, pos[n].y + NODE_H/2];  }

  function cubicPath(x1,y1,x2,y2) {
    const dx = Math.max(40, (x2 - x1) * 0.5);
    const c1x = x1 + dx, c1y = y1;
    const c2x = x2 - dx, c2y = y2;
    return `M ${x1} ${y1} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${x2} ${y2}`;
  }

  // Edges layer
  const edgesGroup = document.createElementNS('http://www.w3.org/2000/svg','g');
  edgesGroup.setAttribute('id','edges');
  vp.appendChild(edgesGroup);

  for (const e of DATA.edges) {
    const [x1,y1] = midRight(e.source);
    const [x2,y2] = midLeft(e.target);
    const path = document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('d', cubicPath(x1,y1,x2,y2));
    path.setAttribute('class', `edge ${e.relation}`);
    path.setAttribute('stroke', getComputedStyle(document.documentElement).getPropertyValue('--edge').trim());
    edgesGroup.appendChild(path);
  }

  // Nodes layer
  const nodesGroup = document.createElementNS('http://www.w3.org/2000/svg','g');
  nodesGroup.setAttribute('id','nodes');
  vp.appendChild(nodesGroup);

  const nodeById = new Map();

  for (const n of DATA.nodes) {
    const g = document.createElementNS('http://www.w3.org/2000/svg','g');
    g.setAttribute('class', `node ${n.sex === 'F' ? 'female' : 'male'} ${n.deceased ? 'deceased' : 'alive'}`);
    g.setAttribute('data-id', n.id);
    g.setAttribute('transform', `translate(${pos[n.id].x},${pos[n.id].y})`);

    const rect = document.createElementNS('http://www.w3.org/2000/svg','rect');
    rect.setAttribute('width', NODE_W);
    rect.setAttribute('height', NODE_H);
    g.appendChild(rect);

    // Labels
    const label = document.createElementNS('http://www.w3.org/2000/svg','text');
    label.setAttribute('x', 14); label.setAttribute('y', 24); label.setAttribute('class','label');
    label.textContent = n.label;
    g.appendChild(label);

    const sub = document.createElementNS('http://www.w3.org/2000/svg','text');
    sub.setAttribute('x', 14); sub.setAttribute('y', 44); sub.setAttribute('class','sub');
    const gen = `Gen ${n.generation}`;
    const mut = `${n.mutations} mut`;
    const sex = n.sex === 'F' ? '♀' : '♂';
    sub.textContent = [sex, gen, mut].join(' · ');
    g.appendChild(sub);

    const ownersub = document.createElementNS('http://www.w3.org/2000/svg','text');
    ownersub.setAttribute('x', 14); ownersub.setAttribute('y', 60); ownersub.setAttribute('class','sub');
    ownersub.textContent = n.owner ? `Owner: ${n.owner}` : '';
    g.appendChild(ownersub);

    // Badges (right side)
    const badges = [];
    if (n.original) badges.push({ text: 'ORIGINAL', color: 'var(--original)'});
    if (n.deceased) badges.push({ text: 'DECEASED', color: 'var(--deceased)'});

    let bx = NODE_W - 10;
    for (const b of badges) {
      const t = document.createElementNS('http://www.w3.org/2000/svg','text');
      t.setAttribute('class','badge');
      t.textContent = b.text;
      nodesGroup.appendChild(t); // temp to measure
      const len = t.getComputedTextLength();
      nodesGroup.removeChild(t);

      const padX = 8, padY = 4;
      const w = len + padX*2, h = 18;
      bx -= (w + 8);
      const by = 10;

      const r = document.createElementNS('http://www.w3.org/2000/svg','rect');
      r.setAttribute('x', bx); r.setAttribute('y', by);
      r.setAttribute('width', w); r.setAttribute('height', h);
      r.setAttribute('class','badge-bg');
      r.setAttribute('stroke', b.color);
      g.appendChild(r);

      const tt = document.createElementNS('http://www.w3.org/2000/svg','text');
      tt.setAttribute('x', bx + padX); tt.setAttribute('y', by + h - 5);
      tt.setAttribute('class','badge');
      tt.setAttribute('fill', b.color);
      tt.textContent = b.text;
      g.appendChild(tt);
    }

    // Tooltip
    g.addEventListener('mousemove', (evt) => {
      tooltip.style.display = 'block';
      tooltip.style.left = (evt.clientX + 12) + 'px';
      tooltip.style.top = (evt.clientY + 12) + 'px';
      tooltip.innerHTML = `
        <div style="font-weight:600;margin-bottom:4px;">${n.label}</div>
        <div style="opacity:.8">ID: ${n.id}</div>
        ${n.species ? `<div style="opacity:.8">Species: ${n.species.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>` : ''}
        <div style="opacity:.8">Sex: ${n.sex === 'F' ? 'Female' : 'Male'}</div>
        <div style="opacity:.8">Generation: ${n.generation}</div>
        <div style="opacity:.8">Mutations: ${n.mutations}</div>
        ${n.deceased ? `<div style="opacity:.8">Deceased</div>` : ''}
        ${n.original ? `<div style="opacity:.8">Original</div>` : ''}
      `;
    });
    g.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
    });

    // Click to highlight lineage
    g.addEventListener('click', () => highlightLineage(n.id));

    nodesGroup.appendChild(g);
    nodeById.set(n.id, g);
  }

  // Edge highlighting & lineage tracing
  function highlightLineage(targetId) {
    for (const p of edgesGroup.querySelectorAll('.edge')) p.classList.remove('highlight-edge');
    for (const n of nodesGroup.querySelectorAll('.node')) n.classList.remove('highlight-node');

    const parentIds = new Set();
    for (const e of DATA.edges) {
      if (e.target === targetId) parentIds.add(e.source);
    }

    nodeById.get(targetId)?.classList.add('highlight-node');

    const stack = [...parentIds];
    const seen = new Set();
    while (stack.length) {
      const cur = stack.pop();
      if (seen.has(cur)) continue;
      seen.add(cur);
      nodeById.get(cur)?.classList.add('highlight-node');
      for (const e of DATA.edges) {
        if (e.target === cur) stack.push(e.source);
      }
    }

    function markEdgesInto(childId) {
      for (const e of DATA.edges) {
        if (e.target === childId) {
          const [x1,y1] = midRight(e.source);
          const [x2,y2] = midLeft(e.target);
          const pathD = cubicPath(x1,y1,x2,y2);
          for (const p of edgesGroup.querySelectorAll('path')) {
            if (p.getAttribute('d') === pathD) p.classList.add('highlight-edge');
          }
          markEdgesInto(e.source);
        }
      }
    }
    markEdgesInto(targetId);
  }

  // Pan/zoom
  let isPanning = false, panStart = null;
  let view = svg.viewBox.baseVal;

  function screenToSvg(dx, dy) {
    const sx = dx * (view.width / svg.clientWidth);
    const sy = dy * (view.height / svg.clientHeight);
    return [sx, sy];
  }

  svg.addEventListener('mousedown', (e) => {
    isPanning = true;
    panStart = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y };
  });
  window.addEventListener('mousemove', (e) => {
    if (!isPanning) return;
    const dx = e.clientX - panStart.x;
    const dy = e.clientY - panStart.y;
    const [sx, sy] = screenToSvg(-dx, -dy);
    view.x = panStart.vx + sx;
    view.y = panStart.vy + sy;
  });
  window.addEventListener('mouseup', () => { isPanning = false; });

  svg.addEventListener('wheel', (e) => {
    e.preventDefault();
    const { deltaY } = e;
    const scale = Math.exp(deltaY * 0.0015);
    const mx = (e.offsetX / svg.clientWidth) * view.width + view.x;
    const my = (e.offsetY / svg.clientHeight) * view.height + view.y;

    view.x = mx - (mx - view.x) * scale;
    view.y = my - (my - view.y) * scale;
    view.width *= scale;
    view.height *= scale;
  }, { passive: false });
</script>
</body>
</html>"""

        # ---- Inject values safely (no f-strings) --------------------------------
        # Escape the title for HTML <title> while preserving plain text (use JSON to quote; strip quotes)
        safe_title = json.dumps(data["title"], ensure_ascii=False)[1:-1]
        html = (
            html_template
            .replace("__TITLE__", safe_title)
            .replace("__WIDTH__", str(width))
            .replace("__HEIGHT__", str(height))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False))
        )

        # ---- Write file ---------------------------------------------------------
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

    def print_tree(self) -> None:
        """
        Print the pedigree as a simple ASCII tree.
        Shows generations, sexes, deceased/original markers, and parent → child relations.
        """

        def node_label(entry: PedigreeEntry) -> str:
            name = entry.dino.tamed_name if entry.dino and getattr(entry.dino, "tamed_name", None) else str(entry.id_)
            sex = "♀" if entry.is_female else "♂"
            markers = []
            if entry.is_original:
                markers.append("O")  # Original
            if entry.is_deceased:
                markers.append("†")  # Deceased
            if entry.mutations:
                markers.append(f"{entry.mutations}m")
            marker_str = f" [{' '.join(markers)}]" if markers else ""
            return f"{name} {sex}{marker_str}"

        def print_entry(entry: PedigreeEntry, prefix: str = "", is_tail: bool = True):
            branch = "└── " if is_tail else "├── "
            print(prefix + branch + node_label(entry))

            children = []
            if entry.father:
                children.append(("F", entry.father))
            if entry.mother:
                children.append(("M", entry.mother))

            for i, (_, child) in enumerate(children):
                is_last = (i == len(children) - 1)
                new_prefix = prefix + ("    " if is_tail else "│   ")
                print_entry(child, new_prefix, is_last)

        print(f"Pedigree ({self.number_of_dinos} dinos, {self.number_of_generations} generations)")
        print("=" * 60)
        for root in self.bottom_entries:
            print_entry(root, "", True)
        print("=" * 60)