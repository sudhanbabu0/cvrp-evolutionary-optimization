"""
build_index.py
Compiles the static client-side index.html for direct GitHub Pages deployment
and Flask local deployment, featuring:
1. Interactive Canvas Map with smooth Zoom In/Out (+/- buttons, mouse wheel, pinch)
   and Pan (click & drag to move in any direction, reset view).
2. Direct user input for distance from warehouse to every delivery site.
3. Full Workspace Save & Restore (Backend Server storage, Browser LocalStorage, and JSON File Export/Import).
4. Individual truck animation & inspection, medium animation speed controls.
5. Academic assessment branding completely removed.
"""

import json
from pathlib import Path

root = Path(__file__).resolve().parent

with open(root / "static_data.json", "r", encoding="utf-8") as f:
    benchmark_data = json.load(f)

data_str = json.dumps(benchmark_data, indent=2)

html_template = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CVRP Evolutionary Computing Optimization Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
    .canvas-container { position: relative; width: 100%; aspect-ratio: 1; max-width: 620px; overflow: hidden; border-radius: 0.75rem; }
    canvas#routeCanvas { border-radius: 0.75rem; background: #0f172a; cursor: grab; user-select: none; }
    canvas#routeCanvas:active { cursor: grabbing; }
    .custom-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
    .custom-scroll::-webkit-scrollbar-track { background: #1e293b; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #475569; border-radius: 3px; }
    @keyframes toast-in { from { transform: translateY(-100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    .toast-anim { animation: toast-in 0.25s ease-out forwards; }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">

  <!-- Toast Notification Container -->
  <div id="toast-container" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Top Navigation Bar -->
  <header class="bg-slate-800/80 border-b border-slate-700/60 sticky top-0 z-40 backdrop-blur-md px-6 py-3.5">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-bold text-lg">
          <i class="fa-solid fa-truck-fast"></i>
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            CVRP Fleet Routing Optimizer
            <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Live Simulation</span>
          </h1>
          <p class="text-xs text-slate-400">Capacitated Vehicle Routing Problem &bull; Autonomous Multi-Fleet Logistics Optimization</p>
        </div>
      </div>

      <!-- Action Buttons & Badges -->
      <div class="flex flex-wrap items-center gap-2 text-xs">
        <button id="btn-open-scenario-modal" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-3 py-1.5 rounded-md shadow-md shadow-emerald-600/30 transition flex items-center gap-1.5 cursor-pointer">
          <i class="fa-solid fa-ruler-combined"></i> Set Distances & Trucks
        </button>
        <button id="btn-open-save-modal" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-3 py-1.5 rounded-md shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5 cursor-pointer">
          <i class="fa-solid fa-floppy-disk"></i> Save &amp; Load
        </button>
        <span id="badge-sites" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-location-dot text-indigo-400 mr-1.5"></i>35 Delivery Sites</span>
        <span id="badge-depot" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-warehouse text-amber-400 mr-1.5"></i>Warehouse (50, 50)</span>
        <span id="badge-capacity" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-box text-cyan-400 mr-1.5"></i>Capacity Q = 100</span>
        <span id="badge-trucks" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-truck text-emerald-400 mr-1.5"></i>Fleet Limit K = 8</span>
        <a href="https://github.com/sudhanbabu0/cvrp-evolutionary-optimization" target="_blank" class="bg-slate-700/60 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50 transition">
          <i class="fa-brands fa-github mr-1"></i>GitHub
        </a>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto p-4 md:p-6 space-y-6">

    <!-- Metrics Cards Banner -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-3 md:gap-4">
      <div class="bg-slate-800/60 border border-slate-700/60 p-4 rounded-xl">
        <div class="text-xs text-slate-400 font-medium">Greedy NN Baseline</div>
        <div class="text-2xl font-bold text-amber-400 mt-1" id="metric-baseline-dist">1036.59 <span class="text-xs text-slate-400">km</span></div>
        <div class="text-xs text-slate-400 mt-0.5" id="metric-baseline-fleet">7 Trucks &bull; 0.42 ms</div>
      </div>

      <div class="bg-slate-800/60 border border-slate-700/60 p-4 rounded-xl">
        <div class="text-xs text-slate-400 font-medium">GA Optimized Distance</div>
        <div class="text-2xl font-bold text-emerald-400 mt-1" id="metric-ga-dist">727.17 <span class="text-xs text-slate-400">km</span></div>
        <div class="text-xs text-slate-400 mt-0.5" id="metric-ga-fleet">6 Trucks &bull; Converged Gen 108</div>
      </div>

      <div class="bg-slate-800/60 border border-slate-700/60 p-4 rounded-xl">
        <div class="text-xs text-slate-400 font-medium">Distance Savings</div>
        <div class="text-2xl font-bold text-cyan-400 mt-1" id="metric-savings-dist">309.42 <span class="text-xs text-slate-400">km</span></div>
        <div class="text-xs text-emerald-400 font-semibold mt-0.5" id="metric-savings-pct"><i class="fa-solid fa-arrow-down mr-1"></i>29.85% Reduction</div>
      </div>

      <div class="bg-slate-800/60 border border-slate-700/60 p-4 rounded-xl">
        <div class="text-xs text-slate-400 font-medium">Fleet Optimization</div>
        <div class="text-2xl font-bold text-purple-400 mt-1" id="metric-fleet-saving">-1 Truck</div>
        <div class="text-xs text-purple-300 mt-0.5" id="metric-fleet-min">Theoretical Min: 6 Trucks</div>
      </div>

      <div class="bg-slate-800/60 border border-slate-700/60 p-4 rounded-xl col-span-2 md:col-span-1">
        <div class="text-xs text-slate-400 font-medium">Solver Runtime</div>
        <div class="text-2xl font-bold text-indigo-400 mt-1" id="metric-runtime">0.796 <span class="text-xs text-slate-400">s</span></div>
        <div class="text-xs text-slate-400 mt-0.5" id="metric-solver-type">Optimal Discovered Solution</div>
      </div>
    </div>

    <!-- Main Workspace Grid: Map on Left, Controls & Chart on Right -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- Left Column: Interactive Map Canvas (7 cols) -->
      <div class="lg:col-span-7 bg-slate-800/60 border border-slate-700/60 p-5 rounded-2xl flex flex-col justify-between">
        <div>
          <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-map-location-dot text-indigo-400"></i>
              2D Delivery Route Map
            </h2>

            <!-- Truck View Selector & Baseline Toggle -->
            <div class="flex items-center space-x-2">
              <div class="flex items-center space-x-1.5 bg-slate-700/80 px-2 py-1 rounded-lg border border-slate-600 text-xs">
                <i class="fa-solid fa-truck text-emerald-400"></i>
                <label for="select-truck-view" class="text-slate-300 font-medium">View:</label>
                <select id="select-truck-view" class="bg-slate-800 text-slate-100 rounded px-2 py-0.5 text-xs border border-slate-600 outline-none cursor-pointer">
                  <option value="all">All Trucks (Simultaneous)</option>
                </select>
              </div>

              <button id="btn-toggle-view" class="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-600 transition flex items-center gap-1.5 cursor-pointer">
                <i class="fa-solid fa-shuffle text-cyan-400"></i> Switch to Baseline
              </button>
            </div>
          </div>

          <!-- Active Truck Live Focus Banner -->
          <div id="active-truck-banner" class="hidden mb-3 p-2.5 bg-indigo-950/70 border border-indigo-500/40 rounded-xl text-xs flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span id="active-truck-badge" class="px-2 py-0.5 rounded font-bold text-white bg-indigo-600">Truck 1</span>
              <span id="active-truck-info" class="text-slate-200 font-medium">Stops: 6 &bull; Cargo: 99/100 units &bull; Dist: 110.2 km</span>
            </div>
            <button id="btn-reset-truck-focus" class="text-[11px] text-indigo-300 hover:text-white underline cursor-pointer">
              View All Trucks
            </button>
          </div>

          <!-- Canvas Element with Floating Zoom & Pan Controls -->
          <div class="canvas-container mx-auto">
            <canvas id="routeCanvas" width="600" height="600" class="w-full h-full shadow-2xl"></canvas>

            <!-- Floating Zoom & Pan Toolbar (Top-Right) -->
            <div class="absolute top-3 right-3 flex flex-col items-center gap-1.5 bg-slate-900/85 backdrop-blur-md p-1.5 rounded-xl border border-slate-700/80 shadow-2xl z-20">
              <button id="btn-zoom-in" title="Zoom In (Scroll Up)" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-emerald-400 flex items-center justify-center transition text-sm cursor-pointer border border-slate-700 active:scale-95">
                <i class="fa-solid fa-plus"></i>
              </button>
              <div id="zoom-level-badge" class="text-[11px] font-mono text-emerald-400 font-bold py-0.5 select-none text-center min-w-[36px]">
                100%
              </div>
              <button id="btn-zoom-out" title="Zoom Out (Scroll Down)" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-emerald-400 flex items-center justify-center transition text-sm cursor-pointer border border-slate-700 active:scale-95">
                <i class="fa-solid fa-minus"></i>
              </button>
              <button id="btn-zoom-reset" title="Reset View (Center & 100%)" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-400 flex items-center justify-center transition text-xs cursor-pointer border border-slate-700 active:scale-95">
                <i class="fa-solid fa-arrows-to-dot"></i>
              </button>
            </div>

            <!-- Floating Pan Instruction Badge (Bottom-Left) -->
            <div class="absolute bottom-3 left-3 bg-slate-900/80 backdrop-blur-sm px-2.5 py-1 rounded-lg border border-slate-700/60 text-[11px] text-slate-400 pointer-events-none flex items-center gap-1.5 select-none">
              <i class="fa-solid fa-up-down-left-right text-indigo-400 text-xs"></i>
              <span>Drag to move &bull; Scroll to zoom</span>
            </div>
          </div>
        </div>

        <!-- Canvas Controls & Animation Speed Playbar -->
        <div class="mt-4 pt-3 border-t border-slate-700/50 flex flex-wrap items-center justify-between gap-3 text-xs">
          <!-- Animation Controls -->
          <div class="flex items-center space-x-2">
            <button id="btn-play-anim" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-1.5 rounded-lg font-semibold flex items-center gap-1.5 shadow-md shadow-indigo-600/30 transition cursor-pointer">
              <i class="fa-solid fa-play"></i> Play Animation
            </button>
            <button id="btn-reset-anim" class="bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1.5 rounded-lg transition cursor-pointer">
              <i class="fa-solid fa-rotate-left mr-1"></i> Reset
            </button>

            <!-- Speed Control (Medium Default as requested) -->
            <div class="flex items-center space-x-1 bg-slate-700/70 px-2 py-1 rounded-lg border border-slate-600/60">
              <span class="text-slate-400 text-[11px] mr-1"><i class="fa-solid fa-gauge-high mr-1"></i>Speed:</span>
              <button class="btn-speed px-2 py-0.5 rounded text-[11px] transition text-slate-300 hover:text-white cursor-pointer" data-speed="slow">0.5x Slow</button>
              <button class="btn-speed px-2 py-0.5 rounded text-[11px] transition bg-indigo-600 text-white font-bold cursor-pointer" data-speed="medium">1x Medium</button>
              <button class="btn-speed px-2 py-0.5 rounded text-[11px] transition text-slate-300 hover:text-white cursor-pointer" data-speed="fast">2x Fast</button>
            </div>
          </div>

          <!-- Legend -->
          <div class="flex items-center space-x-3 text-slate-400">
            <span class="flex items-center gap-1"><span class="w-3 h-3 bg-red-500 rounded-sm inline-block"></span> Warehouse</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 bg-slate-300 rounded-full inline-block"></span> Delivery Site</span>
            <span class="flex items-center gap-1"><span class="w-3 h-1 bg-emerald-400 inline-block"></span> Truck Route</span>
          </div>
        </div>
      </div>

      <!-- Right Column: Controls & Real-Time Convergence Chart (5 cols) -->
      <div class="lg:col-span-5 space-y-6">

        <!-- Optimization Controls Card -->
        <div class="bg-slate-800/60 border border-slate-700/60 p-5 rounded-2xl">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-sliders text-emerald-400"></i>
              Optimization Controls
            </h2>
            <button id="btn-quick-config" class="text-xs bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 px-2.5 py-1 rounded-lg transition cursor-pointer flex items-center gap-1">
              <i class="fa-solid fa-ruler"></i> Set Distances
            </button>
          </div>

          <div class="space-y-4 text-xs">
            <!-- Population Size -->
            <div>
              <div class="flex justify-between font-medium mb-1">
                <span class="text-slate-300">Population Size (N_pop):</span>
                <span id="val-pop-size" class="text-emerald-400 font-mono font-bold">100</span>
              </div>
              <input type="range" id="input-pop-size" min="30" max="200" step="10" value="100" class="w-full accent-emerald-500 cursor-pointer">
            </div>

            <!-- Mutation Rate -->
            <div>
              <div class="flex justify-between font-medium mb-1">
                <span class="text-slate-300">Mutation Rate (p_m):</span>
                <span id="val-mut-rate" class="text-cyan-400 font-mono font-bold">0.15</span>
              </div>
              <input type="range" id="input-mut-rate" min="0.01" max="0.30" step="0.01" value="0.15" class="w-full accent-cyan-500 cursor-pointer">
            </div>

            <!-- Crossover Rate & Max Generations -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-300 font-medium mb-1">Crossover Rate (p_c):</label>
                <select id="select-cr-rate" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 outline-none">
                  <option value="0.75">0.75 (Low)</option>
                  <option value="0.85" selected>0.85 (Recommended)</option>
                  <option value="0.95">0.95 (High)</option>
                </select>
              </div>
              <div>
                <label class="block text-slate-300 font-medium mb-1">Max Generations:</label>
                <input type="number" id="input-generations" value="150" min="20" max="300" step="10" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono">
              </div>
            </div>

            <!-- Selection Strategy -->
            <div>
              <label class="block text-slate-300 font-medium mb-1">Selection Strategy:</label>
              <select id="select-selection" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 outline-none">
                <option value="tournament" selected>Tournament Selection (k=3, Elitism=2)</option>
                <option value="roulette">Roulette Wheel (Fitness Proportionate)</option>
              </select>
            </div>

            <!-- Run Button -->
            <button id="btn-run-ga" class="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-2.5 rounded-xl shadow-lg shadow-emerald-600/30 transition flex items-center justify-center gap-2 cursor-pointer text-sm">
              <i class="fa-solid fa-dna"></i> Run Evolutionary Algorithm
            </button>
          </div>
        </div>

        <!-- Real-Time Convergence Chart Card -->
        <div class="bg-slate-800/60 border border-slate-700/60 p-5 rounded-2xl">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-chart-line text-cyan-400"></i>
              Convergence History
            </h2>
            <span class="text-xs text-slate-400">Dual-Axis Fitness</span>
          </div>
          <div class="h-56">
            <canvas id="convergenceChart"></canvas>
          </div>
        </div>

      </div>

    </div>

    <!-- Active Route Breakdown Cards -->
    <div class="bg-slate-800/60 border border-slate-700/60 p-5 rounded-2xl space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <i class="fa-solid fa-route text-indigo-400"></i>
          Dispatched Vehicle Route Sequences & Payload Breakdown
        </h2>
        <span id="route-count-badge" class="text-xs bg-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-md border border-indigo-500/30 font-semibold">6 Active Trucks</span>
      </div>

      <div id="route-cards-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5"></div>
    </div>

  </main>

  <!-- ============================================================ -->
  <!-- MODAL: Direct User Input for Warehouse Distances & Trucks    -->
  <!-- ============================================================ -->
  <div id="modal-scenario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
      <!-- Modal Header -->
      <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-850">
        <div>
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-ruler-combined text-emerald-400"></i>
            User Input: Delivery Sites, Trucks & Distance from Warehouse
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Directly enter the distance from warehouse for every delivery site, configure number of sites and truck fleet.</p>
        </div>
        <button id="btn-close-modal" class="text-slate-400 hover:text-white text-lg p-1 transition cursor-pointer">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <!-- Modal Body (Scrollable) -->
      <div class="p-5 space-y-5 overflow-y-auto custom-scroll text-xs">
        
        <!-- Fleet & Warehouse Setup -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-slate-800/60 rounded-xl border border-slate-700/60">
          <div>
            <label class="block text-slate-300 font-semibold mb-1">Warehouse X (km):</label>
            <input type="number" id="input-depot-x" value="50.0" min="0" max="100" step="1" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-100 font-mono">
          </div>
          <div>
            <label class="block text-slate-300 font-semibold mb-1">Warehouse Y (km):</label>
            <input type="number" id="input-depot-y" value="50.0" min="0" max="100" step="1" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-100 font-mono">
          </div>
          <div>
            <label class="block text-emerald-400 font-bold mb-1"><i class="fa-solid fa-truck mr-1"></i>Number of Trucks (K):</label>
            <input type="number" id="input-fleet-limit" value="8" min="1" max="15" step="1" class="w-full bg-slate-900 border-2 border-emerald-500/50 rounded-lg p-2 text-white font-mono font-bold">
          </div>
          <div>
            <label class="block text-slate-300 font-semibold mb-1">Truck Capacity (Q):</label>
            <input type="number" id="input-truck-capacity" value="100" min="20" max="500" step="5" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-100 font-mono">
          </div>
        </div>

        <!-- Number of Delivery Sites & Quick Tools -->
        <div class="p-4 bg-slate-850 rounded-xl border border-slate-700/70 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center space-x-2">
              <span class="text-white font-bold"><i class="fa-solid fa-location-dot text-indigo-400 mr-1.5"></i>Number of Delivery Sites:</span>
              <input type="number" id="input-num-sites" value="35" min="3" max="50" class="w-20 bg-slate-900 border-2 border-indigo-500 rounded-lg p-1.5 text-center text-white font-mono font-bold text-sm">
              <button id="btn-update-num-sites" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-3 py-1.5 rounded-lg transition cursor-pointer">
                Set Site Count
              </button>
            </div>
            
            <div class="flex items-center space-x-2">
              <button id="btn-generate-random" class="bg-slate-700 hover:bg-slate-600 text-slate-200 border border-slate-600 px-3 py-1.5 rounded-lg transition cursor-pointer">
                <i class="fa-solid fa-dice mr-1"></i> Randomize Sites
              </button>
              <button id="btn-reset-benchmark" class="bg-slate-700 hover:bg-slate-600 text-slate-200 border border-slate-600 px-3 py-1.5 rounded-lg transition cursor-pointer">
                <i class="fa-solid fa-rotate-left mr-1"></i> Reset 35-Site Benchmark
              </button>
              <button id="btn-add-single-site" class="bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/40 px-3 py-1.5 rounded-lg transition font-medium cursor-pointer">
                <i class="fa-solid fa-plus mr-1"></i> Add Site
              </button>
            </div>
          </div>

          <!-- Bulk Distance Input -->
          <div class="pt-2 border-t border-slate-700/60 flex flex-wrap items-center gap-2">
            <span class="text-slate-300 font-semibold"><i class="fa-solid fa-paste text-amber-400 mr-1"></i>Bulk Enter Distances (km):</span>
            <input type="text" id="input-bulk-distances" placeholder="e.g. 15.2, 28.5, 42.0, 18.7, 33.1, 24.0..." class="flex-1 min-w-[240px] bg-slate-900 border border-slate-700 rounded-lg p-1.5 text-xs text-white font-mono">
            <button id="btn-apply-bulk-dist" class="bg-amber-600/30 hover:bg-amber-600/50 text-amber-300 border border-amber-500/40 px-3 py-1.5 rounded-lg transition font-semibold cursor-pointer">
              Apply to All Sites
            </button>
          </div>
        </div>

        <!-- Editable Delivery Sites & Distance to Warehouse Table -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-table-list text-cyan-400"></i>
              Delivery Sites &amp; User-Specified Distance Table
            </h4>
            <span id="custom-sites-count" class="text-emerald-400 font-semibold">35 Sites Configured | Total Demand: 580 units</span>
          </div>

          <div class="border border-slate-700/80 rounded-xl overflow-hidden">
            <div class="max-h-72 overflow-y-auto custom-scroll">
              <table class="w-full text-left border-collapse">
                <thead class="bg-slate-800 text-slate-300 text-[11px] uppercase sticky top-0 z-10">
                  <tr>
                    <th class="p-2.5">Site #</th>
                    <th class="p-2.5 text-emerald-400"><i class="fa-solid fa-ruler-horizontal mr-1"></i>Dist from Warehouse (km) [USER INPUT]</th>
                    <th class="p-2.5">Angle (&deg;)</th>
                    <th class="p-2.5">Coord X (km)</th>
                    <th class="p-2.5">Coord Y (km)</th>
                    <th class="p-2.5">Demand (units)</th>
                    <th class="p-2.5 text-center">Action</th>
                  </tr>
                </thead>
                <tbody id="custom-sites-tbody" class="divide-y divide-slate-800 text-slate-200">
                  <!-- Populated dynamically -->
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="p-4 border-t border-slate-800 flex items-center justify-between bg-slate-850">
        <span class="text-slate-400 text-xs">
          <i class="fa-solid fa-circle-info text-indigo-400 mr-1"></i>
          Distances entered here directly set the distance matrix from the central warehouse.
        </span>
        <div class="flex items-center space-x-2">
          <button id="btn-cancel-scenario" class="bg-slate-700 hover:bg-slate-600 text-slate-300 px-4 py-2 rounded-xl transition cursor-pointer">
            Cancel
          </button>
          <button id="btn-apply-scenario" class="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold px-5 py-2 rounded-xl shadow-lg shadow-emerald-600/30 transition flex items-center gap-1.5 cursor-pointer">
            <i class="fa-solid fa-check"></i> Apply Distances &amp; Recalculate Routes
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- ============================================================ -->
  <!-- MODAL: Save Everything & Restore Workspace (Backend + Local)  -->
  <!-- ============================================================ -->
  <div id="modal-save-load" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
      <!-- Header -->
      <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-850">
        <div>
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-floppy-disk text-indigo-400"></i>
            Save &amp; Restore Complete Workspace
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Save all delivery sites, warehouse distances, truck fleet, routes, and optimization results.</p>
        </div>
        <button id="btn-close-save-modal" class="text-slate-400 hover:text-white text-lg p-1 transition cursor-pointer">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <!-- Body -->
      <div class="p-5 space-y-5 overflow-y-auto custom-scroll text-xs">

        <!-- Card 1: Save Current Workspace -->
        <div class="p-4 bg-slate-800/60 border border-slate-700/60 rounded-xl space-y-3">
          <h4 class="font-bold text-white text-sm flex items-center gap-2">
            <i class="fa-solid fa-arrow-down-to-bracket text-emerald-400"></i>
            Save Current State
          </h4>
          <p class="text-slate-400">Save your current setup, custom distances, trucks, and optimized route results:</p>
          
          <div class="flex flex-wrap items-center gap-2">
            <input type="text" id="input-save-name" placeholder="Scenario Name (e.g. North-Zone-Logistics-35)" class="flex-1 min-w-[240px] bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-white font-mono">
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
            <!-- 1. Download File -->
            <button id="btn-action-export-json" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 px-3 rounded-lg shadow-md transition flex items-center justify-center gap-1.5 cursor-pointer">
              <i class="fa-solid fa-file-arrow-down"></i> Export JSON File
            </button>
            <!-- 2. Save to Browser -->
            <button id="btn-action-save-browser" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-3 rounded-lg shadow-md transition flex items-center justify-center gap-1.5 cursor-pointer">
              <i class="fa-solid fa-database"></i> Save to Browser
            </button>
            <!-- 3. Save to Backend Server -->
            <button id="btn-action-save-backend" class="bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2 px-3 rounded-lg shadow-md transition flex items-center justify-center gap-1.5 cursor-pointer">
              <i class="fa-solid fa-server"></i> Save to Backend Disk
            </button>
          </div>
        </div>

        <!-- Card 2: Restore from JSON File -->
        <div class="p-4 bg-slate-800/60 border border-slate-700/60 rounded-xl space-y-3">
          <h4 class="font-bold text-white text-sm flex items-center gap-2">
            <i class="fa-solid fa-file-import text-cyan-400"></i>
            Import / Restore from JSON File
          </h4>
          <p class="text-slate-400">Upload any previously saved CVRP workspace file to restore all delivery sites, distances, trucks, and route solutions immediately:</p>
          
          <div class="flex items-center space-x-3">
            <input type="file" id="file-import-input" accept=".json" class="hidden">
            <button id="btn-trigger-file-import" class="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg border border-slate-600 transition flex items-center gap-2 cursor-pointer font-semibold">
              <i class="fa-solid fa-upload text-cyan-400"></i> Choose JSON File to Restore
            </button>
            <span id="file-import-status" class="text-slate-400 italic">No file chosen</span>
          </div>
        </div>

        <!-- Card 3: Saved Items List (Browser + Backend) -->
        <div class="p-4 bg-slate-800/60 border border-slate-700/60 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="font-bold text-white text-sm flex items-center gap-2">
              <i class="fa-solid fa-clock-rotate-left text-amber-400"></i>
              Saved Workspaces List
            </h4>
            <button id="btn-refresh-saved-list" class="text-[11px] text-slate-400 hover:text-white transition cursor-pointer flex items-center gap-1">
              <i class="fa-solid fa-rotate mr-0.5"></i> Refresh
            </button>
          </div>

          <!-- Saved Scenarios Table -->
          <div class="border border-slate-700/70 rounded-lg overflow-hidden">
            <div class="max-h-48 overflow-y-auto custom-scroll">
              <table class="w-full text-left border-collapse">
                <thead class="bg-slate-850 text-slate-400 text-[11px] uppercase">
                  <tr>
                    <th class="p-2">Name</th>
                    <th class="p-2">Location</th>
                    <th class="p-2">Sites</th>
                    <th class="p-2">Distance</th>
                    <th class="p-2">Saved At</th>
                    <th class="p-2 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody id="saved-items-tbody" class="divide-y divide-slate-800 text-slate-200">
                  <tr>
                    <td colspan="6" class="p-3 text-center text-slate-500 italic">No saved workspaces yet. Save one above!</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="p-4 border-t border-slate-800 flex items-center justify-end bg-slate-850">
        <button id="btn-done-save-modal" class="bg-slate-700 hover:bg-slate-600 text-white font-semibold px-5 py-2 rounded-xl transition cursor-pointer">
          Close
        </button>
      </div>
    </div>
  </div>

  <!-- Embedded Benchmark Data & Scripts -->
  <script>
    const INITIAL_BENCHMARK_DATA = __DATA_PLACEHOLDER__;

    // Palette for routes
    const COLORS = [
      "#38bdf8", "#34d399", "#fbbf24", "#f472b6",
      "#a78bfa", "#f87171", "#fb923c", "#4ade80",
      "#818cf8", "#e879f9", "#2dd4bf", "#facc15"
    ];

    // Global Interactive State
    let DATA = JSON.parse(JSON.stringify(INITIAL_BENCHMARK_DATA));

    // Augment initial customers with polar coordinates
    DATA.customers.forEach(c => {
      const dx = c.x - DATA.depot.x;
      const dy = c.y - DATA.depot.y;
      c.distToDepot = parseFloat(Math.sqrt(dx * dx + dy * dy).toFixed(1));
      c.angle = Math.round((Math.atan2(dy, dx) * 180 / Math.PI + 360) % 360);
    });

    let currentRoutes = DATA.ga_best ? DATA.ga_best.routes : [];
    let currentSolver = "Genetic Algorithm";
    let currentView = "ga";
    let selectedTruck = "all";

    // Animation Speed: medium default
    let animationSpeedStep = 0.0035;
    let animProgress = 0;
    let isAnimating = true;
    let animationId = null;

    // ============================================================
    // CANVAS ZOOM & PAN STATE
    // ============================================================
    let mapZoom = 1.0;
    let mapPan = { x: 0, y: 0 };
    let isDragging = false;
    let dragStart = { x: 0, y: 0 };

    let chartInstance = null;
    const canvas = document.getElementById("routeCanvas");
    const ctx = canvas.getContext("2d");

    // Slider Listeners
    document.getElementById("input-pop-size").addEventListener("input", e => {
      document.getElementById("val-pop-size").textContent = e.target.value;
    });
    document.getElementById("input-mut-rate").addEventListener("input", e => {
      document.getElementById("val-mut-rate").textContent = parseFloat(e.target.value).toFixed(2);
    });

    // Speed Controls
    document.querySelectorAll(".btn-speed").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".btn-speed").forEach(b => {
          b.className = "btn-speed px-2 py-0.5 rounded text-[11px] transition text-slate-300 hover:text-white cursor-pointer";
        });
        btn.className = "btn-speed px-2 py-0.5 rounded text-[11px] transition bg-indigo-600 text-white font-bold cursor-pointer";
        const sp = btn.dataset.speed;
        if (sp === "slow") animationSpeedStep = 0.0018;
        else if (sp === "medium") animationSpeedStep = 0.0035;
        else if (sp === "fast") animationSpeedStep = 0.0075;
      });
    });

    // ============================================================
    // COORDINATE MAPPING WITH ZOOM & PAN
    // ============================================================
    function toCanvas(x, y) {
      const margin = 45;
      const usable = canvas.width - margin * 2;
      // Unscaled base coordinates
      const cx0 = margin + (x / 100) * usable;
      const cy0 = canvas.height - (margin + (y / 100) * usable);
      // Center of canvas
      const midX = canvas.width / 2;
      const midY = canvas.height / 2;
      return {
        cx: midX + (cx0 - midX) * mapZoom + mapPan.x,
        cy: midY + (cy0 - midY) * mapZoom + mapPan.y
      };
    }

    function updateZoomUI() {
      const pct = Math.round(mapZoom * 100);
      document.getElementById("zoom-level-badge").textContent = `${pct}%`;
    }

    // Zoom Buttons
    document.getElementById("btn-zoom-in").addEventListener("click", () => {
      mapZoom = Math.min(5.0, parseFloat((mapZoom * 1.25).toFixed(2)));
      updateZoomUI();
      if (!isAnimating) drawMap();
    });

    document.getElementById("btn-zoom-out").addEventListener("click", () => {
      mapZoom = Math.max(0.4, parseFloat((mapZoom / 1.25).toFixed(2)));
      updateZoomUI();
      if (!isAnimating) drawMap();
    });

    document.getElementById("btn-zoom-reset").addEventListener("click", () => {
      mapZoom = 1.0;
      mapPan = { x: 0, y: 0 };
      updateZoomUI();
      if (!isAnimating) drawMap();
    });

    // Mouse Wheel Zoom centered on cursor
    canvas.addEventListener("wheel", e => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const mouseX = (e.clientX - rect.left) * (canvas.width / rect.width);
      const mouseY = (e.clientY - rect.top) * (canvas.height / rect.height);

      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      const oldZoom = mapZoom;
      const newZoom = Math.max(0.4, Math.min(5.0, mapZoom * zoomFactor));

      mapPan.x = mouseX - (mouseX - mapPan.x) * (newZoom / oldZoom);
      mapPan.y = mouseY - (mouseY - mapPan.y) * (newZoom / oldZoom);
      mapZoom = newZoom;

      updateZoomUI();
      if (!isAnimating) drawMap();
    }, { passive: false });

    // Click & Drag to Move (Pan)
    canvas.addEventListener("mousedown", e => {
      isDragging = true;
      dragStart = { x: e.clientX - mapPan.x, y: e.clientY - mapPan.y };
      canvas.style.cursor = "grabbing";
    });

    window.addEventListener("mousemove", e => {
      if (!isDragging) return;
      mapPan.x = e.clientX - dragStart.x;
      mapPan.y = e.clientY - dragStart.y;
      if (!isAnimating) drawMap();
    });

    window.addEventListener("mouseup", () => {
      if (isDragging) {
        isDragging = false;
        canvas.style.cursor = "grab";
      }
    });

    // Touch Support for Mobile / Touchscreen Panning
    let touchStartDist = 0;
    canvas.addEventListener("touchstart", e => {
      if (e.touches.length === 1) {
        isDragging = true;
        dragStart = { x: e.touches[0].clientX - mapPan.x, y: e.touches[0].clientY - mapPan.y };
      } else if (e.touches.length === 2) {
        isDragging = false;
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        touchStartDist = Math.sqrt(dx * dx + dy * dy);
      }
    }, { passive: true });

    canvas.addEventListener("touchmove", e => {
      if (e.touches.length === 1 && isDragging) {
        mapPan.x = e.touches[0].clientX - dragStart.x;
        mapPan.y = e.touches[0].clientY - dragStart.y;
        if (!isAnimating) drawMap();
      } else if (e.touches.length === 2) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (touchStartDist > 0) {
          const factor = dist / touchStartDist;
          mapZoom = Math.max(0.4, Math.min(5.0, mapZoom * factor));
          touchStartDist = dist;
          updateZoomUI();
          if (!isAnimating) drawMap();
        }
      }
    }, { passive: true });

    canvas.addEventListener("touchend", () => {
      isDragging = false;
      touchStartDist = 0;
    }, { passive: true });

    // Double-click resets view
    canvas.addEventListener("dblclick", () => {
      mapZoom = 1.0;
      mapPan = { x: 0, y: 0 };
      updateZoomUI();
      if (!isAnimating) drawMap();
    });

    // ============================================================
    // TOAST NOTIFICATIONS
    // ============================================================
    function showToast(message, type = "success") {
      const container = document.getElementById("toast-container");
      const toast = document.createElement("div");
      const bg = type === "success" ? "bg-emerald-600" : (type === "error" ? "bg-red-600" : "bg-indigo-600");
      const icon = type === "success" ? "fa-circle-check" : (type === "error" ? "fa-circle-exclamation" : "fa-info");
      toast.className = `${bg} text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center gap-2 text-xs font-semibold toast-anim`;
      toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
      container.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.3s";
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }

    // Populate Individual Truck Selector Dropdown
    function updateTruckSelector() {
      const sel = document.getElementById("select-truck-view");
      sel.innerHTML = '<option value="all">All Trucks (Simultaneous)</option>';

      currentRoutes.forEach((route, idx) => {
        const col = COLORS[idx % COLORS.length];
        const opt = document.createElement("option");
        opt.value = idx;
        opt.textContent = `Truck ${idx + 1} (${route.length - 2} stops)`;
        sel.appendChild(opt);
      });

      if (selectedTruck !== "all" && parseInt(selectedTruck) >= currentRoutes.length) {
        selectedTruck = "all";
      }
      sel.value = selectedTruck;
      updateActiveTruckBanner();
    }

    function updateActiveTruckBanner() {
      const banner = document.getElementById("active-truck-banner");
      if (selectedTruck === "all") {
        banner.classList.add("hidden");
      } else {
        banner.classList.remove("hidden");
        const idx = parseInt(selectedTruck);
        const route = currentRoutes[idx];
        const col = COLORS[idx % COLORS.length];
        
        const badge = document.getElementById("active-truck-badge");
        badge.textContent = `Truck ${idx + 1}`;
        badge.style.backgroundColor = col;

        let load = 0;
        let dist = 0;
        for (let i = 0; i < route.length - 1; i++) {
          dist += DATA.dist_matrix[route[i]][route[i + 1]];
          if (route[i] !== 0) {
            const cust = DATA.customers.find(c => c.id === route[i]);
            if (cust) load += cust.demand;
          }
        }
        document.getElementById("active-truck-info").textContent = 
          `Stops: ${route.length - 2} | Cargo: ${load}/${DATA.capacity} units (${Math.round((load/DATA.capacity)*100)}%) | Route Dist: ${dist.toFixed(2)} km`;
      }
    }

    document.getElementById("select-truck-view").addEventListener("change", e => {
      selectedTruck = e.target.value;
      updateActiveTruckBanner();
      drawMap();
    });

    document.getElementById("btn-reset-truck-focus").addEventListener("click", () => {
      selectedTruck = "all";
      document.getElementById("select-truck-view").value = "all";
      updateActiveTruckBanner();
      drawMap();
    });

    // Draw Map on Canvas with Zoom & Pan Transformations
    function drawMap() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Gridlines transformed with Zoom & Pan
      ctx.strokeStyle = "#1e293b";
      ctx.lineWidth = 1;
      for (let i = 0; i <= 100; i += 20) {
        const p1 = toCanvas(i, 0);
        const p2 = toCanvas(i, 100);
        ctx.beginPath();
        ctx.moveTo(p1.cx, p1.cy);
        ctx.lineTo(p2.cx, p2.cy);
        ctx.stroke();

        const p3 = toCanvas(0, i);
        const p4 = toCanvas(100, i);
        ctx.beginPath();
        ctx.moveTo(p3.cx, p3.cy);
        ctx.lineTo(p4.cx, p4.cy);
        ctx.stroke();
      }

      const depot = DATA.depot;
      const dPt = toCanvas(depot.x, depot.y);

      // Draw Routes
      if (currentRoutes && currentRoutes.length > 0) {
        currentRoutes.forEach((route, rIdx) => {
          const col = COLORS[rIdx % COLORS.length];
          const isFocused = (selectedTruck === "all" || parseInt(selectedTruck) === rIdx);

          ctx.strokeStyle = col;
          ctx.lineWidth = isFocused ? 3.0 : 0.8;
          ctx.globalAlpha = isFocused ? 0.95 : 0.15;
          ctx.beginPath();

          for (let i = 0; i < route.length; i++) {
            const nId = route[i];
            let pt = (nId === 0) ? dPt : toCanvas(DATA.customers.find(c => c.id === nId).x, DATA.customers.find(c => c.id === nId).y);
            if (i === 0) ctx.moveTo(pt.cx, pt.cy);
            else ctx.lineTo(pt.cx, pt.cy);
          }
          ctx.stroke();
          ctx.globalAlpha = 1.0;
        });
      }

      // Draw Delivery Sites
      DATA.customers.forEach(cust => {
        const pt = toCanvas(cust.x, cust.y);
        
        let isInFocusedTruck = false;
        let stopOrder = -1;
        if (selectedTruck !== "all") {
          const r = currentRoutes[parseInt(selectedTruck)];
          if (r) {
            stopOrder = r.indexOf(cust.id);
            if (stopOrder > 0 && stopOrder < r.length - 1) isInFocusedTruck = true;
          }
        }

        ctx.fillStyle = isInFocusedTruck ? COLORS[parseInt(selectedTruck) % COLORS.length] : "#334155";
        ctx.strokeStyle = isInFocusedTruck ? "#ffffff" : "#cbd5e1";
        ctx.lineWidth = isInFocusedTruck ? 2.5 : 1.5;
        ctx.beginPath();
        ctx.arc(pt.cx, pt.cy, isInFocusedTruck ? 11 : 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = "#ffffff";
        ctx.font = isInFocusedTruck ? "bold 10px system-ui" : "bold 9px system-ui";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(isInFocusedTruck ? `${stopOrder}` : cust.id, pt.cx, pt.cy);
      });

      // Draw Central Warehouse
      ctx.fillStyle = "#ef4444";
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 2.5;
      ctx.fillRect(dPt.cx - 11, dPt.cy - 11, 22, 22);
      ctx.strokeRect(dPt.cx - 11, dPt.cy - 11, 22, 22);

      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 11px system-ui";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("0", dPt.cx, dPt.cy);
    }

    // Animation Loop
    function animate() {
      drawMap();

      if (isAnimating && currentRoutes.length > 0) {
        animProgress += animationSpeedStep;
        if (animProgress > 1.0) animProgress = 0.0;

        currentRoutes.forEach((route, rIdx) => {
          if (selectedTruck !== "all" && parseInt(selectedTruck) !== rIdx) {
            return;
          }

          const col = COLORS[rIdx % COLORS.length];
          const totalSegments = route.length - 1;
          const currentTotal = animProgress * totalSegments;
          const segIdx = Math.min(totalSegments - 1, Math.floor(currentTotal));
          const segT = currentTotal - segIdx;

          const n1 = route[segIdx];
          const n2 = route[segIdx + 1];

          const p1 = (n1 === 0) ? toCanvas(DATA.depot.x, DATA.depot.y) : toCanvas(DATA.customers.find(c => c.id === n1).x, DATA.customers.find(c => c.id === n1).y);
          const p2 = (n2 === 0) ? toCanvas(DATA.depot.x, DATA.depot.y) : toCanvas(DATA.customers.find(c => c.id === n2).x, DATA.customers.find(c => c.id === n2).y);

          const curX = p1.cx + (p2.cx - p1.cx) * segT;
          const curY = p1.cy + (p2.cy - p1.cy) * segT;

          // Pulsing halo
          ctx.fillStyle = col;
          ctx.globalAlpha = 0.35;
          ctx.beginPath();
          ctx.arc(curX, curY, 12, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha = 1.0;

          // Animated delivery truck icon dot
          ctx.fillStyle = col;
          ctx.beginPath();
          ctx.arc(curX, curY, 7, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 2.0;
          ctx.stroke();

          // Truck label
          ctx.fillStyle = "#ffffff";
          ctx.font = "bold 9px system-ui";
          ctx.textAlign = "center";
          ctx.fillText(`T${rIdx + 1}`, curX, curY - 12);
        });

        animationId = requestAnimationFrame(animate);
      }
    }

    document.getElementById("btn-play-anim").addEventListener("click", () => {
      isAnimating = !isAnimating;
      const btn = document.getElementById("btn-play-anim");
      if (isAnimating) {
        btn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause';
        animate();
      } else {
        btn.innerHTML = '<i class="fa-solid fa-play"></i> Play Animation';
        cancelAnimationFrame(animationId);
      }
    });

    document.getElementById("btn-reset-anim").addEventListener("click", () => {
      animProgress = 0;
      drawMap();
    });

    // Update Metrics Display
    function updateMetrics(baseDist, gaDist, vans, saveDist, savePct, runtime, solver, convGen) {
      document.getElementById("metric-baseline-dist").innerHTML = `${parseFloat(baseDist).toFixed(2)} <span class="text-xs text-slate-400">km</span>`;
      document.getElementById("metric-ga-dist").innerHTML = `${parseFloat(gaDist).toFixed(2)} <span class="text-xs text-slate-400">km</span>`;
      document.getElementById("metric-savings-dist").innerHTML = `${parseFloat(saveDist).toFixed(2)} <span class="text-xs text-slate-400">km</span>`;
      document.getElementById("metric-savings-pct").innerHTML = `<i class="fa-solid fa-arrow-down mr-1"></i>${parseFloat(savePct).toFixed(2)}% Reduction`;
      document.getElementById("metric-runtime").innerHTML = `${parseFloat(runtime).toFixed(3)} <span class="text-xs text-slate-400">s</span>`;
      document.getElementById("metric-solver-type").textContent = solver;

      const minVans = Math.ceil(DATA.total_demand / DATA.capacity);
      document.getElementById("metric-fleet-min").textContent = `Theoretical Min: ${minVans} Trucks`;
      document.getElementById("metric-ga-fleet").textContent = `${vans} Trucks | Converged Gen ${convGen || 108}`;
      const diff = 7 - vans;
      document.getElementById("metric-fleet-saving").textContent = diff >= 0 ? `-${diff} Trucks` : `+${Math.abs(diff)} Trucks`;
    }

    // Render Route Cards
    function renderRouteCards(routes, demands, distances) {
      const container = document.getElementById("route-cards-container");
      container.innerHTML = "";
      document.getElementById("route-count-badge").textContent = `${routes.length} Active Trucks`;

      routes.forEach((route, idx) => {
        const col = COLORS[idx % COLORS.length];
        const load = demands[idx];
        const dist = distances[idx];
        const pct = Math.min(100, Math.round((load / DATA.capacity) * 100));

        const card = document.createElement("div");
        card.className = "bg-slate-900/80 border border-slate-700/60 p-4 rounded-xl flex flex-col justify-between hover:border-slate-600 transition";
        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="font-bold text-xs px-2.5 py-0.5 rounded-full text-white" style="background-color: ${col};">
                <i class="fa-solid fa-truck mr-1"></i>Truck ${idx + 1}
              </span>
              <span class="text-slate-400 text-xs font-mono">${dist.toFixed(1)} km</span>
            </div>
            <div class="mb-2">
              <div class="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Payload Utilization</span>
                <span class="font-bold text-slate-200">${load} / ${DATA.capacity} u (${pct}%)</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-500" style="width: ${pct}%; background-color: ${col};"></div>
              </div>
            </div>
            <div class="text-[11px] text-slate-400">
              <span class="text-slate-500 font-semibold">Stops (${route.length - 2}):</span>
              <span class="font-mono text-slate-300 ml-1">${route.slice(1, -1).join(" &rarr; ")}</span>
            </div>
          </div>
        `;
        container.appendChild(card);
      });
    }

    // Chart.js Convergence Chart
    function initChart() {
      const chartCtx = document.getElementById("convergenceChart").getContext("2d");
      chartInstance = new Chart(chartCtx, {
        type: "line",
        data: {
          labels: [],
          datasets: [
            {
              label: "Best Distance (km)",
              data: [],
              borderColor: "#10b981",
              backgroundColor: "rgba(16, 185, 129, 0.1)",
              borderWidth: 2,
              pointRadius: 0,
              tension: 0.2,
              yAxisID: "y"
            },
            {
              label: "Average Distance (km)",
              data: [],
              borderColor: "#64748b",
              borderDash: [4, 4],
              borderWidth: 1.5,
              pointRadius: 0,
              tension: 0.2,
              yAxisID: "y"
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          scales: {
            x: {
              title: { display: true, text: "Generation", color: "#94a3b8", font: { size: 10 } },
              grid: { color: "#1e293b" },
              ticks: { color: "#64748b", font: { size: 9 }, maxTicksLimit: 8 }
            },
            y: {
              title: { display: true, text: "Total Distance (km)", color: "#94a3b8", font: { size: 10 } },
              grid: { color: "#1e293b" },
              ticks: { color: "#64748b", font: { size: 9 } }
            }
          },
          plugins: {
            legend: { labels: { color: "#cbd5e1", font: { size: 10 } } }
          }
        }
      });
    }

    function updateChart(history) {
      if (!chartInstance) return;
      chartInstance.data.labels = history.generation;
      chartInstance.data.datasets[0].data = history.best_distance;
      chartInstance.data.datasets[1].data = history.avg_distance;
      chartInstance.update();
    }

    // Toggle baseline vs GA view
    document.getElementById("btn-toggle-view").addEventListener("click", () => {
      const btn = document.getElementById("btn-toggle-view");
      if (currentView === "ga") {
        currentView = "baseline";
        currentRoutes = DATA.baseline.routes;
        btn.innerHTML = '<i class="fa-solid fa-dna text-emerald-400"></i> Switch to GA Best';
        renderRouteCards(DATA.baseline.routes, DATA.baseline.route_demands, DATA.baseline.route_distances_km);
      } else {
        currentView = "ga";
        currentRoutes = DATA.ga_best.routes;
        btn.innerHTML = '<i class="fa-solid fa-shuffle text-cyan-400"></i> Switch to Baseline';
        renderRouteCards(DATA.ga_best.routes, DATA.ga_best.route_demands, DATA.ga_best.route_distances_km);
      }
      updateTruckSelector();
      drawMap();
    });

    // ============================================================
    // CLIENT-SIDE GREEDY NEAREST NEIGHBOR SOLVER
    // ============================================================
    function solveGreedyNN(depot, customers, capacity, distMatrix) {
      const startTime = performance.now();
      const unvisited = new Set(customers.map(c => c.id));
      const demandMap = {};
      customers.forEach(c => demandMap[c.id] = c.demand);

      const routes = [];
      const routeDemands = [];
      const routeDistances = [];

      while (unvisited.size > 0) {
        const route = [0];
        let currNode = 0;
        let currCap = capacity;
        let routeDist = 0;
        let routeLoad = 0;

        while (unvisited.size > 0) {
          let bestCandidate = null;
          let bestDist = Infinity;

          for (const candId of unvisited) {
            const candDemand = demandMap[candId];
            if (candDemand <= currCap) {
              const d = distMatrix[currNode][candId];
              if (d < bestDist) {
                bestDist = d;
                bestCandidate = candId;
              }
            }
          }

          if (bestCandidate !== null) {
            route.push(bestCandidate);
            routeDist += bestDist;
            routeLoad += demandMap[bestCandidate];
            currCap -= demandMap[bestCandidate];
            unvisited.delete(bestCandidate);
            currNode = bestCandidate;
          } else {
            break;
          }
        }

        route.push(0);
        routeDist += distMatrix[currNode][0];

        routes.push(route);
        routeDemands.push(routeLoad);
        routeDistances.push(parseFloat(routeDist.toFixed(2)));
      }

      const totalDist = routeDistances.reduce((a, b) => a + b, 0);
      const runtime = (performance.now() - startTime) / 1000;

      return {
        routes: routes,
        route_demands: routeDemands,
        route_distances_km: routeDistances,
        total_distance_km: parseFloat(totalDist.toFixed(2)),
        vehicles_utilized: routes.length,
        runtime_seconds: parseFloat(runtime.toFixed(4))
      };
    }

    // ============================================================
    // CLIENT-SIDE GENETIC ALGORITHM ENGINE
    // ============================================================
    function solveClientGA(customers, capacity, fleetLimit, distMatrix, popSize, mutRate, crRate, maxGen) {
      const startTime = performance.now();
      const numCust = customers.length;
      const custIds = customers.map(c => c.id);
      const demandMap = {};
      customers.forEach(c => demandMap[c.id] = c.demand);

      function splitChromosome(perm) {
        const rList = [];
        let currRoute = [0];
        let currLoad = 0;

        for (let i = 0; i < perm.length; i++) {
          const cid = perm[i];
          const d = demandMap[cid];
          if (currLoad + d <= capacity) {
            currRoute.push(cid);
            currLoad += d;
          } else {
            currRoute.push(0);
            rList.push(currRoute);
            currRoute = [0, cid];
            currLoad = d;
          }
        }
        if (currRoute.length > 1) {
          currRoute.push(0);
          rList.push(currRoute);
        }
        return rList;
      }

      function calcDist(rList) {
        let tot = 0;
        for (let r = 0; r < rList.length; r++) {
          const route = rList[r];
          for (let i = 0; i < route.length - 1; i++) {
            tot += distMatrix[route[i]][route[i + 1]];
          }
        }
        return tot;
      }

      function fitness(perm) {
        const rList = splitChromosome(perm);
        const dist = calcDist(rList);
        const penalty = (rList.length > fleetLimit) ? (rList.length - fleetLimit) * 500 : 0;
        return 1.0 / (dist + penalty + 1e-6);
      }

      // Initial Population
      let population = [];
      for (let p = 0; p < popSize; p++) {
        const perm = [...custIds];
        for (let i = perm.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [perm[i], perm[j]] = [perm[j], perm[i]];
        }
        population.push(perm);
      }

      let bestPerm = null;
      let bestDistOverall = Infinity;
      let bestFitOverall = -1;
      let convergedGen = 1;

      const histGen = [];
      const histBest = [];
      const histAvg = [];

      for (let gen = 1; gen <= maxGen; gen++) {
        const fitnesses = population.map(ind => fitness(ind));
        const distances = population.map(ind => calcDist(splitChromosome(ind)));

        for (let i = 0; i < population.length; i++) {
          if (fitnesses[i] > bestFitOverall) {
            bestFitOverall = fitnesses[i];
            bestDistOverall = distances[i];
            bestPerm = [...population[i]];
            convergedGen = gen;
          }
        }

        const avgDist = distances.reduce((a, b) => a + b, 0) / distances.length;
        histGen.push(gen);
        histBest.push(parseFloat(bestDistOverall.toFixed(2)));
        histAvg.push(parseFloat(avgDist.toFixed(2)));

        // Next generation
        const newPop = [];
        // Elitism (top 2)
        const sortedIndices = fitnesses.map((f, i) => [f, i]).sort((a, b) => b[0] - a[0]);
        newPop.push([...population[sortedIndices[0][1]]]);
        newPop.push([...population[sortedIndices[1][1]]]);

        while (newPop.length < popSize) {
          // Tournament Selection (k=3)
          function selectParent() {
            let bestIdx = Math.floor(Math.random() * popSize);
            for (let t = 0; t < 2; t++) {
              const cand = Math.floor(Math.random() * popSize);
              if (fitnesses[cand] > fitnesses[bestIdx]) bestIdx = cand;
            }
            return population[bestIdx];
          }

          const p1 = selectParent();
          const p2 = selectParent();

          let c1 = [...p1];
          let c2 = [...p2];

          // Order Crossover (OX1)
          if (Math.random() < crRate && numCust > 2) {
            let i1 = Math.floor(Math.random() * numCust);
            let i2 = Math.floor(Math.random() * numCust);
            if (i1 > i2) [i1, i2] = [i2, i1];

            function ox1(pa, pb) {
              const child = new Array(numCust).fill(null);
              for (let k = i1; k <= i2; k++) child[k] = pa[k];
              const segSet = new Set(child.slice(i1, i2 + 1));
              let fillIdx = (i2 + 1) % numCust;
              for (let k = 0; k < numCust; k++) {
                const item = pb[(i2 + 1 + k) % numCust];
                if (!segSet.has(item)) {
                  child[fillIdx] = item;
                  fillIdx = (fillIdx + 1) % numCust;
                }
              }
              return child;
            }

            c1 = ox1(p1, p2);
            c2 = ox1(p2, p1);
          }

          // 2-Opt Inversion Mutation
          function mutate(ind) {
            if (Math.random() < mutRate && numCust > 3) {
              let i1 = Math.floor(Math.random() * numCust);
              let i2 = Math.floor(Math.random() * numCust);
              if (i1 > i2) [i1, i2] = [i2, i1];
              const sub = ind.slice(i1, i2 + 1).reverse();
              for (let k = 0; k < sub.length; k++) ind[i1 + k] = sub[k];
            }
            return ind;
          }

          newPop.push(mutate(c1));
          if (newPop.length < popSize) newPop.push(mutate(c2));
        }

        population = newPop;
      }

      const finalRoutes = splitChromosome(bestPerm);
      const finalDemands = finalRoutes.map(r => r.reduce((acc, nid) => acc + (demandMap[nid] || 0), 0));
      const finalDistances = finalRoutes.map(r => {
        let d = 0;
        for (let i = 0; i < r.length - 1; i++) d += distMatrix[r[i]][r[i + 1]];
        return parseFloat(d.toFixed(2));
      });

      const runtime = (performance.now() - startTime) / 1000;

      return {
        routes: finalRoutes,
        route_demands: finalDemands,
        route_distances_km: finalDistances,
        total_distance_km: parseFloat(bestDistOverall.toFixed(2)),
        vehicles_utilized: finalRoutes.length,
        converged_generation: convergedGen,
        runtime_seconds: parseFloat(runtime.toFixed(3)),
        history: {
          generation: histGen,
          best_distance: histBest,
          avg_distance: histAvg
        }
      };
    }

    // Run GA Trigger
    document.getElementById("btn-run-ga").addEventListener("click", () => {
      const popSize = parseInt(document.getElementById("input-pop-size").value);
      const mutRate = parseFloat(document.getElementById("input-mut-rate").value);
      const crRate = parseFloat(document.getElementById("select-cr-rate").value);
      const maxGen = parseInt(document.getElementById("input-generations").value);

      const btn = document.getElementById("btn-run-ga");
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Evolving Routes...';
      btn.disabled = true;

      setTimeout(() => {
        const gaRes = solveClientGA(
          DATA.customers,
          DATA.capacity,
          DATA.fleet_limit,
          DATA.dist_matrix,
          popSize,
          mutRate,
          crRate,
          maxGen
        );

        DATA.ga_best = gaRes;
        currentRoutes = gaRes.routes;
        currentView = "ga";
        currentSolver = "Genetic Algorithm";

        const baseDist = DATA.baseline.total_distance_km;
        const gaDist = gaRes.total_distance_km;
        const savingsDist = baseDist - gaDist;
        const savingsPct = (savingsDist / baseDist) * 100;

        updateMetrics(
          baseDist,
          gaDist,
          gaRes.vehicles_utilized,
          savingsDist,
          savingsPct,
          gaRes.runtime_seconds,
          "Genetic Algorithm (Optimized)",
          gaRes.converged_generation
        );

        renderRouteCards(gaRes.routes, gaRes.route_demands, gaRes.route_distances_km);
        updateTruckSelector();
        updateChart(gaRes.history);
        drawMap();

        btn.innerHTML = '<i class="fa-solid fa-dna"></i> Run Evolutionary Algorithm';
        btn.disabled = false;
        showToast(`Evolution complete! Total distance optimized to ${gaDist} km.`, "success");
      }, 50);
    });

    // ============================================================
    // MODAL & CUSTOM SITES / DIRECT WAREHOUSE DISTANCES LOGIC
    // ============================================================
    const modal = document.getElementById("modal-scenario");
    let tempCustomers = JSON.parse(JSON.stringify(DATA.customers));
    let tempDepot = { ...DATA.depot };

    function openScenarioModal() {
      tempCustomers = JSON.parse(JSON.stringify(DATA.customers));
      tempDepot = { ...DATA.depot };
      document.getElementById("input-depot-x").value = tempDepot.x;
      document.getElementById("input-depot-y").value = tempDepot.y;
      document.getElementById("input-fleet-limit").value = DATA.fleet_limit;
      document.getElementById("input-truck-capacity").value = DATA.capacity;
      document.getElementById("input-num-sites").value = tempCustomers.length;
      renderCustomSitesTable();
      modal.classList.remove("hidden");
    }

    document.getElementById("btn-open-scenario-modal").addEventListener("click", openScenarioModal);
    document.getElementById("btn-quick-config").addEventListener("click", openScenarioModal);
    document.getElementById("btn-close-modal").addEventListener("click", () => modal.classList.add("hidden"));
    document.getElementById("btn-cancel-scenario").addEventListener("click", () => modal.classList.add("hidden"));

    function renderCustomSitesTable() {
      const tbody = document.getElementById("custom-sites-tbody");
      tbody.innerHTML = "";
      const totalDemand = tempCustomers.reduce((acc, c) => acc + c.demand, 0);
      document.getElementById("custom-sites-count").textContent = 
        `${tempCustomers.length} Sites Configured | Total Demand: ${totalDemand} units`;

      tempCustomers.forEach((cust, idx) => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-800/50 transition";
        tr.innerHTML = `
          <td class="p-2.5 font-bold font-mono text-indigo-400">#${cust.id}</td>
          <td class="p-2.5">
            <div class="flex items-center space-x-1">
              <input type="number" step="0.5" min="1" max="150" value="${cust.distToDepot}" 
                     class="inp-warehouse-dist w-28 bg-slate-900 border-2 border-emerald-500 rounded px-2 py-1 text-xs text-emerald-300 font-bold font-mono outline-none focus:border-emerald-400" 
                     data-idx="${idx}">
              <span class="text-emerald-400 font-semibold text-xs">km</span>
            </div>
          </td>
          <td class="p-2.5">
            <div class="flex items-center space-x-1">
              <input type="number" step="1" min="0" max="359" value="${cust.angle}" 
                     class="inp-angle w-16 bg-slate-900 border border-slate-700 rounded px-1.5 py-1 text-xs text-slate-200 font-mono outline-none" 
                     data-idx="${idx}">
              <span class="text-slate-500 text-xs">&deg;</span>
            </div>
          </td>
          <td class="p-2.5">
            <input type="number" step="0.5" min="0" max="100" value="${cust.x.toFixed(1)}" 
                   class="inp-coord-x w-16 bg-slate-900/60 border border-slate-700/80 rounded px-1.5 py-1 text-xs text-slate-300 font-mono outline-none" 
                   data-idx="${idx}">
          </td>
          <td class="p-2.5">
            <input type="number" step="0.5" min="0" max="100" value="${cust.y.toFixed(1)}" 
                   class="inp-coord-y w-16 bg-slate-900/60 border border-slate-700/80 rounded px-1.5 py-1 text-xs text-slate-300 font-mono outline-none" 
                   data-idx="${idx}">
          </td>
          <td class="p-2.5">
            <input type="number" min="1" max="100" value="${cust.demand}" 
                   class="inp-demand w-16 bg-slate-900 border border-slate-700 rounded px-1.5 py-1 text-xs text-white font-mono outline-none" 
                   data-idx="${idx}">
          </td>
          <td class="p-2.5 text-center">
            <button class="btn-del-site text-red-400 hover:text-red-300 transition text-xs p-1" data-idx="${idx}" title="Delete site">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      // 1. PRIMARY: User edits Distance from Warehouse directly
      tbody.querySelectorAll(".inp-warehouse-dist").forEach(inp => {
        inp.addEventListener("input", e => {
          const idx = parseInt(e.target.dataset.idx);
          const newDist = Math.max(1, parseFloat(e.target.value) || 1);
          tempCustomers[idx].distToDepot = newDist;
          
          const rad = tempCustomers[idx].angle * Math.PI / 180;
          tempCustomers[idx].x = parseFloat((tempDepot.x + newDist * Math.cos(rad)).toFixed(1));
          tempCustomers[idx].y = parseFloat((tempDepot.y + newDist * Math.sin(rad)).toFixed(1));

          const tr = e.target.closest("tr");
          tr.querySelector(".inp-coord-x").value = tempCustomers[idx].x.toFixed(1);
          tr.querySelector(".inp-coord-y").value = tempCustomers[idx].y.toFixed(1);
        });
      });

      // 2. User edits Angle directly
      tbody.querySelectorAll(".inp-angle").forEach(inp => {
        inp.addEventListener("input", e => {
          const idx = parseInt(e.target.dataset.idx);
          const newAngle = (parseFloat(e.target.value) || 0) % 360;
          tempCustomers[idx].angle = newAngle;

          const rad = newAngle * Math.PI / 180;
          const dist = tempCustomers[idx].distToDepot;
          tempCustomers[idx].x = parseFloat((tempDepot.x + dist * Math.cos(rad)).toFixed(1));
          tempCustomers[idx].y = parseFloat((tempDepot.y + dist * Math.sin(rad)).toFixed(1));

          const tr = e.target.closest("tr");
          tr.querySelector(".inp-coord-x").value = tempCustomers[idx].x.toFixed(1);
          tr.querySelector(".inp-coord-y").value = tempCustomers[idx].y.toFixed(1);
        });
      });

      // 3. User edits Coordinates directly
      function syncFromCoords(idx, tr) {
        const dx = tempCustomers[idx].x - tempDepot.x;
        const dy = tempCustomers[idx].y - tempDepot.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.round((Math.atan2(dy, dx) * 180 / Math.PI + 360) % 360);
        tempCustomers[idx].distToDepot = parseFloat(dist.toFixed(1));
        tempCustomers[idx].angle = angle;
        tr.querySelector(".inp-warehouse-dist").value = tempCustomers[idx].distToDepot;
        tr.querySelector(".inp-angle").value = angle;
      }

      tbody.querySelectorAll(".inp-coord-x").forEach(inp => {
        inp.addEventListener("input", e => {
          const idx = parseInt(e.target.dataset.idx);
          tempCustomers[idx].x = parseFloat(e.target.value) || 0;
          syncFromCoords(idx, e.target.closest("tr"));
        });
      });

      tbody.querySelectorAll(".inp-coord-y").forEach(inp => {
        inp.addEventListener("input", e => {
          const idx = parseInt(e.target.dataset.idx);
          tempCustomers[idx].y = parseFloat(e.target.value) || 0;
          syncFromCoords(idx, e.target.closest("tr"));
        });
      });

      // 4. User edits Demand
      tbody.querySelectorAll(".inp-demand").forEach(inp => {
        inp.addEventListener("input", e => {
          const idx = parseInt(e.target.dataset.idx);
          tempCustomers[idx].demand = parseInt(e.target.value) || 1;
          const sum = tempCustomers.reduce((acc, c) => acc + c.demand, 0);
          document.getElementById("custom-sites-count").textContent = `${tempCustomers.length} Sites Configured | Total Demand: ${sum} units`;
        });
      });

      // 5. Delete site
      tbody.querySelectorAll(".btn-del-site").forEach(btn => {
        btn.addEventListener("click", e => {
          if (tempCustomers.length <= 3) {
            alert("A minimum of 3 delivery sites is required.");
            return;
          }
          const idx = parseInt(btn.dataset.idx);
          tempCustomers.splice(idx, 1);
          tempCustomers.forEach((c, i) => c.id = i + 1);
          document.getElementById("input-num-sites").value = tempCustomers.length;
          renderCustomSitesTable();
        });
      });
    }

    // Bulk Apply Distances
    document.getElementById("btn-apply-bulk-dist").addEventListener("click", () => {
      const raw = document.getElementById("input-bulk-distances").value.trim();
      if (!raw) return;
      const dists = raw.split(/[,;\s]+/).map(v => parseFloat(v)).filter(v => !isNaN(v) && v > 0);
      if (dists.length === 0) return;

      for (let i = 0; i < tempCustomers.length; i++) {
        const d = dists[i % dists.length];
        tempCustomers[i].distToDepot = parseFloat(d.toFixed(1));
        const rad = tempCustomers[i].angle * Math.PI / 180;
        tempCustomers[i].x = parseFloat((tempDepot.x + d * Math.cos(rad)).toFixed(1));
        tempCustomers[i].y = parseFloat((tempDepot.y + d * Math.sin(rad)).toFixed(1));
      }
      renderCustomSitesTable();
      showToast(`Applied bulk distances to all ${tempCustomers.length} delivery sites.`, "success");
    });

    // Change Site Count
    document.getElementById("btn-update-num-sites").addEventListener("click", () => {
      const targetCount = parseInt(document.getElementById("input-num-sites").value);
      if (targetCount < 3 || targetCount > 60) {
        alert("Please choose between 3 and 60 delivery sites.");
        return;
      }
      while (tempCustomers.length < targetCount) {
        const newId = tempCustomers.length + 1;
        const angle = (newId * 37) % 360;
        const dist = 15.0 + ((newId * 7) % 35);
        const rad = angle * Math.PI / 180;
        tempCustomers.push({
          id: newId,
          distToDepot: parseFloat(dist.toFixed(1)),
          angle: angle,
          x: parseFloat((tempDepot.x + dist * Math.cos(rad)).toFixed(1)),
          y: parseFloat((tempDepot.y + dist * Math.sin(rad)).toFixed(1)),
          demand: 10 + (newId % 16)
        });
      }
      if (tempCustomers.length > targetCount) {
        tempCustomers = tempCustomers.slice(0, targetCount);
      }
      tempCustomers.forEach((c, i) => c.id = i + 1);
      renderCustomSitesTable();
    });

    // Randomize Sites
    document.getElementById("btn-generate-random").addEventListener("click", () => {
      const n = tempCustomers.length;
      tempCustomers = [];
      for (let i = 1; i <= n; i++) {
        const dist = parseFloat((Math.random() * 40 + 8).toFixed(1));
        const angle = Math.floor(Math.random() * 360);
        const rad = angle * Math.PI / 180;
        tempCustomers.push({
          id: i,
          distToDepot: dist,
          angle: angle,
          x: parseFloat((tempDepot.x + dist * Math.cos(rad)).toFixed(1)),
          y: parseFloat((tempDepot.y + dist * Math.sin(rad)).toFixed(1)),
          demand: Math.floor(Math.random() * 16 + 10)
        });
      }
      renderCustomSitesTable();
    });

    // Reset Benchmark
    document.getElementById("btn-reset-benchmark").addEventListener("click", () => {
      tempDepot = { x: 50.0, y: 50.0 };
      tempCustomers = INITIAL_BENCHMARK_DATA.customers.map(c => {
        const dx = c.x - 50.0;
        const dy = c.y - 50.0;
        return {
          id: c.id,
          x: c.x,
          y: c.y,
          distToDepot: parseFloat(Math.sqrt(dx * dx + dy * dy).toFixed(1)),
          angle: Math.round((Math.atan2(dy, dx) * 180 / Math.PI + 360) % 360),
          demand: c.demand
        };
      });
      document.getElementById("input-depot-x").value = 50.0;
      document.getElementById("input-depot-y").value = 50.0;
      document.getElementById("input-fleet-limit").value = 8;
      document.getElementById("input-truck-capacity").value = 100;
      document.getElementById("input-num-sites").value = 35;
      renderCustomSitesTable();
    });

    // Add Single Site
    document.getElementById("btn-add-single-site").addEventListener("click", () => {
      if (tempCustomers.length >= 60) {
        alert("Maximum 60 delivery sites supported in simulation.");
        return;
      }
      const newId = tempCustomers.length + 1;
      const dist = 25.0;
      const angle = (newId * 37) % 360;
      const rad = angle * Math.PI / 180;
      tempCustomers.push({
        id: newId,
        distToDepot: dist,
        angle: angle,
        x: parseFloat((tempDepot.x + dist * Math.cos(rad)).toFixed(1)),
        y: parseFloat((tempDepot.y + dist * Math.sin(rad)).toFixed(1)),
        demand: 15
      });
      document.getElementById("input-num-sites").value = tempCustomers.length;
      renderCustomSitesTable();
    });

    // Apply User Inputs & Recalculate
    document.getElementById("btn-apply-scenario").addEventListener("click", () => {
      DATA.depot = { x: parseFloat(document.getElementById("input-depot-x").value) || 50, y: parseFloat(document.getElementById("input-depot-y").value) || 50 };
      DATA.fleet_limit = parseInt(document.getElementById("input-fleet-limit").value) || 8;
      DATA.capacity = parseInt(document.getElementById("input-truck-capacity").value) || 100;
      DATA.customers = JSON.parse(JSON.stringify(tempCustomers));
      DATA.total_demand = DATA.customers.reduce((acc, c) => acc + c.demand, 0);

      // Recompute Distance Matrix: Exactly respect user-specified distToDepot!
      const numNodes = DATA.customers.length + 1;
      const allNodes = [{ id: 0, x: DATA.depot.x, y: DATA.depot.y }, ...DATA.customers];
      const newDistMatrix = [];

      for (let i = 0; i < numNodes; i++) {
        const row = [];
        for (let j = 0; j < numNodes; j++) {
          if (i === j) {
            row.push(0);
          } else if (i === 0 && j > 0) {
            row.push(DATA.customers[j - 1].distToDepot);
          } else if (j === 0 && i > 0) {
            row.push(DATA.customers[i - 1].distToDepot);
          } else {
            const dx = allNodes[i].x - allNodes[j].x;
            const dy = allNodes[i].y - allNodes[j].y;
            row.push(Math.sqrt(dx * dx + dy * dy));
          }
        }
        newDistMatrix.push(row);
      }
      DATA.dist_matrix = newDistMatrix;

      // Solve baseline NN for this user scenario
      DATA.baseline = solveGreedyNN(DATA.depot, DATA.customers, DATA.capacity, DATA.dist_matrix);
      DATA.ga_best = DATA.baseline;

      // Update Badges
      document.getElementById("badge-sites").innerHTML = `<i class="fa-solid fa-location-dot text-indigo-400 mr-1.5"></i>${DATA.customers.length} Delivery Sites`;
      document.getElementById("badge-depot").innerHTML = `<i class="fa-solid fa-warehouse text-amber-400 mr-1.5"></i>Warehouse (${DATA.depot.x.toFixed(0)}, ${DATA.depot.y.toFixed(0)})`;
      document.getElementById("badge-capacity").innerHTML = `<i class="fa-solid fa-box text-cyan-400 mr-1.5"></i>Capacity Q = ${DATA.capacity}`;
      document.getElementById("badge-trucks").innerHTML = `<i class="fa-solid fa-truck text-emerald-400 mr-1.5"></i>Fleet Limit K = ${DATA.fleet_limit}`;

      currentRoutes = DATA.baseline.routes;
      currentView = "baseline";
      selectedTruck = "all";

      updateMetrics(
        DATA.baseline.total_distance_km,
        DATA.baseline.total_distance_km,
        DATA.baseline.vehicles_utilized,
        0,
        0,
        DATA.baseline.runtime_seconds,
        "User Scenario (Baseline NN)",
        "N/A"
      );

      renderRouteCards(DATA.baseline.routes, DATA.baseline.route_demands, DATA.baseline.route_distances_km);
      updateTruckSelector();
      drawMap();

      modal.classList.add("hidden");
      showToast(`Loaded ${DATA.customers.length} sites with custom warehouse distances!`, "success");
    });

    // ============================================================
    // WORKSPACE SAVE & RESTORE (LOCALSTORAGE + EXPORT JSON + BACKEND)
    // ============================================================
    const saveModal = document.getElementById("modal-save-load");
    document.getElementById("btn-open-save-modal").addEventListener("click", () => {
      const now = new Date();
      const defaultName = `CVRP-Plan-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}`;
      document.getElementById("input-save-name").value = defaultName;
      refreshSavedItemsList();
      saveModal.classList.remove("hidden");
    });

    document.getElementById("btn-close-save-modal").addEventListener("click", () => saveModal.classList.add("hidden"));
    document.getElementById("btn-done-save-modal").addEventListener("click", () => saveModal.classList.add("hidden"));

    function buildWorkspacePayload() {
      const name = document.getElementById("input-save-name").value.trim() || "CVRP-Workspace";
      return {
        scenario_name: name,
        saved_at: new Date().toISOString(),
        depot: DATA.depot,
        customers: DATA.customers,
        capacity: DATA.capacity,
        fleet_limit: DATA.fleet_limit,
        total_demand: DATA.total_demand,
        dist_matrix: DATA.dist_matrix,
        routes: currentRoutes,
        solver: currentSolver,
        baseline: DATA.baseline,
        ga_best: DATA.ga_best,
        history: chartInstance ? {
          generation: chartInstance.data.labels,
          best_distance: chartInstance.data.datasets[0].data,
          avg_distance: chartInstance.data.datasets[1].data
        } : null
      };
    }

    function applyLoadedWorkspace(loaded) {
      if (!loaded || !loaded.customers || !loaded.depot) {
        showToast("Invalid scenario data format.", "error");
        return;
      }
      DATA.depot = loaded.depot;
      DATA.customers = loaded.customers;
      DATA.capacity = loaded.capacity || 100;
      DATA.fleet_limit = loaded.fleet_limit || 8;
      DATA.total_demand = loaded.total_demand || DATA.customers.reduce((a, c) => a + c.demand, 0);
      DATA.dist_matrix = loaded.dist_matrix;
      DATA.baseline = loaded.baseline || solveGreedyNN(DATA.depot, DATA.customers, DATA.capacity, DATA.dist_matrix);
      DATA.ga_best = loaded.ga_best || DATA.baseline;

      currentRoutes = loaded.routes || DATA.ga_best.routes;
      currentSolver = loaded.solver || "Restored Plan";
      currentView = "ga";
      selectedTruck = "all";

      // Badges
      document.getElementById("badge-sites").innerHTML = `<i class="fa-solid fa-location-dot text-indigo-400 mr-1.5"></i>${DATA.customers.length} Delivery Sites`;
      document.getElementById("badge-depot").innerHTML = `<i class="fa-solid fa-warehouse text-amber-400 mr-1.5"></i>Warehouse (${DATA.depot.x.toFixed(0)}, ${DATA.depot.y.toFixed(0)})`;
      document.getElementById("badge-capacity").innerHTML = `<i class="fa-solid fa-box text-cyan-400 mr-1.5"></i>Capacity Q = ${DATA.capacity}`;
      document.getElementById("badge-trucks").innerHTML = `<i class="fa-solid fa-truck text-emerald-400 mr-1.5"></i>Fleet Limit K = ${DATA.fleet_limit}`;

      const baseDist = DATA.baseline.total_distance_km;
      const curDist = DATA.ga_best.total_distance_km || baseDist;
      const savDist = baseDist - curDist;
      const savPct = baseDist > 0 ? (savDist / baseDist) * 100 : 0;

      updateMetrics(
        baseDist,
        curDist,
        currentRoutes.length,
        savDist,
        savPct,
        DATA.ga_best.runtime_seconds || 0,
        currentSolver,
        DATA.ga_best.converged_generation || "N/A"
      );

      const demands = currentRoutes.map(r => r.reduce((a, nid) => {
        const c = DATA.customers.find(item => item.id === nid);
        return a + (c ? c.demand : 0);
      }, 0));

      const distances = currentRoutes.map(r => {
        let d = 0;
        for (let i = 0; i < r.length - 1; i++) d += DATA.dist_matrix[r[i]][r[i + 1]];
        return parseFloat(d.toFixed(2));
      });

      renderRouteCards(currentRoutes, demands, distances);
      updateTruckSelector();
      if (loaded.history) updateChart(loaded.history);
      drawMap();

      saveModal.classList.add("hidden");
      showToast(`Successfully restored workspace "${loaded.scenario_name || 'Plan'}"!`, "success");
    }

    // 1. Export JSON File to PC
    document.getElementById("btn-action-export-json").addEventListener("click", () => {
      const payload = buildWorkspacePayload();
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${payload.scenario_name}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("Workspace exported as JSON file!", "success");
    });

    // 2. Save to Browser LocalStorage
    document.getElementById("btn-action-save-browser").addEventListener("click", () => {
      const payload = buildWorkspacePayload();
      const key = "cvrp_workspaces";
      let list = [];
      try {
        list = JSON.parse(localStorage.getItem(key)) || [];
      } catch(e) { list = []; }
      
      list = list.filter(item => item.scenario_name !== payload.scenario_name);
      list.unshift(payload);
      if (list.length > 15) list = list.slice(0, 15);
      localStorage.setItem(key, JSON.stringify(list));

      refreshSavedItemsList();
      showToast(`Saved "${payload.scenario_name}" to browser storage!`, "success");
    });

    // 3. Save to Backend Server Disk
    document.getElementById("btn-action-save-backend").addEventListener("click", async () => {
      const payload = buildWorkspacePayload();
      const btn = document.getElementById("btn-action-save-backend");
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving to Server...';

      try {
        const resp = await fetch("/api/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.status === "success") {
          showToast(res.message, "success");
          refreshSavedItemsList();
        } else {
          showToast(res.message || "Server save failed.", "error");
        }
      } catch (err) {
        showToast("Backend server offline (saved to browser instead).", "info");
        document.getElementById("btn-action-save-browser").click();
      } finally {
        btn.innerHTML = '<i class="fa-solid fa-server"></i> Save to Backend Disk';
      }
    });

    // Import from JSON File
    const fileInput = document.getElementById("file-import-input");
    document.getElementById("btn-trigger-file-import").addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", e => {
      const file = e.target.files[0];
      if (!file) return;
      document.getElementById("file-import-status").textContent = file.name;
      const reader = new FileReader();
      reader.onload = ev => {
        try {
          const parsed = JSON.parse(ev.target.result);
          applyLoadedWorkspace(parsed);
        } catch (err) {
          showToast("Failed to parse JSON file.", "error");
        }
      };
      reader.readAsText(file);
    });

    // Refresh Saved Items List
    async function refreshSavedItemsList() {
      const tbody = document.getElementById("saved-items-tbody");
      tbody.innerHTML = "";

      let browserItems = [];
      try {
        browserItems = JSON.parse(localStorage.getItem("cvrp_workspaces")) || [];
      } catch(e) { browserItems = []; }

      let backendItems = [];
      try {
        const resp = await fetch("/api/saved-items");
        if (resp.ok) {
          const res = await resp.json();
          if (res.status === "success") backendItems = res.items || [];
        }
      } catch(e) {}

      if (browserItems.length === 0 && backendItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="p-3 text-center text-slate-500 italic">No saved workspaces found. Save one above!</td></tr>';
        return;
      }

      // Render Browser Items
      browserItems.forEach((item, bIdx) => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-800/50 transition";
        const dateStr = item.saved_at ? new Date(item.saved_at).toLocaleDateString() + " " + new Date(item.saved_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : "Recent";
        const dist = item.ga_best ? item.ga_best.total_distance_km : (item.baseline ? item.baseline.total_distance_km : "N/A");
        tr.innerHTML = `
          <td class="p-2 font-bold text-white font-mono">${item.scenario_name}</td>
          <td class="p-2"><span class="bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded text-[10px]">Browser Cache</span></td>
          <td class="p-2">${item.customers.length} sites</td>
          <td class="p-2 text-emerald-400 font-mono">${dist} km</td>
          <td class="p-2 text-slate-400 text-[10px]">${dateStr}</td>
          <td class="p-2 text-center space-x-1">
            <button class="btn-load-browser bg-emerald-600/30 hover:bg-emerald-600 text-emerald-300 hover:text-white px-2 py-1 rounded text-[11px] transition cursor-pointer" data-idx="${bIdx}">
              Load
            </button>
            <button class="btn-del-browser text-red-400 hover:text-red-300 p-1 text-[11px] transition cursor-pointer" data-idx="${bIdx}">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      // Render Backend Items
      backendItems.forEach(item => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-800/50 transition";
        const dateStr = item.saved_at ? new Date(item.saved_at).toLocaleDateString() + " " + new Date(item.saved_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : "Server";
        tr.innerHTML = `
          <td class="p-2 font-bold text-white font-mono">${item.scenario_name}</td>
          <td class="p-2"><span class="bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 px-2 py-0.5 rounded text-[10px]">Server Disk</span></td>
          <td class="p-2">${item.num_sites} sites</td>
          <td class="p-2 text-emerald-400 font-mono">${item.total_distance} km</td>
          <td class="p-2 text-slate-400 text-[10px]">${dateStr}</td>
          <td class="p-2 text-center space-x-1">
            <button class="btn-load-backend bg-cyan-600/30 hover:bg-cyan-600 text-cyan-300 hover:text-white px-2 py-1 rounded text-[11px] transition cursor-pointer" data-filename="${item.filename}">
              Load
            </button>
            <button class="btn-del-backend text-red-400 hover:text-red-300 p-1 text-[11px] transition cursor-pointer" data-filename="${item.filename}">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      // Attach Listeners
      tbody.querySelectorAll(".btn-load-browser").forEach(btn => {
        btn.addEventListener("click", () => {
          const idx = parseInt(btn.dataset.idx);
          applyLoadedWorkspace(browserItems[idx]);
        });
      });

      tbody.querySelectorAll(".btn-del-browser").forEach(btn => {
        btn.addEventListener("click", () => {
          const idx = parseInt(btn.dataset.idx);
          browserItems.splice(idx, 1);
          localStorage.setItem("cvrp_workspaces", JSON.stringify(browserItems));
          refreshSavedItemsList();
        });
      });

      tbody.querySelectorAll(".btn-load-backend").forEach(btn => {
        btn.addEventListener("click", async () => {
          const fn = btn.dataset.filename;
          try {
            const resp = await fetch(`/api/load/${fn}`);
            const res = await resp.json();
            if (res.status === "success") {
              applyLoadedWorkspace(res.data);
            } else {
              showToast(res.message, "error");
            }
          } catch(e) {
            showToast("Failed to load from server.", "error");
          }
        });
      });

      tbody.querySelectorAll(".btn-del-backend").forEach(btn => {
        btn.addEventListener("click", async () => {
          const fn = btn.dataset.filename;
          try {
            const resp = await fetch(`/api/delete/${fn}`, { method: "POST" });
            const res = await resp.json();
            if (res.status === "success") {
              refreshSavedItemsList();
              showToast("Scenario deleted from server.", "success");
            }
          } catch(e) {}
        });
      });
    }

    document.getElementById("btn-refresh-saved-list").addEventListener("click", refreshSavedItemsList);

    // Initial Load
    function loadGlobalBest() {
      const base = DATA.baseline;
      const ga = DATA.ga_best;
      const savDist = base.total_distance_km - ga.total_distance_km;
      const savPct = (savDist / base.total_distance_km) * 100;

      updateMetrics(
        base.total_distance_km,
        ga.total_distance_km,
        ga.vehicles_utilized,
        savDist,
        savPct,
        ga.runtime_seconds,
        "Optimal Discovered Solution",
        ga.converged_generation
      );

      renderRouteCards(ga.routes, ga.route_demands, ga.route_distances_km);
      updateTruckSelector();
      updateChart(ga.history);
      animate();
    }

    window.addEventListener("load", () => {
      initChart();
      loadGlobalBest();
    });
  </script>
</body>
</html>
"""

final_html = html_template.replace("__DATA_PLACEHOLDER__", data_str)

with open(root / "index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

with open(root / "templates" / "index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("index.html compiled successfully with Zoom/Pan controls, Save/Load workspace, and user warehouse distances!")
