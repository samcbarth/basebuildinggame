const canvas = document.querySelector("#game");
const ctx = canvas.getContext("2d");
const statusEl = document.querySelector("#status");
const restartButton = document.querySelector("#restart");
const actionButtons = [...document.querySelectorAll("[data-action]")];

const W = canvas.width;
const H = canvas.height;
const CELL = 32;
const GRID_W = W / CELL;
const GRID_H = H / CELL;

const colors = {
  bg: "#191d20",
  grid: "#2c3438",
  gridAlt: "#20262a",
  text: "#f2f0df",
  muted: "#9ba89d",
  scrap: "#e7bd52",
  good: "#74c686",
  bad: "#d86562",
  warning: "#eca452",
  hq: "#4e79ae",
  mine: "#a88250",
  turret: "#5b9989",
  barracks: "#9066a1",
  worker: "#efd68c",
  soldier: "#78b7ff",
  enemy: "#cd5252",
  projectile: "#fcee80",
  panel: "#0d1114",
  panelEdge: "#3d4a50",
};

const specs = {
  mine: {
    name: "Mine",
    cost: 40,
    w: 2,
    h: 2,
    hp: 95,
    color: colors.mine,
  },
  turret: {
    name: "Turret",
    cost: 55,
    w: 1,
    h: 1,
    hp: 85,
    color: colors.turret,
  },
  barracks: {
    name: "Barracks",
    cost: 85,
    w: 3,
    h: 2,
    hp: 135,
    color: colors.barracks,
  },
  hq: {
    name: "Core HQ",
    cost: 0,
    w: 3,
    h: 3,
    hp: 260,
    color: colors.hq,
  },
};

const state = {
  scrap: 120,
  wave: 0,
  waveTimer: 28,
  spawnQueue: 0,
  spawnTick: 0,
  gameOver: false,
  selected: "mine",
  economy: 0,
  weapons: 0,
  armor: 0,
  workers: 2,
  message: "Build before the first raid.",
  messageColor: colors.muted,
  messageTimer: 5,
  mouse: { x: W / 2, y: H / 2 },
  buildings: [],
  soldiers: [],
  enemies: [],
  shots: [],
};

let last = performance.now();

function resetGame() {
  Object.assign(state, {
    scrap: 120,
    wave: 0,
    waveTimer: 28,
    spawnQueue: 0,
    spawnTick: 0,
    gameOver: false,
    selected: "mine",
    economy: 0,
    weapons: 0,
    armor: 0,
    workers: 2,
    message: "Build before the first raid.",
    messageColor: colors.muted,
    messageTimer: 5,
    buildings: [makeBuilding("hq", 13, 8)],
    soldiers: [{ x: W / 2 - 36, y: H / 2 + 76, hp: 45, cooldown: 0 }],
    enemies: [],
    shots: [],
  });
  statusEl.textContent = state.message;
  updateButtons();
}

function makeBuilding(kind, gx, gy) {
  const spec = specs[kind];
  return {
    kind,
    gx,
    gy,
    w: spec.w,
    h: spec.h,
    hp: spec.hp + armorBonus(),
    cooldown: 0,
  };
}

function armorBonus() {
  return state.armor * 25;
}

function flash(text, color = colors.text, seconds = 2.2) {
  state.message = text;
  state.messageColor = color;
  state.messageTimer = seconds;
  statusEl.textContent = text;
}

function spend(amount) {
  if (state.scrap < amount) {
    flash(`Need ${amount} scrap.`, colors.bad);
    return false;
  }
  state.scrap -= amount;
  return true;
}

function pointerToGrid(event) {
  const rect = canvas.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * W;
  const y = ((event.clientY - rect.top) / rect.height) * H;
  return {
    gx: Math.floor(x / CELL),
    gy: Math.floor(y / CELL),
    x,
    y,
  };
}

canvas.addEventListener("pointermove", (event) => {
  const pos = pointerToGrid(event);
  state.mouse.x = pos.x;
  state.mouse.y = pos.y;
});

canvas.addEventListener("pointerdown", (event) => {
  if (event.button === 2) {
    state.selected = null;
    updateButtons();
    return;
  }
  const pos = pointerToGrid(event);
  tryPlace(pos.gx, pos.gy);
});

canvas.addEventListener("contextmenu", (event) => event.preventDefault());
restartButton.addEventListener("click", resetGame);

