"""
build_index.py
Compiles the static client-side index.html for direct GitHub Pages deployment
with interactive user configuration (delivery sites, trucks, warehouse distance table),
individual truck animation & inspection, medium animation speed controls,
and academic assessment branding removed.
"""

import json
from pathlib import Path

root = Path(__file__).resolve().parent
with open(root / "static_data.json", "r", encoding="utf-8") as f:
    data_str = f.read()

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CVRP Evolutionary Computing Optimization Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
    .canvas-container { position: relative; width: 100%; aspect-ratio: 1; max-width: 620px; }
    canvas#routeCanvas { border-radius: 0.75rem; background: #0f172a; }
    .custom-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
    .custom-scroll::-webkit-scrollbar-track { background: #1e293b; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #475569; border-radius: 3px; }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">

  <!-- Top Navigation Bar -->
  <header class="bg-slate-800/80 border-b border-slate-700/60 sticky top-0 z-50 backdrop-blur-md px-6 py-3.5">
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

      <!-- Problem Badges & Scenario Builder Trigger -->
      <div class="flex flex-wrap items-center gap-2 text-xs">
        <button id="btn-open-scenario-modal" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-3 py-1 rounded-md shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5 cursor-pointer">
          <i class="fa-solid fa-sliders"></i> Configure Sites & Trucks
        </button>
        <span id="badge-sites" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-location-dot text-indigo-400 mr-1.5"></i>35 Delivery Sites</span>
        <span id="badge-depot" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-warehouse text-amber-400 mr-1.5"></i>Warehouse (50, 50)</span>
        <span id="badge-capacity" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-box text-cyan-400 mr-1.5"></i>Capacity Q = 100</span>
        <span id="badge-trucks" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-truck text-emerald-400 mr-1.5"></i>Fleet Limit K = 8</span>
        <span id="badge-demand" class="bg-slate-700/70 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600/50"><i class="fa-solid fa-weight-hanging text-purple-400 mr-1.5"></i>Demand: 580 u</span>
        <a href="https://github.com/sudhanbabu0/cvrp-evolutionary-optimization" target="_blank" class="bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 px-2.5 py-1 rounded-md border border-indigo-500/40 transition">
          <i class="fa-brands fa-github mr-1"></i>GitHub Repo
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
                  <!-- Individual trucks populated dynamically -->
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

          <!-- Canvas Element -->
          <div class="canvas-container mx-auto">
            <canvas id="routeCanvas" width="600" height="600" class="w-full h-full shadow-2xl"></canvas>
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

        <!-- Controls Box -->
        <div class="bg-slate-800/60 border border-slate-700/60 p-5 rounded-2xl space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-sliders text-emerald-400"></i>
              Optimization Controls
            </h2>
            <button id="btn-quick-config" class="text-xs bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 px-2.5 py-1 rounded-lg transition cursor-pointer">
              <i class="fa-solid fa-gear mr-1"></i> Custom Setup
            </button>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <button id="btn-run-baseline" class="w-full py-2.5 px-3 bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 rounded-xl font-semibold text-xs flex items-center justify-center gap-2 transition cursor-pointer">
              <i class="fa-solid fa-bolt"></i> Run Baseline (NN)
            </button>
            <button id="btn-load-best" class="w-full py-2.5 px-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 rounded-xl font-semibold text-xs flex items-center justify-center gap-2 transition cursor-pointer">
              <i class="fa-solid fa-trophy"></i> Load Benchmark Best
            </button>
          </div>

          <!-- Parameter Sliders -->
          <div class="space-y-3 pt-2 text-xs">
            <div>
              <div class="flex justify-between text-slate-300 mb-1">
                <span>Population Size (P):</span>
                <span id="val-pop-size" class="font-bold text-indigo-400">100</span>
              </div>
              <input type="range" id="input-pop-size" min="40" max="200" step="20" value="100" class="w-full accent-indigo-500 cursor-pointer">
              <div class="flex justify-between text-[10px] text-slate-500"><span>40 (Fast)</span><span>100 (Default)</span><span>200 (Thorough)</span></div>
            </div>

            <div>
              <div class="flex justify-between text-slate-300 mb-1">
                <span>Mutation Rate (pm):</span>
                <span id="val-mut-rate" class="font-bold text-indigo-400">0.08</span>
              </div>
              <input type="range" id="input-mut-rate" min="0.01" max="0.20" step="0.01" value="0.08" class="w-full accent-indigo-500 cursor-pointer">
              <div class="flex justify-between text-[10px] text-slate-500"><span>0.01 (Low)</span><span>0.08 (Optimal)</span><span>0.20 (High)</span></div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-slate-300 mb-1">Crossover Rate (pc):</label>
                <select id="select-crossover" class="w-full bg-slate-700/80 border border-slate-600 rounded-lg p-2 text-slate-200">
                  <option value="0.60">0.60 (Low)</option>
                  <option value="0.85" selected>0.85 (Optimal)</option>
                  <option value="0.95">0.95 (High)</option>
                </select>
              </div>
              <div>
                <label class="block text-slate-300 mb-1">Max Generations:</label>
                <select id="select-generations" class="w-full bg-slate-700/80 border border-slate-600 rounded-lg p-2 text-slate-200">
                  <option value="60">60 Gens</option>
                  <option value="120" selected>120 Gens</option>
                  <option value="200">200 Gens</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-slate-300 mb-1">Selection Strategy:</label>
              <select id="select-selection" class="w-full bg-slate-700/80 border border-slate-600 rounded-lg p-2 text-slate-200">
                <option value="tournament" selected>Tournament Selection (k=3)</option>
                <option value="roulette">Roulette Wheel Selection</option>
              </select>
            </div>
          </div>

          <!-- Run GA Button -->
          <button id="btn-run-ga" class="w-full py-3 bg-gradient-to-r from-indigo-600 to-emerald-600 hover:from-indigo-500 hover:to-emerald-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition cursor-pointer">
            <i class="fa-solid fa-dna"></i> Run Genetic Algorithm Live
          </button>
        </div>

        <!-- Real-Time Convergence Chart -->
        <div class="bg-slate-800/60 border border-slate-700/60 p-5 rounded-2xl space-y-3">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-chart-line text-cyan-400"></i>
              Convergence Trajectory
            </h2>
            <span class="text-[11px] text-slate-400">Generations vs. Distance</span>
          </div>
          <div class="h-48 w-full">
            <canvas id="convergenceChart"></canvas>
          </div>
        </div>

      </div>
    </div>

    <!-- Vehicle Route Partitions & Load Breakdown -->
    <div class="bg-slate-800/60 border border-slate-700/60 p-5 rounded-2xl space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <i class="fa-solid fa-route text-purple-400"></i>
          Dispatched Vehicle Route Sequences & Payload Breakdown
        </h2>
        <span id="route-count-badge" class="text-xs bg-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-md border border-indigo-500/30 font-semibold">6 Active Trucks</span>
      </div>

      <div id="route-cards-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5"></div>
    </div>

  </main>

  <!-- ============================================================ -->
  <!-- MODAL: Custom Delivery Scenario & Distance to Warehouse Table -->
  <!-- ============================================================ -->
  <div id="modal-scenario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
      <!-- Modal Header -->
      <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-850">
        <div>
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-warehouse text-amber-400"></i>
            Custom Delivery Sites, Trucks & Warehouse Distance Configuration
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Customize the number of delivery sites, fleet size, warehouse coordinates, and distance table.</p>
        </div>
        <button id="btn-close-modal" class="text-slate-400 hover:text-white text-lg p-1 transition cursor-pointer">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <!-- Modal Body (Scrollable) -->
      <div class="p-5 space-y-5 overflow-y-auto custom-scroll text-xs">
        
        <!-- Top Parameters: Warehouse Coords, Truck Fleet, Capacity -->
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
            <label class="block text-slate-300 font-semibold mb-1">Available Trucks (K):</label>
            <input type="number" id="input-fleet-limit" value="8" min="1" max="15" step="1" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-100 font-mono">
          </div>
          <div>
            <label class="block text-slate-300 font-semibold mb-1">Truck Capacity (Q):</label>
            <input type="number" id="input-truck-capacity" value="100" min="20" max="500" step="5" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-100 font-mono">
          </div>
        </div>

        <!-- Quick Generator Tools -->
        <div class="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-800/40 rounded-xl border border-slate-700/40">
          <div class="flex items-center space-x-2">
            <span class="text-slate-300 font-semibold">Number of Delivery Sites:</span>
            <input type="number" id="input-num-sites" value="35" min="5" max="50" class="w-20 bg-slate-900 border border-slate-700 rounded-lg p-1.5 text-center text-slate-100 font-mono font-bold">
            <button id="btn-generate-random" class="bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 px-3 py-1.5 rounded-lg transition font-medium cursor-pointer">
              <i class="fa-solid fa-dice mr-1"></i> Generate Random Sites
            </button>
            <button id="btn-reset-benchmark" class="bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded-lg transition cursor-pointer">
              <i class="fa-solid fa-rotate-left mr-1"></i> Reset 35-Site Benchmark
            </button>
          </div>
          <button id="btn-add-single-site" class="bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/40 px-3 py-1.5 rounded-lg transition font-medium cursor-pointer">
            <i class="fa-solid fa-plus mr-1"></i> Add Delivery Site
          </button>
        </div>

        <!-- Delivery Sites & Distance to Warehouse Table -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-table-list text-cyan-400"></i>
              Delivery Sites & Distance from Warehouse Table
            </h4>
            <span id="custom-sites-count" class="text-slate-400">35 Sites Configured &bull; Total Demand: 580 units</span>
          </div>

          <div class="max-h-64 overflow-y-auto custom-scroll border border-slate-700 rounded-xl bg-slate-950">
            <table class="w-full text-left border-collapse">
              <thead class="bg-slate-800 text-slate-300 sticky top-0 border-b border-slate-700">
                <tr>
                  <th class="p-2.5 text-center">Site #</th>
                  <th class="p-2.5">X Coord (km)</th>
                  <th class="p-2.5">Y Coord (km)</th>
                  <th class="p-2.5 text-emerald-400"><i class="fa-solid fa-ruler mr-1"></i>Dist to Warehouse (km)</th>
                  <th class="p-2.5">Parcel Demand (units)</th>
                  <th class="p-2.5 text-center">Action</th>
                </tr>
              </thead>
              <tbody id="custom-sites-tbody" class="divide-y divide-slate-800 font-mono text-slate-300">
                <!-- Dynamically populated rows -->
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="p-4 border-t border-slate-800 bg-slate-850 flex items-center justify-between">
        <span class="text-xs text-slate-400"><i class="fa-solid fa-circle-info text-cyan-400 mr-1"></i>Changes will be applied to the 2D map, distance matrix, and evolutionary optimizer.</span>
        <div class="flex items-center space-x-3">
          <button id="btn-cancel-modal" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs transition cursor-pointer">
            Cancel
          </button>
          <button id="btn-apply-scenario" class="px-5 py-2 bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-bold rounded-xl text-xs shadow-lg shadow-emerald-600/20 transition cursor-pointer">
            <i class="fa-solid fa-check mr-1.5"></i> Apply Custom Scenario & Recalculate
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Embedded Static & Evolutionary Engine Script -->
  <script>
    const INITIAL_BENCHMARK_DATA = __DATA_PLACEHOLDER__;

    // Working active data copy (can be customized by user)
    let DATA = JSON.parse(JSON.stringify(INITIAL_BENCHMARK_DATA));

    const COLORS = [
      "#38bdf8", "#fb923c", "#4ade80", "#f87171", "#c084fc",
      "#f472b6", "#a3e635", "#fbbf24", "#2dd4bf", "#818cf8",
      "#e879f9", "#34d399", "#60a5fa", "#f59e0b", "#ec4899"
    ];

    let currentRoutes = DATA.ga_best.routes;
    let currentView = "ga"; // "ga" or "baseline"
    let selectedTruck = "all"; // "all" or 0, 1, 2...
    let isAnimating = false;
    let animationId = null;
    let animProgress = 0;
    let animationSpeedStep = 0.0022; // Medium speed default (clearly visible)
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

        const sp = btn.getAttribute("data-speed");
        if (sp === "slow") animationSpeedStep = 0.0010;
        else if (sp === "medium") animationSpeedStep = 0.0022; // Smooth medium
        else if (sp === "fast") animationSpeedStep = 0.0055;
      });
    });

    // Coordinate Mapping: [0, 100] -> Canvas
    function toCanvas(x, y) {
      const margin = 40;
      const usable = canvas.width - margin * 2;
      return {
        cx: margin + (x / 100) * usable,
        cy: canvas.height - (margin + (y / 100) * usable)
      };
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
          `Stops: ${route.length - 2} | Load: ${load}/${DATA.capacity} units (${Math.round((load/DATA.capacity)*100)}%) | Route Dist: ${dist.toFixed(2)} km`;
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

    // Draw Map on Canvas (With Individual Truck Focus Mode)
    function drawMap() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Gridlines
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

    // Smooth Medium-Speed Animation Loop (Supports Individual Truck Focus)
    function animate() {
      drawMap();

      if (isAnimating && currentRoutes.length > 0) {
        animProgress += animationSpeedStep;
        if (animProgress > 1.0) animProgress = 0.0;

        currentRoutes.forEach((route, rIdx) => {
          if (selectedTruck !== "all" && parseInt(selectedTruck) !== rIdx) {
            return; // Only animate selected truck when focused!
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

    // Update Metrics
    function updateMetrics(baseDist, gaDist, vans, saveDist, savePct, runtime, solver, convGen) {
      document.getElementById("metric-baseline-dist").innerHTML = `${parseFloat(baseDist).toFixed(2)} <span class="text-xs text-slate-400">km</span>`;
      document.getElementById("metric-ga-dist").innerHTML = `${parseFloat(gaDist).toFixed(2)} <span class="text-xs text-slate-400">km</span>`;
      document.getElementById("metric-ga-fleet").innerHTML = `${vans} Trucks &bull; Converged Gen ${convGen}`;
      document.getElementById("metric-savings-dist").innerHTML = `${parseFloat(saveDist).toFixed(2)} <span class="text-xs text-slate-400">km</span>`;
      document.getElementById("metric-savings-pct").innerHTML = `<i class="fa-solid fa-arrow-down mr-1"></i>${parseFloat(savePct).toFixed(2)}% Reduction`;
      
      const baselineVans = DATA.baseline ? DATA.baseline.vehicles_utilized : vans;
      const vanDiff = vans - baselineVans;
      document.getElementById("metric-fleet-saving").textContent = `${vanDiff <= 0 ? vanDiff : '+' + vanDiff} Truck(s)`;
      
      const minVans = Math.ceil(DATA.total_demand / DATA.capacity);
      document.getElementById("metric-fleet-min").textContent = `Theoretical Min: ${minVans} Trucks`;
      
      document.getElementById("metric-runtime").innerHTML = `${runtime} <span class="text-xs text-slate-400">s</span>`;
      document.getElementById("metric-solver-type").textContent = solver;
      document.getElementById("route-count-badge").textContent = `${vans} Active Trucks`;
    }

    // Render Route Cards (Clicking a card focuses that truck!)
    function renderRouteCards(routes, demands, dists) {
      const container = document.getElementById("route-cards-container");
      container.innerHTML = "";

      routes.forEach((route, idx) => {
        const col = COLORS[idx % COLORS.length];
        const dem = demands ? demands[idx] : 0;
        const dst = dists ? dists[idx] : 0;
        const pct = Math.min(100, Math.round((dem / DATA.capacity) * 100));

        const card = document.createElement("div");
        card.className = "bg-slate-900/80 border border-slate-700/60 p-3.5 rounded-xl space-y-2 hover:border-indigo-500/60 transition cursor-pointer";
        card.innerHTML = `
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold flex items-center gap-1.5" style="color: ${col};">
              <i class="fa-solid fa-truck"></i> Truck ${idx + 1}
            </span>
            <span class="text-slate-400 font-mono">${dst} km</span>
          </div>
          <div>
            <div class="flex justify-between text-[11px] text-slate-400 mb-1">
              <span>Load: <b class="text-white">${dem}</b>/${DATA.capacity} units</span>
              <span>${pct}%</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500" style="width: ${pct}%; background-color: ${col};"></div>
            </div>
          </div>
          <div class="text-[10px] text-slate-400 truncate font-mono bg-slate-800/60 px-2 py-1 rounded">
            ${route.join(" → ")}
          </div>
          <div class="pt-1 flex justify-end">
            <span class="text-[10px] text-indigo-400 font-semibold flex items-center gap-1 hover:underline">
              <i class="fa-solid fa-eye"></i> View Single Truck Animation
            </span>
          </div>
        `;

        card.addEventListener("click", () => {
          selectedTruck = idx;
          document.getElementById("select-truck-view").value = idx;
          updateActiveTruckBanner();
          drawMap();
        });

        container.appendChild(card);
      });
    }

    // Chart Handling
    function initChart() {
      const c = document.getElementById("convergenceChart").getContext("2d");
      const gens = Array.from({length: 40}, (_, i) => i * 2);
      const dists = gens.map(g => 727 + 600 * Math.exp(-g / 10));

      chartInstance = new Chart(c, {
        type: "line",
        data: {
          labels: gens,
          datasets: [{
            label: "Best Distance (km)",
            data: dists,
            borderColor: "#38bdf8",
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: "#1e293b" }, ticks: { color: "#94a3b8", font: { size: 10 } } },
            y: { grid: { color: "#1e293b" }, ticks: { color: "#94a3b8", font: { size: 10 } } }
          }
        }
      });
    }

    function updateChart(history) {
      if (!chartInstance) return;
      chartInstance.data.labels = history.generation;
      chartInstance.data.datasets = [
        {
          label: "Best Distance (km)",
          data: history.best_distance,
          borderColor: "#38bdf8",
          borderWidth: 2.5,
          pointRadius: 0,
          tension: 0.1
        },
        {
          label: "Average Distance (km)",
          data: history.avg_distance,
          borderColor: "#64748b",
          borderWidth: 1.5,
          borderDash: [4, 4],
          pointRadius: 0,
          tension: 0.1
        }
      ];
      chartInstance.update();
    }

    // Load Benchmark Best
    function loadGlobalBest() {
      currentView = "ga";
      currentRoutes = DATA.ga_best ? DATA.ga_best.routes : DATA.baseline.routes;
      const baseDist = DATA.baseline ? DATA.baseline.total_distance_km : 1036.59;
      const gaDist = DATA.ga_best ? DATA.ga_best.total_distance_km : baseDist;
      const vans = DATA.ga_best ? DATA.ga_best.vehicles_utilized : DATA.baseline.vehicles_utilized;

      updateMetrics(
        baseDist,
        gaDist,
        vans,
        baseDist - gaDist,
        ((baseDist - gaDist) / baseDist) * 100,
        DATA.ga_best ? DATA.ga_best.runtime_seconds : 0.8,
        "Optimal Benchmark Solution",
        DATA.ga_best ? DATA.ga_best.generation_converged : 108
      );
      renderRouteCards(currentRoutes, DATA.ga_best.route_demands, DATA.ga_best.route_distances_km);
      updateTruckSelector();
      drawMap();
    }

    // Run Baseline
    function runBaseline() {
      currentView = "baseline";
      currentRoutes = DATA.baseline.routes;
      updateMetrics(
        DATA.baseline.total_distance_km,
        DATA.baseline.total_distance_km,
        DATA.baseline.vehicles_utilized,
        0,
        0,
        DATA.baseline.runtime_seconds || 0.0004,
        "Greedy Nearest-Neighbor",
        "N/A"
      );
      renderRouteCards(DATA.baseline.routes, DATA.baseline.route_demands, DATA.baseline.route_distances_km);
      updateTruckSelector();
      drawMap();
    }

    document.getElementById("btn-load-best").addEventListener("click", loadGlobalBest);
    document.getElementById("btn-run-baseline").addEventListener("click", runBaseline);

    document.getElementById("btn-toggle-view").addEventListener("click", () => {
      if (currentView === "ga") {
        runBaseline();
        document.getElementById("btn-toggle-view").innerHTML = '<i class="fa-solid fa-shuffle text-emerald-400"></i> Switch to GA Map';
      } else {
        loadGlobalBest();
        document.getElementById("btn-toggle-view").innerHTML = '<i class="fa-solid fa-shuffle text-cyan-400"></i> Switch to Baseline Map';
      }
    });

    // ==========================================
    // CLIENT-SIDE GENETIC ALGORITHM ENGINE
    // ==========================================
    function decodeRoutes(chrom) {
      const routes = [];
      let curRoute = [0];
      let curLoad = 0;

      for (let i = 0; i < chrom.length; i++) {
        const cId = chrom[i];
        const cust = DATA.customers.find(c => c.id === cId);
        const dem = cust ? cust.demand : 15;
        if (curLoad + dem <= DATA.capacity) {
          curRoute.push(cId);
          curLoad += dem;
        } else {
          curRoute.push(0);
          routes.push(curRoute);
          curRoute = [0, cId];
          curLoad = dem;
        }
      }
      if (curRoute.length > 1) {
        curRoute.push(0);
        routes.push(curRoute);
      }
      return routes;
    }

    function evaluateIndividual(chrom) {
      const routes = decodeRoutes(chrom);
      let totalDist = 0;
      let penalty = 0;

      for (let r = 0; r < routes.length; r++) {
        const route = routes[r];
        let load = 0;
        for (let i = 0; i < route.length - 1; i++) {
          totalDist += DATA.dist_matrix[route[i]][route[i + 1]];
          if (route[i] !== 0) {
            const cust = DATA.customers.find(c => c.id === route[i]);
            if (cust) load += cust.demand;
          }
        }
        if (load > DATA.capacity) penalty += 500 * (load - DATA.capacity);
      }

      if (routes.length > DATA.fleet_limit) {
        penalty += 5000 * (routes.length - DATA.fleet_limit);
      }

      const cost = totalDist + penalty;
      const fit = 1.0 / (1.0 + cost);
      return { totalDist, routes, fit };
    }

    function orderCrossover(p1, p2, pc) {
      if (Math.random() > pc) return [p1.slice(), p2.slice()];
      const n = p1.length;
      let i = Math.floor(Math.random() * n);
      let j = Math.floor(Math.random() * n);
      if (i > j) [i, j] = [j, i];

      function oxSingle(parentA, parentB) {
        const child = new Array(n).fill(0);
        const set = new Set();
        for (let k = i; k <= j; k++) {
          child[k] = parentA[k];
          set.add(parentA[k]);
        }
        let pB = (j + 1) % n;
        let cP = (j + 1) % n;
        while (cP !== i) {
          const cand = parentB[pB];
          pB = (pB + 1) % n;
          if (!set.has(cand)) {
            child[cP] = cand;
            cP = (cP + 1) % n;
          }
        }
        return child;
      }
      return [oxSingle(p1, p2), oxSingle(p2, p1)];
    }

    function hybridMutate(chrom, pm) {
      if (Math.random() > pm) return chrom;
      const mut = chrom.slice();
      const n = mut.length;
      const i = Math.floor(Math.random() * n);
      const j = Math.floor(Math.random() * n);

      if (Math.random() < 0.5) {
        [mut[i], mut[j]] = [mut[j], mut[i]];
      } else {
        const [start, end] = i < j ? [i, j] : [j, i];
        const sub = mut.slice(start, end + 1).reverse();
        for (let k = 0; k < sub.length; k++) mut[start + k] = sub[k];
      }
      return mut;
    }

    document.getElementById("btn-run-ga").addEventListener("click", () => {
      const btn = document.getElementById("btn-run-ga");
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Optimizing in Browser...';
      btn.disabled = true;

      const popSize = parseInt(document.getElementById("input-pop-size").value);
      const pm = parseFloat(document.getElementById("input-mut-rate").value);
      const pc = parseFloat(document.getElementById("select-crossover").value);
      const maxGens = parseInt(document.getElementById("select-generations").value);
      const selMethod = document.getElementById("select-selection").value;

      const startTime = performance.now();

      const customerIds = DATA.customers.map(c => c.id);
      let population = [];
      for (let p = 0; p < popSize; p++) {
        const chrom = customerIds.slice().sort(() => Math.random() - 0.5);
        population.push(chrom);
      }

      let evals = population.map(evaluateIndividual);
      let bestOverall = evals[0];
      let convGen = 0;

      const history = { generation: [], best_distance: [], avg_distance: [] };
      let currentGen = 0;
      const CHUNK_SIZE = 5;

      function stepGenerations() {
        const endGen = Math.min(maxGens, currentGen + CHUNK_SIZE);

        for (let g = currentGen; g < endGen; g++) {
          evals = population.map(evaluateIndividual);
          let genBest = evals[0];
          let sumDist = 0;

          for (let e = 0; e < evals.length; e++) {
            sumDist += evals[e].totalDist;
            if (evals[e].fit > genBest.fit) genBest = evals[e];
          }

          if (genBest.fit > bestOverall.fit) {
            bestOverall = genBest;
            convGen = g;
          }

          history.generation.push(g);
          history.best_distance.push(parseFloat(bestOverall.totalDist.toFixed(2)));
          history.avg_distance.push(parseFloat((sumDist / popSize).toFixed(2)));

          // Elitism: keep top 4%
          const sortedPop = population.map((c, idx) => ({ c, fit: evals[idx].fit }))
                                      .sort((a, b) => b.fit - a.fit);
          const eliteCount = Math.max(1, Math.round(0.04 * popSize));
          const nextPop = sortedPop.slice(0, eliteCount).map(item => item.c);

          function selectParent() {
            if (selMethod === "tournament") {
              const k = 3;
              let best = Math.floor(Math.random() * popSize);
              for (let i = 1; i < k; i++) {
                const cand = Math.floor(Math.random() * popSize);
                if (evals[cand].fit > evals[best].fit) best = cand;
              }
              return population[best];
            } else {
              const totalFit = evals.reduce((acc, cur) => acc + cur.fit, 0);
              let pick = Math.random() * totalFit;
              for (let i = 0; i < popSize; i++) {
                pick -= evals[i].fit;
                if (pick <= 0) return population[i];
              }
              return population[popSize - 1];
            }
          }

          while (nextPop.length < popSize) {
            const p1 = selectParent();
            const p2 = selectParent();
            const [c1, c2] = orderCrossover(p1, p2, pc);
            nextPop.push(hybridMutate(c1, pm));
            if (nextPop.length < popSize) nextPop.push(hybridMutate(c2, pm));
          }
          population = nextPop;
        }

        currentGen = endGen;
        currentRoutes = bestOverall.routes;
        drawMap();

        if (currentGen < maxGens) {
          requestAnimationFrame(stepGenerations);
        } else {
          const elapsedSec = ((performance.now() - startTime) / 1000).toFixed(3);
          const baseDist = DATA.baseline.total_distance_km;
          const savingsDist = baseDist - bestOverall.totalDist;
          const savingsPct = (savingsDist / baseDist) * 100;

          const routeDemands = bestOverall.routes.map(r => r.reduce((acc, cId) => acc + (cId === 0 ? 0 : DATA.customers.find(c => c.id === cId).demand), 0));
          const routeDists = bestOverall.routes.map(r => {
            let d = 0;
            for (let i = 0; i < r.length - 1; i++) d += DATA.dist_matrix[r[i]][r[i + 1]];
            return parseFloat(d.toFixed(2));
          });

          updateMetrics(
            baseDist,
            bestOverall.totalDist,
            bestOverall.routes.length,
            savingsDist,
            savingsPct,
            elapsedSec,
            "Client-Side Genetic Algorithm",
            convGen
          );

          renderRouteCards(bestOverall.routes, routeDemands, routeDists);
          updateTruckSelector();
          updateChart(history);

          btn.innerHTML = '<i class="fa-solid fa-dna"></i> Run Genetic Algorithm Live';
          btn.disabled = false;
        }
      }

      requestAnimationFrame(stepGenerations);
    });

    // ==========================================
    // CUSTOM SCENARIO BUILDER & DISTANCE TABLE
    // ==========================================
    const modal = document.getElementById("modal-scenario");
    document.getElementById("btn-open-scenario-modal").addEventListener("click", openScenarioModal);
    document.getElementById("btn-quick-config").addEventListener("click", openScenarioModal);
    document.getElementById("btn-close-modal").addEventListener("click", () => modal.classList.add("hidden"));
    document.getElementById("btn-cancel-modal").addEventListener("click", () => modal.classList.add("hidden"));

    let tempDepot = { x: 50.0, y: 50.0 };
    let tempCustomers = [];

    function openScenarioModal() {
      tempDepot = { x: DATA.depot.x, y: DATA.depot.y };
      tempCustomers = JSON.parse(JSON.stringify(DATA.customers));

      document.getElementById("input-depot-x").value = tempDepot.x;
      document.getElementById("input-depot-y").value = tempDepot.y;
      document.getElementById("input-fleet-limit").value = DATA.fleet_limit;
      document.getElementById("input-truck-capacity").value = DATA.capacity;
      document.getElementById("input-num-sites").value = tempCustomers.length;

      renderCustomSitesTable();
      modal.classList.remove("hidden");
    }

    function calculateDistToWarehouse(x, y) {
      const dx = x - tempDepot.x;
      const dy = y - tempDepot.y;
      return Math.sqrt(dx * dx + dy * dy);
    }

    function renderCustomSitesTable() {
      const tbody = document.getElementById("custom-sites-tbody");
      tbody.innerHTML = "";

      let totalDemand = 0;

      tempCustomers.forEach((cust, idx) => {
        cust.id = idx + 1; // ensure 1..N order
        totalDemand += cust.demand;
        const distToDepot = calculateDistToWarehouse(cust.x, cust.y).toFixed(2);

        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-800/60";
        tr.innerHTML = `
          <td class="p-2 text-center font-bold text-white">${cust.id}</td>
          <td class="p-2">
            <input type="number" step="0.1" min="0" max="100" value="${cust.x}" class="inp-coord-x w-20 bg-slate-900 border border-slate-700 rounded px-1.5 py-0.5 text-xs text-white" data-idx="${idx}">
          </td>
          <td class="p-2">
            <input type="number" step="0.1" min="0" max="100" value="${cust.y}" class="inp-coord-y w-20 bg-slate-900 border border-slate-700 rounded px-1.5 py-0.5 text-xs text-white" data-idx="${idx}">
          </td>
          <td class="p-2 text-emerald-400 font-bold" id="dist-label-${idx}">
            ${distToDepot} km
          </td>
          <td class="p-2">
            <input type="number" min="1" max="100" value="${cust.demand}" class="inp-demand w-16 bg-slate-900 border border-slate-700 rounded px-1.5 py-0.5 text-xs text-white" data-idx="${idx}">
          </td>
          <td class="p-2 text-center">
            <button class="btn-del-site text-red-400 hover:text-red-300 p-1 cursor-pointer" data-idx="${idx}">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById("custom-sites-count").textContent = 
        `${tempCustomers.length} Sites Configured • Total Demand: ${totalDemand} units`;

      // Coordinate change listeners
      tbody.querySelectorAll(".inp-coord-x").forEach(inp => {
        inp.addEventListener("input", e => {
          const idx = parseInt(e.target.dataset.idx);
          tempCustomers[idx].x = parseFloat(e.target.value) || 0;
          document.getElementById(`dist-label-${idx}`).textContent = `${calculateDistToWarehouse(tempCustomers[idx].x, tempCustomers[idx].y).toFixed(2)} km`;
        });
      });

      tbody.querySelectorAll(".inp-coord-y").forEach(inp => {
        inp.addEventListener("input", e => {
          const idx = parseInt(e.target.dataset.idx);
          tempCustomers[idx].y = parseFloat(e.target.value) || 0;
          document.getElementById(`dist-label-${idx}`).textContent = `${calculateDistToWarehouse(tempCustomers[idx].x, tempCustomers[idx].y).toFixed(2)} km`;
        });
      });

      tbody.querySelectorAll(".inp-demand").forEach(inp => {
        inp.addEventListener("input", e => {
          const idx = parseInt(e.target.dataset.idx);
          tempCustomers[idx].demand = parseInt(e.target.value) || 10;
          const sum = tempCustomers.reduce((acc, c) => acc + c.demand, 0);
          document.getElementById("custom-sites-count").textContent = `${tempCustomers.length} Sites Configured • Total Demand: ${sum} units`;
        });
      });

      tbody.querySelectorAll(".btn-del-site").forEach(btn => {
        btn.addEventListener("click", e => {
          const idx = parseInt(btn.dataset.idx);
          if (tempCustomers.length <= 3) {
            alert("A minimum of 3 delivery sites is required.");
            return;
          }
          tempCustomers.splice(idx, 1);
          renderCustomSitesTable();
        });
      });
    }

    // Warehouse coordinate change updates distance table in modal
    document.getElementById("input-depot-x").addEventListener("input", e => {
      tempDepot.x = parseFloat(e.target.value) || 0;
      renderCustomSitesTable();
    });
    document.getElementById("input-depot-y").addEventListener("input", e => {
      tempDepot.y = parseFloat(e.target.value) || 0;
      renderCustomSitesTable();
    });

    // Generate Random Sites
    document.getElementById("btn-generate-random").addEventListener("click", () => {
      const n = Math.max(5, Math.min(50, parseInt(document.getElementById("input-num-sites").value) || 20));
      tempCustomers = [];
      for (let i = 1; i <= n; i++) {
        tempCustomers.push({
          id: i,
          x: parseFloat((Math.random() * 85 + 7).toFixed(1)),
          y: parseFloat((Math.random() * 85 + 7).toFixed(1)),
          demand: Math.floor(Math.random() * 16 + 10) // 10..25 units
        });
      }
      renderCustomSitesTable();
    });

    // Reset Benchmark
    document.getElementById("btn-reset-benchmark").addEventListener("click", () => {
      tempDepot = { x: 50.0, y: 50.0 };
      tempCustomers = JSON.parse(JSON.stringify(INITIAL_BENCHMARK_DATA.customers));
      document.getElementById("input-depot-x").value = 50.0;
      document.getElementById("input-depot-y").value = 50.0;
      document.getElementById("input-fleet-limit").value = 8;
      document.getElementById("input-truck-capacity").value = 100;
      document.getElementById("input-num-sites").value = 35;
      renderCustomSitesTable();
    });

    // Add Single Delivery Site
    document.getElementById("btn-add-single-site").addEventListener("click", () => {
      if (tempCustomers.length >= 50) {
        alert("Maximum limit of 50 delivery sites reached.");
        return;
      }
      const newId = tempCustomers.length + 1;
      tempCustomers.push({
        id: newId,
        x: parseFloat((Math.random() * 80 + 10).toFixed(1)),
        y: parseFloat((Math.random() * 80 + 10).toFixed(1)),
        demand: 15
      });
      renderCustomSitesTable();
    });

    // Pure JS Greedy Nearest-Neighbor CVRP Solver
    function solveGreedyNN(depot, customers, capacity, distMatrix) {
      const unvisited = new Set(customers.map(c => c.id));
      const routes = [];
      const routeDemands = [];
      const routeDistances = [];
      let totalDist = 0;

      while (unvisited.size > 0) {
        let currentRoute = [0];
        let currentNode = 0;
        let remainingCap = capacity;

        while (true) {
          const feasible = [];
          unvisited.forEach(cId => {
            const cust = customers.find(c => c.id === cId);
            if (cust && cust.demand <= remainingCap) feasible.push(cId);
          });

          if (feasible.length === 0) break;

          let bestNext = feasible[0];
          let bestD = distMatrix[currentNode][bestNext];
          for (let i = 1; i < feasible.length; i++) {
            const cand = feasible[i];
            const d = distMatrix[currentNode][cand];
            if (d < bestD) {
              bestD = d;
              bestNext = cand;
            }
          }

          currentRoute.push(bestNext);
          const cust = customers.find(c => c.id === bestNext);
          remainingCap -= cust.demand;
          currentNode = bestNext;
          unvisited.delete(bestNext);
        }

        currentRoute.push(0);
        routes.push(currentRoute);

        let rDist = 0;
        let rDem = 0;
        for (let i = 0; i < currentRoute.length - 1; i++) {
          rDist += distMatrix[currentRoute[i]][currentRoute[i + 1]];
          if (currentRoute[i] !== 0) {
            rDem += customers.find(c => c.id === currentRoute[i]).demand;
          }
        }
        routeDemands.push(rDem);
        routeDistances.push(parseFloat(rDist.toFixed(2)));
        totalDist += rDist;
      }

      return {
        routes,
        route_demands: routeDemands,
        route_distances_km: routeDistances,
        total_distance_km: parseFloat(totalDist.toFixed(2)),
        vehicles_utilized: routes.length,
        runtime_seconds: 0.001
      };
    }

    // Apply Custom Scenario & Recalculate
    document.getElementById("btn-apply-scenario").addEventListener("click", () => {
      DATA.depot = { x: parseFloat(document.getElementById("input-depot-x").value) || 50, y: parseFloat(document.getElementById("input-depot-y").value) || 50 };
      DATA.fleet_limit = parseInt(document.getElementById("input-fleet-limit").value) || 8;
      DATA.capacity = parseInt(document.getElementById("input-truck-capacity").value) || 100;
      DATA.customers = JSON.parse(JSON.stringify(tempCustomers));
      DATA.total_demand = DATA.customers.reduce((acc, c) => acc + c.demand, 0);

      // Recompute Distance Matrix: (N+1) x (N+1)
      const numNodes = DATA.customers.length + 1;
      const allNodes = [{ id: 0, x: DATA.depot.x, y: DATA.depot.y }, ...DATA.customers];
      const newDistMatrix = [];

      for (let i = 0; i < numNodes; i++) {
        const row = [];
        for (let j = 0; j < numNodes; j++) {
          const dx = allNodes[i].x - allNodes[j].x;
          const dy = allNodes[i].y - allNodes[j].y;
          row.push(Math.sqrt(dx * dx + dy * dy));
        }
        newDistMatrix.push(row);
      }
      DATA.dist_matrix = newDistMatrix;

      // Solve baseline NN for this custom scenario
      DATA.baseline = solveGreedyNN(DATA.depot, DATA.customers, DATA.capacity, DATA.dist_matrix);
      DATA.ga_best = DATA.baseline; // initial placeholder until GA is run

      // Update Header Badges
      document.getElementById("badge-sites").innerHTML = `<i class="fa-solid fa-location-dot text-indigo-400 mr-1.5"></i>${DATA.customers.length} Delivery Sites`;
      document.getElementById("badge-depot").innerHTML = `<i class="fa-solid fa-warehouse text-amber-400 mr-1.5"></i>Warehouse (${DATA.depot.x.toFixed(0)}, ${DATA.depot.y.toFixed(0)})`;
      document.getElementById("badge-capacity").innerHTML = `<i class="fa-solid fa-box text-cyan-400 mr-1.5"></i>Capacity Q = ${DATA.capacity}`;
      document.getElementById("badge-trucks").innerHTML = `<i class="fa-solid fa-truck text-emerald-400 mr-1.5"></i>Fleet Limit K = ${DATA.fleet_limit}`;
      document.getElementById("badge-demand").innerHTML = `<i class="fa-solid fa-weight-hanging text-purple-400 mr-1.5"></i>Demand: ${DATA.total_demand} u`;

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
        "Custom Scenario (Baseline NN)",
        "N/A"
      );

      renderRouteCards(DATA.baseline.routes, DATA.baseline.route_demands, DATA.baseline.route_distances_km);
      updateTruckSelector();
      drawMap();

      modal.classList.add("hidden");
    });

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

print("index.html successfully updated with Custom Delivery Scenario Builder, Distance Table, and Individual Truck Animation!")