document.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (key === "1") selectBuilding("mine");
  if (key === "2") selectBuilding("turret");
  if (key === "3") selectBuilding("barracks");
  if (key === "w") trainWorker();
  if (key === "s") trainSoldier();
  if (key === "u") buyUpgrade("economy");
  if (key === "i") buyUpgrade("weapons");
  if (key === "o") buyUpgrade("armor");
  if (key === "r") repairBuilding();
  if (key === " ") {
    event.preventDefault();
    startWave();
  }
  if (key === "escape") {
    state.selected = null;
    updateButtons();
  }
  if (key === "enter" && state.gameOver) resetGame();
});

actionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const action = button.dataset.action;
    if (action === "select") selectBuilding(button.dataset.building);
    if (action === "train-worker") trainWorker();
    if (action === "train-soldier") trainSoldier();
    if (action === "upgrade-economy") buyUpgrade("economy");
    if (action === "upgrade-weapons") buyUpgrade("weapons");
    if (action === "upgrade-armor") buyUpgrade("armor");
    if (action === "repair") repairBuilding();
    if (action === "wave") startWave();
  });
});

function selectBuilding(kind) {
  state.selected = kind;
  updateButtons();
}

function updateButtons() {
  actionButtons.forEach((button) => {
    button.classList.toggle("selected", button.dataset.building === state.selected);
  });
}

function tryPlace(gx, gy) {
  if (!state.selected || state.gameOver) return;
  const spec = specs[state.selected];
  if (!canPlace(state.selected, gx, gy)) {
    flash("Can't build there.", colors.bad);
    return;
  }
  if (!spend(spec.cost)) return;
  state.buildings.push(makeBuilding(state.selected, gx, gy));
  flash(`${spec.name} built.`, colors.good);
}

function canPlace(kind, gx, gy) {
  const spec = specs[kind];
  if (gy < 3) return false;
  if (gx < 0 || gy < 0 || gx + spec.w > GRID_W || gy + spec.h > GRID_H) return false;
  return !state.buildings.some((building) => rectsOverlap(
    gx,
    gy,
    spec.w,
    spec.h,
    building.gx,
    building.gy,
    building.w,
    building.h,
  ));
}

function rectsOverlap(ax, ay, aw, ah, bx, by, bw, bh) {
  return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
}

function trainWorker() {
  const cost = 25 + state.workers * 4;
  if (!spend(cost)) return;
  state.workers += 1;
  flash("Worker trained. Income increased.", colors.good);
}

function trainSoldier() {
  if (!state.buildings.some((building) => building.kind === "barracks")) {
    flash("Build a barracks first.", colors.bad);
    return;
  }
  const cost = 35 + state.soldiers.length * 3;
  if (!spend(cost)) return;
  const hq = getHq();
  state.soldiers.push({
    x: centerX(hq) + rand(-44, 44),
    y: centerY(hq) + rand(44, 88),
    hp: 45,
    cooldown: 0,
  });
  flash("Soldier deployed.", colors.good);
}

function buyUpgrade(kind) {
  const level = state[kind === "economy" ? "economy" : kind === "weapons" ? "weapons" : "armor"];
  if (level >= 3) {
    flash(`${title(kind)} already maxed.`, colors.muted);
    return;
  }
  const baseCost = { economy: 80, weapons: 95, armor: 75 }[kind];
  if (!spend(baseCost + level * 55)) return;
  state[kind] += 1;
  if (kind === "armor") {
    state.buildings.forEach((building) => {
      building.hp += 25;
    });
  }
  flash(`${title(kind)} upgraded to level ${level + 1}.`, colors.good);
}

function repairBuilding() {
  const damaged = state.buildings.filter((building) => building.hp < maxHp(building));
  if (!damaged.length) {
    flash("Nothing needs repair.", colors.muted);
    return;
  }
  if (!spend(22)) return;
  damaged.sort((a, b) => a.hp / maxHp(a) - b.hp / maxHp(b));
  damaged[0].hp = Math.min(maxHp(damaged[0]), damaged[0].hp + 45);
  flash(`${specs[damaged[0].kind].name} repaired.`, colors.good);
}

function startWave() {
  if (state.spawnQueue > 0 || state.gameOver) return;
  state.wave += 1;
  state.spawnQueue = 4 + state.wave * 2;
  state.spawnTick = 0;
  state.waveTimer = 28 + Math.min(12, state.wave * 1.5);
  flash(`Wave ${state.wave} incoming.`, colors.warning);
}

function update(dt) {
  if (state.gameOver) return;

  state.messageTimer -= dt;
  if (state.messageTimer <= 0) state.message = "";

  const mineCount = state.buildings.filter((building) => building.kind === "mine").length;
  state.scrap += (state.workers * (0.8 + state.economy * 0.25) + mineCount * (1.5 + state.economy * 0.5)) * dt;

  state.waveTimer -= dt;
  if (state.waveTimer <= 0 && state.spawnQueue <= 0) startWave();

  spawnEnemies(dt);
  updateTurrets(dt);
  updateSoldiers(dt);
  updateShots(dt);
  updateEnemies(dt);

  state.enemies = state.enemies.filter((enemy) => enemy.hp > 0);
  state.shots = state.shots.filter((shot) => shot.ttl > 0);
  state.soldiers = state.soldiers.filter((soldier) => soldier.hp > 0);
  state.buildings = state.buildings.filter((building) => building.hp > 0 || building.kind === "hq");

  const hq = getHq();
  if (!hq || hq.hp <= 0) {
    state.gameOver = true;
    flash("HQ destroyed. Press Enter or Restart.", colors.bad, 999);
  }
}

function spawnEnemies(dt) {
  if (state.spawnQueue <= 0) return;
  state.spawnTick -= dt;
  if (state.spawnTick > 0) return;
  state.enemies.push(makeEnemy());
  state.spawnQueue -= 1;
  state.spawnTick = Math.max(0.25, 0.85 - state.wave * 0.03);
}

function makeEnemy() {
  const side = Math.floor(Math.random() * 4);
  const pos = [
    { x: rand(0, W), y: -16 },
    { x: rand(0, W), y: H + 16 },
    { x: -16, y: rand(0, H) },
    { x: W + 16, y: rand(0, H) },
  ][side];
  return {
    x: pos.x,
    y: pos.y,
    hp: 32 + state.wave * 7,
    speed: 28 + Math.min(36, state.wave * 2.4),
    damage: 7 + state.wave * 0.8,
    cooldown: 0,
  };
}

function updateTurrets(dt) {
  state.buildings.forEach((building) => {
    if (building.kind !== "turret") return;
    building.cooldown -= dt;
    const target = nearestEnemy(centerX(building), centerY(building), 140 + state.weapons * 20);
    if (!target || building.cooldown > 0) return;
    shoot(centerX(building), centerY(building), target, 16 + state.weapons * 6, 300);
    building.cooldown = Math.max(0.18, 0.62 - state.weapons * 0.08);
  });
}

function updateSoldiers(dt) {
  const hq = getHq();
  state.soldiers.forEach((soldier, index) => {
    soldier.cooldown -= dt;
    const target = nearestEnemy(soldier.x, soldier.y, 116 + state.weapons * 16);
    if (target && soldier.cooldown <= 0) {
      shoot(soldier.x, soldier.y, target, 8 + state.weapons * 3, 260);
      soldier.cooldown = Math.max(0.24, 0.72 - state.weapons * 0.08);
      return;
    }
    if (!target && hq) {
      const dx = centerX(hq) + Math.cos(index) * 56 - soldier.x;
      const dy = centerY(hq) + Math.sin(index * 1.7) * 44 - soldier.y;
      const len = Math.hypot(dx, dy);
      if (len > 4) {
        soldier.x += (dx / len) * 48 * dt;
        soldier.y += (dy / len) * 48 * dt;
      }
    }
  });
}

function shoot(x, y, target, damage, speed) {
  const dx = target.x - x;
  const dy = target.y - y;
  const len = Math.hypot(dx, dy) || 1;
  state.shots.push({
    x,
    y,
    vx: (dx / len) * speed,
    vy: (dy / len) * speed,
    damage,
    ttl: 1.2,
  });
}

function updateShots(dt) {
  state.shots.forEach((shot) => {
    shot.x += shot.vx * dt;
    shot.y += shot.vy * dt;
    shot.ttl -= dt;
    for (const enemy of state.enemies) {
      if (enemy.hp <= 0 || Math.hypot(enemy.x - shot.x, enemy.y - shot.y) > 10) continue;
      enemy.hp -= shot.damage;
      shot.ttl = 0;
      if (enemy.hp <= 0) state.scrap += 7 + state.wave;
      break;
    }
  });
}

function updateEnemies(dt) {
  state.enemies.forEach((enemy) => {
    const target = closestBuilding(enemy.x, enemy.y);
    if (!target) return;
    enemy.cooldown -= dt;
    const dx = centerX(target) - enemy.x;
    const dy = centerY(target) - enemy.y;
    const dist = Math.hypot(dx, dy) || 1;
    if (dist > 20) {
      enemy.x += (dx / dist) * enemy.speed * dt;
      enemy.y += (dy / dist) * enemy.speed * dt;
    } else if (enemy.cooldown <= 0) {
      target.hp -= enemy.damage;
      enemy.cooldown = 0.75;
    }
  });
}

function nearestEnemy(x, y, maxRange) {
  let best = null;
  let bestDist = maxRange;
  state.enemies.forEach((enemy) => {
    if (enemy.hp <= 0) return;
    const dist = Math.hypot(enemy.x - x, enemy.y - y);
    if (dist <= bestDist) {
      best = enemy;
      bestDist = dist;
    }
  });
  return best;
}

function closestBuilding(x, y) {
  return state.buildings
    .filter((building) => building.hp > 0)
    .sort((a, b) => distanceToBuilding(x, y, a) - distanceToBuilding(x, y, b))[0];
}

function distanceToBuilding(x, y, building) {
  return Math.hypot(centerX(building) - x, centerY(building) - y);
}

function getHq() {
  return state.buildings.find((building) => building.kind === "hq");
}

function centerX(building) {
  return building.gx * CELL + building.w * CELL * 0.5;
}

function centerY(building) {
  return building.gy * CELL + building.h * CELL * 0.5;
}

function maxHp(building) {
  return specs[building.kind].hp + armorBonus();
}

function draw() {
  ctx.fillStyle = colors.bg;
  ctx.fillRect(0, 0, W, H);
  drawGrid();
  state.buildings.forEach(drawBuilding);
  state.soldiers.forEach(drawSoldier);
  state.enemies.forEach(drawEnemy);
  state.shots.forEach(drawShot);
  drawPreview();
  drawHud();
  if (state.gameOver) drawGameOver();
}

function drawGrid() {
  for (let y = 0; y < GRID_H; y += 1) {
    for (let x = 0; x < GRID_W; x += 1) {
      ctx.fillStyle = (x + y) % 2 === 0 ? colors.gridAlt : colors.bg;
      ctx.fillRect(x * CELL, y * CELL, CELL, CELL);
    }
  }
  ctx.strokeStyle = colors.grid;
  ctx.lineWidth = 1;
  for (let x = 0; x <= W; x += CELL) {
    line(x, 0, x, H);
  }
  for (let y = 0; y <= H; y += CELL) {
    line(0, y, W, y);
  }
}

function drawBuilding(building) {
  const spec = specs[building.kind];
  const x = building.gx * CELL;
  const y = building.gy * CELL;
  const w = building.w * CELL;
  const h = building.h * CELL;
  ctx.fillStyle = spec.color;
  ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = "#080a0c";
  ctx.strokeRect(x, y, w, h);

  if (building.kind === "turret") {
    fillCircle(x + w / 2, y + h / 2, 10, "#161f22");
    ctx.strokeStyle = colors.projectile;
    ctx.lineWidth = 4;
    line(x + w / 2, y + h / 2, x + w / 2 + 14, y + h / 2);
  }
  if (building.kind === "mine") {
    ctx.fillStyle = "#5b4830";
    ctx.fillRect(x + 8, y + 8, w - 16, h - 16);
  }
  if (building.kind === "barracks") {
    ctx.fillStyle = "#372645";
    ctx.fillRect(x + 10, y + 8, w - 20, h - 16);
  }
  if (building.kind === "hq") {
    ctx.fillStyle = "#23395a";
    ctx.fillRect(x + 8, y + 8, w - 16, h - 16);
    ctx.fillStyle = colors.scrap;
    ctx.fillRect(x + 24, y + 24, w - 48, h - 48);
  }
  drawHpBar(x, y - 6, w, building.hp / maxHp(building));
}

function drawSoldier(soldier) {
  ctx.fillStyle = colors.soldier;
  ctx.fillRect(soldier.x - 6, soldier.y - 6, 12, 12);
  ctx.fillStyle = "#142230";
  ctx.fillRect(soldier.x - 2, soldier.y - 10, 4, 6);
}

function drawEnemy(enemy) {
  ctx.fillStyle = colors.enemy;
  ctx.fillRect(enemy.x - 8, enemy.y - 8, 16, 16);
  ctx.fillStyle = "#591c1c";
  ctx.fillRect(enemy.x - 4, enemy.y - 12, 8, 6);
}

function drawShot(shot) {
  fillCircle(shot.x, shot.y, 4, colors.projectile);
}

function drawPreview() {
  if (!state.selected || state.gameOver) return;
  const gx = Math.floor(state.mouse.x / CELL);
  const gy = Math.floor(state.mouse.y / CELL);
  const spec = specs[state.selected];
  const ok = canPlace(state.selected, gx, gy) && state.scrap >= spec.cost;
  ctx.globalAlpha = 0.45;
  ctx.fillStyle = ok ? colors.good : colors.bad;
  ctx.fillRect(gx * CELL, gy * CELL, spec.w * CELL, spec.h * CELL);
  ctx.globalAlpha = 1;
  ctx.strokeStyle = ok ? colors.good : colors.bad;
  ctx.strokeRect(gx * CELL, gy * CELL, spec.w * CELL, spec.h * CELL);
}

function drawHud() {
  const hq = getHq();
  ctx.fillStyle = colors.panel;
  ctx.fillRect(0, 0, W, 76);
  ctx.strokeStyle = colors.panelEdge;
  line(0, 76, W, 76);
  ctx.font = "22px Trebuchet MS";
  ctx.fillStyle = colors.scrap;
  ctx.fillText(`SCRAP ${Math.floor(state.scrap)}`, 12, 30);
  ctx.fillStyle = colors.warning;
  ctx.fillText(`WAVE ${state.wave}`, 150, 30);
  ctx.fillStyle = colors.text;
  ctx.fillText(`WORKERS ${state.workers}`, 260, 30);
  ctx.fillText(`SOLDIERS ${state.soldiers.length}`, 410, 30);
  ctx.fillStyle = colors.muted;
  ctx.fillText(`NEXT ${Math.max(0, Math.floor(state.waveTimer))}s`, 575, 30);
  ctx.fillStyle = hq && hq.hp > 80 ? colors.good : colors.bad;
  ctx.fillText(`BASE ${hq ? Math.floor(hq.hp) : 0}`, 700, 30);
  ctx.fillStyle = colors.muted;
  ctx.font = "18px Trebuchet MS";
  ctx.fillText(`Build: ${state.selected || "none"} | 1 mine 2 turret 3 barracks | W worker S soldier | U/I/O upgrades | R repair | Space wave`, 12, 58);
  if (state.message) {
    ctx.fillStyle = state.messageColor;
    ctx.fillText(state.message, 12, H - 16);
  }
}

function drawGameOver() {
  ctx.fillStyle = "rgba(5, 6, 8, 0.72)";
  ctx.fillRect(0, 0, W, H);
  ctx.textAlign = "center";
  ctx.fillStyle = colors.bad;
  ctx.font = "52px Trebuchet MS";
  ctx.fillText("OUTPOST LOST", W / 2, H / 2 - 12);
  ctx.fillStyle = colors.text;
  ctx.font = "24px Trebuchet MS";
  ctx.fillText("Press Enter or Restart to rebuild from the ashes.", W / 2, H / 2 + 36);
  ctx.textAlign = "left";
}

function drawHpBar(x, y, width, ratio) {
  ctx.fillStyle = colors.bad;
  ctx.fillRect(x, y, width, 4);
  ctx.fillStyle = colors.good;
  ctx.fillRect(x, y, Math.max(0, Math.min(1, ratio)) * width, 4);
}

function fillCircle(x, y, r, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
}

function line(x1, y1, x2, y2) {
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
}

function rand(min, max) {
  return min + Math.random() * (max - min);
}

function title(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function loop(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  update(dt);
  draw();
  requestAnimationFrame(loop);
}

resetGame();
requestAnimationFrame(loop);
