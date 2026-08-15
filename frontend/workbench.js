// ═══════════════════════════════════════════════════════════════════════════
// CELLAB WORKBENCH v3.1
// Nested Tab Groups + Three-Column Module Layout (COMSOL/Overleaf style)
// ═══════════════════════════════════════════════════════════════════════════

// ═════════════════════════════════════════════
// CUSTOM SVG ICONS
// ═════════════════════════════════════════════

const ICONS = {
    fastia: (size = 14) => `<svg width="${size}" height="${size}" viewBox="0 0 14 14" style="vertical-align:middle;display:inline-block"><ellipse cx="7" cy="7" rx="5.5" ry="4" fill="none" stroke="#8e44ad" stroke-width="0.4" stroke-dasharray="1,1" opacity="0.4"/><ellipse cx="4.5" cy="8" rx="2.2" ry="0.8" transform="rotate(-35,4.5,8)" fill="#8e44ad" opacity="0.9"/><ellipse cx="9" cy="5" rx="2.5" ry="0.7" transform="rotate(-50,9,5)" fill="#8e44ad" opacity="0.8"/><ellipse cx="6" cy="4" rx="1.8" ry="0.6" transform="rotate(-20,6,4)" fill="#8e44ad" opacity="0.7"/><ellipse cx="10" cy="9" rx="1.5" ry="0.55" transform="rotate(-45,10,9)" fill="#8e44ad" opacity="0.65"/></svg>`,

    immunia: (size = 14) => `<svg width="${size}" height="${size}" viewBox="0 0 14 14" style="vertical-align:middle;display:inline-block"><circle cx="7" cy="7" r="5.5" fill="#f5e6e0" stroke="#c0392b" stroke-width="0.5" opacity="0.7"/><circle cx="5.5" cy="6" r="2" fill="#c0392b" opacity="0.55"/><circle cx="8" cy="5.5" r="1.7" fill="#c0392b" opacity="0.5"/><circle cx="8.5" cy="8" r="1.8" fill="#c0392b" opacity="0.45"/><circle cx="5.8" cy="8.5" r="1.5" fill="#c0392b" opacity="0.4"/><path d="M6,6 Q7.5,4.5 8.5,6.5 Q9,8 7,9 Q5.5,9 5.5,7.5Z" fill="#c0392b" opacity="0.2"/></svg>`,

    cornealia: '👁',
    cellfade: '🧫',

    cellvisia: (size = 14) => `<svg width="${size}" height="${size}" viewBox="0 0 14 14" style="vertical-align:middle;display:inline-block"><rect x="1.5" y="1.5" width="11" height="11" rx="1.5" fill="none" stroke="#2196f3" stroke-width="0.5" opacity="0.5"/><rect x="3" y="3" width="8" height="8" rx="1" fill="none" stroke="#2196f3" stroke-width="0.4" stroke-dasharray="1,0.8" opacity="0.4"/><circle cx="7" cy="7" r="2.8" fill="#2196f3" opacity="0.15"/><circle cx="7" cy="7" r="1.8" fill="none" stroke="#2196f3" stroke-width="0.6" opacity="0.8"/><circle cx="7" cy="7" r="0.7" fill="#2196f3" opacity="0.9"/><line x1="7" y1="1" x2="7" y2="3.5" stroke="#2196f3" stroke-width="0.3" opacity="0.3"/><line x1="7" y1="10.5" x2="7" y2="13" stroke="#2196f3" stroke-width="0.3" opacity="0.3"/><line x1="1" y1="7" x2="3.5" y2="7" stroke="#2196f3" stroke-width="0.3" opacity="0.3"/><line x1="10.5" y1="7" x2="13" y2="7" stroke="#2196f3" stroke-width="0.3" opacity="0.3"/></svg>`,

    associa: (size = 14) => `<svg width="${size}" height="${size}" viewBox="0 0 14 14" style="vertical-align:middle;display:inline-block"><circle cx="4" cy="4" r="2" fill="none" stroke="#ff9800" stroke-width="0.8" opacity="0.8"/><circle cx="10" cy="10" r="2" fill="none" stroke="#ff9800" stroke-width="0.8" opacity="0.8"/><line x1="5.5" y1="5.5" x2="8.5" y2="8.5" stroke="#ff9800" stroke-width="0.6" stroke-dasharray="1.5,1" opacity="0.6"/><path d="M2 10 Q4 8, 6 9 Q8 10, 10 7 Q12 4, 12 3" fill="none" stroke="#ff9800" stroke-width="0.5" opacity="0.4"/></svg>`,

    cellade: (size = 14) => `<svg width="${size}" height="${size}" viewBox="0 0 14 14" style="vertical-align:middle;display:inline-block"><ellipse cx="5" cy="5" rx="3.5" ry="3" fill="none" stroke="#66bb6a" stroke-width="0.7" opacity="0.7"/><ellipse cx="9.5" cy="8.5" rx="3" ry="2.5" fill="none" stroke="#66bb6a" stroke-width="0.7" opacity="0.7"/><circle cx="5" cy="5" r="0.8" fill="#66bb6a" opacity="0.5"/><circle cx="9.5" cy="8.5" r="0.8" fill="#66bb6a" opacity="0.5"/><line x1="7" y1="6" x2="8" y2="7" stroke="#66bb6a" stroke-width="0.4" stroke-dasharray="1,1" opacity="0.4"/></svg>`,

    cellfade: (size = 14) => `<svg width="${size}" height="${size}" viewBox="0 0 14 14" style="vertical-align:middle;display:inline-block"><ellipse cx="4" cy="7" rx="2.5" ry="1.2" fill="#e91e63" opacity="0.2" transform="rotate(-30 4 7)"/><ellipse cx="4" cy="7" rx="2.5" ry="1.2" fill="none" stroke="#e91e63" stroke-width="0.6" opacity="0.7" transform="rotate(-30 4 7)"/><ellipse cx="9.5" cy="5" rx="2" ry="0.8" fill="#e91e63" opacity="0.2" transform="rotate(15 9.5 5)"/><ellipse cx="9.5" cy="5" rx="2" ry="0.8" fill="none" stroke="#e91e63" stroke-width="0.6" opacity="0.7" transform="rotate(15 9.5 5)"/><ellipse cx="7" cy="10" rx="1.8" ry="0.7" fill="#e91e63" opacity="0.2" transform="rotate(-10 7 10)"/><ellipse cx="7" cy="10" rx="1.8" ry="0.7" fill="none" stroke="#e91e63" stroke-width="0.6" opacity="0.7" transform="rotate(-10 7 10)"/><circle cx="4" cy="7" r="0.5" fill="#e91e63" opacity="0.8"/><circle cx="9.5" cy="5" r="0.5" fill="#e91e63" opacity="0.8"/><circle cx="7" cy="10" r="0.5" fill="#e91e63" opacity="0.8"/></svg>`,

    annotade: (size = 14) => `<svg width="${size}" height="${size}" viewBox="0 0 14 14" style="vertical-align:middle;display:inline-block"><rect x="1" y="1" width="12" height="12" rx="1.5" fill="none" stroke="#ff9800" stroke-width="0.7" opacity="0.5"/><path d="M3 9 L5 3 L7 9" stroke="#ff9800" stroke-width="1" fill="none" stroke-linecap="round" stroke-linejoin="round"/><line x1="3.8" y1="7" x2="6.2" y2="7" stroke="#ff9800" stroke-width="0.6"/><circle cx="10" cy="4" r="1.5" fill="none" stroke="#ff9800" stroke-width="0.7"/><line x1="10" y1="6" x2="10" y2="11" stroke="#ff9800" stroke-width="0.7"/><circle cx="10" cy="11" r="0.5" fill="#ff9800"/></svg>`,
};

const state = {
    workspaces: new Map(),
    activeWorkspace: null,
    wsCounter: 0,
    moduleCounter: 0,
    subtabCounter: 0,
    collapsedGroups: new Set(), // track collapsed pipeline tab groups
    focusedGroups: new Map(),  // pipelineId → focused stepId (single-tab view with springs)
};

// ═════════════════════════════════════════════
// WORKSPACE (Level 1)
// ═════════════════════════════════════════════

function createWorkspace(name) {
    state.wsCounter++;
    const wsId = `ws-${state.wsCounter}`;
    name = name || `Workspace ${state.wsCounter}`;

    state.subtabCounter++;
    const canvasSubId = `subtab-${state.subtabCounter}`;

    const ws = {
        id: wsId, name,
        subtabs: new Map(),
        pipelines: new Map(),
        activeSubtab: canvasSubId,
    };

    ws.subtabs.set(canvasSubId, {
        id: canvasSubId, type: 'canvas', label: 'Home',
        icon: '◈', pipelineId: null, stepId: null, closeable: false,
    });

    state.workspaces.set(wsId, ws);
    renderWorkspaceTabs();
    switchWorkspace(wsId);
    updateStatus(`Created ${name}`);

    // Sync to backend
    if (state._projectOpen) {
        api('workspace/create', 'POST', { name, ws_id: ws.id });
    }
}

let _codeChatCounter = 0;
function createCodeChat(name) {
    _codeChatCounter++;
    const wsId = `cc-${_codeChatCounter}`;
    name = name || `Code & Chat ${_codeChatCounter}`;

    const ws = {
        id: wsId, name,
        type: 'codechat',
        _isDefault: _codeChatCounter === 1,
        consoleTabs: [],
        activeConsoleTab: null,
    };

    // Add a default Python tab
    const tabId = `cctab_${Date.now()}`;
    const info = CONSOLE_TYPES['shared'];
    ws.consoleTabs.push({
        id: tabId,
        sessionId: null,
        type: 'shared',
        name: `${info.label} 1`,
        scope: { level: 'none' },
        lines: [{ html: `<span class="console-welcome">CelLAB Console — ${info.welcome}</span>` }],
        history: [],
        histIdx: -1,
    });
    ws.activeConsoleTab = tabId;

    state.workspaces.set(wsId, ws);

    // Create backend session
    api('console/create', 'POST', { type: 'shared' }).then(res => {
        if (res.success) {
            ws.consoleTabs[0].sessionId = res.data.session_id;
        }
    });

    renderWorkspaceTabs();
    switchWorkspace(wsId);
    updateStatus(`Created ${name}`);
}

function switchWorkspace(wsId) {
    const ws = state.workspaces.get(wsId);
    if (!ws) return;

    // Exiting a codechat workspace — restore layout
    const prevWs = state.workspaces.get(state.activeWorkspace);
    if (prevWs && prevWs.type === 'codechat' && wsId !== state.activeWorkspace) {
        _exitCodeChat();
    }

    // If clicking the already-active workspace
    if (state.activeWorkspace === wsId) {
        if (ws.type === 'codechat') return;
        const canvasTab = [...ws.subtabs.values()].find(s => s.type === 'canvas');
        if (canvasTab && ws.activeSubtab !== canvasTab.id) {
            ws.activeSubtab = canvasTab.id;
            renderSubtabs();
            renderLeftPanel();
            renderViewport();
            updateOpenModulesList();
        }
        return;
    }

    state.activeWorkspace = wsId;

    if (ws.type === 'codechat') {
        _enterCodeChat(ws);
    } else {
        renderAll();
    }

    renderWorkspaceTabs();
    document.getElementById('statusWorkspace').textContent = ws.name;
}

function _findOrCreateCodeChat() {
    let ccWs = [...state.workspaces.values()].find(w => w.type === 'codechat');
    if (!ccWs) {
        createCodeChat();
        ccWs = [...state.workspaces.values()].find(w => w.type === 'codechat');
    } else {
        switchWorkspace(ccWs.id);
    }
    return ccWs;
}

function _enterCodeChat(ws) {
    document.getElementById('leftPanel').style.display = 'none';
    document.getElementById('leftResizer').style.display = 'none';
    document.getElementById('rightPanel').style.display = 'none';
    document.getElementById('rightResizer').style.display = 'none';
    document.getElementById('subtabBar').style.display = 'none';

    const viewport = document.getElementById('viewport');
    viewport.className = 'viewport codechat-viewport';
    _renderCodeChatView(viewport, ws);
}

function _exitCodeChat() {
    document.getElementById('leftPanel').style.display = '';
    document.getElementById('leftResizer').style.display = '';
    document.getElementById('rightPanel').style.display = '';
    document.getElementById('rightResizer').style.display = '';
    document.getElementById('subtabBar').style.display = '';

    const viewport = document.getElementById('viewport');
    viewport.className = 'viewport';
}

function _renderCodeChatView(viewport, ws) {
    viewport.innerHTML = `
        <div class="codechat-container">
            <div class="codechat-tabs-bar">
                <div class="codechat-tabs" id="codeChatTabs"></div>
                <div class="codechat-actions">
                    <button class="codechat-btn" onclick="_addCodeChatTab('shared')" title="New Python">+ Python</button>
                    <button class="codechat-btn" onclick="_addCodeChatTab('cellintella')" title="New CellIntella">+ CellIntella</button>
                    <button class="codechat-btn" onclick="_addCodeChatTab('git')" title="New Git">+ Git</button>
                </div>
            </div>
            <div class="codechat-body" id="codeChatBody" onclick="document.getElementById('consoleInput')?.focus()" oncontextmenu="if(!event.target.closest('.console-input')){event.preventDefault();openWorkspaceRadialNav(event, true);}"></div>
        </div>
    `;
    _renderCodeChatTabs();
    _renderCodeChatBody();
}

function _getActiveCodeChatWs() {
    const ws = state.workspaces.get(state.activeWorkspace);
    return (ws && ws.type === 'codechat') ? ws : null;
}

function _getActiveCodeChatTab() {
    const ws = _getActiveCodeChatWs();
    if (!ws) return null;
    return ws.consoleTabs.find(t => t.id === ws.activeConsoleTab);
}

async function _addCodeChatTab(type) {
    const ws = _getActiveCodeChatWs();
    if (!ws) return;

    let sessionId = null;
    if (type === 'cellintella' || type === 'cellintella_fresh') {
        sessionId = `cellintella_${Date.now()}`;
    } else {
        const res = await api('console/create', 'POST', { type });
        if (!res.success) return;
        sessionId = res.data.session_id;
    }

    const info = CONSOLE_TYPES[type];
    if (!info) return;
    const tabId = `cctab_${Date.now()}`;
    const count = ws.consoleTabs.filter(t => t.type === type).length + 1;

    const tab = {
        id: tabId,
        sessionId,
        type,
        name: `${info.label} ${count}`,
        scope: { level: 'none' },
        lines: [
            { html: `<span class="console-welcome">CelLAB Console — ${info.welcome}</span>` },
            ...(type === 'cellintella' || type === 'cellintella_fresh' ? [
                { html: `<span class="console-welcome">⏳ First message takes ~2-3 min to load the model. After that, responses are fast.</span>` },
                { html: `<span class="console-welcome">Powered by Llama 3.2 3B (local, private — no data leaves your machine)</span>` },
            ] : []),
        ],
        history: [],
        histIdx: -1,
    };

    ws.consoleTabs.push(tab);
    ws.activeConsoleTab = tabId;
    _renderCodeChatTabs();
    _renderCodeChatBody();
}

function _closeCodeChatTab(tabId, ev) {
    if (ev) ev.stopPropagation();
    const ws = _getActiveCodeChatWs();
    if (!ws) return;
    ws.consoleTabs = ws.consoleTabs.filter(t => t.id !== tabId);
    if (ws.activeConsoleTab === tabId) {
        ws.activeConsoleTab = ws.consoleTabs.length > 0 ? ws.consoleTabs[0].id : null;
    }
    _renderCodeChatTabs();
    _renderCodeChatBody();
}

function _renderCodeChatTabs() {
    const bar = document.getElementById('codeChatTabs');
    if (!bar) return;
    const ws = _getActiveCodeChatWs();
    if (!ws) return;
    bar.innerHTML = '';

    ws.consoleTabs.forEach(tab => {
        const el = document.createElement('div');
        const info = CONSOLE_TYPES[tab.type] || { label: tab.type, color: '#888' };
        const isActive = tab.id === ws.activeConsoleTab;
        el.className = `codechat-tab ${isActive ? 'active' : ''}`;
        el.style.borderTopColor = info.color;
        el.onclick = () => { ws.activeConsoleTab = tab.id; _renderCodeChatTabs(); _renderCodeChatBody(); };
        el.innerHTML = `
            <span class="codechat-tab-dot" style="color:${info.color}">●</span>
            <span class="codechat-tab-name">${tab.name}</span>
            ${ws.consoleTabs.length > 1 ? `<span class="codechat-tab-close" onclick="_closeCodeChatTab('${tab.id}',event)">×</span>` : ''}
        `;
        bar.appendChild(el);
    });
}

function _renderCodeChatBody() {
    const body = document.getElementById('codeChatBody');
    if (!body) return;

    const tab = _getActiveCodeChatTab();
    if (!tab) { body.innerHTML = '<p style="padding:20px;color:var(--text-secondary)">No tabs open. Add one above.</p>'; return; }

    const info = CONSOLE_TYPES[tab.type] || { prompt: '> ', color: '#888' };
    const linesHtml = tab.lines.map(l => `<div class="console-line">${l.html}</div>`).join('');

    body.innerHTML = `
        ${linesHtml}
        <div class="console-input-row">
            <span class="console-prompt" style="color:${info.color}">${info.prompt}</span>
            <input class="console-input" id="consoleInput" type="text"
                   onkeydown="_codeChatKeyDown(event)"
                   placeholder="Type a command or message..."
                   autocomplete="off" spellcheck="false" />
        </div>
    `;

    body.scrollTop = body.scrollHeight;
    document.getElementById('consoleInput')?.focus();
}

function _codeChatKeyDown(e) {
    const tab = _getActiveCodeChatTab();
    if (!tab) return;

    if (e.key === 'Enter') {
        const input = document.getElementById('consoleInput');
        const code = input.value.trim();
        if (!code) return;

        tab.history.push(code);
        tab.histIdx = tab.history.length;

        const info = CONSOLE_TYPES[tab.type] || { prompt: '> ', color: '#888' };
        tab.lines.push({ html: `<span class="console-prompt-echo" style="color:${info.color}">${info.prompt}</span><span class="console-code">${escapeHtml(code)}</span>` });

        input.value = '';
        _renderCodeChatBody();
        _codeChatExec(tab, code);
    }

    if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (tab.histIdx > 0) {
            tab.histIdx--;
            document.getElementById('consoleInput').value = tab.history[tab.histIdx] || '';
        }
    }
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (tab.histIdx < tab.history.length - 1) {
            tab.histIdx++;
            document.getElementById('consoleInput').value = tab.history[tab.histIdx] || '';
        } else {
            tab.histIdx = tab.history.length;
            document.getElementById('consoleInput').value = '';
        }
    }
}

async function _codeChatExec(tab, code) {
    if (tab.type === 'cellintella' || tab.type === 'cellintella_fresh') {
        // Show thinking indicator
        tab.lines.push({ html: `<span class="console-out" style="color:rgba(203,166,247,.4);font-style:italic">${_cellIntellaModelLoaded ? '⏳ Thinking...' : '⏳ Loading model & thinking... (~2-3 min first time)'}</span>` });
        _renderCodeChatBody();

        try {
            const res = await api('cellintella/query', 'POST', {
                message: code,
                session_id: tab.sessionId,
                fresh: tab.type === 'cellintella_fresh',
                scope: tab.scope || { level: 'none' },
                accumulated_context: [],
            });

            // Remove thinking indicator
            tab.lines.pop();

            if (res.success && res.data.response) {
                tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">🤖 ${escapeHtml(res.data.response)}</span>` });
                _cellIntellaModelLoaded = true;
            } else {
                tab.lines.push({ html: `<span class="console-err">${escapeHtml(res.error || 'No response')}</span>` });
            }
        } catch (err) {
            tab.lines.pop();
            tab.lines.push({ html: `<span class="console-err">Connection error: ${escapeHtml(err.message)}</span>` });
        }
        _renderCodeChatBody();
        return;
    }

    try {
        // Ensure session exists
        if (!tab.sessionId) {
            const createRes = await api('console/create', 'POST', { type: tab.type });
            if (createRes.success) {
                tab.sessionId = createRes.data.session_id;
            } else {
                tab.lines.push({ html: `<span class="console-error">Failed to create console session</span>` });
                _renderCodeChatBody();
                return;
            }
        }
        const res = await api('console/exec', 'POST', {
            session_id: tab.sessionId,
            code: code,
        });

        if (!res.success) {
            tab.lines.push({ html: `<span class="console-err">${escapeHtml(res.error || 'Failed')}</span>` });
            _renderCodeChatBody();
            return;
        }

        const { stdout, stderr, result, magic } = res.data;
        if (magic === 'clear') { tab.lines = []; _renderCodeChatBody(); return; }

        if (stdout) tab.lines.push({ html: `<span class="console-out">${escapeHtml(stdout)}</span>` });
        if (result) tab.lines.push({ html: `<span class="console-result">${escapeHtml(result)}</span>` });
        if (stderr) tab.lines.push({ html: `<span class="console-err">${escapeHtml(stderr)}</span>` });
    } catch (err) {
        tab.lines.push({ html: `<span class="console-err">Network error: ${escapeHtml(err.message)}</span>` });
    }
    _renderCodeChatBody();
}

function closeWorkspace(wsId, ev) {
    if (ev) ev.stopPropagation();
    if (state.workspaces.size <= 1) { updateStatus('Cannot close last workspace'); return; }
    const ws = state.workspaces.get(wsId);
    if (!ws) return;

    if (ws.type === 'codechat') {
        if (ws._isDefault) { updateStatus('Cannot close default Code & Chat'); return; }
        if (!confirm(`Close "${ws.name}"?`)) return;
        // Exit codechat layout if it's active
        if (state.activeWorkspace === wsId) _exitCodeChat();
    } else {
        const mc = ws.subtabs.size - 1;
        if (mc > 0 && !confirm(`Close "${ws.name}" and ${mc} module(s)?`)) return;
    }

    state.workspaces.delete(wsId);
    if (state.activeWorkspace === wsId) switchWorkspace(state.workspaces.keys().next().value);
    else renderWorkspaceTabs();
    updateStatus(`Closed ${ws.name}`);

    if (state._projectOpen && ws.type !== 'codechat') {
        api(`workspace/${wsId}/delete`, 'DELETE');
    }
}

function renameWorkspace(wsId) {
    const ws = state.workspaces.get(wsId);
    if (!ws) return;
    const n = prompt('Rename workspace:', ws.name);
    if (n?.trim()) {
        ws.name = n.trim();
        renderWorkspaceTabs();
        if (state.activeWorkspace === wsId) document.getElementById('statusWorkspace').textContent = ws.name;

        if (state._projectOpen) {
            api(`workspace/${wsId}/rename`, 'POST', { name: ws.name });
        }
    }
}

// ═════════════════════════════════════════════
// SUB-TABS (Level 2) — grouped by pipeline
// ═════════════════════════════════════════════

function openModuleSubtab(pipelineId, stepId, focused = false) {
    const ws = getActiveWorkspace();
    if (!ws) return;

    const wasCollapsed = state.collapsedGroups.has(pipelineId);

    // Already open? Switch to it without changing expand/collapse
    for (const [subId, sub] of ws.subtabs) {
        if (sub.pipelineId === pipelineId && sub.stepId === stepId) {
            // If collapsed, use focused mode to show just this tab
            if (wasCollapsed) {
                state.collapsedGroups.delete(pipelineId);
                state.focusedGroups.set(pipelineId, stepId);
            }
            switchSubtab(subId);
            return;
        }
    }

    const pipeline = ws.pipelines.get(pipelineId);
    if (!pipeline) return;

    state.subtabCounter++;
    const subId = `subtab-${state.subtabCounter}`;
    const stepDef = getStepDef(pipeline.type, stepId);

    const newTab = {
        id: subId, type: 'module',
        label: stepDef.name,
        icon: stepDef.icon || getPipelineDef(pipeline.type).icon,
        pipelineId, stepId,
        moduleType: pipeline.type,
        closeable: true,
        activeTreeItem: null,
    };

    // Insert in step-order position (not at end)
    _insertTabOrdered(ws, subId, newTab);

    // If was collapsed, open in focused mode (only this tab visible)
    // If was expanded, stay expanded (just add the new tab)
    if (wasCollapsed) {
        state.collapsedGroups.delete(pipelineId);
        state.focusedGroups.set(pipelineId, stepId);
    } else if (focused) {
        state.focusedGroups.set(pipelineId, stepId);
    }

    switchSubtab(subId);
    updateStatus(`Opened ${stepDef.name}`);
}

function _insertTabOrdered(ws, newSubId, newTab) {
    // Get the canonical step order for this pipeline type
    const def = getPipelineDef(newTab.moduleType);
    const stepOrder = def.steps.map(s => s.id);
    const newStepIdx = stepOrder.indexOf(newTab.stepId);

    // Find the right insertion point among existing tabs
    // Strategy: rebuild the Map with the new tab in the correct position
    const entries = [...ws.subtabs.entries()];
    const newEntries = [];
    let inserted = false;

    for (const [id, tab] of entries) {
        // If this tab belongs to the same pipeline, check order
        if (!inserted && tab.pipelineId === newTab.pipelineId && tab.type === 'module') {
            const existingStepIdx = stepOrder.indexOf(tab.stepId);
            if (newStepIdx < existingStepIdx) {
                // Insert new tab before this one
                newEntries.push([newSubId, newTab]);
                inserted = true;
            }
        }
        newEntries.push([id, tab]);
    }

    if (!inserted) {
        // Find the last tab of this pipeline's group and insert after it
        let lastPipelineIdx = -1;
        for (let i = 0; i < newEntries.length; i++) {
            if (newEntries[i][1].pipelineId === newTab.pipelineId) lastPipelineIdx = i;
        }
        if (lastPipelineIdx >= 0) {
            newEntries.splice(lastPipelineIdx + 1, 0, [newSubId, newTab]);
        } else {
            newEntries.push([newSubId, newTab]);
        }
    }

    // Rebuild the Map
    ws.subtabs = new Map(newEntries);
}

function openAllSteps(pipelineId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const pipeline = ws.pipelines.get(pipelineId);
    if (!pipeline) return;

    const def = getPipelineDef(pipeline.type);

    // Open all steps in order (skip already-open ones)
    let lastSubId = null;
    for (const step of def.steps) {
        // Check if already open
        let existing = null;
        for (const [subId, sub] of ws.subtabs) {
            if (sub.pipelineId === pipelineId && sub.stepId === step.id) {
                existing = subId;
                break;
            }
        }
        if (existing) {
            lastSubId = existing;
        } else {
            state.subtabCounter++;
            const subId = `subtab-${state.subtabCounter}`;
            const stepDef = getStepDef(pipeline.type, step.id);
            const newTab = {
                id: subId, type: 'module',
                label: stepDef.name,
                icon: stepDef.icon || def.icon,
                pipelineId, stepId: step.id,
                moduleType: pipeline.type,
                closeable: true,
                activeTreeItem: null,
            };
            _insertTabOrdered(ws, subId, newTab);
            lastSubId = subId;
        }
    }

    // Expand group and switch to first step
    state.collapsedGroups.delete(pipelineId);
    if (lastSubId) {
        // Switch to first step tab
        for (const [subId, sub] of ws.subtabs) {
            if (sub.pipelineId === pipelineId && sub.type === 'module') {
                switchSubtab(subId);
                break;
            }
        }
    }
    updateStatus(`Opened all steps for ${pipeline.name}`);
}

function switchSubtab(subId) {
    const ws = getActiveWorkspace();
    if (!ws || !ws.subtabs.has(subId)) return;

    // ── Collect params from current tab before switching ──
    _collectCurrentParams(ws);

    if (_taskManagerActive) {
        _taskManagerActive = false;
        const btn = document.getElementById('tmToolbarBtn');
        if (btn) btn.classList.remove('active');
        const rp = document.querySelector('.right-panel');
        const rr = document.getElementById('rightResizer');
        if (rp) rp.style.display = '';
        if (rr) rr.style.display = '';
    }
    ws.activeSubtab = subId;
    renderSubtabs();
    renderLeftPanel();
    renderViewport();
    updateOpenModulesList();
    updatePropertiesPanel();

    // Load saved params from backend for module tabs
    const sub = ws.subtabs.get(subId);
    if (sub?.type === 'module' && state._projectOpen) {
        populateModuleSettings(subId);
        discoverExistingResults(subId);
    }
}

function _collectCurrentParams(ws) {
    if (!ws.activeSubtab) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    if (!sub || sub.type !== 'module' || !sub.activeTreeItem) return;
    const bodyEl = document.getElementById(`settingsBody-${ws.activeSubtab}`);
    if (!bodyEl) return;
    if (!sub._localParams) sub._localParams = {};
    const params = {};
    bodyEl.querySelectorAll('[data-param]').forEach(el => {
        if (el.type === 'checkbox') params[el.dataset.param] = el.checked;
        else params[el.dataset.param] = el.value;
    });
    sub._localParams[sub.activeTreeItem.id] = params;
}

function closeSubtab(subId, ev) {
    if (ev) ev.stopPropagation();
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub || !sub.closeable) return;
    // Persist CellVisia state before destroying
    if (sub.moduleType === 'cellvisia') cvPersistState(sub);
    if (sub.moduleType === 'cellade') cdPersistState(sub);
    if (sub.moduleType === 'associa') asPersistState(sub);
    if (sub.moduleType === 'cellfade') cfPersistState(sub);
    if (sub.moduleType === 'annotade') anPersistState(sub);
    ws.subtabs.delete(subId);

    if (ws.activeSubtab === subId) {
        const canvas = [...ws.subtabs.values()].find(s => s.type === 'canvas');
        ws.activeSubtab = canvas ? canvas.id : ws.subtabs.keys().next().value;
    }
    renderAll();
}

function closeSubtabsForPipeline(pipelineId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const toClose = [];
    for (const [id, sub] of ws.subtabs) {
        if (sub.pipelineId === pipelineId) toClose.push(id);
    }
    toClose.forEach(id => ws.subtabs.delete(id));
    if (toClose.includes(ws.activeSubtab)) {
        const canvas = [...ws.subtabs.values()].find(s => s.type === 'canvas');
        ws.activeSubtab = canvas ? canvas.id : ws.subtabs.keys().next().value;
    }
    renderAll();
}

function toggleTabGroup(pipelineId) {
    // If focused, expand to full view
    if (state.focusedGroups.has(pipelineId)) {
        state.focusedGroups.delete(pipelineId);
        renderSubtabs();
        return;
    }
    // Normal collapse/expand toggle
    if (state.collapsedGroups.has(pipelineId)) state.collapsedGroups.delete(pipelineId);
    else state.collapsedGroups.add(pipelineId);
    state.focusedGroups.delete(pipelineId);
    renderSubtabs();
}

function closeTabGroup(pipelineId, ev) {
    if (ev) ev.stopPropagation();
    closeSubtabsForPipeline(pipelineId);
}

function openWorkspaceRadialNav(ev, fromCodeChat = false) {
    const existing = document.querySelector('.radial-nav-overlay');
    if (existing) existing.remove();

    const ws = getActiveWorkspace();

    let items;
    if (fromCodeChat) {
        // Find first regular workspace to switch back to
        const mainWs = [...state.workspaces.values()].find(w => w.type === 'workspace' || w.type === undefined);
        items = [
            { icon: '◈', label: 'Workspace', action: () => { if (mainWs) switchWorkspace(mainWs.id); } },
            { icon: '💾', label: 'Save', action: () => { if (state._projectOpen) saveProject(); } },
            { icon: '🐍', label: '+ Python', action: () => { _addCodeChatTab('shared'); } },
            { icon: '🤖', label: '+ CellIntella', action: () => { _addCodeChatTab('cellintella'); } },
            { icon: '📦', label: '+ Git', action: () => { _addCodeChatTab('git'); } },
        ];
    } else {
        items = [
            { icon: '💾', label: 'Save', action: () => { if (state._projectOpen) saveProject(); } },
            { icon: '📂', label: 'Open', action: () => { showStartupDialog(); } },
            { icon: '💾', label: 'Save As', action: () => { saveProjectAs(); } },
            { icon: '🐍', label: 'Python', action: () => { openSharedConsole(); } },
            { icon: '🤖', label: 'CellIntella', action: () => { togglecinteliaPanel(); } },
            { icon: '📦', label: 'Git', action: () => { openGitConsole(); } },
        ];
    }

    const n = items.length;
    const outerR = 120;
    const innerR = 65;
    const navSize = outerR * 2 + 20;
    const gapAngle = 4;
    const segAngle = 360 / n;

    // Clamp to viewport
    let cx = ev.clientX;
    let cy = ev.clientY;
    const margin = outerR + 15;
    cx = Math.max(margin, Math.min(window.innerWidth - margin, cx));
    cy = Math.max(margin, Math.min(window.innerHeight - margin, cy));

    const overlay = document.createElement('div');
    overlay.className = 'radial-nav-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

    const nav = document.createElement('div');
    nav.className = 'radial-nav';
    nav.style.left = cx + 'px';
    nav.style.top = cy + 'px';
    nav.style.width = navSize + 'px';
    nav.style.height = navSize + 'px';

    const svgNS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'radial-nav-ring');
    svg.setAttribute('viewBox', `0 0 ${navSize} ${navSize}`);
    svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%';

    const ctr = navSize / 2;
    const accent = 'rgba(137,180,250,0.8)';

    items.forEach((item, i) => {
        const startDeg = -90 + i * segAngle + gapAngle / 2;
        const endDeg = -90 + (i + 1) * segAngle - gapAngle / 2;
        const startRad = startDeg * Math.PI / 180;
        const endRad = endDeg * Math.PI / 180;

        const x1o = ctr + outerR * Math.cos(startRad);
        const y1o = ctr + outerR * Math.sin(startRad);
        const x2o = ctr + outerR * Math.cos(endRad);
        const y2o = ctr + outerR * Math.sin(endRad);
        const x1i = ctr + innerR * Math.cos(endRad);
        const y1i = ctr + innerR * Math.sin(endRad);
        const x2i = ctr + innerR * Math.cos(startRad);
        const y2i = ctr + innerR * Math.sin(startRad);
        const largeArc = (endDeg - startDeg > 180) ? 1 : 0;

        const path = document.createElementNS(svgNS, 'path');
        path.setAttribute('d', [
            `M ${x1o} ${y1o}`,
            `A ${outerR} ${outerR} 0 ${largeArc} 1 ${x2o} ${y2o}`,
            `L ${x1i} ${y1i}`,
            `A ${innerR} ${innerR} 0 ${largeArc} 0 ${x2i} ${y2i}`,
            'Z'
        ].join(' '));
        path.setAttribute('fill', 'rgba(30,30,50,0.85)');
        path.setAttribute('stroke', accent);
        path.setAttribute('stroke-width', '1');
        path.setAttribute('cursor', 'pointer');
        path.style.transition = 'all .15s';

        path.onmouseenter = () => {
            path.setAttribute('fill', `rgba(137,180,250,0.25)`);
            path.setAttribute('stroke-width', '2.5');
        };
        path.onmouseleave = () => {
            path.setAttribute('fill', 'rgba(30,30,50,0.85)');
            path.setAttribute('stroke-width', '1');
        };
        path.onclick = () => { overlay.remove(); item.action(); };
        svg.appendChild(path);

        // Icon
        const midDeg = (startDeg + endDeg) / 2;
        const midRad = midDeg * Math.PI / 180;
        const iconR = innerR + (outerR - innerR) * 0.35;
        const ix = ctr + iconR * Math.cos(midRad);
        const iy = ctr + iconR * Math.sin(midRad) - 4;

        const iconEl = document.createElementNS(svgNS, 'text');
        iconEl.setAttribute('x', ix);
        iconEl.setAttribute('y', iy);
        iconEl.setAttribute('text-anchor', 'middle');
        iconEl.setAttribute('dominant-baseline', 'central');
        iconEl.setAttribute('font-size', '16');
        iconEl.setAttribute('pointer-events', 'none');
        iconEl.textContent = item.icon;
        svg.appendChild(iconEl);

        // Angular text
        const textR = innerR + (outerR - innerR) * 0.75;
        const tx = ctr + textR * Math.cos(midRad);
        const ty = ctr + textR * Math.sin(midRad);

        let textRotation = midDeg + 90;
        let normRot = ((textRotation % 360) + 360) % 360;
        if (normRot > 110 && normRot < 250) textRotation += 180;

        const textEl = document.createElementNS(svgNS, 'text');
        textEl.setAttribute('x', tx);
        textEl.setAttribute('y', ty);
        textEl.setAttribute('text-anchor', 'middle');
        textEl.setAttribute('dominant-baseline', 'central');
        textEl.setAttribute('font-size', '9');
        textEl.setAttribute('font-weight', '600');
        textEl.setAttribute('fill', 'rgba(255,255,255,0.9)');
        textEl.setAttribute('pointer-events', 'none');
        textEl.setAttribute('transform', `rotate(${textRotation}, ${tx}, ${ty})`);
        textEl.textContent = item.label;
        svg.appendChild(textEl);
    });

    // Hollow center
    const hollowCircle = document.createElementNS(svgNS, 'circle');
    hollowCircle.setAttribute('cx', ctr);
    hollowCircle.setAttribute('cy', ctr);
    hollowCircle.setAttribute('r', innerR - 2);
    hollowCircle.setAttribute('fill', 'rgba(15,15,25,0.95)');
    hollowCircle.setAttribute('stroke', accent);
    hollowCircle.setAttribute('stroke-width', '1');
    svg.appendChild(hollowCircle);

    nav.appendChild(svg);

    // Center label
    const center = document.createElement('div');
    center.className = 'radial-nav-center';
    center.style.borderColor = accent;
    center.innerHTML = ws ? ws.name : 'CelLAB';
    center.onclick = () => overlay.remove();
    nav.appendChild(center);

    overlay.appendChild(nav);
    document.body.appendChild(overlay);
}

function openRadialNavigator(pipelineId, ev) {
    // Remove existing overlay
    const existing = document.querySelector('.radial-nav-overlay');
    if (existing) existing.remove();

    const ws = getActiveWorkspace();
    if (!ws) return;
    const pipeline = ws.pipelines.get(pipelineId);
    if (!pipeline) return;
    const def = getPipelineDef(pipeline.type);
    const steps = def.steps || [];
    if (steps.length === 0) return;

    const accent = getAccent(pipeline.type);
    const stepIcons = ['📥', '🔬', '📊', '📈', '⚙️', '📦', '🎯', '🧪', '📉', '🔍'];
    const n = steps.length;
    const outerR = 135;
    const innerR = 80;
    const navSize = outerR * 2 + 20;

    // Clamp position to keep within viewport
    let cx = ev.clientX;
    let cy = ev.clientY;
    const margin = outerR + 15;
    cx = Math.max(margin, Math.min(window.innerWidth - margin, cx));
    cy = Math.max(margin, Math.min(window.innerHeight - margin, cy));

    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'radial-nav-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

    // Create radial container
    const nav = document.createElement('div');
    nav.className = 'radial-nav';
    nav.style.left = cx + 'px';
    nav.style.top = cy + 'px';
    nav.style.width = navSize + 'px';
    nav.style.height = navSize + 'px';

    // Build SVG ring with pie segments
    const svgNS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'radial-nav-ring');
    svg.setAttribute('viewBox', `0 0 ${navSize} ${navSize}`);
    svg.style.position = 'absolute';
    svg.style.top = '0';
    svg.style.left = '0';
    svg.style.width = '100%';
    svg.style.height = '100%';

    const ctr = navSize / 2;
    const gapAngle = 3;
    const segAngle = 360 / n;

    steps.forEach((step, i) => {
        const startDeg = -90 + i * segAngle + gapAngle / 2;
        const endDeg = -90 + (i + 1) * segAngle - gapAngle / 2;
        const startRad = startDeg * Math.PI / 180;
        const endRad = endDeg * Math.PI / 180;

        // Outer arc points
        const x1o = ctr + outerR * Math.cos(startRad);
        const y1o = ctr + outerR * Math.sin(startRad);
        const x2o = ctr + outerR * Math.cos(endRad);
        const y2o = ctr + outerR * Math.sin(endRad);
        // Inner arc points
        const x1i = ctr + innerR * Math.cos(endRad);
        const y1i = ctr + innerR * Math.sin(endRad);
        const x2i = ctr + innerR * Math.cos(startRad);
        const y2i = ctr + innerR * Math.sin(startRad);

        const largeArc = (endDeg - startDeg > 180) ? 1 : 0;

        // Segment path
        const path = document.createElementNS(svgNS, 'path');
        const d = [
            `M ${x1o} ${y1o}`,
            `A ${outerR} ${outerR} 0 ${largeArc} 1 ${x2o} ${y2o}`,
            `L ${x1i} ${y1i}`,
            `A ${innerR} ${innerR} 0 ${largeArc} 0 ${x2i} ${y2i}`,
            'Z'
        ].join(' ');
        path.setAttribute('d', d);

        const isOpen = [...ws.subtabs.values()].some(
            s => s.pipelineId === pipelineId && s.stepId === step.id
        );

        path.setAttribute('fill', isOpen
            ? `color-mix(in srgb, ${accent} 45%, #1a1a2e)`
            : 'rgba(30,30,50,0.85)');
        path.setAttribute('stroke', accent);
        path.setAttribute('stroke-width', isOpen ? '2' : '1');
        path.setAttribute('cursor', 'pointer');
        path.style.transition = 'all .15s';

        path.onmouseenter = () => {
            path.setAttribute('fill', `color-mix(in srgb, ${accent} 60%, #1a1a2e)`);
            path.setAttribute('stroke-width', '2.5');
        };
        path.onmouseleave = () => {
            path.setAttribute('fill', isOpen
                ? `color-mix(in srgb, ${accent} 45%, #1a1a2e)`
                : 'rgba(30,30,50,0.85)');
            path.setAttribute('stroke-width', isOpen ? '2' : '1');
        };
        path.onclick = () => {
            overlay.remove();
            openModuleSubtab(pipelineId, step.id);
        };
        svg.appendChild(path);

        // Icon at mid-radius, mid-angle
        const midDeg = (startDeg + endDeg) / 2;
        const midRad = midDeg * Math.PI / 180;
        const iconR = innerR + (outerR - innerR) * 0.35;
        const ix = ctr + iconR * Math.cos(midRad);
        const iy = ctr + iconR * Math.sin(midRad);

        const icon = document.createElementNS(svgNS, 'text');
        icon.setAttribute('x', ix);
        icon.setAttribute('y', iy - 4);
        icon.setAttribute('text-anchor', 'middle');
        icon.setAttribute('dominant-baseline', 'central');
        icon.setAttribute('font-size', '14');
        icon.setAttribute('pointer-events', 'none');
        icon.textContent = stepIcons[i] || '📋';
        svg.appendChild(icon);

        // Step number below icon
        const stepNum = document.createElementNS(svgNS, 'text');
        stepNum.setAttribute('x', ix);
        stepNum.setAttribute('y', iy + 10);
        stepNum.setAttribute('text-anchor', 'middle');
        stepNum.setAttribute('dominant-baseline', 'central');
        stepNum.setAttribute('font-size', '8');
        stepNum.setAttribute('font-weight', '700');
        stepNum.setAttribute('fill', 'rgba(255,255,255,0.5)');
        stepNum.setAttribute('pointer-events', 'none');
        stepNum.textContent = `${i + 1}/${n}`;
        svg.appendChild(stepNum);

        // Angular text — positioned at outer part, rotated to follow arc
        const textR = innerR + (outerR - innerR) * 0.75;
        const tx = ctr + textR * Math.cos(midRad);
        const ty = ctr + textR * Math.sin(midRad);

        const cleanName = step.name.replace(/^\d+\.\s*/, '');
        const displayName = cleanName.length > 14 ? cleanName.slice(0, 13) + '…' : cleanName;

        // Text rotation: follow CW tangent, flip if it would read right-to-left
        // CW tangent angle = midDeg + 90
        // Flip when tangent points leftward (cos < 0)
        let textRotation = midDeg + 90;
        // Normalize to [0, 360)
        let normRot = ((textRotation % 360) + 360) % 360;
        // If tangent points into left half (between 110° and 250°), flip by 180°
        // Using 110/250 instead of 90/270 gives tolerance near vertical positions
        if (normRot > 110 && normRot < 250) {
            textRotation += 180;
        }

        const textEl = document.createElementNS(svgNS, 'text');
        textEl.setAttribute('x', tx);
        textEl.setAttribute('y', ty);
        textEl.setAttribute('text-anchor', 'middle');
        textEl.setAttribute('dominant-baseline', 'central');
        textEl.setAttribute('font-size', '9');
        textEl.setAttribute('font-weight', '600');
        textEl.setAttribute('fill', 'rgba(255,255,255,0.9)');
        textEl.setAttribute('pointer-events', 'none');
        textEl.setAttribute('transform', `rotate(${textRotation}, ${tx}, ${ty})`);
        textEl.textContent = displayName;
        svg.appendChild(textEl);
    });

    // Hollow center circle (visual ring gap)
    const hollowCircle = document.createElementNS(svgNS, 'circle');
    hollowCircle.setAttribute('cx', ctr);
    hollowCircle.setAttribute('cy', ctr);
    hollowCircle.setAttribute('r', innerR - 2);
    hollowCircle.setAttribute('fill', 'rgba(15,15,25,0.95)');
    hollowCircle.setAttribute('stroke', accent);
    hollowCircle.setAttribute('stroke-width', '1');
    svg.appendChild(hollowCircle);

    nav.appendChild(svg);

    // Center button
    const center = document.createElement('div');
    center.className = 'radial-nav-center';
    center.style.borderColor = accent;
    center.innerHTML = pipeline.shortName;
    center.onclick = () => overlay.remove();
    nav.appendChild(center);

    overlay.appendChild(nav);
    document.body.appendChild(overlay);
}

// ═════════════════════════════════════════════
// PIPELINES
// ═════════════════════════════════════════════

function createPipeline(type, x, y) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    state.moduleCounter++;
    const pid = `${type}-${state.moduleCounter}`;
    const def = getPipelineDef(type);

    // Auto-layout if no explicit position
    if (x === undefined || y === undefined) {
        const count = ws.pipelines.size;
        const col = count % 3;
        const row = Math.floor(count / 3);
        const pos = findNearestFreeCell(ws, col * GRID_X, row * GRID_Y);
        x = pos.x;
        y = pos.y;
    } else {
        const pos = findNearestFreeCell(ws, x, y);
        x = pos.x;
        y = pos.y;
    }

    ws.pipelines.set(pid, {
        id: pid, type, name: `${def.name} - ${state.moduleCounter}`,
        shortName: `${def.short}-${state.moduleCounter}`,
        steps: def.steps.map(s => ({ ...s, status: 'idle' })),
        x, y,
    });

    renderViewport();
    updateStatus(`Created ${def.name} pipeline`);

    // Sync to backend
    const pipeline = ws.pipelines.get(pid);
    syncPipelineToBackend(ws, pipeline);
}

function deletePipeline(pid, ev) {
    if (ev) ev.stopPropagation();
    const ws = getActiveWorkspace();
    if (!ws) return;
    if (!confirm('Delete pipeline and close all its tabs?')) return;
    closeSubtabsForPipeline(pid);
    ws.pipelines.delete(pid);
    renderViewport();
    updateStatus('Pipeline deleted');

    // Sync to backend
    if (state._projectOpen) {
        api(`pipeline/${ws.id}/${pid}/delete`, 'DELETE');
    }
}

function selectPipeline(pid, ev) {
    if (ev) ev.stopPropagation();
    const ws = getActiveWorkspace();
    const p = ws?.pipelines.get(pid);
    if (!p) return;
    document.querySelectorAll('.pipeline-node').forEach(n => n.classList.remove('selected'));
    const node = document.getElementById(`node-${pid}`);
    if (node) node.classList.add('selected');

    updatePropertiesPanel(pid);
}

// ═════════════════════════════════════════════
// MODULES (standalone, single sub-tab)
// ═════════════════════════════════════════════
// Modules live on the canvas as single-row nodes (no step list). They are
// created by dragging from the Modules toolbox — same path as pipelines —
// and rendered differently in buildNode(). Opening a module never creates
// per-step sub-tabs; it creates exactly one sub-tab whose tree contains the
// former "steps" as top-level groups. Inspired by ANSYS DesignModeler.
//
// Registered module types that render as single-row nodes on the canvas:
const MODULE_TYPES = new Set(['cellvisia', 'associa', 'cellade', 'cellfade', 'annotade']);

function openModuleTab(pipelineId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const pipeline = ws.pipelines.get(pipelineId);
    if (!pipeline) return;

    // Already open? Just switch to it (idempotent).
    for (const [subId, sub] of ws.subtabs) {
        if (sub.type === 'module' && sub.pipelineId === pipelineId && sub.stepId == null) {
            switchSubtab(subId);
            return;
        }
    }

    const def = getPipelineDef(pipeline.type);
    state.subtabCounter++;
    const subId = `subtab-${state.subtabCounter}`;

    const newTab = {
        id: subId, type: 'module',
        label: def.name,
        icon: def.icon,
        pipelineId,              // tied to the canvas node
        stepId: null,            // whole module, no specific step
        moduleType: pipeline.type,
        closeable: true,
        activeTreeItem: null,
        insertedResults: [],
    };

    ws.subtabs.set(subId, newTab);
    switchSubtab(subId);
    updateStatus(`Opened ${def.name}`);
}

// ═════════════════════════════════════════════
// RENDER ALL
// ═════════════════════════════════════════════

function renderAll() {
    renderWorkspaceTabs();
    renderSubtabs();
    renderLeftPanel();
    renderViewport();
    updateOpenModulesList();
}

// ── Workspace Tabs ──────────────────────────

function renderWorkspaceTabs() {
    const c = document.getElementById('workspaceTabsScroll');
    c.innerHTML = '';
    for (const [wsId, ws] of state.workspaces) {
        const t = document.createElement('div');
        const isCodeChat = ws.type === 'codechat';
        t.className = `ws-tab ${isCodeChat ? 'ws-tab-codechat' : ''} ${wsId === state.activeWorkspace ? 'active' : ''}`;
        t.onclick = () => switchWorkspace(wsId);
        if (!isCodeChat) t.ondblclick = () => renameWorkspace(wsId);
        const icon = isCodeChat ? '⌘' : '◈';
        const showClose = !(isCodeChat && ws._isDefault);
        const closeBtn = showClose ? `<span class="ws-tab-close" onclick="closeWorkspace('${wsId}',event)">×</span>` : '';
        t.innerHTML = `<span class="ws-tab-icon">${icon}</span><span class="ws-tab-label">${ws.name}</span>${closeBtn}`;
        c.appendChild(t);
    }
}

// ── Grouped Sub-Tabs ────────────────────────

function renderSubtabs() {
    const ws = getActiveWorkspace();
    if (!ws) return;
    if (ws.type === 'codechat') return; // codechat has no subtabs
    const bar = document.getElementById('subtabScroll');
    bar.innerHTML = '';

    // 1. Canvas/Home tab (always first)
    const canvasSub = [...ws.subtabs.values()].find(s => s.type === 'canvas');
    if (canvasSub) {
        bar.appendChild(makeSubtabEl(canvasSub, ws));
    }

    // 2. Group module tabs by pipelineId
    const groups = new Map(); // pipelineId → [subtab, ...]
    for (const sub of ws.subtabs.values()) {
        if (sub.type !== 'module') continue;
        if (!groups.has(sub.pipelineId)) groups.set(sub.pipelineId, []);
        groups.get(sub.pipelineId).push(sub);
    }

    for (const [pid, tabs] of groups) {
        const pipeline = ws.pipelines.get(pid);
        if (!pipeline) continue;

        const hasActive = tabs.some(t => t.id === ws.activeSubtab);
        const isCollapsed = state.collapsedGroups.has(pid);
        const isFocused = state.focusedGroups.has(pid);
        const focusedStepId = state.focusedGroups.get(pid);

        const group = document.createElement('div');
        group.className = `tab-group ${hasActive ? 'has-active' : ''}`;

        // Group header (colored by pipeline type)
        const header = document.createElement('div');
        header.className = `tab-group-header ${pipeline.type}`;
        // Click on header (not collapse icon) → open radial navigator
        header.onclick = (e) => {
            if (e.target.closest('.group-collapse-btn') || e.target.closest('.group-close')) return;
            openRadialNavigator(pid, e);
        };
        header.oncontextmenu = (e) => {
            e.preventDefault();
            if (e.target.closest('.group-collapse-btn') || e.target.closest('.group-close')) return;
            openRadialNavigator(pid, e);
        };
        const collapseState = isCollapsed ? 'collapsed' : (isFocused ? '' : '');
        const arrowSvg = `<svg width="10" height="10" viewBox="0 0 10 10" style="transition:transform .15s${isCollapsed ? ';transform:rotate(-90deg)' : ''}"><path d="M2 3.5L5 6.5L8 3.5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>`;
        header.innerHTML = `
            <span class="group-icon">${getPipelineDef(pipeline.type).icon}</span>
            <span class="group-label">${pipeline.shortName}</span>
            <span class="group-collapse-btn ${isCollapsed ? 'collapsed' : ''}" onclick="toggleTabGroup('${pid}');event.stopPropagation()">${arrowSvg}</span>
            <span class="group-close" onclick="closeTabGroup('${pid}',event)">×</span>
        `;

        // Step tabs — three modes: collapsed, focused, expanded
        const tabsContainer = document.createElement('div');
        if (isCollapsed) {
            tabsContainer.className = 'tab-group-tabs collapsed';
        } else if (isFocused) {
            tabsContainer.className = 'tab-group-tabs';
            // Find tabs before and after the focused tab
            const focusedIdx = tabs.findIndex(t => t.stepId === focusedStepId);
            const tabsBefore = focusedIdx > 0 ? tabs.slice(0, focusedIdx) : [];
            const tabsAfter = focusedIdx < tabs.length - 1 ? tabs.slice(focusedIdx + 1) : [];
            const focusedTab = focusedIdx >= 0 ? tabs[focusedIdx] : null;

            // Left spring (tabs before focused)
            if (tabsBefore.length > 0) {
                const springLeft = document.createElement('div');
                springLeft.className = 'tab-spring';
                springLeft.title = tabsBefore.map(t => t.label).join(', ');
                springLeft.innerHTML = `<span class="spring-dots">${'·'.repeat(tabsBefore.length)}</span>`;
                springLeft.onclick = () => {
                    state.focusedGroups.delete(pid);
                    renderSubtabs();
                };
                const accent = getAccent(pipeline.type);
                springLeft.style.borderTop = `2px solid ${accent}`;
                tabsContainer.appendChild(springLeft);
            }

            // Focused tab
            if (focusedTab) {
                tabsContainer.appendChild(makeSubtabEl(focusedTab, ws, 0, 1));
            }

            // Right spring (tabs after focused)
            if (tabsAfter.length > 0) {
                const springRight = document.createElement('div');
                springRight.className = 'tab-spring';
                springRight.title = tabsAfter.map(t => t.label).join(', ');
                springRight.innerHTML = `<span class="spring-dots">${'·'.repeat(tabsAfter.length)}</span>`;
                springRight.onclick = () => {
                    state.focusedGroups.delete(pid);
                    renderSubtabs();
                };
                const accent = getAccent(pipeline.type);
                springRight.style.borderTop = `2px solid ${accent}`;
                tabsContainer.appendChild(springRight);
            }
        } else {
            tabsContainer.className = 'tab-group-tabs';
            const totalTabs = tabs.length;
            tabs.forEach((sub, idx) => tabsContainer.appendChild(makeSubtabEl(sub, ws, idx, totalTabs)));
        }

        group.appendChild(header);
        group.appendChild(tabsContainer);
        bar.appendChild(group);
    }
}

function makeSubtabEl(sub, ws, tabIdx = 0, totalTabs = 1) {
    const el = document.createElement('div');
    const isActive = sub.id === ws.activeSubtab;
    el.className = `subtab ${isActive ? 'active' : ''} ${sub.type === 'canvas' ? 'canvas-tab' : ''}`;
    el.onclick = () => switchSubtab(sub.id);

    // Apply pipeline accent color with gradient fade across tabs
    if (sub.type === 'module' && sub.moduleType) {
        const accent = getAccent(sub.moduleType);
        // Gradient: first tab 30%, fading to ~8% for last tab
        const basePct = Math.max(8, 30 - (tabIdx * 22 / Math.max(totalTabs - 1, 1)));
        const activePct = basePct + 12;

        el.style.borderTop = `2px solid ${accent}`;
        if (isActive) {
            el.style.background = `color-mix(in srgb, ${accent} ${Math.round(activePct)}%, var(--surface-2))`;
            el.style.borderTopColor = accent;
            el.style.color = 'rgba(255,255,255,.95)';
        } else {
            el.style.background = `color-mix(in srgb, ${accent} ${Math.round(basePct)}%, var(--surface-1))`;
        }
    }

    el.innerHTML = `
        <span class="subtab-icon">${sub.icon}</span>
        <span class="subtab-label">${sub.label}</span>
        ${sub.closeable ? `<span class="subtab-close" onclick="closeSubtab('${sub.id}',event)">×</span>` : ''}
    `;
    return el;
}

// ── Left Panel ──────────────────────────────

function renderLeftPanel() {
    const ws = getActiveWorkspace();
    if (ws && ws.type === 'codechat') return;
    const panel = document.getElementById('leftPanel');
    const resizer = document.getElementById('leftResizer');
    const sub = ws ? ws.subtabs.get(ws.activeSubtab) : null;

    // Only show toolbox on canvas/schematic view (not task manager)
    if (_taskManagerActive || !sub || sub.type !== 'canvas') {
        panel.style.display = 'none';
        if (resizer) resizer.style.display = 'none';
        return;
    }

    panel.style.display = '';
    if (resizer) resizer.style.display = '';

    panel.innerHTML = `
        <div class="left-panel-header">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><rect x="1" y="1" width="10" height="10" rx="1" stroke="currentColor" stroke-width="1.2"/><path d="M1 4h10M4 4v7" stroke="currentColor" stroke-width="1.2"/></svg>
            Toolbox
        </div>
        <div class="left-panel-body">
            ${buildCat('Pipelines', 'pipelines', [
                { id:'fastia', icon: ICONS.fastia(14), label:'FASTIA — Focal Adhesion' },
                { id:'immunia', icon: ICONS.immunia(14), label:'IMMUNIA — Immune Cell' },
                { id:'cornealia', icon:'👁', label:'Cornealia — Single Image' },
                { id:'cornealia_batch', icon:'👁', label:'Cornealia — Batch' },
                { id:'cellfade', icon:'🧫', label:'CellFADE — FA (DL)' },
            ], true)}
            ${buildCat('Modules', 'modules', [
                { id:'cellvisia', icon: ICONS.cellvisia(14), label:'CellVisia — Image Processing', asModule: true },
                { id:'associa', icon: ICONS.associa(14), label:'Associa — Signal Coupling', asModule: true },
                { id:'cellade', icon: ICONS.cellade(14), label:'CellADE — Cell Segmentation', asModule: true },
                { id:'cellfade', icon: ICONS.cellfade(14), label:'CellFADE — FA Detection', asModule: true },
                { id:'data-import', icon:'📥', label:'Data Import' },
                { id:'detection', icon:'🔍', label:'Detection' },
                { id:'tracking', icon:'📈', label:'Tracking' },
                { id:'analysis', icon:'📊', label:'Analysis' },
            ], true)}
            ${buildCat('Tools', 'tools', [
                { id:'annotade', icon: ICONS.annotade(14), label:'AnnotADE — Annotation', asModule: true },
                { id:'plot-manager', icon:'📈', label:'Plot Manager' },
                { id:'file-explorer', icon:'📁', label:'File Explorer' },
            ])}
        </div>`;
}

function buildCat(title, catId, items, open = false) {
    return `<div class="toolbox-category">
        <div class="cat-header" onclick="toggleCat(this)">
            <span class="cat-arrow ${open ? 'open' : ''}">▶</span><span>${title}</span>
        </div>
        <div class="cat-body ${open ? 'open' : ''}">
            ${items.map(i => `<div class="cat-item" draggable="true" ondragstart="startDrag(event,'${i.id}')" ondblclick="createPipelineOnCanvas('${i.id}')"><span class="cat-item-icon">${i.icon}</span><span>${i.label}</span></div>`).join('')}
        </div>
    </div>`;
}

// ── Viewport ────────────────────────────────

function renderViewport() {
    const ws = getActiveWorkspace();
    if (!ws) return;
    if (ws.type === 'codechat') return; // codechat renders its own viewport
    const vp = document.getElementById('viewport');
    const sub = ws.subtabs.get(ws.activeSubtab);

    if (_taskManagerActive) renderTaskManagerView(vp, ws);
    else if (!sub || sub.type === 'canvas') renderCanvasView(vp, ws);
    else renderModuleView(vp, sub, ws);
}

function renderCanvasView(vp, ws) {
    const cv = document.createElement('div');
    cv.className = 'canvas-view fade-in';
    cv.ondragover = e => { e.preventDefault(); if (!cv.classList.contains('show-grid')) showCanvasGrid(true); };
    cv.ondragleave = (e) => { if (e.target === cv) showCanvasGrid(false); };
    cv.ondrop = e => { showCanvasGrid(false); handleCanvasDrop(e); };
    cv.oncontextmenu = (e) => {
        // Only trigger on empty canvas, not on pipeline nodes
        if (e.target.closest('.pipeline-node')) return;
        e.preventDefault();
        openWorkspaceRadialNav(e);
    };

    if (ws.pipelines.size === 0) {
        cv.innerHTML = `<div class="canvas-placeholder"><h3>◈ ${ws.name}</h3><p>Drag a pipeline from the Toolbox, or double-click to create</p><p style="margin-top:6px;font-size:10px;opacity:.6">Steps open as full-viewport tabs grouped by pipeline</p></div>`;
    }

    for (const [pid, p] of ws.pipelines) cv.appendChild(buildNode(p));

    vp.innerHTML = '';
    vp.appendChild(cv);
    for (const [pid] of ws.pipelines) makeDraggable(document.getElementById(`node-${pid}`), cv);
}

function buildNode(p) {
    const def = getPipelineDef(p.type);
    const isModule = MODULE_TYPES.has(p.type);
    const n = document.createElement('div');
    n.className = 'pipeline-node' + (isModule ? ' module-node' : '');
    n.id = `node-${p.id}`;
    n.style.left = p.x + 'px'; n.style.top = p.y + 'px';
    n.onclick = e => selectPipeline(p.id, e);
    n.oncontextmenu = e => showPipelineContextMenu(e, p);

    if (isModule) {
        // Module nodes: single-row; double-click opens the module window.
        // No step body — steps live inside the module's tree instead.
        n.innerHTML = `
            <div class="pipeline-node-header ${p.type}" ondblclick="event.stopPropagation();openModuleTab('${p.id}')" title="Double-click to open">
                <span>${def.iconLg}</span><span style="flex:1">${p.name}</span>
                <span style="cursor:pointer;opacity:.7;font-size:13px" onclick="deletePipeline('${p.id}',event)">×</span>
            </div>`;
        return n;
    }

    // Pipeline nodes: header + list of step rows.
    n.innerHTML = `
        <div class="pipeline-node-header ${p.type}" ondblclick="event.stopPropagation();openAllSteps('${p.id}')">
            <span>${def.iconLg}</span><span style="flex:1">${p.name}</span>
            <span style="cursor:pointer;opacity:.7;font-size:13px" onclick="deletePipeline('${p.id}',event)">×</span>
        </div>
        <div class="pipeline-node-body">
            ${p.steps.map(s => {
                const hasTab = isStepOpen(p.id, s.id);
                const doneCheck = s.status === 'done' ? '<span class="step-done-check">✓</span>' : '';
                return `<div class="pipeline-step ${hasTab ? 'has-tab' : ''} ${s.status}" ondblclick="openModuleSubtab('${p.id}','${s.id}')">
                    <span class="step-status ${s.status}"></span><span class="step-label">${s.name}</span>${doneCheck}<span class="step-open-indicator">⇱</span>
                </div>`;
            }).join('')}
        </div>`;
    return n;
}

// ═════════════════════════════════════════════
// THREE-COLUMN MODULE VIEW
// ═════════════════════════════════════════════

function toggleRunFolder(folderEl) {
    if (!folderEl) return;
    const folder = folderEl.classList?.contains('mtree-run-folder') ? folderEl : folderEl.closest('.mtree-run-folder');
    if (!folder) return;
    const runId = folder.dataset.runId;
    const body = folder.querySelector('.run-folder-body');
    const arrow = folder.querySelector('.run-folder-arrow');
    if (!body) return;

    const isOpen = body.style.display !== 'none';
    body.style.display = isOpen ? 'none' : '';
    if (arrow) arrow.textContent = isOpen ? '▶' : '▼';

    // Persist collapsed state
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (sub && runId) {
        if (!sub._collapsedRuns) sub._collapsedRuns = {};
        sub._collapsedRuns[runId] = isOpen;  // true = now collapsed
    }
}

function _buildAssociationRunsSection(sub, inserted) {
    const collapsed = sub._collapsedRuns || {};
    const runItems = inserted.filter(r => r._isRun);
    const edgeItems = inserted.filter(r => r._isEdge);
    const nonRunItems = inserted.filter(r => !r._isRun && !r._isEdge);

    let edgeHtml = '';
    for (const e of edgeItems) {
        edgeHtml += `
        <div class="mtree-item result-item" data-result="${e.plotType}" onclick="onInsertedResultClick('${sub.id}','${e.plotType}')" oncontextmenu="showResultContextMenu(event,'${sub.id}','${e.plotType}')">
            <span class="mtree-item-icon">${e.icon}</span>
            <span style="flex:1">${e.label}</span>
            <span class="result-remove" onclick="event.stopPropagation();removeInsertedResult('${sub.id}','${e.plotType}')" title="Remove">×</span>
        </div>`;
    }

    let runsHtml = '';
    if (runItems.length === 0 && edgeItems.length === 0) {
        runsHtml = '<div class="mtree-placeholder">Right-click for edge plots. Run association for coupling results.</div>';
    } else {
        for (const run of runItems) {
            const runId = run._runId;
            const runPlots = nonRunItems.filter(r => r._runId === runId);
            const isCollapsed = collapsed[runId] || false;
            const arrowChar = runPlots.length === 0 ? '▷' : (isCollapsed ? '▶' : '▼');

            runsHtml += `
            <div class="mtree-run-folder" data-run-id="${runId}">
                <div class="mtree-item" onclick="toggleRunFolder(this.parentElement);selectMTreeItem('${sub.id}','${run.plotType}',this)" oncontextmenu="event.preventDefault();event.stopPropagation();${sub.moduleType === 'immunia' ? 'showIMMUNIAAssocRunMenu' : 'showAssocRunContextMenu'}(event,'${sub.id}','${runId}')" style="font-weight:600">
                    <span class="run-folder-arrow" style="font-size:10px;width:14px;text-align:center;display:inline-block;flex-shrink:0">${arrowChar}</span>
                    <span class="mtree-item-icon" style="margin-left:0">📁</span>
                    <span style="flex:1;font-size:11px">${run.label}</span>
                    <span style="font-size:10px;color:var(--text-tertiary);margin-right:4px">${runPlots.length || ''}</span>
                </div>
                <div class="run-folder-body"${isCollapsed ? ' style="display:none"' : ''}>
                ${runPlots.map(r => `
                <div class="mtree-item result-item" style="padding-left:36px;font-size:11px;opacity:.85" data-result="${r.plotType}" onclick="onInsertedResultClick('${sub.id}','${r.plotType}')" oncontextmenu="showResultContextMenu(event,'${sub.id}','${r.plotType}')">
                    <span class="mtree-item-icon">${r.icon}</span>
                    <span style="flex:1">${r.label}</span>
                    <span class="result-remove" onclick="event.stopPropagation();removeInsertedResult('${sub.id}','${r.plotType}')" title="Remove">×</span>
                </div>`).join('')}
                </div>
            </div>`;
        }
    }

    return `<div class="mtree-section">
        <div class="mtree-section-head assoc-results-header" onclick="toggleMTreeSection(this)" oncontextmenu="event.preventDefault();event.stopPropagation();showAssocEdgePlotsMenu(event,'${sub.id}')">
            <span class="cat-arrow open">▶</span>
            <span style="font-size:var(--fs-xs);color:var(--text-secondary);text-transform:uppercase;letter-spacing:.5px;font-weight:700">Results</span>
            <span style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-left:auto">${runItems.length + edgeItems.length || ''}</span>
        </div>
        <div class="mtree-section-body open">${edgeHtml}${runsHtml}</div>
    </div>`;
}

function _buildResultsSection(sub, title, items, statusIcons, section) {
    let placeholder;
    if (sub.stepId === 'examination' && section === 'individual') {
        placeholder = '<div class="mtree-placeholder">Select an FA and click Detailed Analysis</div>';
    } else if (section === 'individual') {
        placeholder = '<div class="mtree-placeholder">Use Track Inspector to inspect tracks</div>';
    } else {
        placeholder = '<div class="mtree-placeholder">Right-click here to insert results</div>';
    }
    return `<div class="mtree-section">
        <div class="mtree-section-head results-header" data-subid="${sub.id}" data-module="${sub.moduleType}" data-step="${sub.stepId || sub.moduleType}" data-section="${section}" onclick="toggleMTreeSection(this)">
            <span class="cat-arrow open">▶</span>
            <span style="font-size:var(--fs-xs);color:var(--text-secondary);text-transform:uppercase;letter-spacing:.5px;font-weight:700">${title}</span>
            <span style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-left:auto">${items.length || ''}</span>
        </div>
        <div class="mtree-section-body open">
            ${items.length === 0
                ? placeholder
                : items.map(r => `
                    <div class="mtree-item result-item${r.status === 'stale' ? ' result-stale' : ''}" data-result="${r.plotType}" onclick="onInsertedResultClick('${sub.id}','${r.plotType}')" oncontextmenu="showResultContextMenu(event,'${sub.id}','${r.plotType}')" ${r.status === 'stale' ? 'title="Outdated — click to regenerate"' : ''}>
                        <span class="mtree-item-icon">${r.status === 'done' ? r.icon : statusIcons[r.status] || '📊'}</span>
                        <span style="flex:1">${r.label}</span>${r.status === 'stale' ? '<span style="font-size:9px;color:var(--status-warning);margin-right:4px">outdated</span>' : ''}<span class="result-remove" onclick="event.stopPropagation();removeInsertedResult('${sub.id}','${r.plotType}')" title="Remove">×</span>
                    </div>
                `).join('')}
        </div>
    </div>`;
}

function renderModuleView(vp, sub, ws) {
    const p = ws.pipelines.get(sub.pipelineId);
    const stepDef = getStepDef(sub.moduleType, sub.stepId);
    const accent = getAccent(sub.moduleType);
    const treeItems = getModuleTreeItems(sub.moduleType, sub.stepId);
    const activeItem = sub.activeTreeItem || { id: treeItems[0]?.id || 'params' };

    // Group tree items by their group field
    const groups = new Map();
    for (const item of treeItems) {
        const g = item.group || 'General';
        if (!groups.has(g)) groups.set(g, []);
        groups.get(g).push(item);
    }

    // Build tree HTML
    let treeHtml = '';

    // CellVisia module-level view: fully dynamic, insert-based feature tree.
    if (isCellVisiaModule(sub)) {
        treeHtml = buildCellVisiaTree(sub, activeItem);
    } else {
    const isKinetics = sub.moduleType === 'fastia' && sub.stepId === 'kinetics';
    const isExamination = sub.moduleType === 'fastia' && sub.stepId === 'examination';
    const isCellADE_init = sub.moduleType === 'cellade';
    const isCellFADE_init = sub.moduleType === 'cellfade';
    const hasResults_init = stepHasResults(sub.moduleType, sub.stepId);

    // Pre-build results HTML
    let initResultsHtml = '';
    if (hasResults_init) {
        const statusIcons = { generating: '⏳', done: '✅', error: '❌', stale: '⟳' };
        const inserted = sub.insertedResults || [];

        if (isKinetics) {
            const collectiveIds = ['rate_distributions', 'rates_by_group', 'assembly_vs_disassembly', 'time_to_peak', 'rate_quality', 'fa_area_distribution', 'intensity_spaghetti', 'intensity_spaghetti_peak'];
            const collective = inserted.filter(r => collectiveIds.includes(r.plotType));
            const individual = inserted.filter(r => !collectiveIds.includes(r.plotType));

            initResultsHtml += _buildResultsSection(sub, 'Collective Results', collective, statusIcons, 'collective');

            const indivItems = treeItems.filter(i => i.group === 'Individual');
            if (indivItems.length > 0) {
                initResultsHtml += buildMTreeGroup('Individual', indivItems, activeItem, sub.id);
            }

            initResultsHtml += _buildResultsSection(sub, 'Individual Results', individual, statusIcons, 'individual');
        } else if (isExamination) {
            initResultsHtml += _buildResultsSection(sub, 'Detailed Analyses', inserted, statusIcons, 'individual');
        } else if ((sub.moduleType === 'fastia' && sub.stepId === 'association') ||
                   (sub.moduleType === 'immunia' && sub.stepId === 'signal_association') ||
                   (sub.moduleType === 'immunia' && sub.stepId === 'graph_theory')) {
            initResultsHtml += _buildAssociationRunsSection(sub, inserted);
        } else {
            const resultsTitle = (isCellADE_init || isCellFADE_init) ? '3. Results' : 'Results';
            initResultsHtml += _buildResultsSection(sub, resultsTitle, inserted, statusIcons, 'all');
        }
    }

    for (const [groupName, items] of groups) {
        if (isKinetics && groupName === 'Individual') continue;

        // For CellADE/CellFADE: insert Results before Export
        if ((isCellADE_init || isCellFADE_init) && groupName.includes('Export') && initResultsHtml) {
            treeHtml += initResultsHtml;
            initResultsHtml = '';
        }

        treeHtml += buildMTreeGroup(groupName, items, activeItem, sub.id);
    }

    // Append results at end for non-CellADE (or if no Export group)
    if (initResultsHtml) {
        treeHtml += initResultsHtml;
    }
    }

    vp.innerHTML = `
    <div class="module-view fade-in" >
        <div class="module-view-bar" style="border-left:4px solid ${accent};">
            <div class="mvt-breadcrumb">
                <span class="mvt-accent" style="background:${accent}"></span>
                ${sub.stepId == null
                    ? `<span class="mvt-step">${stepDef.name}</span>`
                    : `<span>${p ? p.shortName : ''}</span>
                       <span style="opacity:.4">→</span>
                       <span class="mvt-step">${stepDef.name}</span>`}
            </div>
        </div>
        <div class="module-columns">

            <div class="module-cols-left" id="colsLeft-${sub.id}">
                <div class="module-col-tree" id="colTree-${sub.id}">
                    <div class="module-col-tree-header" style="border-left:3px solid ${accent};">${stepDef.name}</div>
                    <div class="module-col-tree-body" id="moduleTree-${sub.id}">
                        ${treeHtml}
                    </div>
                </div>

                <div class="col-resizer" onmousedown="initColResize(event, this)"></div>

                <div class="module-col-settings" id="colSettings-${sub.id}">
                    <div class="module-col-settings-header" id="settingsHeader-${sub.id}">
                        <span>⚙️</span> <span id="settingsTitle-${sub.id}">${getActiveItemLabel(treeItems, activeItem)}</span>
                    </div>
                    <div class="module-col-settings-body" id="settingsBody-${sub.id}">
                        ${renderSettingsContent(sub.moduleType, sub.stepId, activeItem)}
                    </div>
                </div>
            </div>

            <div class="col-resizer-main" onmousedown="initColResize(event, this)">
                <span class="col-toggle-btn" onclick="toggleLeftCols('${sub.id}')" title="Toggle panels">◀</span>
            </div>

            <div class="module-col-graphics" style="contain:layout paint;transform:translateZ(0)">
                <div class="module-col-graphics-header" style="display:flex;align-items:center;gap:0;padding:0">
                    <div class="cv-gfx-tab" id="gfxTabInput-${sub.id}" onclick="cvSwitchGfxTab('${sub.id}','input')"
                         style="padding:6px 14px;cursor:pointer;font-size:var(--fs-xs);font-weight:600;color:var(--text-tertiary);border-bottom:2px solid transparent;user-select:none;opacity:.6">
                        📥 Input
                    </div>
                    <div class="cv-gfx-tab active" id="gfxTabGraphics-${sub.id}" onclick="cvSwitchGfxTab('${sub.id}','graphics')"
                         style="padding:6px 14px;cursor:pointer;font-size:var(--fs-xs);font-weight:600;color:var(--text-secondary);border-bottom:2px solid var(--brand-accent);user-select:none">
                        🖼 Graphics
                    </div>
                    <div class="cv-gfx-tab" id="gfxTabTables-${sub.id}" onclick="cvSwitchGfxTab('${sub.id}','tables')"
                         style="padding:6px 14px;cursor:pointer;font-size:var(--fs-xs);font-weight:600;color:var(--text-tertiary);border-bottom:2px solid transparent;user-select:none;opacity:.6">
                        📊 Tables
                    </div>
                    <div class="cv-gfx-tab" id="gfxTabFigures-${sub.id}" onclick="cvSwitchGfxTab('${sub.id}','figures')"
                         style="padding:6px 14px;cursor:pointer;font-size:var(--fs-xs);font-weight:600;color:var(--text-tertiary);border-bottom:2px solid transparent;user-select:none;opacity:.6">
                        📈 Figures
                    </div>
                    <span style="flex:1"></span>
                </div>
                <div class="module-col-graphics-body" id="graphicsBody-${sub.id}">
                    <div class="graphics-placeholder">
                        <div style="font-size:24px;margin-bottom:6px;opacity:.4">🖼</div>
                        <p>Preview and results will appear here</p>
                    </div>
                </div>
                <div id="tablesBody-${sub.id}" style="display:none;flex:1;overflow:auto;background:var(--surface-0);flex-direction:column">
                    <div style="color:var(--text-tertiary);font-size:var(--fs-xs);padding:20px;text-align:center">
                        <div style="font-size:24px;margin-bottom:8px;opacity:.4">📊</div>
                        Apply a Measurement to see tables here.
                    </div>
                </div>
                <div id="figuresBody-${sub.id}" style="display:none;flex:1;overflow:auto;background:var(--surface-0);flex-direction:column">
                    <div style="color:var(--text-tertiary);font-size:var(--fs-xs);padding:20px;text-align:center">
                        <div style="font-size:24px;margin-bottom:8px;opacity:.4">📈</div>
                        Apply a Measurement to see figures here.
                    </div>
                </div>
            </div>

        </div>
    </div>`;

    // ── Restore local params after DOM is set ──
    setTimeout(() => {
        const bodyEl = document.getElementById(`settingsBody-${sub.id}`);
        if (bodyEl && sub._localParams) {
            _restoreParams(bodyEl, sub, activeItem.id);
        }

        // Add workspace radial nav on right-click (only on areas without existing context menu)
        const modView = vp.querySelector('.module-view');
        if (modView) {
            modView.addEventListener('contextmenu', (e) => {
                // Skip if target has its own context menu
                const hasOwnMenu = e.target.closest('.result-item, .mtree-item, .ctx-item, .console-input, .form-input, .run-log, textarea, input');
                if (hasOwnMenu) return;
                // Skip if any ancestor between target and module-view has oncontextmenu
                let el = e.target;
                while (el && el !== modView) {
                    if (el.getAttribute && el.getAttribute('oncontextmenu')) return;
                    el = el.parentElement;
                }
                e.preventDefault();
                openWorkspaceRadialNav(e);
            });
        }
    }, 0);
}

function buildMTreeGroup(groupName, items, activeItem, subId) {
    return `<div class="mtree-section">
        <div class="mtree-section-head" onclick="toggleMTreeSection(this)">
            <span class="cat-arrow open">▶</span>
            <span style="font-size:var(--fs-xs);color:var(--text-secondary);text-transform:uppercase;letter-spacing:.5px;font-weight:700">${groupName}</span>
        </div>
        <div class="mtree-section-body open">
            ${items.map(i => `<div class="mtree-item ${activeItem.id === i.id ? 'active' : ''}" onclick="selectMTreeItem('${subId}','${i.id}',this)"><span class="mtree-item-icon">${i.icon}</span><span>${i.label}</span></div>`).join('')}
        </div>
    </div>`;
}

function renderModuleTree(sub) {
    const treeBody = document.getElementById(`moduleTree-${sub.id}`);
    if (!treeBody) return;

    // CellVisia feature tree: fully dynamic, insert-based (not a fixed list).
    if (isCellVisiaModule(sub)) {
        treeBody.innerHTML = buildCellVisiaTree(sub, sub.activeTreeItem);
        return;
    }

    const treeItems = getModuleTreeItems(sub.moduleType, sub.stepId);
    const activeItem = sub.activeTreeItem || { id: treeItems[0]?.id || 'params' };

    // Group tree items
    const groups = new Map();
    for (const item of treeItems) {
        const g = item.group || 'General';
        if (!groups.has(g)) groups.set(g, []);
        groups.get(g).push(item);
    }

    let html = '';
    const isKinetics2 = sub.moduleType === 'fastia' && sub.stepId === 'kinetics';
    const isExamination2 = sub.moduleType === 'fastia' && sub.stepId === 'examination';
    const isCellADE = sub.moduleType === 'cellade';
    const isCellFADE = sub.moduleType === 'cellfade';
    const hasResults = stepHasResults(sub.moduleType, sub.stepId);

    // Build results HTML once (reused below)
    let resultsHtml = '';
    if (hasResults) {
        const statusIcons = { generating: '⏳', done: '✅', error: '❌', stale: '⟳' };
        const inserted = sub.insertedResults || [];

        if (isKinetics2) {
            const collectiveIds = ['rate_distributions', 'rates_by_group', 'assembly_vs_disassembly', 'time_to_peak', 'rate_quality', 'fa_area_distribution', 'intensity_spaghetti', 'intensity_spaghetti_peak'];
            const collective = inserted.filter(r => collectiveIds.includes(r.plotType));
            const individual = inserted.filter(r => !collectiveIds.includes(r.plotType));

            resultsHtml += _buildResultsSection(sub, 'Collective Results', collective, statusIcons, 'collective');

            const indivItems = treeItems.filter(i => i.group === 'Individual');
            if (indivItems.length > 0) {
                resultsHtml += buildMTreeGroup('Individual', indivItems, activeItem, sub.id);
            }

            resultsHtml += _buildResultsSection(sub, 'Individual Results', individual, statusIcons, 'individual');
        } else if (isExamination2) {
            resultsHtml += _buildResultsSection(sub, 'Detailed Analyses', inserted, statusIcons, 'individual');
        } else if ((sub.moduleType === 'fastia' && sub.stepId === 'association') ||
                   (sub.moduleType === 'immunia' && sub.stepId === 'signal_association') ||
                   (sub.moduleType === 'immunia' && sub.stepId === 'graph_theory')) {
            resultsHtml += _buildAssociationRunsSection(sub, inserted);
        } else {
            const resultsTitle = (isCellADE || isCellFADE) ? '3. Results' : 'Results';
            resultsHtml += _buildResultsSection(sub, resultsTitle, inserted, statusIcons, 'all');
        }
    }

    for (const [groupName, items] of groups) {
        if (isKinetics2 && groupName === 'Individual') continue;

        // For CellADE/CellFADE: insert Results before Export
        if ((isCellADE || isCellFADE) && groupName.includes('Export') && resultsHtml) {
            html += resultsHtml;
            resultsHtml = ''; // consumed
        }

        html += buildMTreeGroup(groupName, items, activeItem, sub.id);
    }

    // Append results at end for non-CellADE modules (or if Export group wasn't found)
    if (resultsHtml) {
        html += resultsHtml;
    }

    treeBody.innerHTML = html;
}

function selectMTreeItem(subId, itemId, el) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub) return;

    // ── Collect current params before switching ──
    const bodyEl = document.getElementById(`settingsBody-${subId}`);
    if (bodyEl && sub.activeTreeItem) {
        if (!sub._localParams) sub._localParams = {};
        const params = {};
        bodyEl.querySelectorAll('[data-param]').forEach(el => {
            if (el.type === 'checkbox') params[el.dataset.param] = el.checked;
            else params[el.dataset.param] = el.value;
        });
        sub._localParams[sub.activeTreeItem.id] = params;
    }

    sub.activeTreeItem = { id: itemId };

    // Highlight in tree
    el.closest('.module-col-tree-body').querySelectorAll('.mtree-item').forEach(i => i.classList.remove('active'));
    el.classList.add('active');

    // Update settings column
    const treeItems = getModuleTreeItems(sub.moduleType, sub.stepId);
    const titleEl = document.getElementById(`settingsTitle-${subId}`);
    // For CellVisia: check Source items, Scope fixed items, and inserted features
    let activeLabel = getActiveItemLabel(treeItems, sub.activeTreeItem);
    if (activeLabel === 'Settings' && sub.moduleType === 'cellvisia') {
        const scopeItem = CV_SCOPE_FIXED_ITEMS.find(i => i.id === itemId);
        const sourceItem = CV_SOURCE_ITEMS.find(i => i.id === itemId);
        const cvFeat = sub.cvFeatures?.find(f => f.id === itemId);
        if (scopeItem) activeLabel = scopeItem.label;
        else if (sourceItem) activeLabel = sourceItem.label;
        else if (cvFeat) activeLabel = cvFeat.label;
    }
    if (titleEl) titleEl.textContent = activeLabel;
    if (bodyEl) {
        // Hide during update to prevent sibling repaint blink
        bodyEl.style.visibility = 'hidden';
        bodyEl.innerHTML = renderSettingsContent(sub.moduleType, sub.stepId, sub.activeTreeItem);
        _restoreParams(bodyEl, sub, itemId);
        requestAnimationFrame(() => { bodyEl.style.visibility = ''; });
    }
}

function _restoreParams(bodyEl, sub, itemId) {
    const localParams = sub._localParams?.[itemId];
    const backendParams = sub._loadedParams;
    bodyEl.querySelectorAll('[data-param]').forEach(el => {
        const key = el.dataset.param;
        // Local params take priority (user just typed them)
        if (localParams && key in localParams) {
            if (el.type === 'checkbox') el.checked = localParams[key];
            else el.value = localParams[key];
        }
        // Fallback: backend-loaded params (from project file)
        else if (backendParams) {
            // Search all sections for the key
            for (const section of Object.values(backendParams)) {
                if (section && typeof section === 'object' && key in section) {
                    if (el.type === 'checkbox') el.checked = section[key];
                    else el.value = section[key];
                    break;
                }
            }
        }
    });
}

function toggleMTreeSection(head) {
    head.querySelector('.cat-arrow').classList.toggle('open');
    head.nextElementSibling.classList.toggle('open');
}

function toggleLeftCols(subId) {
    const left = document.getElementById(`colsLeft-${subId}`);
    if (!left) return;
    const btn = left.parentElement.querySelector('.col-toggle-btn');
    if (left.classList.contains('collapsed')) {
        left.classList.remove('collapsed');
        if (btn) btn.textContent = '◀';
    } else {
        left.classList.add('collapsed');
        if (btn) btn.textContent = '▶';
    }
}

// ═════════════════════════════════════════════
// CELLVISIA — OPERATION CATALOG & FEATURE TREE
// ═════════════════════════════════════════════
// SolidWorks-style feature tree. Users insert operations into groups via
// right-click. Source group is fixed (one source per module). The other
// groups start empty and grow as the user inserts features. Multiple
// instances of the same operation are allowed (e.g. two Gaussian blurs).
//
// Group coverage is validated against FIJI / CellProfiler / napari common
// operations. Entries tagged `multi_input: true` require two or more
// upstream streams — UI wire concept is pending; these render as placeholders
// until the wire UX lands.
//
// Design notes:
//   - Each feature is an instance: { id, type, group, label, icon, params, suppressed }
//   - Features live on the sub-tab: sub.cvFeatures = []
//   - The backend Python kernel (planned) mirrors this model; for now, the
//     tree is the recipe, to be serialized to disk when persistence lands.

const CV_GROUPS = [
    '0. Source',
    '1. Scope',
    '2. Image Processing',
    '3. Segmentation',
    '4. Advanced',
    '5. Measurement',
    '6. Export',
];

const CV_OPERATIONS = {
    '1. Scope': [
        { type: 'crop',                icon: '✂', label: 'Crop (ROI)',               defaults: { x: 0, y: 0, w: 512, h: 512 } },
        { type: 'z_project',           icon: '📚', label: 'Z-Project (Max/Mean/Sum)', defaults: { method: 'max', axis: 'z' } },
        { type: 'flip_rotate',         icon: '🔄', label: 'Flip / Rotate',            defaults: { flip: 'none', rotate_deg: 0 } },
        { type: 'resize',              icon: '⇲', label: 'Resize / Downsample',      defaults: { factor: 0.5, order: 1 } },
        { type: 'concatenate',         icon: '🔗', label: 'Concatenate Movies',       defaults: { sources: [], axis: 't' }, multi_input: true },
        { type: 'stitch_tiles',        icon: '🧩', label: 'Stitch Tiles',             defaults: { overlap_pct: 10 }, multi_input: true },
        { type: 'register_pair',       icon: '🎯', label: 'Register Two Images',      defaults: { method: 'phase_corr' }, multi_input: true },
    ],
    '2. Image Processing': [
        // ── Noise Reduction ──
        { type: '_header', label: 'Noise Reduction' },
        { type: 'gaussian_blur',       icon: '🔧', label: 'Gaussian Blur',             defaults: { sigma: 1.0 } },
        { type: 'median_filter',       icon: '🔧', label: 'Median Filter',             defaults: { size: 3 } },
        { type: 'bilateral_filter',    icon: '🔧', label: 'Bilateral Filter',          defaults: { sigma_spatial: 3, sigma_intensity: 0.1 } },
        { type: 'remove_outliers',     icon: '🔧', label: 'Remove Outliers',           defaults: { radius: 2, threshold: 50 } },
        { type: 'despeckle',           icon: '🔧', label: 'Despeckle',                 defaults: {} },
        { type: 'dl_denoise',          icon: '🧠', label: 'DL Denoise (Noise2Void)',   defaults: { model: 'default' } },
        // ── Correction ──
        { type: '_header', label: 'Correction' },
        { type: 'background_subtract', icon: '🔧', label: 'Background Subtraction',   defaults: { radius: 50 } },
        { type: 'rolling_ball',        icon: '🔧', label: 'Rolling Ball',              defaults: { radius: 30 } },
        { type: 'bleach_correction',   icon: '🔧', label: 'Bleach Correction',         defaults: { method: 'exponential' } },
        { type: 'drift_correction',    icon: '🔧', label: 'Drift Correction',          defaults: { method: 'phase_corr' } },
        { type: 'flatfield',           icon: '🔧', label: 'Flat-Field Correction',     defaults: { method: 'basic' } },
        // ── Enhancement ──
        { type: '_header', label: 'Enhancement' },
        { type: 'clahe',               icon: '✨', label: 'CLAHE',                     defaults: { clip_limit: 2.0, tile: 8 } },
        { type: 'contrast_stretch',    icon: '✨', label: 'Contrast Stretch',          defaults: { p_low: 1, p_high: 99 } },
        { type: 'unsharp_mask',        icon: '✨', label: 'Unsharp Mask',              defaults: { radius: 2, amount: 0.5 } },
        { type: 'sharpen',             icon: '✨', label: 'Sharpen',                   defaults: { amount: 1.0 } },
        { type: 'gamma',               icon: '✨', label: 'Gamma Correction',          defaults: { gamma: 1.0 } },
        // ── Feature Detection ──
        { type: '_header', label: 'Feature Detection' },
        { type: 'bandpass',            icon: '🔬', label: 'Band-Pass Filter',          defaults: { low: 1, high: 30 } },
        { type: 'find_edges',          icon: '🔬', label: 'Find Edges',                defaults: { method: 'sobel' } },
        { type: 'enhance_features',    icon: '🔬', label: 'Enhance/Suppress Features', defaults: { mode: 'enhance', shape: 'speckles', size: 5 } },
        { type: 'invert',              icon: '🔬', label: 'Invert',                    defaults: {} },
        // ── Math ──
        { type: '_header', label: 'Math' },
        { type: 'image_math',          icon: '➕', label: 'Image Math (A±B, A/B)',    defaults: { op: 'subtract' }, multi_input: true },
    ],
    '3. Segmentation': [
        // ── Thresholding ──
        { type: '_header', label: 'Thresholding' },
        { type: 'threshold_global',    icon: '🎚', label: 'Global Threshold',          defaults: { method: 'otsu', value: 128 } },
        { type: 'threshold_adaptive',  icon: '🎚', label: 'Adaptive Threshold',        defaults: { block_size: 31, offset: 0 } },
        // ── Morphology ──
        { type: '_header', label: 'Morphology' },
        { type: 'morph_open',          icon: '⚙️', label: 'Morphological Open',        defaults: { radius: 2 } },
        { type: 'morph_close',         icon: '⚙️', label: 'Morphological Close',       defaults: { radius: 2 } },
        { type: 'erode',               icon: '⚙️', label: 'Erode',                     defaults: { radius: 1 } },
        { type: 'dilate',              icon: '⚙️', label: 'Dilate',                    defaults: { radius: 1 } },
        { type: 'fill_holes',          icon: '⚙️', label: 'Fill Holes',                defaults: {} },
        { type: 'clear_border',        icon: '⚙️', label: 'Clear Border',              defaults: { margin: 0 } },
        // ── Instance Segmentation ──
        { type: '_header', label: 'Instance Segmentation' },
        { type: 'distance_transform',  icon: '🔵', label: 'Distance Transform',        defaults: { metric: 'euclidean' } },
        { type: 'watershed',           icon: '🔵', label: 'Watershed',                 defaults: { min_distance: 10 } },
        { type: 'connected_components',icon: '🔵', label: 'Connected Components',      defaults: { connectivity: 2 } },
        { type: 'skeletonize',         icon: '🔵', label: 'Skeletonize',               defaults: { method: 'medial_axis' } },
        // ── Deep Learning ──
        { type: '_header', label: 'Deep Learning' },
        { type: 'cellpose',            icon: '🧠', label: 'Cellpose',                  defaults: { model: 'cyto', diameter: 30 } },
        { type: 'stardist',            icon: '🧠', label: 'StarDist',                  defaults: { model: '2D_versatile_fluo' } },
        { type: 'sam',                 icon: '🧠', label: 'Segment Anything (SAM)',    defaults: { prompt: 'auto' } },
        { type: 'pixel_classifier',    icon: '🧠', label: 'Pixel Classifier',          defaults: { model: null } },
    ],
    '4. Advanced': [
        { type: 'track_objects',       icon: '📈', label: 'Track Objects',             defaults: { method: 'trackpy', link_radius: 15, memory: 3 } },
        { type: 'filter_objects',      icon: '🔍', label: 'Filter Objects by Measurement', defaults: { by: 'area', min: 0, max: 1e9 }, multi_input: true },
        { type: 'relate_objects',      icon: '🔗', label: 'Relate Objects (Parent/Child)', defaults: {}, multi_input: true },
        { type: 'identify_tertiary',   icon: '⊖', label: 'Identify Tertiary (A − B)', defaults: { mode: 'subtract' }, multi_input: true },
        { type: 'combine_objects',     icon: '⊕', label: 'Combine Objects',           defaults: { overlap: 'prefer_first' }, multi_input: true },
        { type: 'split_objects',       icon: '✂', label: 'Split Merged Objects',      defaults: { method: 'shape_watershed' } },
        { type: 'expand_shrink',       icon: '⇔', label: 'Expand / Shrink Objects',   defaults: { pixels: 5 } },
        { type: 'classify_objects',    icon: '🏷', label: 'Classify Objects',          defaults: { model: null, features: [] }, multi_input: true },
    ],
    '5. Measurement': [
        // ── Object Properties ──
        { type: '_header', label: 'Object Properties' },
        { type: 'region_props',        icon: '📐', label: 'Region Properties',         defaults: { include: 'area,perimeter,eccentricity' } },
        { type: 'intensity_stats',     icon: '📊', label: 'Intensity Statistics',      defaults: { channels: 'all' } },
        { type: 'shape_descriptors',   icon: '📐', label: 'Shape Descriptors',         defaults: {} },
        { type: 'texture',             icon: '🎨', label: 'Texture (GLCM)',            defaults: { distances: '1', angles: '0,45,90,135' } },
        { type: 'granularity',         icon: '📏', label: 'Granularity Spectrum',      defaults: { range: 16 } },
        // ── Spatial ──
        { type: '_header', label: 'Spatial' },
        { type: 'spatial_stats',       icon: '🗺', label: 'Spatial Statistics',        defaults: {} },
        { type: 'neighbors',           icon: '🕸', label: 'Neighbor Analysis',         defaults: { distance: 50 } },
        { type: 'colocalization',      icon: '🎯', label: 'Colocalization',            defaults: { method: 'pearson' }, multi_input: true },
        // ── Image-Level ──
        { type: '_header', label: 'Image-Level' },
        { type: 'image_quality',       icon: '✅', label: 'Image Quality Metrics',     defaults: {} },
        { type: 'histogram',           icon: '📊', label: 'Intensity Histogram',       defaults: { bins: 256 } },
        { type: 'intensity_distribution', icon: '📊', label: 'Radial Intensity',       defaults: { bins: 4 } },
        { type: 'plot_profile',        icon: '📉', label: 'Line Profile',              defaults: { x0: 0, y0: 0, x1: 100, y1: 100 } },
        // ── Derived ──
        { type: '_header', label: 'Derived' },
        { type: 'calculate_math',      icon: '🧮', label: 'Calculate Math',            defaults: { formula: '' } },
        { type: 'skeleton_measure',    icon: '🦴', label: 'Skeleton Measurements',     defaults: {} },
    ],
    '6. Export': [
        // ── Image Export ──
        { type: '_header', label: 'Image Export' },
        { type: 'save_image',          icon: '💾', label: 'Save Image (TIFF/PNG)',     defaults: { fmt: 'tiff', suffix: '_processed' } },
        { type: 'export_mask',         icon: '💾', label: 'Export Masks',              defaults: { fmt: 'tiff', suffix: '_mask' } },
        { type: 'export_overlay',      icon: '🖼', label: 'Export Overlay',            defaults: { alpha: 0.5, suffix: '_overlay' } },
        // ── Data Export ──
        { type: '_header', label: 'Data Export' },
        { type: 'export_csv',          icon: '📄', label: 'Export Measurements (CSV)', defaults: { suffix: '_measurements' } },
        { type: 'export_database',     icon: '🗄', label: 'Export to Database',        defaults: { kind: 'sqlite', suffix: '_data' } },
        // ── Pipeline ──
        { type: '_header', label: 'Pipeline' },
        { type: 'export_recipe',       icon: '📋', label: 'Export Recipe (JSON)',      defaults: {} },
        { type: 'export_batch',        icon: '📦', label: 'Create Batch',             defaults: {} },
    ],
};

// Fixed items in the Source group (one per module — not insertable).
const CV_SOURCE_ITEMS = [
    { id: 'cv-select-image',  icon: '📥', label: 'Load Image / Stack' },
    { id: 'cv-channel-setup', icon: '🎨', label: 'Channel Assignment' },
    { id: 'cv-metadata',      icon: '📋', label: 'Imaging Metadata' },
];

const CV_SCOPE_FIXED_ITEMS = [
    { id: 'cv-scope-channels', icon: '🎨', label: 'Channels' },
    { id: 'cv-scope-temporal', icon: '🎞', label: 'Temporal' },
    { id: 'cv-scope-format',   icon: '🔢', label: 'Format' },
];

// Parameter definitions per feature type — drives the dynamic settings form.
// Each entry: { label, key, type: 'int'|'float'|'select', step?, unit?, width?, options?, fallback? }
const CV_PARAM_DEFS = {
    // 1. Scope
    crop:             [{ label:'X', key:'x', type:'int', fallback:0 }, { label:'Y', key:'y', type:'int', fallback:0 },
                       { label:'Width', key:'w', type:'int', fallback:512 }, { label:'Height', key:'h', type:'int', fallback:512 }],
    channel_select:   [{ label:'Keep (comma-sep)', key:'keep', type:'text', fallback:'0', width:'120px' }],
    channel_remove:   [{ label:'Drop (comma-sep)', key:'drop', type:'text', fallback:'', width:'120px' }],
    frame_range:      [{ label:'Start', key:'start', type:'int', fallback:0 }, { label:'End', key:'end', type:'int', fallback:-1, unit:'-1 = last' }],
    frame_subsample:  [{ label:'Every N', key:'every', type:'int', fallback:2 }],
    z_project:        [{ label:'Method', key:'method', type:'select', options:['max','mean','sum','min','std'], fallback:'max' },
                       { label:'Axis', key:'axis', type:'select', options:['T','Z'], fallback:'T' }],
    flip_rotate:      [{ label:'Flip', key:'flip', type:'select', options:['none','h','v','hv'], fallback:'none' },
                       { label:'Rotate', key:'rotate_deg', type:'select', options:[0,90,180,270], fallback:0 }],
    resize:           [{ label:'Factor', key:'factor', type:'float', step:0.1, fallback:0.5 },
                       { label:'Interp Order', key:'order', type:'select', options:[0,1,2,3], fallback:1 }],
    bit_depth:        [{ label:'Target', key:'target', type:'select', options:['uint8','uint16','float32','float64'], fallback:'uint8' }],
    reorder_axes:     [{ label:'Order', key:'order', type:'text', fallback:'TZYXC', width:'100px' }],
    deinterleave:     [{ label:'N Channels', key:'n_channels', type:'int', fallback:2 }],
    concatenate:      [],
    stitch_tiles:     [{ label:'Overlap %', key:'overlap_pct', type:'float', fallback:10 }],
    register_pair:    [{ label:'Method', key:'method', type:'select', options:['phase_corr','sift'], fallback:'phase_corr' }],
    // 2. Pre-processing
    background_subtract: [{ label:'Radius', key:'radius', type:'int', fallback:50, unit:'px' }],
    rolling_ball:     [{ label:'Radius', key:'radius', type:'int', fallback:30, unit:'px' }],
    gaussian_blur:    [{ label:'Sigma', key:'sigma', type:'float', step:0.1, fallback:1.0, unit:'px' }],
    median_filter:    [{ label:'Size', key:'size', type:'int', fallback:3, unit:'px' }],
    bilateral_filter: [{ label:'Spatial σ', key:'sigma_spatial', type:'float', fallback:3 }, { label:'Intensity σ', key:'sigma_intensity', type:'float', step:0.01, fallback:0.1 }],
    remove_outliers:  [{ label:'Radius', key:'radius', type:'int', fallback:2 }, { label:'Threshold', key:'threshold', type:'int', fallback:50 }],
    despeckle:        [],
    dl_denoise:       [{ label:'Model', key:'model', type:'select', options:['default'], fallback:'default' }],
    bleach_correction:[{ label:'Method', key:'method', type:'select', options:['exponential','ratio','histogram'], fallback:'exponential' }],
    drift_correction: [{ label:'Method', key:'method', type:'select', options:['phase_corr','optical_flow'], fallback:'phase_corr' }],
    flatfield:        [{ label:'Method', key:'method', type:'select', options:['basic','cidre'], fallback:'basic' }],
    image_math:       [{ label:'Operation', key:'op', type:'select', options:['add','subtract','multiply','divide','average'], fallback:'subtract' }],
    // 3. Enhancement
    clahe:            [{ label:'Clip Limit', key:'clip_limit', type:'float', step:0.5, fallback:2.0 }, { label:'Tile Size', key:'tile', type:'int', fallback:8 }],
    contrast_stretch: [{ label:'Low %', key:'p_low', type:'float', fallback:1 }, { label:'High %', key:'p_high', type:'float', fallback:99 }],
    unsharp_mask:     [{ label:'Radius', key:'radius', type:'float', fallback:2 }, { label:'Amount', key:'amount', type:'float', step:0.1, fallback:0.5 }],
    sharpen:          [{ label:'Amount', key:'amount', type:'float', step:0.1, fallback:1.0 }],
    bandpass:         [{ label:'Low', key:'low', type:'int', fallback:1, unit:'px' }, { label:'High', key:'high', type:'int', fallback:30, unit:'px' }],
    gamma:            [{ label:'Gamma', key:'gamma', type:'float', step:0.1, fallback:1.0 }],
    invert:           [],
    find_edges:       [{ label:'Method', key:'method', type:'select', options:['sobel','scharr','prewitt','laplacian'], fallback:'sobel' }],
    enhance_features: [{ label:'Mode', key:'mode', type:'select', options:['enhance','suppress'], fallback:'enhance' },
                       { label:'Shape', key:'shape', type:'select', options:['speckles','ridges','dark_holes'], fallback:'speckles' },
                       { label:'Size', key:'size', type:'int', fallback:5 }],
    // 4. Segmentation
    threshold_global: [{ label:'Method', key:'method', type:'select', options:['otsu','li','yen','triangle','isodata','manual'], fallback:'otsu' },
                       { label:'Manual Value', key:'value', type:'int', fallback:128 }],
    threshold_adaptive:[{ label:'Block Size', key:'block_size', type:'int', fallback:31 }, { label:'Offset', key:'offset', type:'int', fallback:0 }],
    morph_open:       [{ label:'Radius', key:'radius', type:'int', fallback:2, unit:'px' }],
    morph_close:      [{ label:'Radius', key:'radius', type:'int', fallback:2, unit:'px' }],
    erode:            [{ label:'Radius', key:'radius', type:'int', fallback:1, unit:'px' }],
    dilate:           [{ label:'Radius', key:'radius', type:'int', fallback:1, unit:'px' }],
    fill_holes:       [],
    clear_border:     [{ label:'Margin', key:'margin', type:'int', fallback:0, unit:'px' }],
    distance_transform:[{ label:'Metric', key:'metric', type:'select', options:['euclidean','chessboard','taxicab'], fallback:'euclidean' }],
    skeletonize:      [{ label:'Method', key:'method', type:'select', options:['medial_axis','lee','thin'], fallback:'medial_axis' }],
    watershed:        [{ label:'Min Distance', key:'min_distance', type:'int', fallback:10, unit:'px' }],
    connected_components:[{ label:'Connectivity', key:'connectivity', type:'select', options:[1,2], fallback:2 }],
    pixel_classifier: [],
    cellpose:         [{ label:'Model', key:'model', type:'select', options:['cyto','cyto2','nuclei'], fallback:'cyto' },
                       { label:'Diameter', key:'diameter', type:'int', fallback:30, unit:'px' }],
    stardist:         [{ label:'Model', key:'model', type:'select', options:['2D_versatile_fluo','2D_versatile_he','2D_paper_dsb2018'], fallback:'2D_versatile_fluo' }],
    sam:              [{ label:'Prompt', key:'prompt', type:'select', options:['auto','box','point'], fallback:'auto' }],
    // 5. Advanced
    track_objects:    [{ label:'Method', key:'method', type:'select', options:['trackpy','lap'], fallback:'trackpy' },
                       { label:'Link Radius', key:'link_radius', type:'int', fallback:15, unit:'px' },
                       { label:'Memory', key:'memory', type:'int', fallback:3, unit:'frames' }],
    filter_objects:   [{ label:'By', key:'by', type:'select', options:['area','perimeter','eccentricity','intensity'], fallback:'area' },
                       { label:'Min', key:'min', type:'float', fallback:0 }, { label:'Max', key:'max', type:'float', fallback:1e9 }],
    relate_objects:   [],
    identify_tertiary:[{ label:'Mode', key:'mode', type:'select', options:['subtract'], fallback:'subtract' }],
    combine_objects:  [{ label:'Overlap', key:'overlap', type:'select', options:['prefer_first','prefer_second','merge'], fallback:'prefer_first' }],
    split_objects:    [{ label:'Method', key:'method', type:'select', options:['shape_watershed','convexity'], fallback:'shape_watershed' }],
    expand_shrink:    [{ label:'Pixels', key:'pixels', type:'int', fallback:5, unit:'px' }],
    classify_objects: [],
    // 6. Measurement
    region_props:     [{ label:'Properties', key:'include', type:'text', fallback:'area,perimeter,eccentricity', width:'200px' }],
    intensity_stats:  [{ label:'Channels', key:'channels', type:'text', fallback:'all', width:'120px' }],
    intensity_distribution:[{ label:'Radial Bins', key:'bins', type:'int', fallback:4 }],
    shape_descriptors:[{ label:'Min Area', key:'min_area', type:'int', fallback:0, unit:'px²' }],
    spatial_stats:    [{ label:'Min Area', key:'min_area', type:'int', fallback:0, unit:'px²' }, { label:'Units', key:'units', type:'select', options:['pixels','physical'], fallback:'pixels' }],
    neighbors:        [{ label:'Max Distance', key:'distance', type:'int', fallback:50, unit:'px' }],
    texture:          [{ label:'Distances', key:'distances', type:'text', fallback:'1', width:'80px' }, { label:'Angles (°)', key:'angles', type:'text', fallback:'0,45,90,135', width:'120px' }],
    granularity:      [{ label:'Max Radius', key:'range', type:'int', fallback:16 }],
    colocalization:   [{ label:'Method', key:'method', type:'select', options:['pearson','manders','costes'], fallback:'pearson' }],
    skeleton_measure: [{ label:'Min Branch', key:'min_branch', type:'int', fallback:0, unit:'px' }],
    image_quality:    [{ label:'Focus Method', key:'focus_method', type:'select', options:['laplacian','brenner','tenengrad'], fallback:'laplacian' }, { label:'Saturation %', key:'sat_thresh', type:'float', step:0.1, fallback:99 }],
    plot_profile:     [{ label:'X₀', key:'x0', type:'int', fallback:0 }, { label:'Y₀', key:'y0', type:'int', fallback:0 }, { label:'X₁', key:'x1', type:'int', fallback:100 }, { label:'Y₁', key:'y1', type:'int', fallback:100 }],
    histogram:        [{ label:'Bins', key:'bins', type:'int', fallback:256 }],
    calculate_math:   [{ label:'Formula', key:'formula', type:'text', fallback:'', width:'200px' }],
    // 7. Export
    save_image:       [{ label:'Output', key:'output_path', type:'browse_save', fallback:'', width:'200px', filetypes:'tiff,png' }, { label:'Format', key:'fmt', type:'select', options:['tiff','png','ome.tiff'], fallback:'tiff' }, { label:'Suffix', key:'suffix', type:'text', fallback:'_processed', width:'120px' }],
    export_mask:      [{ label:'Output', key:'output_path', type:'browse_save', fallback:'', width:'200px', filetypes:'tiff,png' }, { label:'Format', key:'fmt', type:'select', options:['tiff','png'], fallback:'tiff' }, { label:'Suffix', key:'suffix', type:'text', fallback:'_mask', width:'120px' }],
    export_csv:       [{ label:'Output Folder', key:'output_path', type:'browse_folder', fallback:'', width:'200px' }, { label:'Separator', key:'sep', type:'select', options:[',',';','\\t'], fallback:',' }, { label:'Suffix', key:'suffix', type:'text', fallback:'_measurements', width:'140px' }],
    export_overlay:   [{ label:'Output', key:'output_path', type:'browse_save', fallback:'', width:'200px', filetypes:'png,tiff' }, { label:'Alpha', key:'alpha', type:'float', step:0.1, fallback:0.5 }, { label:'Format', key:'fmt', type:'select', options:['png','tiff'], fallback:'png' }, { label:'Suffix', key:'suffix', type:'text', fallback:'_overlay', width:'120px' }],
    export_database:  [{ label:'Output', key:'output_path', type:'browse_save', fallback:'', width:'200px', filetypes:'sqlite,h5' }, { label:'Kind', key:'kind', type:'select', options:['sqlite','hdf5'], fallback:'sqlite' }, { label:'Suffix', key:'suffix', type:'text', fallback:'_data', width:'120px' }],
    export_recipe:    [{ label:'Output', key:'output_path', type:'browse_save', fallback:'', width:'200px', filetypes:'json' }, { label:'Include params', key:'include_params', type:'select', options:['all','modified'], fallback:'all' }],
    export_batch:     [{ label:'Output Folder', key:'output_path', type:'browse_folder', fallback:'', width:'200px' }, { label:'Folder pattern', key:'pattern', type:'text', fallback:'*', width:'140px' }],
};

// Globally unique feature ids across the app.
let _cvFeatureCounter = 0;
function nextCvFeatureId() { _cvFeatureCounter++; return `cvf-${_cvFeatureCounter}`; }

// Is this sub-tab rendering CellVisia at module level?
function isCellVisiaModule(sub) {
    return sub && sub.moduleType === 'cellvisia' && sub.stepId == null;
}

function buildCellVisiaTree(sub, activeItem) {
    const features = sub.cvFeatures || [];
    const byGroup = new Map();
    for (const g of CV_GROUPS) byGroup.set(g, []);
    for (const f of features) {
        const arr = byGroup.get(f.group);
        if (arr) arr.push(f);
    }

    let html = '';
    for (const group of CV_GROUPS) {
        const isSource = group === '0. Source';
        const isScope = group === '1. Scope';

        // Fixed items: Source has its own, Scope has settings + inserted features
        let fixedItems = [];
        if (isSource) fixedItems = CV_SOURCE_ITEMS;
        else if (isScope) fixedItems = CV_SCOPE_FIXED_ITEMS;

        const insertedItems = isSource ? [] : (byGroup.get(group) || []);
        const allItems = [...fixedItems, ...insertedItems];
        const insertable = !isSource; // Scope and all others support right-click insert

        const rightClickAttr = insertable
            ? `oncontextmenu="event.preventDefault();event.stopPropagation();showCVInsertMenu(event,'${sub.id}','${group.replace(/'/g, "\\'")}')"`
            : '';
        const titleAttr = insertable
            ? 'title="Right-click to insert an operation"'
            : '';

        const emptyHint = insertable && insertedItems.length === 0 && fixedItems.length === 0
            ? `<div class="mtree-placeholder" style="padding:6px 18px;font-size:var(--fs-xs);color:var(--text-tertiary);font-style:italic">Right-click to insert…</div>`
            : '';

        // For Scope: show hint only if no inserted features (fixed items always visible)
        const scopeHint = isScope && insertedItems.length === 0
            ? `<div class="mtree-placeholder" style="padding:6px 18px;font-size:var(--fs-xs);color:var(--text-tertiary);font-style:italic">Right-click to add operations…</div>`
            : '';

        const countBadge = allItems.length
            ? `<span style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-left:auto">${allItems.length}</span>`
            : '';

        const plusHint = insertable
            ? `<span style="font-size:11px;color:var(--text-tertiary);margin-left:6px;opacity:.6">＋</span>`
            : '';

        html += `<div class="mtree-section">
            <div class="mtree-section-head ${insertable ? 'cv-insertable-group' : ''}"
                 onclick="toggleMTreeSection(this)"
                 ${rightClickAttr} ${titleAttr}>
                <span class="cat-arrow open">▶</span>
                <span style="font-size:var(--fs-xs);color:var(--text-secondary);text-transform:uppercase;letter-spacing:.5px;font-weight:700">${group}</span>
                ${plusHint}
                ${countBadge}
            </div>
            <div class="mtree-section-body open">
                ${fixedItems.map(i => {
                    const active = activeItem && activeItem.id === i.id ? 'active' : '';
                    return `<div class="mtree-item ${active}" onclick="selectMTreeItem('${sub.id}','${i.id}',this)">
                        <span class="mtree-item-icon">${i.icon}</span>
                        <span style="flex:1">${i.label}</span>
                    </div>`;
                }).join('')}
                ${insertedItems.map(i => {
                    const active = activeItem && activeItem.id === i.id ? 'active' : '';
                    const isFrozen = i.frozen || false;
                    const isSupp = i.suppressed || false;
                    // Visual state
                    let itemStyle = '';
                    let statusDot = '';
                    const st = i._status || (isSupp ? 'suppressed' : isFrozen ? 'frozen' : 'ok');
                    if (st === 'ok')         statusDot = '<span style="color:#4caf50;font-size:8px;margin-right:3px">●</span>';
                    if (st === 'stale')      statusDot = '<span style="color:#ff9800;font-size:8px;margin-right:3px">●</span>';
                    if (st === 'error')      statusDot = '<span style="color:#f44336;font-size:8px;margin-right:3px">●</span>';
                    if (st === 'suppressed') { statusDot = '<span style="color:#9e9e9e;font-size:8px;margin-right:3px">●</span>'; itemStyle = 'opacity:.4;text-decoration:line-through'; }
                    if (st === 'frozen')     statusDot = '<span style="color:#42a5f5;font-size:8px;margin-right:3px">●</span>';
                    if (isFrozen) itemStyle = 'border-left:2px solid #42a5f5;padding-left:6px';
                    if (isSupp) itemStyle = 'opacity:.4;text-decoration:line-through';
                    // Action icon
                    const actionIcon = isFrozen ? '🔒' : isSupp ? '◻' : '◼';
                    const actionTitle = isFrozen ? 'Unfreeze' : isSupp ? 'Activate' : 'Suppress';
                    const actionFn = isFrozen
                        ? `cvToggleFreeze('${sub.id}','${i.id}')`
                        : `cvToggleSuppression('${sub.id}','${i.id}')`;
                    return `<div class="mtree-item ${active}" onclick="selectMTreeItem('${sub.id}','${i.id}',this)"
                                oncontextmenu="event.preventDefault();event.stopPropagation();showCVItemMenu(event,'${sub.id}','${i.id}')"
                                style="${itemStyle}">
                        ${statusDot}
                        <span class="mtree-item-icon">${i.icon}</span>
                        <span style="flex:1">${i.label}</span>
                        <span style="cursor:pointer;font-size:10px;padding:0 3px;opacity:.5" onclick="event.stopPropagation();${actionFn}" title="${actionTitle}">${actionIcon}</span>
                        <span class="result-remove" onclick="event.stopPropagation();cvRemoveFeature('${sub.id}','${i.id}')" title="Remove">×</span>
                    </div>`;
                }).join('')}
                ${isScope ? scopeHint : emptyHint}
            </div>
        </div>`;
    }

    return html;
}

function showCVInsertMenu(e, subId, groupName) {
    hideContextMenu();
    const ops = CV_OPERATIONS[groupName] || [];
    if (ops.length === 0) return;

    const menu = document.createElement('div');
    menu.id = 'cellabContextMenu';
    menu.className = 'cellab-ctx-menu';

    menu.innerHTML = `
        <div style="padding:6px 12px;font-size:var(--fs-xs);color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--chrome-border);margin-bottom:4px">
            Insert into ${groupName}
        </div>
        ${ops.map(op => {
            // Sub-header divider
            if (op.type === '_header') {
                return `<div style="padding:4px 12px 2px;font-size:10px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px;border-top:1px solid var(--chrome-border);margin-top:4px;opacity:.7">${op.label}</div>`;
            }
            const multi = op.multi_input
                ? '<span style="font-size:9px;color:var(--text-tertiary);margin-left:auto;padding:1px 5px;border:1px solid var(--chrome-border);border-radius:3px;letter-spacing:.5px">MULTI</span>'
                : '';
            const title = op.multi_input
                ? 'title="Takes multiple inputs — wire UX pending"'
                : '';
            return `<div class="ctx-item" onclick="cvInsertFeature('${subId}','${groupName.replace(/'/g, "\\'")}','${op.type}')" ${title}>
                <span class="ctx-icon">${op.icon}</span>
                <span style="flex:1">${op.label}</span>
                ${multi}
            </div>`;
        }).join('')}
    `;

    menu.style.left = e.clientX + 'px';
    menu.style.top = e.clientY + 'px';
    document.body.appendChild(menu);

    // Clamp to viewport + allow scroll if too tall
    menu.style.maxHeight = (window.innerHeight - 20) + 'px';
    menu.style.overflowY = 'auto';
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) menu.style.left = (e.clientX - rect.width) + 'px';
    if (rect.bottom > window.innerHeight) menu.style.top = Math.max(10, e.clientY - rect.height) + 'px';
}

function showCVItemMenu(e, subId, featureId) {
    hideContextMenu();
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(subId);
    if (!sub?.cvFeatures) return;
    const feat = sub.cvFeatures.find(f => f.id === featureId);
    if (!feat) return;

    const isSuppressed = feat.suppressed;
    const isFrozen = feat.frozen || false;
    const suppLabel = isSuppressed ? '✅ Activate' : '⏸ Suppress';
    const freezeLabel = isFrozen ? '🔓 Unfreeze' : '🔒 Freeze';
    const menu = document.createElement('div');
    menu.id = 'cellabContextMenu';
    menu.className = 'cellab-ctx-menu';
    menu.innerHTML = `
        <div style="padding:6px 12px;font-size:var(--fs-xs);color:var(--text-tertiary);border-bottom:1px solid var(--chrome-border);margin-bottom:4px">${feat.label}</div>
        <div class="ctx-item" onclick="hideContextMenu();cvToggleSuppression('${subId}','${featureId}')">
            <span class="ctx-icon">${isSuppressed ? '✅' : '⏸'}</span> ${suppLabel}
        </div>
        <div class="ctx-item" onclick="hideContextMenu();cvToggleFreeze('${subId}','${featureId}')">
            <span class="ctx-icon">${isFrozen ? '🔓' : '🔒'}</span> ${freezeLabel}
        </div>
        <div style="border-top:1px solid var(--chrome-border);margin:4px 0"></div>
        <div class="ctx-item" onclick="hideContextMenu();cvRemoveFeature('${subId}','${featureId}')">
            <span class="ctx-icon">🗑</span> Remove
        </div>
    `;
    menu.style.left = e.clientX + 'px';
    menu.style.top = e.clientY + 'px';
    document.body.appendChild(menu);
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) menu.style.left = (e.clientX - rect.width) + 'px';
    if (rect.bottom > window.innerHeight) menu.style.top = (e.clientY - rect.height) + 'px';
}

function cvInsertFeature(subId, groupName, opType) {
    hideContextMenu();
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub) return;

    const op = (CV_OPERATIONS[groupName] || []).find(o => o.type === opType);
    if (!op) return;

    if (!sub.cvFeatures) sub.cvFeatures = [];

    // Disambiguate multiple instances of the same op in the same group
    const count = sub.cvFeatures.filter(f => f.type === opType && f.group === groupName).length;
    const label = count === 0 ? op.label : `${op.label} (${count + 1})`;

    const feature = {
        id: nextCvFeatureId(),
        type: opType,
        group: groupName,
        label,
        icon: op.icon,
        params: JSON.parse(JSON.stringify(op.defaults)),  // deep copy
        suppressed: false,
    };

    sub.cvFeatures.push(feature);
    sub.activeTreeItem = { id: feature.id };
    renderModuleTree(sub);
    // Auto-show settings for the new feature
    const titleEl = document.getElementById(`settingsTitle-${subId}`);
    if (titleEl) titleEl.textContent = feature.label;
    const bodyEl = document.getElementById(`settingsBody-${subId}`);
    if (bodyEl) bodyEl.innerHTML = renderSettingsContent(sub.moduleType, sub.stepId, sub.activeTreeItem);
    updateStatus(`Inserted: ${label}`);
    cvPersistState(sub);
}

function cvRemoveFeature(subId, featureId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub || !sub.cvFeatures) return;

    const idx = sub.cvFeatures.findIndex(f => f.id === featureId);
    if (idx < 0) return;

    const removed = sub.cvFeatures[idx];
    sub.cvFeatures.splice(idx, 1);
    if (sub.activeTreeItem && sub.activeTreeItem.id === featureId) {
        sub.activeTreeItem = null;
    }
    renderModuleTree(sub);
    updateStatus(`Removed: ${removed.label}`);
    cvPersistState(sub);
}

async function cvToggleSuppression(subId, featureId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub?.cvFeatures) return;
    const feat = sub.cvFeatures.find(f => f.id === featureId);
    if (!feat) return;

    const newState = !feat.suppressed;

    if (feat._backendId) {
        // Incremental: toggle on existing backend feature
        try {
            const res = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${feat._backendId}/suppress`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ suppressed: newState }),
            });
            const data = await res.json();
            if (!data.success) {
                updateStatus(`Suppress failed: ${data.error}`);
                return;
            }
        } catch (e) {
            updateStatus(`Suppress error: ${e.message}`);
            return;
        }
    }
    // else: no backend_id yet — just toggle locally, will be sent on next Apply/rebuild

    feat.suppressed = newState;
    if (newState) feat.frozen = false;
    renderModuleTree(sub);
    updateStatus(`${feat.label}: ${newState ? 'suppressed' : 'activated'}`);
    if (feat._backendId) cvRefreshViewer();
    cvPersistState(sub);
}

async function cvToggleFreeze(subId, featureId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub?.cvFeatures) return;
    const feat = sub.cvFeatures.find(f => f.id === featureId);
    if (!feat) return;

    const newFrozen = !feat.frozen;

    // If freezing, need a backend_id (feature must be in the engine)
    if (!feat._backendId) {
        updateStatus('Cannot freeze: feature not yet applied');
        return;
    }

    try {
        const res = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${feat._backendId}/freeze`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ frozen: newFrozen }),
        });
        const data = await res.json();
        if (data.success) {
            feat.frozen = newFrozen;
            feat._status = data.status;
            // Clear suppression if freezing (mutually exclusive)
            if (newFrozen) feat.suppressed = false;
            renderModuleTree(sub);
            updateStatus(`${feat.label}: ${newFrozen ? 'frozen 🔒' : 'unfrozen'}`);
            if (!newFrozen) {
                await cvRebuildPipeline();
                cvRefreshViewer();
            }
            cvPersistState(sub);
        } else {
            updateStatus(`Freeze failed: ${data.error}`);
        }
    } catch (e) {
        updateStatus(`Freeze error: ${e.message}`);
    }
}

// ═════════════════════════════════════════════
// MODULE TREE ITEMS (per module/step)
// ═════════════════════════════════════════════

function getModuleTreeItems(moduleType, stepId) {
    // ── CORNEALIA ─────────────────────────────────
    if (moduleType === 'cornealia') {
        if (stepId === 'import') return [
            { id: 'select-image', icon: '📥', label: 'Select Image', group: 'Setup' },
            { id: 'image-type', icon: '🔧', label: 'Image Settings', group: 'Setup' },
            { id: 'run-import', icon: '▶', label: 'Import & Preview', group: 'Action' },
        ];
        if (stepId === 'segmentation') return [
            { id: 'seg-params', icon: '⚙️', label: 'Segmentation Parameters', group: 'Configure' },
            { id: 'run-seg', icon: '▶', label: 'Run Segmentation', group: 'Execute' },
        ];
        if (stepId === 'morphometry') return [
            { id: 'morph-params', icon: '⚙️', label: 'Analysis Settings', group: 'Configure' },
            { id: 'run-morph', icon: '▶', label: 'Run Analysis', group: 'Execute' },
        ];
    }

    // ── CORNEALIA BATCH ──────────────────────────
    if (moduleType === 'cornealia_batch') {
        if (stepId === 'batch_setup') return [
            { id: 'batch-folder', icon: '📁', label: 'Select Image Folder', group: 'Setup' },
            { id: 'image-type', icon: '🔧', label: 'Image Settings', group: 'Setup' },
            { id: 'seg-params', icon: '⚙️', label: 'Segmentation Parameters', group: 'Configure' },
            { id: 'morph-params', icon: '⚙️', label: 'Analysis Parameters', group: 'Configure' },
            { id: 'run-batch_setup', icon: '▶', label: 'Validate Folder', group: 'Action' },
        ];
        if (stepId === 'batch_run') return [
            { id: 'batch-workers', icon: '⚙️', label: 'Parallel Workers', group: 'Configure' },
            { id: 'run-batch_run', icon: '▶', label: 'Run Batch', group: 'Execute' },
        ];
        if (stepId === 'batch_results') return [
            { id: 'batch-export', icon: '💾', label: 'Export CSV', group: 'Output' },
        ];
    }

    // ── FASTIA ────────────────────────────────────
    if (moduleType === 'fastia') {
        if (stepId === 'import') return [
            { id: 'select-movie', icon: '📥', label: 'Select Movie', group: 'Setup' },
            { id: 'channel-setup', icon: '🎨', label: 'Channel Assignment', group: 'Setup' },
            { id: 'metadata', icon: '📋', label: 'Imaging Metadata', group: 'Setup' },
            { id: 'preview', icon: '🖼', label: 'Preview', group: 'View' },
        ];
        if (stepId === 'detection') return [
            { id: 'fa-det-params', icon: '⚙️', label: 'FA Detection Parameters', group: 'Configure' },
            { id: 'cell-seg-params', icon: '⚙️', label: 'Cell Segmentation Parameters', group: 'Configure' },
            { id: 'fa-det-preview', icon: '🔬', label: 'Preview FA Detection', group: 'Preview' },
            { id: 'cell-seg-preview', icon: '🔍', label: 'Preview Cell Segmentation', group: 'Preview' },
            { id: 'run-det', icon: '▶', label: 'Run Full Stack', group: 'Execute' },
            { id: 'det-results', icon: '🎬', label: 'View Results', group: 'View' },
        ];
        if (stepId === 'tracking') return [
            { id: 'track-params', icon: '⚙️', label: 'Tracking Parameters', group: 'Configure' },
            { id: 'run-track', icon: '▶', label: 'Run Tracking', group: 'Execute' },
            { id: 'track-results', icon: '🎬', label: 'View Trajectories', group: 'View' },
        ];
        if (stepId === 'classification') return [
            { id: 'class-params', icon: '⚙️', label: 'Classification Parameters', group: 'Configure' },
            { id: 'run-class', icon: '▶', label: 'Run Classification', group: 'Execute' },
        ];
        if (stepId === 'kinetics') return [
            { id: 'kin-params', icon: '⚙️', label: 'Display Parameters', group: 'Collective' },
            { id: 'kin-inspector', icon: '🔬', label: 'Track Inspector', group: 'Individual' },
        ];
        if (stepId === 'association') return [
            { id: 'assoc-method', icon: '🔬', label: 'Method Selection', group: 'Setup' },
            { id: 'assoc-pairs', icon: '🔗', label: 'Pair Selection', group: 'Setup' },
            { id: 'assoc-params', icon: '⚙️', label: 'Analysis Parameters', group: 'Configure' },
            { id: 'assoc-edge', icon: '🌊', label: 'Edge Analysis', group: 'Configure' },
            { id: 'run-assoc', icon: '▶', label: 'Run Association Analysis', group: 'Execute' },
        ];
        if (stepId === 'examination') return [
            { id: 'exam-display', icon: '⚙️', label: 'Display Settings', group: 'Overview' },
        ];
    }

    // ── IMMUNIA ───────────────────────────────────
    if (moduleType === 'immunia') {
        if (stepId === 'import') return [
            { id: 'select-movie', icon: '📥', label: 'Select Movie', group: 'Setup' },
            { id: 'channel-setup', icon: '🎨', label: 'Channel Assignment', group: 'Setup' },
            { id: 'metadata', icon: '📋', label: 'Imaging Metadata', group: 'Setup' },
            { id: 'preview', icon: '🖼', label: 'Preview', group: 'View' },
        ];
        if (stepId === 'segment') return [
            { id: 'seg-dead', icon: '🔴', label: 'Cytotoxicity Settings', group: 'Configure' },
            { id: 'seg-tumor', icon: '🟢', label: 'Target Cell Settings', group: 'Configure' },
            { id: 'seg-tissue', icon: '🔵', label: 'Substrate Settings', group: 'Configure' },
            { id: 'seg-nk', icon: '🟠', label: 'Effector Cell Settings', group: 'Configure' },
            { id: 'run-seg', icon: '▶', label: 'Run Segmentation', group: 'Execute' },
        ];
        if (stepId === 'track') return [
            { id: 'track-source', icon: '🔗', label: 'Tracking Source', group: 'Configure' },
            { id: 'track-linking', icon: '⚙️', label: 'Linking Parameters', group: 'Configure' },
            { id: 'track-filtering', icon: '🔍', label: 'Filtering', group: 'Configure' },
            { id: 'run-track', icon: '▶', label: 'Run Tracking', group: 'Execute' },
        ];
        if (stepId === 'signal_association') return [
            { id: 'sa-signals', icon: '📡', label: 'Signal Extraction', group: 'Configure' },
            { id: 'sa-method', icon: '⚙️', label: 'Association Method', group: 'Configure' },
            { id: 'sa-surrogates', icon: '🎲', label: 'Surrogate Testing', group: 'Configure' },
            { id: 'run-sa', icon: '▶', label: 'Run Association', group: 'Execute' },
        ];
        if (stepId === 'keller_segel') return [
            { id: 'ks-source', icon: '🧫', label: 'Source Configuration', group: 'Configure' },
            { id: 'ks-pde', icon: '📐', label: 'PDE Parameters', group: 'Configure' },
            { id: 'ks-solver', icon: '⚙️', label: 'Solver Settings', group: 'Configure' },
            { id: 'run-ks', icon: '▶', label: 'Run Analysis', group: 'Execute' },
        ];
        if (stepId === 'particle_tracking') return [
            { id: 'pt-motion', icon: '🏃', label: 'Motion Classification', group: 'Configure' },
            { id: 'pt-spatial', icon: '🗺', label: 'Spatial Analysis', group: 'Configure' },
            { id: 'pt-advanced', icon: '⚙️', label: 'Advanced Settings', group: 'Configure' },
            { id: 'run-pt', icon: '▶', label: 'Run Analysis', group: 'Execute' },
        ];
        if (stepId === 'graph_theory') return [
            { id: 'gt-networks', icon: '🕸', label: 'Network Construction', group: 'Configure' },
            { id: 'gt-analysis', icon: '📊', label: 'Analysis Modes', group: 'Configure' },
            { id: 'gt-advanced', icon: '⚙️', label: 'Advanced Parameters', group: 'Configure' },
            { id: 'run-gt', icon: '▶', label: 'Run Analysis', group: 'Execute' },
        ];
        if (stepId === 'integrated_analysis') return [
            { id: 'ia-placeholder', icon: '🔮', label: 'Integrated Analysis', group: 'Configure' },
        ];
        if (stepId === 'track_examiner') return [
            { id: 'te-placeholder', icon: '🔬', label: 'Track Examiner', group: 'Configure' },
        ];
    }

    // ── CELLVISIA ─────────────────────────────────
    if (moduleType === 'cellvisia') {
        // Module-level tree: all former "steps" become top-level groups.
        // This is the primary path now — cellvisia opens as a single sub-tab.
        if (stepId == null) return [
            // === 1. Source ===
            { id: 'cv-select-image',  icon: '📥', label: 'Load Image / Stack',      group: '1. Source' },
            { id: 'cv-channel-setup', icon: '🎨', label: 'Channel Assignment',      group: '1. Source' },
            { id: 'cv-metadata',      icon: '📋', label: 'Imaging Metadata',        group: '1. Source' },

            // === 2. Image Processing ===
            { id: 'cv-bg-sub',        icon: '🔧', label: 'Background Subtraction',  group: '2. Image Processing' },
            { id: 'cv-denoise',       icon: '🔧', label: 'Denoise',                 group: '2. Image Processing' },
            { id: 'cv-bleach',        icon: '🔧', label: 'Bleach Correction',       group: '2. Image Processing' },
            { id: 'cv-drift',         icon: '🔧', label: 'Drift Correction',        group: '2. Image Processing' },
            { id: 'cv-flatfield',     icon: '🔧', label: 'Flat-Field Correction',   group: '2. Image Processing' },
            { id: 'cv-contrast',      icon: '✨', label: 'Contrast (CLAHE)',        group: '2. Image Processing' },
            { id: 'cv-sharpen',       icon: '✨', label: 'Sharpen',                 group: '2. Image Processing' },
            { id: 'cv-bandpass',      icon: '🔬', label: 'Band-Pass Filter',        group: '2. Image Processing' },

            // === 3. Segmentation ===
            { id: 'cv-threshold',     icon: '⚙️', label: 'Threshold',               group: '3. Segmentation' },
            { id: 'cv-morphology',    icon: '⚙️', label: 'Morphological Ops',       group: '3. Segmentation' },
            { id: 'cv-watershed',     icon: '⚙️', label: 'Watershed',               group: '3. Segmentation' },

            // === 5. Measurement ===
            { id: 'cv-region-props',  icon: '📐', label: 'Region Properties',       group: '5. Measurement' },
            { id: 'cv-intensity',     icon: '📊', label: 'Intensity Statistics',    group: '5. Measurement' },
            { id: 'cv-spatial',       icon: '🗺', label: 'Spatial Statistics',      group: '5. Measurement' },

            // === 6. Export ===
            { id: 'cv-export-masks',  icon: '💾', label: 'Export Masks',            group: '6. Export' },
            { id: 'cv-export-csv',    icon: '💾', label: 'Export Measurements',     group: '6. Export' },
            { id: 'cv-export-overlay',icon: '🖼', label: 'Export Overlays',         group: '6. Export' },
        ];

        // Legacy per-step trees — kept for safety, not reached via normal flow.
        if (stepId === 'source') return [
            { id: 'select-image', icon: '📥', label: 'Load Image / Stack', group: 'Setup' },
            { id: 'channel-setup', icon: '🎨', label: 'Channel Assignment', group: 'Setup' },
            { id: 'metadata', icon: '📋', label: 'Imaging Metadata', group: 'Setup' },
            { id: 'preview', icon: '🖼', label: 'Preview', group: 'View' },
        ];
        if (stepId === 'preprocess') return [
            { id: 'cv-bg-sub', icon: '🔧', label: 'Background Subtraction', group: 'Operations' },
            { id: 'cv-denoise', icon: '🔧', label: 'Denoise', group: 'Operations' },
            { id: 'cv-bleach', icon: '🔧', label: 'Bleach Correction', group: 'Operations' },
            { id: 'cv-drift', icon: '🔧', label: 'Drift Correction', group: 'Operations' },
            { id: 'cv-flatfield', icon: '🔧', label: 'Flat-Field Correction', group: 'Operations' },
        ];
        if (stepId === 'enhance') return [
            { id: 'cv-contrast', icon: '🔧', label: 'Contrast (CLAHE)', group: 'Operations' },
            { id: 'cv-sharpen', icon: '🔧', label: 'Sharpen', group: 'Operations' },
            { id: 'cv-bandpass', icon: '🔧', label: 'Band-Pass Filter', group: 'Operations' },
        ];
        if (stepId === 'segment') return [
            { id: 'cv-threshold', icon: '⚙️', label: 'Threshold', group: 'Configure' },
            { id: 'cv-morphology', icon: '⚙️', label: 'Morphological Ops', group: 'Configure' },
            { id: 'cv-watershed', icon: '⚙️', label: 'Watershed', group: 'Configure' },
            { id: 'run-seg', icon: '▶', label: 'Run Segmentation', group: 'Execute' },
        ];
        if (stepId === 'measure') return [
            { id: 'cv-region-props', icon: '📐', label: 'Region Properties', group: 'Configure' },
            { id: 'cv-intensity', icon: '📊', label: 'Intensity Statistics', group: 'Configure' },
            { id: 'cv-spatial', icon: '🗺', label: 'Spatial Statistics', group: 'Configure' },
            { id: 'run-measure', icon: '▶', label: 'Run Measurement', group: 'Execute' },
        ];
        if (stepId === 'export') return [
            { id: 'cv-export-masks', icon: '💾', label: 'Export Masks', group: 'Output' },
            { id: 'cv-export-csv', icon: '💾', label: 'Export Measurements', group: 'Output' },
            { id: 'cv-export-overlay', icon: '🖼', label: 'Export Overlays', group: 'Output' },
        ];
    }

    // ── ASSOCIA ──────────────────────────────────
    if (moduleType === 'associa') {
        if (stepId == null) return [
            // === 0. Source ===
            { id: 'as-load-signals',    icon: '📥', label: 'Load Signals (CSV)',    group: '0. Source' },
            { id: 'as-signal-info',     icon: '📋', label: 'Signal Info',           group: '0. Source' },

            // === 1. Association ===
            { id: 'as-methods',         icon: '🔗', label: 'Method Config',         group: '1. Association' },

            // === 2. Pre-processing ===
            { id: 'as-stationarizer',   icon: '📐', label: 'Stationarizer',         group: '2. Pre-processing' },

            // === 3. Surrogate ===
            { id: 'as-surrogate',       icon: '🎲', label: 'Surrogate Config',      group: '3. Surrogate' },

            // === 4. Results ===
            { id: 'as-run',             icon: '▶', label: 'Run Analysis',           group: '4. Results' },

            // === 5. Export ===
            { id: 'as-export',          icon: '💾', label: 'Export Results',         group: '5. Export' },
        ];
    }

    // ── CELLADE ──────────────────────────────────
    if (moduleType === 'cellade') {
        if (stepId == null) return [
            // === 0. Source ===
            { id: 'cd-load-image',      icon: '📥', label: 'Load Image',              group: '0. Source' },
            { id: 'cd-image-info',      icon: '📋', label: 'Image Info',              group: '0. Source' },
            { id: 'cd-load-gt',         icon: '🎯', label: 'Load Ground Truth',       group: '0. Source' },

            // === 1. Parameters ===
            { id: 'cd-base-seg',        icon: '🔬', label: 'Base Segmentation',       group: '1. Parameters' },
            { id: 'cd-smoothing',       icon: '〰', label: 'Boundary Smoothing',      group: '1. Parameters' },
            { id: 'cd-merging',         icon: '🔗', label: 'Merging',                 group: '1. Parameters' },
            { id: 'cd-splitting',       icon: '✂', label: 'Splitting',               group: '1. Parameters' },

            // === 2. Run ===
            { id: 'cd-run',             icon: '▶', label: 'Run CellADE',             group: '2. Run' },

            // === 3. Results — populated via right-click Insert (handled by _buildResultsSection) ===

            // === 4. Export ===
            { id: 'cd-export-mask',     icon: '💾', label: 'Save Masks',              group: '4. Export' },
            { id: 'cd-export-overlay',  icon: '🖼', label: 'Save Overlay',            group: '4. Export' },
        ];
    }

    // ── CELLFADE ─────────────────────────────────
    if (moduleType === 'cellfade') {
        if (stepId == null) return [
            // === 0. Source ===
            { id: 'cf-load-image',      icon: '📥', label: 'Load FA Image',           group: '0. Source' },
            { id: 'cf-image-info',      icon: '📋', label: 'Image Info',              group: '0. Source' },

            // === 1. Parameters ===
            { id: 'cf-preprocess',      icon: '🔧', label: 'Preprocessing',           group: '1. Parameters' },
            { id: 'cf-seeds',           icon: '🎯', label: 'Seed Detection',          group: '1. Parameters' },
            { id: 'cf-fcm',             icon: '📐', label: 'FCM Objects',             group: '1. Parameters' },
            { id: 'cf-segmentation',    icon: '⚙️', label: 'Segmentation Mode',       group: '1. Parameters' },

            // === 2. Run ===
            { id: 'cf-run',             icon: '▶', label: 'Run CellFADE',            group: '2. Run' },

            // === 3. Results — insert-style ===

            // === 4. Export ===
            { id: 'cf-export-mask',     icon: '💾', label: 'Save Masks',              group: '4. Export' },
            { id: 'cf-export-overlay',  icon: '🖼', label: 'Save Overlay',            group: '4. Export' },
        ];
    }

    // ── ANNOTADE ──────────────────────────────────
    if (moduleType === 'annotade') {
        if (stepId == null) return [
            // === 0. Source ===
            { id: 'an-load-image',     icon: '📥', label: 'Load Image',              group: '0. Source' },
            { id: 'an-image-info',     icon: '📋', label: 'Image Info',              group: '0. Source' },
            { id: 'an-frame-nav',      icon: '🎞', label: 'Frame Navigation',        group: '0. Source' },

            // === 1. Tools ===
            { id: 'an-brush',          icon: '🖌', label: 'Brush / Eraser',          group: '1. Tools' },
            { id: 'an-shapes',         icon: '⬜', label: 'Rectangle / Ellipse',     group: '1. Tools' },
            { id: 'an-polygon',        icon: '📐', label: 'Polygon',                 group: '1. Tools' },
            { id: 'an-objects',        icon: '🏷', label: 'Object Manager',          group: '1. Tools' },

            // === 2. Assists ===
            { id: 'an-otsu',           icon: '📊', label: 'Otsu Threshold',          group: '2. Assists' },
            { id: 'an-threshold',      icon: '🔧', label: 'Manual Threshold',        group: '2. Assists' },
            { id: 'an-flood',          icon: '💧', label: 'Flood Fill',              group: '2. Assists' },
            { id: 'an-fcm',            icon: '🎯', label: 'Fuzzy C-Means',           group: '2. Assists' },

            // === 3. Export ===
            { id: 'an-export-labels',  icon: '💾', label: 'Export Labels',            group: '3. Export' },
        ];
    }

    // ── FALLBACK ──────────────────────────────────
    return [
        { id: 'params', icon: '⚙️', label: 'Parameters', group: 'Configure' },
        { id: 'run', icon: '▶', label: 'Run', group: 'Execute' },
        { id: 'results', icon: '📊', label: 'Results', group: 'Results' },
    ];
}

function getActiveItemLabel(treeItems, activeItem) {
    // treeItems is now a flat array
    const found = treeItems.find(i => i.id === activeItem.id);
    return found ? found.label : 'Settings';
}

// ═════════════════════════════════════════════
// SETTINGS CONTENT (middle column)
// ═════════════════════════════════════════════

function renderSettingsContent(moduleType, stepId, activeItem) {
    const { id } = activeItem;
    const wrap = (html) => `<div class="settings-form" data-module="${moduleType}" data-step="${stepId}" data-section="${id}" onchange="debouncedSaveParams(this)">${html}</div>`;

    // ── MOVIE PREVIEW (FASTIA + IMMUNIA) ─────────
    if (id === 'preview' && (moduleType === 'fastia' || moduleType === 'immunia')) {
        setTimeout(() => showMoviePlayer(), 50);
        return `<div style="display:flex;flex-direction:column;gap:10px">
            <p style="font-size:var(--fs-sm);color:var(--text-secondary)">Multi-channel viewer is shown in the Graphics panel.</p>
            <button class="btn btn-default" onclick="showMoviePlayer()">🔄 Refresh Viewer</button>

            <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:8px -12px 4px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">🔆 Brightness & Contrast</div>
            <p style="font-size:10px;color:var(--text-tertiary);margin-bottom:2px">Adjust display window. Auto uses 0.5–99.5 percentile of visible channels.</p>

            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary);min-width:28px">Min</span>
                <input type="range" min="0" max="65535" value="0" style="flex:1;accent-color:#42a5f5;height:3px" id="bcMin" oninput="updateBCSliderFromRange('min')">
                <input type="number" min="0" max="65535" value="0" style="width:60px;background:var(--surface-1);color:var(--text-primary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:2px 4px;font-size:var(--fs-xs);font-family:var(--font-mono);text-align:right" id="bcMinBox" oninput="updateBCSliderFromBox('min')">
            </div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary);min-width:28px">Max</span>
                <input type="range" min="0" max="65535" value="65535" style="flex:1;accent-color:#42a5f5;height:3px" id="bcMax" oninput="updateBCSliderFromRange('max')">
                <input type="number" min="0" max="65535" value="65535" style="width:60px;background:var(--surface-1);color:var(--text-primary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:2px 4px;font-size:var(--fs-xs);font-family:var(--font-mono);text-align:right" id="bcMaxBox" oninput="updateBCSliderFromBox('max')">
            </div>

            <div style="display:flex;gap:6px;margin-top:2px">
                <button class="btn btn-default" onclick="autoBrightContrast('percentile')" style="flex:1;font-size:var(--fs-xs)">⚡ Auto</button>
                <button class="btn btn-default" onclick="autoBrightContrast('reset')" style="font-size:var(--fs-xs)">↺ Reset</button>
            </div>
        </div>`;
    }

    // ── CORNEALIA ─────────────────────────────────
    if (moduleType === 'cornealia') {
        if (id === 'select-image') return wrap(`
            <div class="form-row" style="flex-direction:column;align-items:stretch"><span class="form-label">Image File</span><input class="form-input" data-param="input_file" placeholder="Select image..." readonly><button class="btn btn-default" onclick="selectInputFile(this)" style="margin-top:4px">Browse</button></div>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Select a corneal endothelium image (specular microscopy or raw).</p>`);

        if (id === 'image-type') return wrap(`
            <div class="form-row"><span class="form-label">Machine Output?</span><select class="form-select" data-param="is_machine_output"><option>Yes</option><option>No</option></select></div>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">"Yes" if the image has built-in cell detection dots from the specular microscope.</p>`);

        if (id === 'preview') return `
            <p style="font-size:var(--fs-sm);color:var(--text-tertiary)">Select an image first, then preview will appear in the Graphics panel.</p>`;

        if (id === 'seg-params') return wrap(`
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">CellADE Segmentation Parameters</p>
            <div class="form-row"><span class="form-label">FCM Method</span><select class="form-select" data-param="fcm_method"><option value="local">Local</option><option value="global">Global</option></select></div>
            <div class="form-row"><span class="form-label">LoG Min Sigma</span><input class="form-input" data-param="log_min_sigma" type="number" value="5" style="width:80px"></div>
            <div class="form-row"><span class="form-label">LoG Max Sigma</span><input class="form-input" data-param="log_max_sigma" type="number" value="30" style="width:80px"></div>
            <div class="form-row"><span class="form-label">LoG Num Sigma</span><input class="form-input" data-param="log_num_sigma" type="number" value="15" style="width:80px"></div>
            <div class="form-row"><span class="form-label">LoG Threshold</span><input class="form-input" data-param="log_threshold" type="number" value="0.01" step="0.001" style="width:80px"></div>
            <div class="form-row"><span class="form-label">FCM Threshold</span><input class="form-input" data-param="fcm_threshold" type="number" value="0.4" step="0.05" style="width:80px"></div>
            <div class="form-row"><span class="form-label">Min Cell Area</span><input class="form-input" data-param="min_area" type="number" value="30" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>`);

        if (id === 'morph-params') return wrap(`
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Collective Order Analysis</p>
            <div class="form-row"><span class="form-label">Pixel Size</span><input class="form-input" data-param="pixel_size" type="number" value="0.58" step="0.01" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">μm/px</span></div>
            <div class="form-row"><span class="form-label">Fitting Method</span><select class="form-select" data-param="fitting_method"><option value="ds">Damped Sine (recommended)</option><option value="morse_guided">Morse Guided</option><option value="quad_guided">Quadratic Guided</option><option value="morse_raw">Morse Raw</option><option value="quad_raw">Quadratic Raw (Yamamoto)</option></select></div>
            <div class="form-row"><span class="form-label">Exclusion Ratio</span><input class="form-input" data-param="exclusion_ratio" type="number" value="0.15" step="0.01" style="width:80px"></div>
            <div class="form-row"><span class="form-label">Shell Thickness</span><input class="form-input" data-param="shell_thickness" type="number" value="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
            <div class="form-row"><span class="form-label">Fitting Half Width</span><input class="form-input" data-param="fitting_half_width" type="number" value="10" style="width:80px"></div>
            <div class="form-row"><span class="form-label">Savgol Window</span><input class="form-input" data-param="savgol_window" type="number" value="11" style="width:80px"></div>
            <div class="form-row"><span class="form-label">Savgol Order</span><input class="form-input" data-param="savgol_order" type="number" value="3" style="width:80px"></div>`);
    }

    // ── CORNEALIA BATCH ──────────────────────────
    if (moduleType === 'cornealia_batch') {
        if (id === 'batch-folder') return wrap(`
            <div class="form-row" style="flex-direction:column;align-items:stretch"><span class="form-label">Image Folder</span><input class="form-input" data-param="batch_folder" placeholder="Select folder..." readonly><button class="btn btn-default" onclick="selectBatchFolder(this)" style="margin-top:4px">Browse</button></div>
            <div id="batchFolderInfo" style="margin-top:8px;font-size:var(--fs-xs);color:var(--text-tertiary)"></div>`);

        if (id === 'image-type') return wrap(`
            <div class="form-row"><span class="form-label">Machine Output?</span><select class="form-select" data-param="is_machine_output"><option>Yes</option><option>No</option></select></div>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">"Yes" if images have built-in cell detection dots.</p>`);

        if (id === 'seg-params') return wrap(`
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">CellADE Segmentation Parameters</p>
            <div class="form-row"><span class="form-label">FCM Method</span><select class="form-select" data-param="fcm_method"><option value="local">Local</option><option value="global">Global</option></select></div>
            <div class="form-row"><span class="form-label">LoG Min Sigma</span><input class="form-input" data-param="log_min_sigma" type="number" value="5" style="width:80px"></div>
            <div class="form-row"><span class="form-label">LoG Max Sigma</span><input class="form-input" data-param="log_max_sigma" type="number" value="30" style="width:80px"></div>
            <div class="form-row"><span class="form-label">LoG Threshold</span><input class="form-input" data-param="log_threshold" type="number" value="0.01" step="0.001" style="width:80px"></div>
            <div class="form-row"><span class="form-label">Min Cell Area</span><input class="form-input" data-param="min_area" type="number" value="30" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>`);

        if (id === 'morph-params') return wrap(`
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Analysis Parameters</p>
            <div class="form-row"><span class="form-label">Pixel Size</span><input class="form-input" data-param="pixel_size" type="number" value="0.58" step="0.01" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">μm/px</span></div>
            <div class="form-row"><span class="form-label">Fitting Method</span><select class="form-select" data-param="fitting_method"><option value="ds">Damped Sine (recommended)</option><option value="morse_guided">Morse Guided</option><option value="quad_guided">Quadratic Guided</option><option value="morse_raw">Morse Raw</option><option value="quad_raw">Quadratic Raw (Yamamoto)</option></select></div>
            <div class="form-row"><span class="form-label">Exclusion Ratio</span><input class="form-input" data-param="exclusion_ratio" type="number" value="0.15" step="0.01" style="width:80px"></div>
            <div class="form-row"><span class="form-label">Shell Thickness</span><input class="form-input" data-param="shell_thickness" type="number" value="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>`);

        if (id === 'batch-workers') return wrap(`
            <div class="form-row"><span class="form-label">Parallel Workers</span><input class="form-input" data-param="n_workers" type="number" value="1" min="1" max="16" style="width:80px"></div>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Number of CPU cores to use. Set to 1 for sequential processing.</p>`);

        if (id === 'batch-export') return `
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Batch Results</p>
            <button class="btn btn-primary" onclick="showBatchTable('${moduleType}','${stepId}')" style="margin-bottom:8px">📊 Show Results Table</button>
            <button class="btn btn-default" onclick="downloadBatchCSV('${moduleType}','${stepId}')">💾 Download CSV</button>`;
    }

    // ── RUN BUTTONS (any module) ──────────────────
    if (id.startsWith('run-') || id === 'run') {
        const runStepId = stepId;
        const runKey = `${moduleType}-${runStepId}`;
        // Restore saved run state if available
        const ws = getActiveWorkspace();
        const sub = ws?.subtabs.get(ws?.activeSubtab);
        const savedLog = sub?._runLogs?.[runKey] || '';
        const defaultMsg = savedLog || 'Ready to run. Click ▶ to start.';
        // Check if a task is currently running for this step
        const isRunning = _tasks.some(t => t.stepId === runStepId && t.pipelineId === sub?.pipelineId && t.status === 'running');
        // Also try to load from backend if no in-memory state
        if (!savedLog && sub) {
            setTimeout(() => _loadSavedRunLog(sub, moduleType, runStepId), 100);
        }
        return `
            <div class="run-panel" data-module="${moduleType}" data-step="${runStepId}">
                <div style="display:flex;gap:6px;margin-bottom:12px">
                    <button class="btn btn-primary" onclick="doRunAnalysis('${moduleType}','${runStepId}')">▶ Run</button>
                    <button class="btn btn-default" onclick="doStopAnalysis('${moduleType}','${runStepId}')" id="stopBtn-${moduleType}-${runStepId}" ${isRunning ? '' : 'disabled'} style="${isRunning ? 'color:var(--status-error)' : 'opacity:0.4;cursor:default'}">⏹ Stop</button>
                    <button class="btn btn-default" onclick="doResetParams('${moduleType}','${runStepId}')">Reset</button>
                </div>
                <div style="position:relative">
                    <button onclick="navigator.clipboard.writeText(document.getElementById('runLog-${moduleType}-${runStepId}').innerText).then(()=>{this.textContent='✓ Copied';setTimeout(()=>this.textContent='📋 Copy',1500)})" style="position:absolute;top:4px;right:4px;z-index:1;font-size:10px;padding:2px 6px;background:var(--surface-3);border:1px solid var(--chrome-border);border-radius:3px;color:var(--text-tertiary);cursor:pointer">📋 Copy</button>
                    <div class="run-log" id="runLog-${moduleType}-${runStepId}" style="background:var(--surface-1);border:1px solid var(--surface-3);border-radius:4px;padding:8px;font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--text-tertiary);min-height:200px;max-height:calc(100vh - 280px);overflow-y:auto">
                    ${defaultMsg}
                </div>
                </div>
            </div>`;
    }

    // ── FASTIA: DETECTION PARAMETERS ────────────
    if (id === 'fa-det-params' && moduleType === 'fastia') {
        // Populate FA channel dropdown from channel assignment after render
        setTimeout(() => {
            const sel = document.getElementById('detChannelSelect');
            if (!sel) return;
            const ws = getActiveWorkspace();
            const sub = ws?.subtabs.get(ws?.activeSubtab);
            // Look for channel names in import step's local params or backend params
            const importSub = [...(ws?.subtabs.values() || [])].find(s => s.stepId === 'import' && s.pipelineId === sub?.pipelineId);
            const chParams = importSub?._localParams?.['channel-setup'] || {};
            const names = [chParams.ch1_name, chParams.ch2_name, chParams.ch3_name, chParams.ch4_name].filter(Boolean);
            if (names.length === 0) names.push('Vinculin', 'Paxillin');
            sel.innerHTML = names.map(n => `<option value="${n.toLowerCase()}">${n}</option>`).join('');
            // Restore saved selection after populating options
            const saved = sub?._localParams?.['fa-det-params']?.detection_channel;
            if (saved) sel.value = saved;
        }, 50);
        const hdr = (label) => `<div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:10px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">${label}</div>`;
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:4px">CellFADE — Focal Adhesion Detection</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:6px">Seed-guided local clustering for training-free FA segmentation.</p>
        ${hdr('Channel & Execution')}
        <div class="form-row"><span class="form-label">FA Channel</span><select class="form-select" data-param="detection_channel" id="detChannelSelect"><option>Loading...</option></select></div>
        <div class="form-row"><span class="form-label">Workers</span><input class="form-input" data-param="n_workers" type="number" value="1" min="1" max="16" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">for full stack</span></div>
        ${hdr('Difference of Gaussians')}
        <div class="form-row"><span class="form-label">Low Sigma</span><input class="form-input" data-param="dog_low_sigma" type="number" value="1" min="0.1" step="0.5" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
        <div class="form-row"><span class="form-label">High Sigma</span><input class="form-input" data-param="dog_high_sigma" type="number" value="20" min="1" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
        ${hdr('Frangi Vesselness Filter')}
        <div class="form-row"><span class="form-label">Scales</span><input class="form-input" data-param="frangi_scales" type="text" value="1,2,3" style="width:100px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">comma-separated</span></div>
        <div class="form-row"><span class="form-label">Threshold</span><input class="form-input" data-param="frangi_threshold" type="number" value="0.015" min="0" step="0.005" style="width:100px"></div>
        <div class="form-row"><span class="form-label">Beta</span><input class="form-input" data-param="frangi_beta" type="number" value="0.5" min="0" step="0.1" style="width:80px"></div>
        ${hdr('Hessian')}
        <div class="form-row"><span class="form-label">Sigma</span><input class="form-input" data-param="hessian_sigma" type="number" value="2.0" min="0.1" step="0.5" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
        ${hdr('Shape Filtering')}
        <div class="form-row"><span class="form-label">Min Aspect Ratio</span><input class="form-input" data-param="min_aspect_ratio" type="number" value="1.0" min="0" step="0.5" style="width:80px"></div>
        <div class="form-row"><span class="form-label">Max Aspect Ratio</span><input class="form-input" data-param="max_aspect_ratio" type="number" value="5.0" min="1" step="0.5" style="width:80px"></div>
        <div class="form-row"><span class="form-label">Min Object Area</span><input class="form-input" data-param="min_object_area" type="number" value="10" min="1" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px²</span></div>
        ${hdr('Fuzzy C-Means Clustering')}
        <div class="form-row"><span class="form-label">Min Membership</span><input class="form-input" data-param="global_fcm_min_membership" type="number" value="0.7" min="0" max="1" step="0.05" style="width:80px"></div>
        ${hdr('Watershed & Seeds')}
        <div class="form-row"><span class="form-label">Use Watershed</span><select class="form-select" data-param="use_watershed"><option value="true">Yes</option><option value="false">No</option></select></div>
        <div class="form-row"><span class="form-label">Fallback Seed Radius</span><input class="form-input" data-param="fallback_seed_radius" type="number" value="4" min="1" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
        ${hdr('Feature Fusion')}
        <div class="form-row"><span class="form-label">Structure Weight</span><input class="form-input" data-param="structure_weight" type="number" value="0.4" min="0" max="1" step="0.05" style="width:80px"></div>
        <div class="form-row"><span class="form-label">Fusion Mode</span><select class="form-select" data-param="fusion_mode"><option value="additive">Additive</option><option value="multiplicative">Multiplicative</option></select></div>`);
    }

    if (id === 'cell-seg-params' && moduleType === 'fastia') {
        // Populate channel dropdown for cell segmentation
        setTimeout(() => {
            const sel = document.getElementById('cellSegChannelSelect');
            if (!sel) return;
            const ws = getActiveWorkspace();
            const sub = ws?.subtabs.get(ws?.activeSubtab);
            const importSub = [...(ws?.subtabs.values() || [])].find(s => s.stepId === 'import' && s.pipelineId === sub?.pipelineId);
            const chParams = importSub?._localParams?.['channel-setup'] || {};
            const names = [chParams.ch1_name, chParams.ch2_name, chParams.ch3_name, chParams.ch4_name].filter(Boolean);
            if (names.length === 0) names.push('Vinculin', 'Paxillin');
            sel.innerHTML = names.map(n => `<option value="${n.toLowerCase()}">${n}</option>`).join('');
            // Restore saved selection after populating options
            const saved = sub?._localParams?.['cell-seg-params']?.seg_channel;
            if (saved) sel.value = saved;
            // Show/hide conditional fields based on saved method
            _updateCellSegMethodFields();
        }, 50);
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Cell Segmentation</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Global cell area segmentation. The largest connected component is kept as the cell body, removing debris and small objects.</p>
        <div class="form-row"><span class="form-label">Channel</span><select class="form-select" data-param="seg_channel" id="cellSegChannelSelect"><option>Loading...</option></select></div>
        <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="seg_method" id="cellSegMethodSelect" onchange="_updateCellSegMethodFields()"><option value="otsu">Otsu (automatic)</option><option value="manual">Manual Threshold</option><option value="min_max">Min/Max Removal + Otsu</option></select></div>
        <div class="form-row"><span class="form-label">Smooth Sigma</span><input class="form-input" data-param="smooth_sigma" type="number" value="5" step="0.5" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
        <div id="cellSegOtsuFields">
            <div class="form-row"><span class="form-label">Global Threshold</span><select class="form-select" data-param="global_threshold"><option value="true">Yes (stable Otsu)</option><option value="false">No (per-frame)</option></select></div>
        </div>
        <div id="cellSegManualFields" style="display:none">
            <div class="form-row"><span class="form-label">Threshold Value</span><input class="form-input" data-param="manual_threshold" type="number" step="1" style="width:100px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">intensity</span></div>
        </div>
        <div id="cellSegMinMaxFields" style="display:none">
            <div class="form-row"><span class="form-label">Intensity Min</span><input class="form-input" data-param="intensity_min" type="number" step="1" style="width:100px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">remove below</span></div>
            <div class="form-row"><span class="form-label">Intensity Max</span><input class="form-input" data-param="intensity_max" type="number" step="1" style="width:100px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">clip above</span></div>
        </div>
        <div class="form-row"><span class="form-label">Keep Largest Only</span><select class="form-select" data-param="keep_largest"><option value="true">Yes</option><option value="false">No (keep all)</option></select></div>`);
    }

    // ── FASTIA: FA DETECTION PREVIEW ────────────
    if (id === 'fa-det-preview' && moduleType === 'fastia') {
        const ws = getActiveWorkspace();
        const activeSub = ws?.subtabs.get(ws?.activeSubtab);
        const movieInfo = activeSub?._movieInfo || {};
        const nFrames = movieInfo.n_frames || 91;
        const savedResult = activeSub?._detPreviewResult;
        const savedFrame = savedResult?.frame || 0;
        const savedStatus = activeSub?._statusBoxes?.detPreviewStatus || (savedResult?.error ? `<span style="color:var(--status-error)">✗ ${savedResult.error}</span>` : 'Set parameters, select a frame, then click Detect.');
        // Restore graphics when this panel opens
        setTimeout(() => {
            if (savedResult?.image) {
                _showDetectionGraphics(savedResult.image, savedResult.nFA, savedResult.frame, savedResult.channel, savedResult.warning);
            } else {
                const frameIdx = parseInt(document.getElementById('detPreviewFrameInput')?.value || '0');
                _showDetectionPreviewFrame(frameIdx);
            }
            _restoreStatusBoxes(activeSub, 'detPreviewStatus');
        }, 100);
        return `
        <div style="display:flex;flex-direction:column;gap:8px">
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Preview FA Detection</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Select a frame and run CellFADE to preview. Tune parameters before running the full stack.</p>
            <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:4px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">Frame Selection</div>
            <div class="form-row"><span class="form-label">Frame</span><input class="form-input" id="detPreviewFrameInput" type="number" value="${savedFrame}" min="0" max="${nFrames - 1}" style="width:70px" onchange="_showDetectionPreviewFrame(parseInt(this.value))"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">/ ${nFrames - 1}</span></div>
            <input type="range" min="0" max="${nFrames - 1}" value="${savedFrame}" style="width:100%;accent-color:var(--brand-accent)" oninput="document.getElementById('detPreviewFrameInput').value=this.value;_showDetectionPreviewFrame(parseInt(this.value))">
            <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:4px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">Run Detection</div>
            <button class="btn btn-primary" onclick="doDetectionPreview()">🔍 Detect on This Frame</button>
            <div id="detPreviewStatus" style="font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                ${savedStatus}
            </div>
        </div>`;
    }

    // ── FASTIA: CELL SEGMENTATION PREVIEW ─────────
    if (id === 'cell-seg-preview' && moduleType === 'fastia') {
        const ws = getActiveWorkspace();
        const activeSub = ws?.subtabs.get(ws?.activeSubtab);
        const movieInfo = activeSub?._movieInfo || {};
        const nFrames = movieInfo.n_frames || 91;
        const savedResult = activeSub?._cellSegPreviewResult;
        const savedFrame = savedResult?.frame || 0;
        const savedStatus = activeSub?._statusBoxes?.cellSegPreviewStatus || (savedResult?.error ? `<span style="color:var(--status-error)">✗ ${savedResult.error}</span>` : 'Set parameters, select a frame, then click Segment.');
        // Restore graphics when this panel opens
        setTimeout(() => {
            if (savedResult?.image) {
                _showCellSegGraphics(savedResult.image, savedResult.frame, savedResult.info);
            } else {
                const frameIdx = parseInt(document.getElementById('cellSegPreviewFrameInput')?.value || '0');
                _showCellSegPreviewFrame(frameIdx);
            }
            _restoreStatusBoxes(activeSub, 'cellSegPreviewStatus');
        }, 100);
        return `
        <div style="display:flex;flex-direction:column;gap:8px">
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Preview Cell Segmentation</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Preview the global cell area mask. The largest connected component is kept as the cell body.</p>
            <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:4px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">Frame Selection</div>
            <div class="form-row"><span class="form-label">Frame</span><input class="form-input" id="cellSegPreviewFrameInput" type="number" value="${savedFrame}" min="0" max="${nFrames - 1}" style="width:70px" onchange="_showCellSegPreviewFrame(parseInt(this.value))"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">/ ${nFrames - 1}</span></div>
            <input type="range" min="0" max="${nFrames - 1}" value="${savedFrame}" style="width:100%;accent-color:var(--brand-accent)" oninput="document.getElementById('cellSegPreviewFrameInput').value=this.value;_showCellSegPreviewFrame(parseInt(this.value))">
            <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:4px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">Run Segmentation</div>
            <button class="btn btn-primary" onclick="doCellSegPreview()">🔍 Segment This Frame</button>
            <div id="cellSegPreviewStatus" style="font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                ${savedStatus}
            </div>
        </div>`;
    }

    // ── FASTIA: DETECTION RESULTS (video player) ─
    if (id === 'det-results' && moduleType === 'fastia') {
        setTimeout(() => showDetectionResultsPanel(), 100);
        return `
        <div style="display:flex;flex-direction:column;gap:10px">
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Detection Results</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Pre-render the detection overlay for smooth playback.</p>
            <button class="btn btn-primary" id="renderOverlayBtn" onclick="renderDetectionOverlay()">🎬 Render Overlay</button>
            <div id="renderProgress" style="display:none">
                <div class="run-progress-bar" style="margin-bottom:4px"><div class="run-progress-fill" id="renderProgressFill" style="width:0%"></div></div>
                <div id="renderProgressLabel" style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">Preparing...</div>
            </div>
            <div id="renderStatus" style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono);min-height:40px;padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                Click Render to pre-compute all frames.
            </div>
        </div>`;
    }

    // ── FASTIA: TRACKING PARAMETERS ──────────────
    if (id === 'track-params' && moduleType === 'fastia') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const savedTrackStatus = sub0?._statusBoxes?.trackParamsStatus || 'Configure parameters, then click Run Tracking.';
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">FA Tracking Parameters</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Links detected FAs across frames into tracks using trackpy.</p>
        <div class="form-row"><span class="form-label">Max Search Range</span><input class="form-input" data-param="max_search_range" type="number" value="5" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
        <div class="form-row"><span class="form-label">Memory (gap close)</span><input class="form-input" data-param="memory" type="number" value="8" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        <div class="form-row"><span class="form-label">Min Track Length</span><input class="form-input" data-param="min_track_length" type="number" value="3" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-top:14px;margin-bottom:10px">Cost Function Weights</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:6px">Weights for the assignment cost matrix (distance, size similarity, orientation).</p>
        <div class="form-row"><span class="form-label">Distance</span><input class="form-input" data-param="w_dist" type="number" value="1.0" step="0.05" style="width:80px"></div>
        <div class="form-row"><span class="form-label">Size</span><input class="form-input" data-param="w_size" type="number" value="0.05" step="0.01" style="width:80px"></div>
        <div class="form-row"><span class="form-label">Orientation</span><input class="form-input" data-param="w_orient" type="number" value="0.3" step="0.05" style="width:80px"></div>
        <div id="trackParamsStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
            ${savedTrackStatus}
        </div>`);
    }

    if (id === 'track-results' && moduleType === 'fastia') {
        setTimeout(() => showTrackingResultsPanel(), 100);
        return `
        <div style="display:flex;flex-direction:column;gap:10px">
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Tracking Results</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Pre-render trajectory overlay for smooth playback.</p>
            <button class="btn btn-primary" id="renderTrackBtn" onclick="renderTrackingOverlay()">🎬 Render Trajectories</button>
            <div id="trackRenderProgress" style="display:none">
                <div class="run-progress-bar" style="margin-bottom:4px"><div class="run-progress-fill" id="trackRenderFill" style="width:0%"></div></div>
                <div id="trackRenderLabel" style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">Preparing...</div>
            </div>
            <div id="trackResultsStatus" style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono);min-height:40px;padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                Checking results...
            </div>
        </div>`;
    }

    // ── FASTIA: CLASSIFICATION PARAMETERS ────────
    if (id === 'class-params' && moduleType === 'fastia') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const savedClassStatus = sub0?._statusBoxes?.classParamsStatus || 'Configure parameters, then click Run Classification.';
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">FA Classification</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Extracts 30 features per track, then classifies into functional groups.</p>
        <div class="form-row"><span class="form-label">Mode</span><select class="form-select" data-param="class_mode"><option value="9G">9-Group</option><option value="5G">5-Group</option></select></div>
        <div class="form-row"><span class="form-label">Min Group Size</span><input class="form-input" data-param="min_group_size" type="number" value="5" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">tracks</span></div>
        <div class="form-row"><span class="form-label">Discriminability</span><select class="form-select" data-param="run_discriminability"><option value="true">Run</option><option value="false">Skip</option></select></div>
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-top:14px;margin-bottom:10px">Performance</p>
        <div class="form-row"><span class="form-label">Workers</span><input class="form-input" data-param="n_workers" type="number" value="0" step="1" min="0" max="32" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">0 = auto (CPU count)</span></div>
        <div id="classParamsStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
            ${savedClassStatus}
        </div>`);
    }

    if (id === 'class-results' && moduleType === 'fastia') {
        setTimeout(() => showClassificationResultsPanel(), 100);
        return `
        <div style="display:flex;flex-direction:column;gap:10px">
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Classification Results</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">View feature extraction and group assignment results.</p>
            <div id="classResultsStatus" style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono);min-height:60px;padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                Checking results...
            </div>
        </div>`;
    }

    // ── FASTIA: KINETICS DISPLAY PARAMETERS ─────
    if (id === 'kin-params' && moduleType === 'fastia') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const savedStatus = sub0?._statusBoxes?.kinParamsStatus || 'Rates are pre-computed during classification. Use Insert Results for collective plots.';
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Kinetic Rate Display</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Assembly and disassembly rates were extracted during classification (30 features per track). Configure display filters for plots.</p>
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-top:12px;margin-bottom:8px">Filters</p>
        <div class="form-row"><span class="form-label">Min R²</span><input class="form-input" data-param="kin_min_r2" type="number" value="0.5" step="0.05" min="0" max="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">exclude poor fits</span></div>
        <div class="form-row"><span class="form-label">Min Track Length</span><input class="form-input" data-param="kin_min_length" type="number" value="5" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        <div class="form-row"><span class="form-label">Show Groups</span><select class="form-select" data-param="kin_groups"><option value="all">All Groups</option><option value="na">NAs only (G1-G5)</option><option value="fa">FAs only (G6-G8)</option><option value="valid">Exclude Noise (G9)</option></select></div>
        <div id="kinParamsStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
            ${savedStatus}
        </div>`);
    }

    // ── FASTIA: TRACK INSPECTOR ──────────────────
    if (id === 'kin-inspector' && moduleType === 'fastia') {
        setTimeout(() => initTrackInspector(), 100);
        return `
        <div style="display:flex;flex-direction:column;gap:8px">
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Track Inspector</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Select a track to view individual kinetic fit details.</p>
            <div class="form-row"><span class="form-label">Group Filter</span><select class="form-select" id="inspectorGroupFilter" style="width:140px" onchange="filterInspectorTracks()">
                <option value="all">All Groups</option>
            </select></div>
            <div class="form-row"><span class="form-label">Track</span><select class="form-select" id="inspectorTrackSelect" style="width:180px" onchange="onInspectorTrackChange()">
                <option value="">— Select Track —</option>
            </select></div>
            <div style="display:flex;gap:6px">
                <button class="btn btn-primary" onclick="inspectSelectedTrack()" id="inspectBtn" disabled>🔬 Inspect</button>
                <button class="btn btn-default" onclick="inspectPrevTrack()">◀</button>
                <button class="btn btn-default" onclick="inspectNextTrack()">▶</button>
            </div>
            <div id="inspectorQuickStats" style="font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:60px;padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                Loading classification data...
            </div>
        </div>`;
    }

    // ── EXPORT ────────────────────────────────────
    if (id === 'export') return `
        <div class="form-row"><span class="form-label">Format</span><select class="form-select"><option>CSV</option><option>JSON</option><option>Excel</option></select></div>
        <button class="btn btn-primary" style="margin-top:8px">💾 Export</button>`;

    // ── FASTIA: ASSOCIATION ANALYSIS ─────────────
    if (id === 'assoc-method') return wrap(`
        <div style="padding:4px 0;margin:0 0 8px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Methods</div>
        <div class="form-row"><span class="form-label">Correlation</span><select class="form-select" data-param="run_correlation"><option value="true">Enabled</option><option value="false">Disabled</option></select></div>
        <div class="form-row"><span class="form-label">Granger Causality</span><select class="form-select" data-param="run_granger"><option value="true">Enabled</option><option value="false">Disabled</option></select></div>
        <div class="form-row"><span class="form-label">CCM</span><select class="form-select" data-param="run_ccm"><option value="true">Enabled</option><option value="false">Disabled</option></select></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Select which coupling methods to run. Configure pairs and parameters in the next panels.</p>`);

    // ── FASTIA: PAIR SELECTION ────────────────────
    // ── FASTIA: ASSOCIATION RUN METADATA ────────
    if (id.startsWith('run_meta_') && moduleType === 'fastia') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const runItem = sub0?.insertedResults?.find(r => r.plotType === id);
        const meta = runItem?._runMeta || {};
        const runId = runItem?._runId || '';

        return `
        <div style="display:flex;flex-direction:column;gap:8px">
            <div style="padding:4px 0;margin:0 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Run Info</div>
            <div style="font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-secondary);padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);line-height:1.6">
                <div><span style="color:var(--text-tertiary)">Methods:</span> <b>${(meta.methods || []).join(', ')}</b></div>
                <div><span style="color:var(--text-tertiary)">Pairs:</span> ${meta.channel_pairs || '—'}</div>
                <div><span style="color:var(--text-tertiary)">Tracks:</span> ${meta.n_tracks || 0}</div>
                <div><span style="color:var(--text-tertiary)">Surrogates:</span> ${meta.n_surrogates || 0} (${meta.surrogate_method || '—'})</div>
                <div><span style="color:var(--text-tertiary)">Stationarizer:</span> ${meta.stationarizer || '—'}</div>
                <div><span style="color:var(--text-tertiary)">Min Length:</span> ${meta.min_track_length || '—'} frames</div>
                <div style="margin-top:4px;padding-top:4px;border-top:1px solid var(--chrome-border)">
                    <span style="color:var(--text-tertiary)">Significant:</span> <b style="color:var(--status-ok)">${meta.n_significant || 0}/${meta.n_total_tests || 0}</b> (${((meta.significance_rate || 0) * 100).toFixed(1)}%)
                </div>
                <div><span style="color:var(--text-tertiary)">Time:</span> ${meta.elapsed_s || 0}s</div>
                <div><span style="color:var(--text-tertiary)">Date:</span> ${meta.timestamp ? new Date(meta.timestamp).toLocaleString() : '—'}</div>
            </div>

            <div style="padding:4px 0;margin:8px 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Generate Plots</div>
            <div style="display:flex;flex-direction:column;gap:4px">
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_significance')" style="text-align:left;font-size:var(--fs-xs)">📊 Significance Rates</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_distributions')" style="text-align:left;font-size:var(--fs-xs)">📦 Statistic Distributions</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_effect_sizes')" style="text-align:left;font-size:var(--fs-xs)">📈 P-value Distribution</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_method_agreement')" style="text-align:left;font-size:var(--fs-xs)">🗺 Method Agreement</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_group_coupling')" style="text-align:left;font-size:var(--fs-xs)">🏷 Coupling by Group</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_spatial_coupling')" style="text-align:left;font-size:var(--fs-xs)">🗺 Spatial Coupling Map</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_edge_pie')" style="text-align:left;font-size:var(--fs-xs)">🥧 Edge × Coupling Pie</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_edge_spatial')" style="text-align:left;font-size:var(--fs-xs)">🌊 Edge × Coupling Spatial</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_edge_pie')" style="text-align:left;font-size:var(--fs-xs)">🥧 Coupling × Edge Condition</button>
                <button class="btn btn-default" onclick="insertAssociationRunPlot('${runId}','assoc_edge_spatial')" style="text-align:left;font-size:var(--fs-xs)">🌊 Edge Spatial Map</button>
            </div>

            <div style="padding:4px 0;margin:8px 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px">Actions</div>
            <button class="btn btn-default" onclick="deleteAssociationRun('${runId}')" style="color:var(--status-error);font-size:var(--fs-xs)">🗑 Delete This Run</button>
        </div>`;
    }

    if (id.startsWith('run_meta_') && moduleType === 'immunia') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const runItem = sub0?.insertedResults?.find(r => r.plotType === id);
        const meta = runItem?._runMeta || {};
        const runId = runItem?._runId || '';

        // ── GRAPH THEORY RUN INFO ──
        if (sub0?.stepId === 'graph_theory') {
            const nets = (meta.network_types || []).join(', ');
            const modes = (meta.analysis_modes || []).join(', ');
            const methods = (meta.available_methods || []).join(', ');
            return `
            <div style="display:flex;flex-direction:column;gap:8px">
                <div style="padding:4px 0;margin:0 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Run Info</div>
                <div style="font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-secondary);padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);line-height:1.6">
                    <div><span style="color:var(--text-tertiary)">Networks:</span> <b>${nets || '—'}</b></div>
                    <div><span style="color:var(--text-tertiary)">Methods:</span> ${methods || '—'}</div>
                    <div><span style="color:var(--text-tertiary)">Tracks:</span> ${meta.n_tracks || 0}</div>
                    <div><span style="color:var(--text-tertiary)">Analyses:</span> ${modes || '—'}</div>
                    <div><span style="color:var(--text-tertiary)">Source Runs:</span> ${Array.isArray(meta.source_runs) ? meta.source_runs.length + ' selected' : 'all'}</div>
                    <div><span style="color:var(--text-tertiary)">Date:</span> ${meta.timestamp ? new Date(meta.timestamp).toLocaleString() : '—'}</div>
                </div>
                <div style="padding:4px 0;margin:8px 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Generate Plots</div>
                <div style="display:flex;flex-direction:column;gap:4px">
                    <button class="btn btn-default" onclick="insertGTRunPlot('${runId}','comprehensive')" style="text-align:left;font-size:var(--fs-xs)">📊 Comprehensive Overview</button>
                    <button class="btn btn-default" onclick="insertGTRunPlot('${runId}','metrics')" style="text-align:left;font-size:var(--fs-xs)">📈 Network Metrics</button>
                    <button class="btn btn-default" onclick="insertGTRunPlot('${runId}','regions')" style="text-align:left;font-size:var(--fs-xs)">🗺 Regional Analysis</button>
                    <button class="btn btn-default" onclick="insertGTRunPlot('${runId}','boundary')" style="text-align:left;font-size:var(--fs-xs)">🔀 Boundary Analysis</button>
                    <button class="btn btn-default" onclick="insertGTRunPlot('${runId}','metric_fields')" style="text-align:left;font-size:var(--fs-xs)">🌡 Metric Fields</button>
                    <button class="btn btn-default" onclick="insertGTRunPlot('${runId}','node_distributions')" style="text-align:left;font-size:var(--fs-xs)">📉 Node Distributions</button>
                    <button class="btn btn-default" onclick="insertGTRunPlot('${runId}','comparative_summary')" style="text-align:left;font-size:var(--fs-xs)">⚖ Comparative Summary</button>
                </div>
                <div style="padding:4px 0;margin:8px 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px">Actions</div>
                <button class="btn btn-default" onclick="deleteGTRun('${sub0?.id}','${runId}')" style="color:var(--status-error);font-size:var(--fs-xs)">🗑 Delete This Run</button>
            </div>`;
        }

        // ── SIGNAL ASSOCIATION RUN INFO ──
        const cfg = meta.config || {};
        const stats = meta.statistics || {};
        const methodKey = Object.keys(stats)[0] || cfg.method || 'ccm';
        const s = stats[methodKey] || {};

        return `
        <div style="display:flex;flex-direction:column;gap:8px">
            <div style="padding:4px 0;margin:0 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Run Info</div>
            <div style="font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-secondary);padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);line-height:1.6">
                <div><span style="color:var(--text-tertiary)">Method:</span> <b>${cfg.method || '—'}</b></div>
                <div><span style="color:var(--text-tertiary)">Signal:</span> ${cfg.signal_type || '—'}</div>
                <div><span style="color:var(--text-tertiary)">Tracks:</span> ${meta.n_tracks || s.n_signals || 0}</div>
                <div><span style="color:var(--text-tertiary)">Pairs:</span> ${s.n_pairs || 0}</div>
                <div><span style="color:var(--text-tertiary)">Surrogates:</span> ${cfg.n_surrogates || 0} (${cfg.surrogate_method || '—'})</div>
                <div><span style="color:var(--text-tertiary)">Stationarizer:</span> ${cfg.stationarize || 'none'}</div>
                <div><span style="color:var(--text-tertiary)">Min Overlap:</span> ${cfg.min_overlap || '—'} frames</div>
                <div style="margin-top:4px;padding-top:4px;border-top:1px solid var(--chrome-border)">
                    <span style="color:var(--text-tertiary)">Mean ρ:</span> <b>${(s.mean || 0).toFixed(3)}</b> ± ${(s.std || 0).toFixed(3)}
                </div>
                <div><span style="color:var(--text-tertiary)">Strong (ρ>0.3):</span> <b style="color:#ffa726">${s.n_strong || 0}</b> (${(s.strong_rate || 0).toFixed(1)}%)</div>
                <div><span style="color:var(--text-tertiary)">Significant:</span> <b style="color:var(--status-ok)">${s.n_significant || 0}</b> (${(s.significance_rate || 0).toFixed(1)}%)</div>
                <div><span style="color:var(--text-tertiary)">Date:</span> ${meta.timestamp ? meta.timestamp.replace('_', ' ') : '—'}</div>
            </div>

            <div style="padding:4px 0;margin:8px 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Generate Plots</div>
            <div style="display:flex;flex-direction:column;gap:4px">
                <button class="btn btn-default" onclick="insertIMMUNIAAssocRunPlot('${runId}','comprehensive')" style="text-align:left;font-size:var(--fs-xs)">📊 Comprehensive (6-panel)</button>
                <button class="btn btn-default" onclick="insertIMMUNIAAssocRunPlot('${runId}','influence_matrix')" style="text-align:left;font-size:var(--fs-xs)">🗺 Influence Matrix</button>
                <button class="btn btn-default" onclick="insertIMMUNIAAssocRunPlot('${runId}','distribution')" style="text-align:left;font-size:var(--fs-xs)">📈 ρ Distribution</button>
                <button class="btn btn-default" onclick="insertIMMUNIAAssocRunPlot('${runId}','significance')" style="text-align:left;font-size:var(--fs-xs)">🎯 Significance Analysis</button>
                <button class="btn btn-default" onclick="insertIMMUNIAAssocRunPlot('${runId}','comparison')" style="text-align:left;font-size:var(--fs-xs)">⚬ Strength vs Significance</button>
            </div>

            <div style="padding:4px 0;margin:8px 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px">Actions</div>
            <button class="btn btn-default" onclick="deleteIMMUNIAAssocRun('${sub0?.id}','${runId}')" style="color:var(--status-error);font-size:var(--fs-xs)">🗑 Delete This Run</button>
        </div>`;
    }

    if (id === 'assoc-pairs' && moduleType === 'fastia') {
        setTimeout(() => initAssocPairSelection(), 100);
        return `
        <div style="display:flex;flex-direction:column;gap:8px">
            <div style="padding:4px 0;margin:0 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Channels</div>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Select channels to form signal pairs. All checked combinations will be tested.</p>
            <div style="display:flex;gap:4px;margin-bottom:4px">
                <button class="btn btn-default" onclick="document.querySelectorAll('#assocChannelChecks input[type=checkbox]').forEach(c=>c.checked=true);assocSaveChannelState()" style="font-size:10px;padding:2px 6px">All</button>
                <button class="btn btn-default" onclick="document.querySelectorAll('#assocChannelChecks input[type=checkbox]').forEach(c=>c.checked=false);assocSaveChannelState()" style="font-size:10px;padding:2px 6px">None</button>
            </div>
            <div id="assocChannelChecks" style="display:flex;flex-wrap:wrap;gap:6px">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Loading channels...</span>
            </div>
            <input type="hidden" data-param="selected_channels" id="assocSelectedChannels" value="all">
            <div id="assocPairPreview" style="font-size:var(--fs-xs);color:var(--text-tertiary);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);min-height:30px">
            </div>

            <div style="padding:4px 0;margin:8px 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Track Scope</div>
            <div class="form-row"><span class="form-label">Run Mode</span><select class="form-select" data-param="assoc_run_mode" id="assocRunMode" onchange="assocToggleTrackSelector()">
                <option value="all">All Tracks</option>
                <option value="single">Single Track</option>
            </select></div>
            <div class="form-row"><span class="form-label">Min Length</span><input class="form-input" data-param="min_track_length" type="number" value="10" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>

            <div id="assocTrackSelector" style="display:none">
                <div style="padding:4px 0;margin:8px 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Track Inspector</div>
                <div class="form-row"><span class="form-label">Group Filter</span><select class="form-select" data-param="assoc_group_filter" id="assocGroupFilter" style="width:140px" onchange="assocFilterTracks()">
                    <option value="all">All Groups</option>
                </select></div>
                <div class="form-row"><span class="form-label">Track</span><select class="form-select" id="assocTrackSelect" data-param="assoc_single_track_id" style="width:180px">
                    <option value="">— Select Track —</option>
                </select></div>
                <div style="display:flex;gap:4px;align-items:center">
                    <button class="btn btn-default" onclick="assocStepTrack(-1)" style="font-size:10px;padding:2px 6px">◀</button>
                    <button class="btn btn-default" onclick="assocStepTrack(1)" style="font-size:10px;padding:2px 6px">▶</button>
                    <span id="assocTrackCount" style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-left:4px"></span>
                </div>
            </div>

            <div id="assocPairStats" style="margin-top:4px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);min-height:40px">
                Loading data...
            </div>
        </div>`;
    }

    // ── FASTIA: EDGE ANALYSIS ─────────────────
    if (id === 'assoc-edge' && moduleType === 'fastia') {
        setTimeout(() => _loadEdgeStatus(), 100);
        return `
        <div style="display:flex;flex-direction:column;gap:8px">
            <div style="padding:4px 0;margin:0 0 4px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:var(--brand-accent);text-transform:uppercase;letter-spacing:.5px">Edge Dynamics</div>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Classifies cell periphery into protruding, retracting, and steady regions using cell mask boundary velocity.</p>
            <div class="form-row"><span class="form-label">Sectors</span><input class="form-input" data-param="edge_num_sectors" type="number" value="24" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">angular divisions</span></div>
            <div class="form-row"><span class="form-label">Velocity Threshold</span><input class="form-input" data-param="edge_vel_threshold" type="number" value="0" step="0.1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px/frame (0=auto)</span></div>
            <div class="form-row"><span class="form-label">Smoothing Window</span><input class="form-input" data-param="edge_smooth_window" type="number" value="3" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
            <button class="btn btn-primary" onclick="runEdgeAnalysis()" style="margin-top:6px">🌊 Run Edge Analysis</button>
            <div id="edgeAnalysisStatus" style="font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:60px;padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                Checking for existing edge analysis...
            </div>
        </div>`;
    }

    if (id === 'assoc-params') {
        // Read method toggles from local params to show/hide sections
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const mp = sub0?._localParams?.['assoc-method'] || {};
        const gcOn = (mp.run_granger || 'true') !== 'false';
        const ccmOn = (mp.run_ccm || 'true') !== 'false';
        const corrOn = (mp.run_correlation || 'true') !== 'false';
        const anyOn = gcOn || ccmOn || corrOn;
        const dimStyle = 'opacity:0.3;pointer-events:none';

        // Read surrogate toggle from own local params
        const ap = sub0?._localParams?.['assoc-params'] || {};
        const surrOn = (ap.run_surrogates || 'true') !== 'false';

        return wrap(`
        <div style="padding:4px 0;margin:0 0 8px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:${gcOn ? 'var(--brand-accent)' : 'var(--text-tertiary)'};text-transform:uppercase;letter-spacing:.5px">Stationarizer ${gcOn ? '' : '(not needed)'}</div>
        <div style="${gcOn ? '' : dimStyle}">
            <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="stationarizer_method"><option value="bandpass" selected>Bandpass (recommended)</option><option value="detrend">Detrend</option><option value="lazy">Lazy Separation</option><option value="difference">Difference</option><option value="bandpass_diff">Bandpass + Diff</option><option value="lazy_diff">Lazy + Diff</option></select></div>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin:4px 0 0">${gcOn ? 'Used by Granger Causality (requires stationary signals).' : '⚠ Granger Causality disabled — stationarizer not needed.'}</p>
        </div>
        <div style="padding:4px 0;margin:12px 0 8px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:${anyOn ? 'var(--brand-accent)' : 'var(--text-tertiary)'};text-transform:uppercase;letter-spacing:.5px">Surrogate Testing</div>
        <div style="${anyOn ? '' : dimStyle}">
            <div class="form-row"><span class="form-label">Surrogates</span><select class="form-select" data-param="run_surrogates" onchange="this.closest('.settings-form')?.querySelector('#assocSurrParams')?.style.setProperty('opacity',this.value==='true'?'1':'0.3');this.closest('.settings-form')?.querySelector('#assocSurrParams')?.style.setProperty('pointer-events',this.value==='true'?'auto':'none')"><option value="true">Enabled</option><option value="false">Disabled</option></select></div>
            <div id="assocSurrParams" style="${surrOn ? '' : dimStyle}">
                <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="surrogate_method"><option value="iaaft" selected>IAAFT (recommended)</option><option value="shuffle">Shuffle</option><option value="circular">Circular Shift</option><option value="block_bootstrap">Block Bootstrap</option></select></div>
                <div class="form-row"><span class="form-label">N Surrogates</span><input class="form-input" data-param="n_surrogates" type="number" value="100" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">per pair</span></div>
            </div>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin:4px 0 0">Provides empirical p-values via null distribution. Recommended for CCM, MI, and TE.</p>
        </div>
        <div style="padding:4px 0;margin:12px 0 8px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:${gcOn ? 'var(--brand-accent)' : 'var(--text-tertiary)'};text-transform:uppercase;letter-spacing:.5px">Granger Causality ${gcOn ? '' : '(disabled)'}</div>
        <div style="${gcOn ? '' : dimStyle}">
            <div class="form-row"><span class="form-label">Max Lag</span><input class="form-input" data-param="granger_max_lag" type="number" value="5" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
            <div class="form-row"><span class="form-label">Lag Criterion</span><select class="form-select" data-param="gc_criterion"><option value="aic">AIC</option><option value="bic">BIC</option></select></div>
        </div>
        <div style="padding:4px 0;margin:12px 0 8px;border-bottom:1px solid var(--chrome-border);font-size:var(--fs-xs);font-weight:700;color:${ccmOn ? 'var(--brand-accent)' : 'var(--text-tertiary)'};text-transform:uppercase;letter-spacing:.5px">Convergent Cross Mapping ${ccmOn ? '' : '(disabled)'}</div>
        <div style="${ccmOn ? '' : dimStyle}">
            <div class="form-row"><span class="form-label">Embedding Dim</span><input class="form-input" data-param="ccm_embedding_dim" type="number" value="2" style="width:80px"></div>
            <div class="form-row"><span class="form-label">Bootstraps</span><input class="form-input" data-param="ccm_n_boot" type="number" value="20" style="width:80px"></div>
        </div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:10px">Enable methods in Method Selection to configure their parameters.</p>`);
    }

    // ── FASTIA: FA EXAMINATION ───────────────────
    if (id === 'exam-display' && moduleType === 'fastia') {
        setTimeout(() => initExaminationCanvas(), 150);
        return `
        <div style="display:flex;flex-direction:column;gap:8px">
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">FA Visual Examination</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Interactive viewer for inspecting focal adhesions on the cell image.</p>

            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-top:6px">Playback</p>
            <div style="display:flex;gap:4px;align-items:center">
                <button class="btn btn-primary" id="examPlayBtn" onclick="examTogglePlay()" style="min-width:60px">▶ Play</button>
                <button class="btn btn-default" onclick="examStepFrame(-1)">◀</button>
                <button class="btn btn-default" onclick="examStepFrame(1)">▶</button>
                <select class="form-select" id="examSpeed" style="width:70px" onchange="examSetSpeed()">
                    <option value="200">5 fps</option>
                    <option value="100">10 fps</option>
                    <option value="50" selected>20 fps</option>
                    <option value="33">30 fps</option>
                </select>
            </div>
            <div style="display:flex;align-items:center;gap:6px">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary);min-width:40px" id="examFrameLabel">1</span>
                <input type="range" id="examFrameSlider" min="0" max="90" value="0" style="flex:1" oninput="examSeekFrame(this.value)">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary);min-width:40px" id="examFrameTotal">/ 91</span>
            </div>

            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-top:6px">Channel</p>
            <div id="examChannelBtns" style="display:flex;gap:4px;flex-wrap:wrap"></div>

            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-top:6px">FA Overlay</p>
            <div class="form-row"><span class="form-label">Circle Size</span>
                <input type="range" id="examCircleSize" min="4" max="30" value="12" style="width:100px" oninput="examUpdateOverlay()">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary)" id="examCircleVal">12</span></div>
            <div class="form-row"><span class="form-label">Min Lifetime</span>
                <input type="range" id="examMinLife" min="1" max="50" value="3" style="width:100px" oninput="examUpdateOverlay()">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary)" id="examMinLifeVal">3</span></div>
            <div style="margin-top:4px">
                <span class="form-label" style="display:block;margin-bottom:4px">Show Groups</span>
                <div style="display:flex;gap:4px;margin-bottom:4px">
                    <button class="btn btn-default" onclick="document.querySelectorAll('#examGroupChecks input').forEach(c=>c.checked=true);examUpdateOverlay()" style="font-size:10px;padding:2px 6px">All</button>
                    <button class="btn btn-default" onclick="document.querySelectorAll('#examGroupChecks input').forEach(c=>c.checked=false);examUpdateOverlay()" style="font-size:10px;padding:2px 6px">None</button>
                </div>
                <div id="examGroupChecks" style="display:flex;flex-wrap:wrap;gap:4px"></div>
                <div id="examGroupLegend" style="margin-top:6px;display:flex;flex-wrap:wrap;gap:6px;font-size:10px"></div>
            </div>
            <div class="form-row"><span class="form-label">Show Labels</span>
                <input type="checkbox" id="examShowLabels" onchange="examUpdateOverlay()"></div>

            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-top:6px">Track Search</p>
            <div style="display:flex;gap:4px">
                <input class="form-input" id="examSearchTrack" placeholder="Track ID" style="flex:1">
                <button class="btn btn-default" onclick="examSearchTrack()">Go</button>
            </div>

            <div id="examStats" style="margin-top:8px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);min-height:50px">
                Loading examination data...
            </div>

            <div id="examSelectedInfo" style="display:none;margin-top:4px;font-size:var(--fs-xs);padding:8px;background:var(--surface-0);border:2px solid var(--status-ok);border-radius:var(--r-sm)">
            </div>
        </div>`;
    }

    // ── CELLVISIA ─────────────────────────────────
    if (moduleType === 'cellvisia') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const cvs = sub0?._cvState || {};
        // Override wrap to save under step='cellvisia' (not null)
        const cvWrap = (html) => `<div class="settings-form" data-module="cellvisia" data-step="cellvisia" data-section="${id}" onchange="debouncedSaveParams(this)">${html}</div>`;

        if (id === 'cv-select-image') {
            const savedStatus = cvs.loadStatusHtml || sub0?._statusBoxes?.cvLoadStatus || 'Select a TIFF file and click Load.';
            const fileVal = cvs.filePath || '';
            const fmtVal = cvs.format || 'auto';
            return cvWrap(`
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Image / Stack File</p>
            <div style="display:flex;gap:4px;align-items:center;margin-bottom:8px"><input class="form-input" data-param="input_file" id="cvFileInput" placeholder="Select file..." readonly style="flex:1;min-width:0;font-size:var(--fs-xs)" value="${fileVal}"><button class="btn btn-default" onclick="selectInputFile(this)" style="flex-shrink:0;white-space:nowrap">Browse</button></div>
            <div class="form-row"><span class="form-label">Format</span><select class="form-select" data-param="format">${['auto','TIFF Stack','ND2','CZI','PNG'].map(f=>`<option${f===fmtVal?' selected':''}>${f}</option>`).join('')}</select></div>
            <div style="margin-top:12px"><button class="btn btn-primary" onclick="doCellVisiaLoad()">📥 Load Image</button></div>
            <div id="cvLoadStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:60px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">${savedStatus}</div>`);
        }
        if (id === 'cv-channel-setup') {
            const info = sub0?._cvLoadInfo;
            if (!info) return cvWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Channel Assignment</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Load an image first.</p>`);
            const nCh = info.n_channels || 1;
            const savedNames = cvs.channelNames || [];
            const savedRoles = cvs.channelRoles || [];
            const roleOpts = ['','nuclei','membrane','target','dead','effector','brightfield','other'];
            const roleLabels = ['— role —','Nuclei','Membrane','Target','Dead/Cytotox','Effector','Brightfield','Other'];
            let rows = '';
            for (let i = 0; i < nCh; i++) {
                const nm = savedNames[i] || '';
                const rl = savedRoles[i] || '';
                rows += `<div class="cv-ch-row" style="display:flex;gap:6px;align-items:center;margin-bottom:6px">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);min-width:22px">Ch${i}</span>
                    <input class="form-input cv-ch-name" placeholder="Name (e.g. DAPI)" style="flex:1;font-size:var(--fs-xs)" value="${nm}">
                    <select class="form-select cv-ch-role" style="width:110px;font-size:var(--fs-xs)">${roleOpts.map((r,j)=>`<option value="${r}"${r===rl?' selected':''}>${roleLabels[j]}</option>`).join('')}</select>
                </div>`;
            }
            return cvWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Channel Assignment</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">${nCh} channel(s) detected. Name each and assign a role.</p>
                ${rows}
                <button class="btn btn-primary" onclick="cvSaveChannelAssignment()" style="margin-top:8px">💾 Save Channels</button>`);
        }
        if (id === 'cv-metadata') {
            const px = cvs.pixel_size_um || '';
            const dt = cvs.dt_s || '';
            const dz = cvs.dz_um || '';
            return cvWrap(`
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Imaging Metadata</p>
            <div class="form-row"><span class="form-label">Pixel Size</span><input class="form-input" data-param="pixel_size_um" type="number" step="0.01" placeholder="μm/px" style="width:90px" value="${px}"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">μm/px</span></div>
            <div class="form-row"><span class="form-label">Time Step</span><input class="form-input" data-param="dt_s" type="number" step="0.1" placeholder="seconds" style="width:90px" value="${dt}"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">s</span></div>
            <div class="form-row"><span class="form-label">Z Spacing</span><input class="form-input" data-param="dz_um" type="number" step="0.1" placeholder="μm" style="width:90px" value="${dz}"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">μm</span></div>
            <button class="btn btn-primary" onclick="cvSaveMetadata()" style="margin-top:10px">💾 Save Metadata</button>`);
        }

        // ── Scope fixed settings ─────────────────────────────────
        if (id === 'cv-scope-channels') {
            const info = sub0?._cvOriginalInfo || sub0?._cvLoadInfo;
            const nCh = info?.n_channels || 1;
            const savedKeep = cvs.scopeKeepChannels || Array.from({length: nCh}, (_, i) => i);
            let checkboxes = '';
            for (let i = 0; i < nCh; i++) {
                const chName = cvs.channelNames?.[i] || `Ch ${i}`;
                const checked = savedKeep.includes(i) ? 'checked' : '';
                checkboxes += `<label style="display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:var(--fs-xs);cursor:pointer">
                    <input type="checkbox" class="cv-scope-ch" data-ch="${i}" ${checked}> ${chName}
                </label>`;
            }
            return cvWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">🎨 Channels</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Select which channels to include in downstream processing.</p>
                ${info ? checkboxes : '<p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Load an image first.</p>'}
                ${info ? '<button class="btn btn-primary" onclick="cvSaveScopeChannels()" style="margin-top:8px">💾 Apply Channels</button>' : ''}
                <div id="cvScopeChStatus" style="margin-top:6px;font-size:var(--fs-xs);color:var(--text-tertiary)"></div>`);
        }
        if (id === 'cv-scope-temporal') {
            const origInfo = sub0?._cvOriginalInfo || sub0?._cvLoadInfo;
            const nFrames = origInfo?.n_frames || 0;
            const start = cvs.scopeFrameStart ?? 0;
            const end = cvs.scopeFrameEnd ?? -1;
            const every = cvs.scopeSubsample ?? 1;
            return cvWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">🎞 Temporal</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">${nFrames} frames available.</p>
                <div class="form-row"><span class="form-label">Start Frame</span><input class="form-input" data-param="scope_frame_start" type="number" value="${start}" style="width:80px"></div>
                <div class="form-row"><span class="form-label">End Frame</span><input class="form-input" data-param="scope_frame_end" type="number" value="${end}" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">-1 = last</span></div>
                <div class="form-row"><span class="form-label">Subsample</span><input class="form-input" data-param="scope_subsample" type="number" min="1" value="${every}" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">every Nth</span></div>
                <button class="btn btn-primary" onclick="cvSaveScopeTemporal()" style="margin-top:8px">💾 Apply Temporal</button>
                <div id="cvScopeTemporalStatus" style="margin-top:6px;font-size:var(--fs-xs);color:var(--text-tertiary)"></div>`);
        }
        if (id === 'cv-scope-format') {
            const bitDepth = cvs.scopeBitDepth || '';
            const axesOrder = cvs.scopeAxesOrder || '';
            const deinterleaveN = cvs.scopeDeinterleave || '';
            return cvWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">🔢 Format</p>
                <div class="form-row"><span class="form-label">Bit Depth</span><select class="form-select" data-param="scope_bit_depth" style="width:120px">
                    <option value="">— unchanged —</option>
                    ${['uint8','uint16','float32','float64'].map(t => `<option${t===bitDepth?' selected':''}>${t}</option>`).join('')}
                </select></div>
                <div class="form-row"><span class="form-label">Reorder Axes</span><input class="form-input" data-param="scope_axes_order" type="text" placeholder="e.g. TCZYX" value="${axesOrder}" style="width:100px"></div>
                <div class="form-row"><span class="form-label">Deinterleave</span><input class="form-input" data-param="scope_deinterleave" type="number" min="0" placeholder="N ch" value="${deinterleaveN}" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">0 = off</span></div>
                <button class="btn btn-primary" onclick="cvSaveScopeFormat()" style="margin-top:8px">💾 Apply Format</button>
                <div id="cvScopeFormatStatus" style="margin-top:6px;font-size:var(--fs-xs);color:var(--text-tertiary)"></div>`);
        }

        // ── Inserted features (cvf-*) — dynamic params form ──────────
        const feat = sub0?.cvFeatures?.find(f => f.id === id);
        if (feat) {
            const defs = CV_PARAM_DEFS[feat.type] || [];
            if (defs.length === 0) {
                return cvWrap(`
                    <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">${feat.icon} ${feat.label}</p>
                    <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">No configurable parameters.</p>`);
            }
            const rows = defs.map(d => {
                const val = feat.params[d.key] ?? d.fallback ?? '';
                const displayVal = Array.isArray(val) ? val.join(',') : val;
                if (d.type === 'select') {
                    const opts = d.options.map(o => `<option value="${o}"${String(o)===String(displayVal)?' selected':''}>${o}</option>`).join('');
                    return `<div class="form-row"><span class="form-label">${d.label}</span><select class="form-select" data-param="${d.key}" style="width:${d.width||'120px'}">${opts}</select></div>`;
                }
                if (d.type === 'browse_save' || d.type === 'browse_folder') {
                    const mode = d.type === 'browse_folder' ? 'folder' : 'file';
                    const ftypes = (d.filetypes || '').split(',').filter(Boolean);
                    const ftJson = JSON.stringify(ftypes.map(e => [`${e.toUpperCase()} Files`, `*.${e}`]).concat([['All Files', '*.*']])).replace(/"/g, '&quot;');
                    return `<div class="form-row"><span class="form-label">${d.label}</span>
                        <input class="form-input" data-param="${d.key}" type="text" value="${displayVal}" placeholder="${mode === 'folder' ? 'Select folder...' : 'Select file...'}" style="width:${d.width||'180px'};flex:1" readonly>
                        <button class="btn btn-sm" onclick="cvBrowseSave(this,'${d.key}','${mode}','${ftJson}')" style="padding:2px 8px;font-size:11px;margin-left:4px" title="Browse">📂</button></div>`;
                }
                if (d.type === 'text') {
                    return `<div class="form-row"><span class="form-label">${d.label}</span><input class="form-input" data-param="${d.key}" type="text" value="${displayVal}" style="width:${d.width||'120px'}">${d.unit ? `<span style="font-size:var(--fs-xs);color:var(--text-tertiary)">${d.unit}</span>` : ''}</div>`;
                }
                const step = d.step || (d.type === 'float' ? '0.1' : '1');
                return `<div class="form-row"><span class="form-label">${d.label}</span><input class="form-input" data-param="${d.key}" type="number" step="${step}" value="${displayVal}" style="width:${d.width||'90px'}">${d.unit ? `<span style="font-size:var(--fs-xs);color:var(--text-tertiary)">${d.unit}</span>` : ''}</div>`;
            }).join('');
            const info = sub0?._cvLoadInfo;
            const imgCtx = info?.shape
                ? `<div style="font-size:var(--fs-xs);color:var(--text-tertiary);padding:4px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);margin-bottom:10px">Image: ${info.axes} ${info.shape.join('×')} · ${info.dtype || ''}</div>`
                : '';
            return cvWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">${feat.icon} ${feat.label}</p>
                ${imgCtx}
                ${rows}
                <button class="btn btn-primary" onclick="cvApplyFeature('${feat.id}')" style="margin-top:10px">▶ Apply</button>
                <div id="cvFeatureStatus-${feat.id}" style="margin-top:8px;font-size:var(--fs-xs);color:var(--text-tertiary)"></div>`);
        }
    }

    // ── ASSOCIA ─────────────────────────────────
    if (moduleType === 'associa') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const asState = sub0?._asState || {};
        const asWrap = (html) => `<div class="settings-form" data-module="associa" data-step="associa" data-section="${id}" onchange="debouncedSaveParams(this)">${html}</div>`;

        if (id === 'as-load-signals') {
            const fileVal = asState.filePath || '';
            const modeLabel = asState.mode === 'batch'
                ? `Batch: ${asState.nSignals || '?'} signals · ${asState.nPairs || '?'} pairs`
                : asState.mode === 'single' ? 'Single: 1 pair' : '';
            return asWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Load Signals (CSV)</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">CSV format: each column is a signal. 2 columns = single pair, N columns = batch (all C(N,2) pairs).</p>
                <div style="display:flex;gap:4px;align-items:center;margin-bottom:8px">
                    <input class="form-input" data-param="csv_file" id="asFileInput" placeholder="Select CSV file..." readonly style="flex:1;min-width:0;font-size:var(--fs-xs)" value="${fileVal}">
                    <button class="btn btn-default" onclick="assocBrowseCSV(this)" style="flex-shrink:0;white-space:nowrap">Browse</button>
                </div>
                <div class="form-row"><span class="form-label">Header row</span><select class="form-select" data-param="has_header"><option value="auto" selected>Auto-detect</option><option value="yes">Yes</option><option value="no">No</option></select></div>
                <div style="margin-top:12px"><button class="btn btn-primary" onclick="assocLoadCSV()">📥 Load</button></div>
                <div id="asLoadStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">${modeLabel || 'Select a CSV file and click Load.'}</div>`);
        }

        if (id === 'as-signal-info') {
            if (!asState.signalNames) return asWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Signal Info</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Load signals first.</p>`);
            return asWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Signal Info</p>
                <div style="font-size:var(--fs-xs);color:var(--text-tertiary);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                    <div><b>Mode:</b> ${asState.mode}</div>
                    <div><b>Signals:</b> ${asState.nSignals} · ${asState.nSamples} samples</div>
                    <div><b>Pairs:</b> ${asState.nPairs}</div>
                    <div><b>Names:</b> ${asState.signalNames?.join(', ') || '—'}</div>
                </div>
                <div class="form-row" style="margin-top:10px"><span class="form-label">Sampling Rate (Hz)</span><input class="form-input" data-param="sampling_rate" type="number" step="0.001" value="${asState.samplingRate || 1}" style="width:90px"></div>`);
        }

        if (id === 'as-stationarizer') {
            const st = asState.stationarizer || {};
            return asWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Stationarizer</p>
                <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="stat_method">${['none','detrend','difference','bandpass'].map(m => `<option value="${m}"${m===(st.method||'none')?' selected':''}>${m}</option>`).join('')}</select></div>
                <div class="form-row"><span class="form-label">Bandpass Low</span><input class="form-input" data-param="bp_low" type="number" step="0.001" value="${st.bp_low ?? 0.008}" style="width:90px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Hz</span></div>
                <div class="form-row"><span class="form-label">Bandpass High</span><input class="form-input" data-param="bp_high" type="number" step="0.001" value="${st.bp_high ?? 0.25}" style="width:90px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Hz</span></div>`);
        }

        if (id === 'as-methods') {
            const mc = asState.methods || {};
            const ccmOn = mc.ccm !== false;
            const gcOn = mc.granger === true;
            const pearOn = mc.pearson === true;
            const miOn = mc.mutual_info === true;
            const teOn = mc.transfer_entropy === true;
            return asWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Association Methods</p>
                <div style="margin-bottom:12px;font-size:var(--fs-xs);color:var(--text-tertiary)">Select one or more coupling methods.</div>
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="m_ccm" ${ccmOn?'checked':''}> <b>CCM</b> — Convergent Cross Mapping</label>
                <div style="margin-left:20px;margin-bottom:4px;padding:4px 8px;background:rgba(76,175,80,.08);border-left:2px solid #4caf50;font-size:10px;color:var(--text-tertiary)">✓ Works on raw (non-stationary) signals. Detects nonlinear causal coupling.</div>
                <div style="margin-left:20px;margin-bottom:10px">
                    <div class="form-row"><span class="form-label">Embedding dim (E)</span><input class="form-input" data-param="ccm_E" type="number" value="${mc.ccm_E ?? 2}" style="width:60px"></div>
                    <div class="form-row"><span class="form-label">Time delay (τ)</span><input class="form-input" data-param="ccm_tau" type="number" value="${mc.ccm_tau ?? 1}" style="width:60px"></div>
                    <div class="form-row"><span class="form-label">Bootstrap (n)</span><input class="form-input" data-param="ccm_n_boot" type="number" value="${mc.ccm_n_boot ?? 20}" style="width:60px"></div>
                </div>
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="m_granger" ${gcOn?'checked':''}> <b>Granger</b> — Granger Causality</label>
                <div style="margin-left:20px;margin-bottom:4px;padding:4px 8px;background:rgba(255,152,0,.08);border-left:2px solid #ff9800;font-size:10px;color:var(--text-tertiary)">⚠ Requires stationary signals. Enable Stationarizer (bandpass or difference) below.</div>
                <div style="margin-left:20px;margin-bottom:10px">
                    <div class="form-row"><span class="form-label">Max lag</span><input class="form-input" data-param="gc_maxlag" type="number" value="${mc.gc_maxlag ?? 5}" style="width:60px"></div>
                    <div class="form-row"><span class="form-label">Lag criterion</span><select class="form-select" data-param="gc_criterion"><option value="aic"${(mc.gc_criterion||'aic')==='aic'?' selected':''}>AIC</option><option value="bic"${mc.gc_criterion==='bic'?' selected':''}>BIC</option></select></div>
                </div>
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="m_pearson" ${pearOn?'checked':''}> <b>Pearson</b> — Correlation</label>
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="m_mi" ${miOn?'checked':''}> <b>MI</b> — Mutual Information</label>
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="m_te" ${teOn?'checked':''}> <b>TE</b> — Transfer Entropy</label>`);
        }

        if (id === 'as-surrogate') {
            const sg = asState.surrogate || {};
            return asWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Surrogate Testing</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Generate null-hypothesis surrogates to compute empirical p-values.</p>
                <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="surr_method">${[
                    ['iaaft', 'IAAFT (preserves spectrum + distribution)'],
                    ['shuffle', 'Shuffle (destroys all temporal structure)'],
                    ['circular', 'Circular Shift (preserves autocorrelation)'],
                    ['block_bootstrap', 'Block Bootstrap (preserves local structure)'],
                ].map(([v, label]) => `<option value="${v}"${v===(sg.method||'iaaft')?' selected':''}>${label}</option>`).join('')}</select></div>
                <div class="form-row"><span class="form-label">N Surrogates</span><input class="form-input" data-param="surr_n" type="number" value="${sg.n ?? 100}" style="width:80px"></div>
                <div class="form-row"><span class="form-label">Alpha (α)</span><input class="form-input" data-param="surr_alpha" type="number" step="0.01" value="${sg.alpha ?? 0.05}" style="width:80px"></div>`);
        }

        if (id === 'as-run') {
            return asWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Run Analysis</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:12px">Configure Source, Methods, and Surrogate settings above, then run.</p>
                <button class="btn btn-primary" onclick="assocRunAnalysis()" style="width:100%">▶ Run Association Analysis</button>
                <div id="asRunStatus" style="margin-top:12px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">Ready.</div>
                <div id="asRunsList" style="margin-top:12px"></div>`);
        }

        if (id === 'as-export') {
            return asWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Export Results</p>
                <div class="form-row"><span class="form-label">Output</span>
                    <input class="form-input" data-param="export_path" type="text" placeholder="Select folder..." readonly style="flex:1">
                    <button class="btn btn-sm" onclick="cvBrowseSave(this,'export_path','folder','')" style="padding:2px 8px;font-size:11px;margin-left:4px">📂</button>
                </div>
                <div class="form-row"><span class="form-label">Format</span><select class="form-select" data-param="export_fmt"><option value="csv">CSV</option><option value="pickle">Pickle</option><option value="json">JSON</option></select></div>
                <button class="btn btn-primary" onclick="assocExport()" style="margin-top:10px">💾 Export</button>`);
        }

        return asWrap(`<p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Select an item from the tree.</p>`);
    }

    // ── CELLADE ──────────────────────────────────
    if (moduleType === 'cellade') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const cdState = sub0?._cdState || {};
        const cdWrap = (html) => `<div class="settings-form" data-module="cellade" data-step="cellade" data-section="${id}" onchange="debouncedSaveParams(this)">${html}</div>`;

        if (id === 'cd-load-image') {
            const fileVal = cdState.filePath || '';
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Load Image</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Single grayscale or RGB image (TIFF, PNG, JPG). Converted to grayscale internally.</p>
                <div style="display:flex;gap:4px;align-items:center;margin-bottom:8px">
                    <input class="form-input" data-param="image_file" id="cdFileInput" placeholder="Select image..." readonly style="flex:1;min-width:0;font-size:var(--fs-xs)" value="${fileVal}">
                    <button class="btn btn-default" onclick="celladeBrowseImage()" style="flex-shrink:0">Browse</button>
                </div>
                <div style="margin-top:12px"><button class="btn btn-primary" onclick="celladeLoadImage()">📥 Load</button></div>
                <div id="cdLoadStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">${cdState.loadStatus || 'Select an image and click Load.'}</div>`);
        }

        if (id === 'cd-image-info') {
            if (!cdState.shape) return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Image Info</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Load an image first.</p>`);
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Image Info</p>
                <div style="font-size:var(--fs-xs);color:var(--text-tertiary);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                    <div><b>Shape:</b> ${cdState.shape}</div>
                    <div><b>Dtype:</b> ${cdState.dtype || '—'}</div>
                    <div><b>Range:</b> [${cdState.vmin ?? '—'}, ${cdState.vmax ?? '—'}]</div>
                </div>`);
        }

        if (id === 'cd-load-gt') {
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Ground Truth (optional)</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Load a label image for evaluation. Each integer = one cell.</p>
                <div style="display:flex;gap:4px;align-items:center;margin-bottom:8px">
                    <input class="form-input" data-param="gt_file" id="cdGtInput" placeholder="Select GT mask..." readonly style="flex:1;min-width:0;font-size:var(--fs-xs)" value="${cdState.gtPath || ''}">
                    <button class="btn btn-default" onclick="celladeBrowseGT()" style="flex-shrink:0">Browse</button>
                </div>
                <div style="margin-top:8px"><button class="btn btn-default" onclick="celladeLoadGT()">🎯 Load GT</button></div>
                <div id="cdGtStatus" style="margin-top:8px;font-size:var(--fs-xs);color:var(--text-tertiary)">${cdState.gtStatus || ''}</div>`);
        }

        if (id === 'cd-base-seg') {
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Base Segmentation</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">CLAHE → Fuzzy C-Means → H-maxima seeds → radial expansion.</p>
                <div class="form-row"><span class="form-label">CLAHE Clip</span><input class="form-input" data-param="clahe_clip" type="number" step="0.001" value="${cdState.clahe_clip ?? 0.01}" style="width:80px"></div>
                <div class="form-row"><span class="form-label">FCM Clusters</span><input class="form-input" data-param="fcm_clusters" type="number" value="${cdState.fcm_clusters ?? 2}" style="width:60px"></div>
                <div class="form-row"><span class="form-label">FCM Min Sep</span><input class="form-input" data-param="fcm_min_sep" type="number" step="0.01" value="${cdState.fcm_min_sep ?? 0.1}" style="width:80px"></div>
                <div class="form-row"><span class="form-label">H-maxima (h)</span><input class="form-input" data-param="h_maxima_h" type="number" step="0.01" value="${cdState.h_maxima_h ?? 0.05}" style="width:80px"></div>
                <div class="form-row"><span class="form-label">Seed Min Dist</span><input class="form-input" data-param="seed_min_dist" type="number" value="${cdState.seed_min_dist ?? 5}" style="width:60px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
                <div class="form-row"><span class="form-label">Max Radius</span><input class="form-input" data-param="max_radius" type="number" value="${cdState.max_radius ?? 100}" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
                <div class="form-row"><span class="form-label">Local FCM Sep</span><input class="form-input" data-param="local_fcm_sep" type="number" step="0.01" value="${cdState.local_fcm_sep ?? 0.08}" style="width:80px"></div>`);
        }

        if (id === 'cd-smoothing') {
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Boundary Smoothing</p>
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="use_morphological_smoothing" ${(cdState.use_morphological_smoothing !== false)?'checked':''}> Morphological Smoothing</label>
                <div class="form-row"><span class="form-label">Base Radius</span><input class="form-input" data-param="morphological_base_radius" type="number" value="${cdState.morphological_base_radius ?? 2}" style="width:60px"></div>
                <div class="form-row"><span class="form-label">Aggressiveness</span><input class="form-input" data-param="morphological_aggressiveness" type="number" step="0.1" value="${cdState.morphological_aggressiveness ?? 1.5}" style="width:70px"></div>
                <hr style="border:none;border-top:1px solid var(--chrome-border);margin:10px 0">
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="use_fft_smoothing" ${(cdState.use_fft_smoothing !== false)?'checked':''}> FFT Smoothing</label>
                <div class="form-row"><span class="form-label">FFT Points</span><input class="form-input" data-param="fft_n_points" type="number" value="${cdState.fft_n_points ?? 256}" style="width:70px"></div>
                <div class="form-row"><span class="form-label">Min Wavelength</span><input class="form-input" data-param="fft_min_wavelength" type="number" value="${cdState.fft_min_wavelength ?? 6}" style="width:60px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>`);
        }

        if (id === 'cd-merging') {
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Merging</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Curvature-based merge + honeycomb merge + fragment removal.</p>
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="use_honeycomb_merging" ${(cdState.use_honeycomb_merging !== false)?'checked':''}> Honeycomb Merging</label>
                <div class="form-row"><span class="form-label">Small Threshold</span><input class="form-input" data-param="honeycomb_small_threshold" type="number" step="0.1" value="${cdState.honeycomb_small_threshold ?? 0.5}" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">× median</span></div>
                <div class="form-row"><span class="form-label">Adjacency Radius</span><input class="form-input" data-param="honeycomb_adjacency_radius" type="number" value="${cdState.honeycomb_adjacency_radius ?? 5}" style="width:60px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
                <hr style="border:none;border-top:1px solid var(--chrome-border);margin:10px 0">
                <label style="display:flex;gap:6px;align-items:center;margin-bottom:8px;font-size:var(--fs-xs)"><input type="checkbox" data-param="use_fragment_removal" ${(cdState.use_fragment_removal !== false)?'checked':''}> Fragment Removal (4σ)</label>
                <div class="form-row"><span class="form-label">Min Fragment Size</span><input class="form-input" data-param="fragment_min_size" type="number" value="${cdState.fragment_min_size ?? 50}" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>`);
        }

        if (id === 'cd-splitting') {
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Stress-Based Splitting</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Poisson equation → Von Mises stress → neck detection → cut lines.</p>
                <div class="form-row"><span class="form-label">Z Threshold</span><input class="form-input" data-param="z_threshold" type="number" step="0.1" value="${cdState.z_threshold ?? 2.5}" style="width:70px"></div>
                <div class="form-row"><span class="form-label">Min Region Size</span><input class="form-input" data-param="cut_min_region_size" type="number" value="${cdState.cut_min_region_size ?? 100}" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
                <div class="form-row"><span class="form-label">Min Area Ratio</span><input class="form-input" data-param="poly_min_area_ratio" type="number" step="0.01" value="${cdState.poly_min_area_ratio ?? 0.15}" style="width:70px"></div>
                <div class="form-row"><span class="form-label">Max Iterations</span><input class="form-input" data-param="max_split_iterations" type="number" value="${cdState.max_split_iterations ?? 5}" style="width:60px"></div>
                <div class="form-row"><span class="form-label">Cluster Max AR</span><input class="form-input" data-param="cluster_max_aspect_ratio" type="number" step="0.1" value="${cdState.cluster_max_aspect_ratio ?? 4.0}" style="width:70px"></div>`);
        }

        if (id === 'cd-run') {
            const run = cdState.lastRun || {};
            const hasRun = !!run.n_regions;
            const m = run.metrics;
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Run CellADE</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:12px">7-step pipeline: Base Seg → Merge → Morph Smooth → FFT Smooth → Honeycomb → Cleanup → Split</p>
                <button class="btn btn-primary" onclick="celladeRun()" style="width:100%">▶ Run CellADE</button>
                <div id="cdRunStatus" style="margin-top:12px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">${hasRun ? `✓ ${run.n_regions} regions · ${run.elapsed_s}s` : 'Ready.'}</div>
                <div id="cdRunMetrics" style="margin-top:8px">${m ? `<div style="font-size:var(--fs-xs);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)"><b>F1@0.5:</b> ${m.F1?.toFixed(3)||'—'} · <b>mAP:</b> ${m.mAP?.toFixed(3)||'—'} · <b>Dice:</b> ${m.Dice_FG?.toFixed(3)||'—'} · Pred: ${m.Pred||'—'} / GT: ${m.GT||'—'}</div>` : ''}
                </div>
                ${hasRun ? '<p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:10px">Right-click <b>Results</b> header in the tree to insert plots.</p>' : ''}
            `);
        }

        if (id === 'cd-export-mask') {
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Save Masks</p>
                <div class="form-row"><span class="form-label">Output</span>
                    <input class="form-input" data-param="mask_output_path" type="text" placeholder="Select file..." readonly style="flex:1">
                    <button class="btn btn-sm" onclick="cvBrowseSave(this,'mask_output_path','file','[[\u0022TIFF\u0022,\u0022*.tif\u0022],[\u0022PNG\u0022,\u0022*.png\u0022]]')" style="padding:2px 8px;font-size:11px;margin-left:4px">📂</button>
                </div>
                <div class="form-row"><span class="form-label">Format</span><select class="form-select" data-param="mask_fmt"><option value="tiff">TIFF (uint16 labels)</option><option value="png">PNG (colored)</option></select></div>
                <button class="btn btn-primary" onclick="celladeExportMask()" style="margin-top:10px">💾 Save Mask</button>`);
        }

        if (id === 'cd-export-overlay') {
            return cdWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Save Overlay</p>
                <div class="form-row"><span class="form-label">Output</span>
                    <input class="form-input" data-param="overlay_output_path" type="text" placeholder="Select file..." readonly style="flex:1">
                    <button class="btn btn-sm" onclick="cvBrowseSave(this,'overlay_output_path','file','[[\u0022PNG\u0022,\u0022*.png\u0022]]')" style="padding:2px 8px;font-size:11px;margin-left:4px">📂</button>
                </div>
                <div class="form-row"><span class="form-label">Alpha</span><input class="form-input" data-param="overlay_alpha" type="number" step="0.1" value="0.4" style="width:70px"></div>
                <button class="btn btn-primary" onclick="celladeExportOverlay()" style="margin-top:10px">🖼 Save Overlay</button>`);
        }

        return cdWrap(`<p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Select an item from the tree.</p>`);
    }

    // ── CELLFADE ─────────────────────────────────
    if (moduleType === 'cellfade') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const cfState = sub0?._cfState || {};
        const cfWrap = (html) => `<div class="settings-form" data-module="cellfade" data-step="cellfade" data-section="${id}" onchange="debouncedSaveParams(this)">${html}</div>`;

        if (id === 'cf-load-image') {
            return cfWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Load FA Image</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Single frame focal adhesion channel (TIFF, PNG). Optionally load a cell boundary channel.</p>
                <div style="display:flex;gap:4px;align-items:center;margin-bottom:8px">
                    <input class="form-input" data-param="fa_file" id="cfFileInput" placeholder="FA channel..." readonly style="flex:1;min-width:0;font-size:var(--fs-xs)" value="${cfState.filePath || ''}">
                    <button class="btn btn-default" onclick="cellfadeBrowse('cfFileInput')" style="flex-shrink:0">Browse</button>
                </div>
                <div style="display:flex;gap:4px;align-items:center;margin-bottom:8px">
                    <input class="form-input" data-param="boundary_file" id="cfBoundaryInput" placeholder="Boundary channel (optional)..." readonly style="flex:1;min-width:0;font-size:var(--fs-xs)" value="${cfState.boundaryPath || ''}">
                    <button class="btn btn-default" onclick="cellfadeBrowse('cfBoundaryInput')" style="flex-shrink:0">Browse</button>
                </div>
                <div style="margin-top:12px"><button class="btn btn-primary" onclick="cellfadeLoad()">📥 Load</button></div>
                <div id="cfLoadStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">${cfState.loadStatus || 'Select FA image and click Load.'}</div>`);
        }

        if (id === 'cf-image-info') {
            if (!cfState.shape) return cfWrap(`<p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Image Info</p><p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Load an image first.</p>`);
            return cfWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Image Info</p>
                <div style="font-size:var(--fs-xs);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                    <div><b>Shape:</b> ${cfState.shape}</div>
                    <div><b>Range:</b> [${cfState.vmin ?? '—'}, ${cfState.vmax ?? '—'}]</div>
                    <div><b>Boundary:</b> ${cfState.hasBoundary ? '✓ loaded' : '—'}</div>
                </div>`);
        }

        if (id === 'cf-preprocess') {
            return cfWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Preprocessing</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">DoG filter: enhance FA structures, suppress background.</p>
                <div class="form-row"><span class="form-label">DoG Low σ</span><input class="form-input" data-param="dog_low_sigma" type="number" step="0.5" value="${cfState.dog_low_sigma ?? 1}" style="width:70px"></div>
                <div class="form-row"><span class="form-label">DoG High σ</span><input class="form-input" data-param="dog_high_sigma" type="number" step="1" value="${cfState.dog_high_sigma ?? 20}" style="width:70px"></div>`);
        }

        if (id === 'cf-seeds') {
            return cfWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Seed Detection</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Frangi ridge filter → local maxima → Hessian orientation.</p>
                <div class="form-row"><span class="form-label">Frangi Scales</span><input class="form-input" data-param="frangi_scales" type="text" value="${cfState.frangi_scales || '1,2,3,4,5'}" style="width:120px"></div>
                <div class="form-row"><span class="form-label">Frangi Threshold</span><input class="form-input" data-param="frangi_threshold" type="number" step="0.005" value="${cfState.frangi_threshold ?? 0.01}" style="width:80px"></div>
                <div class="form-row"><span class="form-label">Frangi β</span><input class="form-input" data-param="frangi_beta" type="number" step="0.1" value="${cfState.frangi_beta ?? 0.5}" style="width:70px"></div>
                <div class="form-row"><span class="form-label">Hessian σ</span><input class="form-input" data-param="hessian_sigma" type="number" step="0.5" value="${cfState.hessian_sigma ?? 2.0}" style="width:70px"></div>`);
        }

        if (id === 'cf-fcm') {
            return cfWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">FCM Objects</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Global fuzzy c-means to segment foreground objects.</p>
                <div class="form-row"><span class="form-label">Min Membership</span><input class="form-input" data-param="global_fcm_min_membership" type="number" step="0.05" value="${cfState.global_fcm_min_membership ?? 0.5}" style="width:70px"></div>
                <div class="form-row"><span class="form-label">Min Object Area</span><input class="form-input" data-param="min_object_area" type="number" value="${cfState.min_object_area ?? 10}" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
                <div class="form-row"><span class="form-label">Fallback Radius</span><input class="form-input" data-param="fallback_seed_radius" type="number" value="${cfState.fallback_seed_radius ?? 5}" style="width:60px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px (orphan seeds)</span></div>`);
        }

        if (id === 'cf-segmentation') {
            const mode = cfState.mode || 'expansion';
            return cfWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Segmentation Mode</p>
                <div class="form-row"><span class="form-label">Mode</span><select class="form-select" data-param="mode">
                    <option value="expansion"${mode==='expansion'?' selected':''}>Expansion (t-test)</option>
                    <option value="watershed"${mode==='watershed'?' selected':''}>Watershed</option>
                </select></div>
                <div style="margin-top:10px;padding:6px 8px;background:rgba(76,175,80,.08);border-left:2px solid #4caf50;font-size:10px;color:var(--text-tertiary)">
                    <b>Expansion:</b> Seed-object association → iterative t-test boundary growth. Better shape fidelity.<br>
                    <b>Watershed:</b> Marker-controlled global watershed with structural fusion. Faster.
                </div>
                <hr style="border:none;border-top:1px solid var(--chrome-border);margin:10px 0">
                <p style="font-size:var(--fs-xs);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Expansion Params</p>
                <div class="form-row"><span class="form-label">Expansion %</span><input class="form-input" data-param="expansion_percent" type="number" step="0.01" value="${cfState.expansion_percent ?? 0.10}" style="width:70px"></div>
                <div class="form-row"><span class="form-label">Max Iterations</span><input class="form-input" data-param="max_expansion_iterations" type="number" value="${cfState.max_expansion_iterations ?? 5}" style="width:60px"></div>
                <div class="form-row"><span class="form-label">Alpha (t-test)</span><input class="form-input" data-param="expansion_alpha" type="number" step="0.01" value="${cfState.expansion_alpha ?? 0.05}" style="width:70px"></div>
                <hr style="border:none;border-top:1px solid var(--chrome-border);margin:10px 0">
                <p style="font-size:var(--fs-xs);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Watershed Params</p>
                <div class="form-row"><span class="form-label">Structure Weight</span><input class="form-input" data-param="structure_weight" type="number" step="0.1" value="${cfState.structure_weight ?? 0.3}" style="width:70px"></div>
                <div class="form-row"><span class="form-label">Fusion Mode</span><select class="form-select" data-param="fusion_mode"><option value="additive"${(cfState.fusion_mode||'additive')==='additive'?' selected':''}>Additive</option><option value="max"${cfState.fusion_mode==='max'?' selected':''}>Max</option></select></div>`);
        }

        if (id === 'cf-run') {
            const run = cfState.lastRun || {};
            const hasRun = !!run.n_final;
            return cfWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Run CellFADE</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:12px">Frangi seeds → FCM objects → ${cfState.mode || 'expansion'} segmentation</p>
                <button class="btn btn-primary" onclick="cellfadeRun()" style="width:100%">▶ Run CellFADE</button>
                <div id="cfRunStatus" style="margin-top:12px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">${hasRun ? `✓ ${run.n_final} FAs · ${run.n_seeds} seeds · ${run.elapsed_s}s` : 'Ready.'}</div>
                ${hasRun ? '<p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:10px">Right-click <b>Results</b> header to insert plots.</p>' : ''}
            `);
        }

        if (id === 'cf-export-mask' || id === 'cf-export-overlay') {
            const isOverlay = id === 'cf-export-overlay';
            return cfWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">${isOverlay ? 'Save Overlay' : 'Save Masks'}</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Export: TODO — connect to backend.</p>`);
        }

        return cfWrap(`<p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Select an item from the tree.</p>`);
    }

    // ── ANNOTADE ─────────────────────────────────
    if (moduleType === 'annotade') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const anState = sub0?._anState || {};
        const anWrap = (html) => `<div class="settings-form" data-module="annotade" data-step="annotade" data-section="${id}" onchange="debouncedSaveParams(this)">${html}</div>`;

        if (id === 'an-load-image') {
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Load Image</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">TIFF stacks, PNG, JPEG. Multi-frame supported.</p>
                <div style="display:flex;gap:4px;align-items:center;margin-bottom:8px">
                    <input class="form-input" data-param="image_file" id="anFileInput" placeholder="Select image..." readonly style="flex:1;min-width:0;font-size:var(--fs-xs)" value="${anState.filePath || ''}">
                    <button class="btn btn-default" onclick="annotadeBrowse()" style="flex-shrink:0">Browse</button>
                </div>
                <div style="margin-top:12px"><button class="btn btn-primary" onclick="annotadeLoad()">📥 Load</button></div>
                <div id="anLoadStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:40px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">${anState.loadStatus || 'Select an image and click Load.'}</div>`);
        }

        if (id === 'an-image-info') {
            if (!anState.shape) return anWrap(`<p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Image Info</p><p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Load an image first.</p>`);
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Image Info</p>
                <div style="font-size:var(--fs-xs);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                    <div><b>File:</b> ${anState.filename || '—'}</div>
                    <div><b>Size:</b> ${anState.shape}</div>
                    <div><b>Frames:</b> ${anState.n_frames || 1}</div>
                    <div><b>Type:</b> ${anState.dtype || '—'}</div>
                </div>`);
        }

        if (id === 'an-frame-nav') {
            const curFrame = anState.currentFrame || 0;
            const nFrames = anState.n_frames || 1;
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Frame Navigation</p>
                <div class="form-row"><span class="form-label">Frame</span>
                    <button class="btn btn-default btn-sm" onclick="annotadeFrame(-1)">◀</button>
                    <span id="anFrameLabel" style="min-width:60px;text-align:center;font-size:var(--fs-xs)">${curFrame + 1} / ${nFrames}</span>
                    <button class="btn btn-default btn-sm" onclick="annotadeFrame(1)">▶</button>
                </div>
                <div class="form-row" style="margin-top:8px"><span class="form-label">Brightness</span><input class="form-input" data-param="brightness" type="range" min="-100" max="100" value="${anState.brightness ?? 0}" style="flex:1" oninput="annotadeDisplay()"></div>
                <div class="form-row"><span class="form-label">Contrast</span><input class="form-input" data-param="contrast" type="range" min="10" max="300" value="${Math.round((anState.contrast ?? 1.0) * 100)}" style="flex:1" oninput="annotadeDisplay()"></div>`);
        }

        if (id === 'an-brush') {
            const curTool = anState.tool || 'brush';
            const bActive = curTool === 'brush' ? 'background:var(--accent);color:#fff' : '';
            const eActive = curTool === 'eraser' ? 'background:#e53935;color:#fff' : '';
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Brush / Eraser</p>
                <div style="display:flex;gap:4px;margin-bottom:10px">
                    <button class="btn btn-default" onclick="annotadeSetTool('brush')" style="flex:1;${bActive}">🖌 Brush</button>
                    <button class="btn btn-default" onclick="annotadeSetTool('eraser')" style="flex:1;${eActive}">🧹 Eraser</button>
                </div>
                <div class="form-row"><span class="form-label">Size</span><input class="form-input" data-param="brush_size" type="range" min="1" max="30" value="${anState.brush_size ?? 5}" style="flex:1" oninput="this.nextElementSibling.textContent=this.value;_anSettingsChanged(this)"><span style="width:24px;text-align:right;font-size:var(--fs-xs)">${anState.brush_size ?? 5}</span></div>
                <div class="form-row" style="margin-top:6px"><span class="form-label">Class</span><select class="form-select" data-param="class_id" onchange="_anSettingsChanged(this)">
                    <option value="1"${(anState.class_id||1)==1?' selected':''}>1 — Cell</option>
                    <option value="2"${anState.class_id==2?' selected':''}>2 — Nucleus</option>
                    <option value="3"${anState.class_id==3?' selected':''}>3 — Focal Adhesion</option>
                    <option value="4"${anState.class_id==4?' selected':''}>4 — Boundary</option>
                    <option value="5"${anState.class_id==5?' selected':''}>5 — Background</option>
                </select></div>
                <p style="font-size:10px;color:var(--text-tertiary);margin-top:8px">Keys: <b>B</b> brush, <b>E</b> eraser, <b>[</b>/<b>]</b> size, <b>1-5</b> class</p>`);
        }

        if (id === 'an-shapes') {
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Rectangle / Ellipse</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Click-drag to draw bounding box. Fills with current class.</p>
                <div class="form-row"><span class="form-label">Shape</span><select class="form-select" data-param="shape_type">
                    <option value="rectangle">Rectangle</option>
                    <option value="ellipse">Ellipse</option>
                </select></div>`);
        }

        if (id === 'an-polygon') {
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Polygon</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Click to add vertices. Double-click to close and fill.</p>
                <p style="font-size:10px;color:var(--text-tertiary);margin-top:6px">Press <b>Esc</b> to cancel.</p>`);
        }

        if (id === 'an-objects') {
            const stats = anState.labelStats || {};
            const entries = Object.entries(stats);
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Object Manager</p>
                ${entries.length === 0 ? '<p style="font-size:var(--fs-xs);color:var(--text-tertiary)">No labels yet.</p>' :
                  entries.map(([id,count]) => `<div style="font-size:var(--fs-xs);padding:3px 0"><b>Object ${id}:</b> ${count} px</div>`).join('')}
                <button class="btn btn-default" onclick="annotadeClearLabels()" style="margin-top:10px">🗑 Clear All Labels</button>`);
        }

        if (id === 'an-otsu') {
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Otsu Threshold</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Automatic threshold. Drag on canvas to select ROI, or apply to full image.</p>
                <button class="btn btn-primary" onclick="annotadeOtsu()" style="width:100%">📊 Apply Otsu</button>
                <div id="anOtsuStatus" style="margin-top:8px;font-size:var(--fs-xs);color:var(--text-tertiary)"></div>`);
        }

        if (id === 'an-threshold') {
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Manual Threshold</p>
                <div class="form-row"><span class="form-label">Value</span><input class="form-input" data-param="threshold_value" type="range" min="0" max="255" value="${anState.threshold_value ?? 128}" style="flex:1" oninput="this.nextElementSibling.textContent=this.value"><span style="width:30px;text-align:right;font-size:var(--fs-xs)">${anState.threshold_value ?? 128}</span></div>
                <button class="btn btn-primary" onclick="annotadeThreshold()" style="width:100%;margin-top:8px">🔧 Apply Threshold</button>`);
        }

        if (id === 'an-flood') {
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Flood Fill</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Click on the canvas to seed. Grows by intensity similarity.</p>
                <div class="form-row"><span class="form-label">Tolerance</span><input class="form-input" data-param="flood_tolerance" type="number" min="1" max="100" value="${anState.flood_tolerance ?? 30}" style="width:60px"></div>
                <button class="btn btn-primary" onclick="annotadeSetTool('flood')" style="width:100%;margin-top:8px">💧 Activate Flood Fill</button>`);
        }

        if (id === 'an-fcm') {
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Fuzzy C-Means</p>
                <div class="form-row"><span class="form-label">Clusters</span><input class="form-input" data-param="fcm_clusters" type="number" min="2" max="5" value="${anState.fcm_clusters ?? 2}" style="width:60px"></div>
                <button class="btn btn-primary" onclick="annotadeFCM()" style="width:100%;margin-top:8px">🎯 Apply FCM</button>`);
        }

        if (id === 'an-export-labels') {
            return anWrap(`
                <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Export Labels</p>
                <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Export as 16-bit TIFF label image.</p>
                <button class="btn btn-primary" onclick="annotadeExport()" style="width:100%">💾 Export Labels</button>`);
        }

        return anWrap(`<p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Select an item from the tree.</p>`);
    }

    // ── GENERIC FALLBACKS ─────────────────────────
    if (id === 'select-movie' || id === 'data-import') {
        const ws0 = getActiveWorkspace();
        const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
        const savedImportStatus = sub0?._statusBoxes?.importStatus || 'Select a TIFF file and click Import to load.';
        setTimeout(() => _restoreStatusBoxes(sub0, 'importStatus'), 60);
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Movie File</p>
        <div style="display:flex;gap:4px;align-items:center;margin-bottom:8px"><input class="form-input" data-param="input_file" id="movieFileInput" placeholder="Select file..." readonly style="flex:1;min-width:0;font-size:var(--fs-xs)"><button class="btn btn-default" onclick="selectInputFile(this)" style="flex-shrink:0;white-space:nowrap">Browse</button></div>
        <div class="form-row"><span class="form-label">Format</span><select class="form-select" data-param="format"><option>TIFF Stack</option><option>ND2</option><option>CZI</option><option>PNG Sequence</option></select></div>
        <div style="margin-top:12px;display:flex;gap:8px">
            <button class="btn btn-primary" onclick="doImportMovie()">📥 Import Movie</button>
        </div>
        <div id="importStatus" style="margin-top:10px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:60px;padding:8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
            ${savedImportStatus}
        </div>`);
    }

    if (id === 'channel-setup' && moduleType === 'immunia') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Channel Role Assignment</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Assign each channel to its biological role. IMMUNIA processes each role differently during segmentation.</p>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:6px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:#ef5350;text-transform:uppercase;letter-spacing:1px">🔴 Cytotoxicity Indicator</div>
        <p style="font-size:10px;color:var(--text-tertiary);margin-bottom:4px">Dead cell marker (PI, Sytox, Annexin V). Thresholded per frame to count cell death events.</p>
        <div class="form-row"><span class="form-label">Channel</span><select class="form-select immunia-ch-select" data-param="dead_channel_idx" data-role="dead" style="width:140px"><option value="">— select —</option><option value="0" selected>Channel 0</option><option value="1">Channel 1</option><option value="2">Channel 2</option><option value="3">Channel 3</option></select></div>
        <div class="form-row"><span class="form-label">Marker Name</span><input class="form-input" data-param="dead_channel_name" list="immunia-marker-list" placeholder="e.g. Sytox Blue" style="width:140px"></div>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:10px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:#66bb6a;text-transform:uppercase;letter-spacing:1px">🟢 Target Cells</div>
        <p style="font-size:10px;color:var(--text-tertiary);margin-bottom:4px">Cells being targeted (tumor, cancer). Time-averaged mask for spatial reference.</p>
        <div class="form-row"><span class="form-label">Channel</span><select class="form-select immunia-ch-select" data-param="tumor_channel_idx" data-role="tumor" style="width:140px"><option value="">— select —</option><option value="0">Channel 0</option><option value="1" selected>Channel 1</option><option value="2">Channel 2</option><option value="3">Channel 3</option></select></div>
        <div class="form-row"><span class="form-label">Cell Type</span><input class="form-input" data-param="tumor_channel_name" list="immunia-target-list" placeholder="e.g. MDA-MB-231" style="width:140px"></div>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:10px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">🔵 Substrate / Stromal</div>
        <p style="font-size:10px;color:var(--text-tertiary);margin-bottom:4px">Tissue or endothelial cell layer. Time-averaged mask for spatial context.</p>
        <div class="form-row"><span class="form-label">Channel</span><select class="form-select immunia-ch-select" data-param="tissue_channel_idx" data-role="tissue" style="width:140px"><option value="">— select —</option><option value="0">Channel 0</option><option value="1">Channel 1</option><option value="2" selected>Channel 2</option><option value="3">Channel 3</option></select></div>
        <div class="form-row"><span class="form-label">Cell Type</span><input class="form-input" data-param="tissue_channel_name" list="immunia-substrate-list" placeholder="e.g. HUVEC" style="width:140px"></div>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:10px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:#ffa726;text-transform:uppercase;letter-spacing:1px">🟠 Effector Cells</div>
        <p style="font-size:10px;color:var(--text-tertiary);margin-bottom:4px">Immune cells to track (NK, T cells, macrophages). Segmented per frame → tracked individually.</p>
        <div class="form-row"><span class="form-label">Channel</span><select class="form-select immunia-ch-select" data-param="nk_channel_idx" data-role="nk" style="width:140px"><option value="">— select —</option><option value="0">Channel 0</option><option value="1">Channel 1</option><option value="2">Channel 2</option><option value="3" selected>Channel 3</option></select></div>
        <div class="form-row"><span class="form-label">Cell Type</span><input class="form-input" data-param="nk_channel_name" list="immunia-effector-list" placeholder="e.g. NK-92" style="width:140px"></div>

        <datalist id="immunia-marker-list">
            <option value="Sytox Blue"><option value="Sytox Green"><option value="Sytox Red">
            <option value="PI"><option value="Propidium Iodide"><option value="Annexin V">
            <option value="DAPI"><option value="Hoechst 33342"><option value="EthD-1">
            <option value="LIVE/DEAD"><option value="Calcein AM"><option value="7-AAD">
        </datalist>
        <datalist id="immunia-target-list">
            <option value="MDA-MB-231"><option value="MCF-7"><option value="HeLa">
            <option value="A549"><option value="K562"><option value="Raji">
            <option value="Tumor Spheroid"><option value="Cancer Cells"><option value="Target Cells">
        </datalist>
        <datalist id="immunia-substrate-list">
            <option value="HUVEC"><option value="Endothelial"><option value="HMEC-1">
            <option value="Fibroblast"><option value="Stromal"><option value="Matrigel">
            <option value="Collagen"><option value="ECM"><option value="Substrate">
        </datalist>
        <datalist id="immunia-effector-list">
            <option value="NK-92"><option value="Primary NK"><option value="NK Cells">
            <option value="CD8+ T"><option value="CAR-T"><option value="T Cells">
            <option value="Macrophages"><option value="Neutrophils"><option value="Monocytes">
            <option value="Dendritic Cells"><option value="γδ T Cells"><option value="Effector Cells">
        </datalist>
    `);
    }

    // ── IMMUNIA: SEGMENTATION PANELS (4 roles) ──────
    if (moduleType === 'immunia' && id?.startsWith('seg-')) {
        const roleMap = {
            'seg-dead':   { key: 'dead',   label: 'Cytotoxicity Indicator', color: '#ef5350', threshFactor: 0.8, minSize: 10,   method: 'grid',   separate: false, output: 'Binary mask', desc: 'Binarization only. Dead cell events counted by area, no individual labeling needed.' },
            'seg-tumor':  { key: 'tumor',  label: 'Target Cells',          color: '#66bb6a', threshFactor: 1.0, minSize: 200,  method: 'global', separate: true,  output: 'Binary + labeled', desc: 'Binarized and labeled. Individual tumor cells/regions identified for spatial analysis.' },
            'seg-tissue': { key: 'tissue', label: 'Substrate / Stromal',   color: '#42a5f5', threshFactor: 0.7, minSize: 1000, method: 'global', separate: false, output: 'Binary mask', desc: 'Binarization only. Endothelial monolayer mask for spatial context — no individual labeling.' },
            'seg-nk':     { key: 'nk',     label: 'Effector Cells',        color: '#ffa726', threshFactor: 0.9, minSize: 30,   method: 'global', separate: true,  output: 'Binary + labeled', desc: 'Binarized and labeled per frame. Individual immune cells segmented for tracking.' },
        };
        const role = roleMap[id];
        if (role) {
            // Get channel name from import step
            const ws0 = getActiveWorkspace();
            const sub0 = ws0?.subtabs.get(ws0?.activeSubtab);
            const importSub = [...(ws0?.subtabs.values() || [])].find(s => s.stepId === 'import' && s.pipelineId === sub0?.pipelineId);
            const chParams = importSub?._localParams?.['channel-setup'] || {};
            const chIdx = chParams[`${role.key}_channel_idx`] || '?';
            const chName = chParams[`${role.key}_channel_name`] || role.label;

            const _segHtml = wrap(`
            <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:-4px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:${role.color};text-transform:uppercase;letter-spacing:1px">● ${role.label}</div>
            <p style="font-size:10px;color:var(--text-tertiary);margin-bottom:8px">${role.desc}</p>
            <div style="font-size:var(--fs-xs);color:${role.color};margin-bottom:10px;padding:4px 8px;background:${role.color}10;border:1px solid ${role.color}30;border-radius:var(--r-sm)">Channel ${chIdx}: <strong>${chName}</strong></div>

            <div class="form-row"><span class="form-label">Threshold Factor</span><input class="form-input" data-param="${role.key}_threshold_factor" type="number" step="0.05" value="${role.threshFactor}" style="width:70px" id="tf_${role.key}"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">× Otsu</span></div>
            <div class="form-row"><span class="form-label">Min Object Size</span><input class="form-input" data-param="${role.key}_min_size" type="number" step="1" value="${role.minSize}" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
            <div class="form-row"><span class="form-label">Gaussian Sigma</span><input class="form-input" data-param="${role.key}_gaussian_sigma" type="number" step="0.5" value="2.0" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
            <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="${role.key}_threshold_method" onchange="immuniaSegMethodChanged('${role.key}', this.value)">
                <option value="global"${role.method === 'global' ? ' selected' : ''}>Global Otsu</option>
                <option value="grid"${role.method === 'grid' ? ' selected' : ''}>Grid Otsu (local)</option>
                <option value="adaptive">Local Gaussian</option>
                <option value="clahe_global">CLAHE + Otsu</option>
                <option value="manual">Manual Threshold</option>
                <option value="min_max">Min/Max Clip + Otsu</option>
            </select></div>
            <div id="segManualFields_${role.key}" style="display:none">
                <div class="form-row"><span class="form-label">Threshold Value</span><input class="form-input" data-param="${role.key}_manual_threshold" type="number" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">raw intensity</span></div>
            </div>
            <div id="segMinMaxFields_${role.key}" style="display:none">
                <div class="form-row"><span class="form-label">Intensity Min</span><input class="form-input" data-param="${role.key}_intensity_min" type="number" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">remove below</span></div>
                <div class="form-row"><span class="form-label">Intensity Max</span><input class="form-input" data-param="${role.key}_intensity_max" type="number" step="1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">clip above</span></div>
            </div>
            <div class="form-row"><span class="form-label">Output</span><span style="font-size:var(--fs-xs);color:${role.separate ? '#66bb6a' : 'var(--text-tertiary)'};font-weight:600">${role.output}</span></div>
            <input type="hidden" data-param="${role.key}_separate_objects" value="${role.separate}">

            <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">Preview</div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Frame</span>
                <input class="form-input" id="segPreviewFrame_${role.key}" type="number" value="0" min="0" style="width:60px">
                <input type="range" min="0" max="180" value="0" style="flex:1;accent-color:${role.color};height:3px" oninput="document.getElementById('segPreviewFrame_${role.key}').value=this.value">
            </div>
            <button class="btn btn-primary" data-role="${role.key}" onclick="doImmuniaSegPreview(this.dataset.role)" style="width:100%;background:${role.color}">🔍 Preview Segmentation</button>
            <div id="segPreviewStatus_${role.key}" style="margin-top:8px;font-size:var(--fs-xs);font-family:var(--font-mono);color:var(--text-tertiary);min-height:30px;padding:6px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm)">
                Set parameters, select a frame, then click Preview.
            </div>
            `);
            return _segHtml;
        }
    }

    // ── IMMUNIA: TRACKING PANELS ──────────────
    if (moduleType === 'immunia' && id === 'track-source') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Tracking Source</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Select which cell type to track. Typically effector (immune) cells are tracked individually across frames.</p>
        <div class="form-row"><span class="form-label">Track</span><select class="form-select" data-param="track_target">
            <option value="nk" selected>Effector Cells (NK/T)</option>
            <option value="dead">Cytotoxicity Events</option>
            <option value="tumor">Target Cells</option>
        </select></div>
        <div class="form-row"><span class="form-label">Detection Mode</span><select class="form-select" data-param="use_masks">
            <option value="true" selected>From Masks (recommended)</option>
            <option value="false">From Raw Images (trackpy)</option>
        </select></div>
        <div class="form-row"><span class="form-label">Pixel Size</span><input class="form-input" data-param="pixel_to_um" type="number" step="0.01" value="0.65" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">μm/px</span></div>
        <div class="form-row"><span class="form-label">Time Interval</span><input class="form-input" data-param="frame_to_min" type="number" step="0.1" value="3.0" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">min/frame</span></div>
        `);
    }

    if (moduleType === 'immunia' && id === 'track-linking') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Linking Parameters</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Controls how detections are linked across frames into trajectories.</p>
        <div class="form-row"><span class="form-label">Search Range</span><input class="form-input" data-param="search_range" type="number" step="1" value="15" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px max displacement</span></div>
        <div class="form-row"><span class="form-label">Memory</span><input class="form-input" data-param="memory" type="number" step="1" value="3" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames gap allowed</span></div>
        <div class="form-row"><span class="form-label">Adaptive Stop</span><input class="form-input" data-param="adaptive_stop" type="number" step="1" value="5" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">iterations</span></div>
        <div class="form-row"><span class="form-label">Adaptive Step</span><input class="form-input" data-param="adaptive_step" type="number" step="0.01" value="0.95" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">shrink factor</span></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Search Range: max px a cell can move between frames. Memory: how many frames a cell can disappear and be re-linked.</p>
        `);
    }

    if (moduleType === 'immunia' && id === 'track-filtering') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Track Filtering</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Remove short or unrealistic trajectories.</p>
        <div class="form-row"><span class="form-label">Min Track Length</span><input class="form-input" data-param="min_frames" type="number" step="1" value="10" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        <div class="form-row"><span class="form-label">Max Velocity</span><input class="form-input" data-param="max_velocity" type="number" step="1" value="50" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px/frame</span></div>
        <div class="form-row"><span class="form-label">Min Velocity</span><input class="form-input" data-param="min_velocity" type="number" step="0.01" value="0.1" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px/frame</span></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Tracks shorter than Min Length are discarded. Tracks with velocity above Max or below Min are filtered out.</p>
        `);
    }

    // ── IMMUNIA: SIGNAL ASSOCIATION PANELS ─────
    if (moduleType === 'immunia' && id === 'sa-signals') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Signal Extraction</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Convert cell trajectories into 1D time signals for pairwise coupling analysis.</p>
        <div class="form-row"><span class="form-label">Signal Type</span><select class="form-select" data-param="signal_type">
            <option value="position_pca" selected>Position PCA — PCA₁(x, y)</option>
            <option value="speed">Speed — √(Δx² + Δy²)</option>
            <option value="velocity_pca">Velocity PCA — PCA₁(vx, vy)</option>
        </select></div>
        <div class="form-row"><span class="form-label">Min Track Length</span><input class="form-input" data-param="min_signal_length" type="number" step="1" value="20" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        <div class="form-row"><span class="form-label">Min Overlap</span><input class="form-input" data-param="min_overlap" type="number" step="1" value="20" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames for pairs</span></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px"><strong>Position PCA:</strong> captures dominant drift direction (chemotaxis). <strong>Speed:</strong> scalar velocity magnitude. <strong>Velocity PCA:</strong> captures directional coordination between cells.</p>
        `);
    }

    if (moduleType === 'immunia' && id === 'sa-method') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Association Method</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Select the statistical coupling method for pairwise signal analysis.</p>
        <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="assoc_method" onchange="immuniaAssocMethodChanged(this.value)">
            <option value="ccm" selected>CCM — Convergent Cross Mapping</option>
            <option value="granger">Granger Causality</option>
            <option value="correlation">Pearson Correlation</option>
            <option value="mutual_info">Mutual Information</option>
            <option value="transfer_entropy">Transfer Entropy</option>
        </select></div>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">Stationarizer</div>
        <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="stationarize">
            <option value="none">None (raw signals)</option>
            <option value="lazy">Lazy (minimal)</option>
            <option value="detrend">Detrend</option>
            <option value="difference">First Difference</option>
            <option value="bandpass" selected>Bandpass (recommended)</option>
            <option value="bandpass_diff">Bandpass + Difference</option>
        </select></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary)">Used by Granger Causality (requires stationary signals).</p>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">Granger Causality</div>
        <div id="saGrangerFields">
            <div class="form-row"><span class="form-label">Max Lag</span><input class="form-input" data-param="granger_max_lag" type="number" step="1" value="5" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
            <div class="form-row"><span class="form-label">Lag Criterion</span><select class="form-select" data-param="granger_lag_criterion">
                <option value="aic" selected>AIC</option>
                <option value="bic">BIC</option>
            </select></div>
        </div>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">Convergent Cross Mapping</div>
        <div id="saCCMFields">
            <div class="form-row"><span class="form-label">Embedding Dim</span><input class="form-input" data-param="ccm_embedding_dim" type="number" step="1" value="2" style="width:70px"></div>
            <div class="form-row"><span class="form-label">Bootstraps</span><input class="form-input" data-param="ccm_n_boot" type="number" step="1" value="20" style="width:70px"></div>
        </div>

        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Enable methods in Method Selection to configure their parameters.</p>
        `);
    }

    if (moduleType === 'immunia' && id === 'sa-surrogates') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Surrogate Testing</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Statistical significance via surrogate time series. More surrogates = more precise p-values but slower.</p>
        <div class="form-row"><span class="form-label">N Surrogates</span>
            <select class="form-select" data-param="n_surrogates_preset" style="width:100px" onchange="if(this.value!=='custom'){document.getElementById('sa_n_surr_custom').value=this.value;document.getElementById('sa_n_surr_custom').style.display='none'}else{document.getElementById('sa_n_surr_custom').style.display=''}">
                <option value="50">50 (fast)</option>
                <option value="100" selected>100 (standard)</option>
                <option value="200">200 (precise)</option>
                <option value="500">500 (publication)</option>
                <option value="custom">Custom...</option>
            </select>
            <input class="form-input" id="sa_n_surr_custom" data-param="n_surrogates" type="number" min="10" max="5000" step="10" value="100" style="width:70px;display:none">
        </div>
        <div class="form-row"><span class="form-label">Method</span><select class="form-select" data-param="surrogate_method">
            <option value="iaaft" selected>IAAFT</option>
            <option value="circular">Circular Shift</option>
            <option value="block_bootstrap">Block Bootstrap</option>
            <option value="shuffle">Random Shuffle</option>
        </select></div>
        <div class="form-row"><span class="form-label">α (significance)</span><input class="form-input" data-param="alpha" type="number" step="0.01" value="0.05" style="width:70px"></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">
            <strong>IAAFT:</strong> preserves power spectrum + amplitude distribution. Gold standard for nonlinear systems.
            <strong>Circular:</strong> preserves autocorrelation structure via random time shift.
            <strong>Block Bootstrap:</strong> resamples blocks, preserves local temporal patterns.
            <strong>Random Shuffle:</strong> fastest but destroys all temporal structure.
        </p>
        `);
    }

    // ── IMMUNIA: GRAPH THEORY PANELS ──────────
    if (moduleType === 'immunia' && id === 'gt-networks') {
        // Dynamically load association runs
        setTimeout(() => _loadGTAssocRuns(), 100);
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Source Data</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Select which association runs to use as input for graph construction.</p>
        <div id="gtAssocRunsList" style="display:flex;flex-direction:column;gap:4px;margin-bottom:12px">
            <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Loading association runs...</span>
        </div>
        <input type="hidden" data-param="gt_selected_runs" id="gtSelectedRuns" value="all">

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">Additional Networks</div>
        <div class="form-row"><span class="form-label">Spatial Networks</span><select class="form-select" data-param="gt_use_spatial"><option value="true">Yes</option><option value="false" selected>No</option></select><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">proximity-based (slow)</span></div>
        <div class="form-row"><span class="form-label">Temporal Networks</span><select class="form-select" data-param="gt_use_temporal"><option value="true">Yes</option><option value="false" selected>No</option></select><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">co-occurrence (slow)</span></div>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">Thresholds</div>
        <div class="form-row"><span class="form-label">CCM Threshold</span><input class="form-input" data-param="ccm_threshold" type="number" step="0.05" value="0.3" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">ρ min edge weight</span></div>
        <div class="form-row"><span class="form-label">GC p-value</span><input class="form-input" data-param="gc_threshold" type="number" step="0.01" value="0.05" style="width:70px"></div>
        <div class="form-row"><span class="form-label">Spatial Radius</span><input class="form-input" data-param="spatial_radius" type="number" step="10" value="100" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
        <div class="form-row"><span class="form-label">Temporal Window</span><input class="form-input" data-param="temporal_window" type="number" step="1" value="10" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        `);
    }

    if (moduleType === 'immunia' && id === 'gt-analysis') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Analysis Modes</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Select which analyses to run on the constructed networks.</p>
        <div class="form-row"><span class="form-label">Network Metrics</span><select class="form-select" data-param="gt_do_metrics"><option value="true" selected>Yes</option><option value="false">No</option></select><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">degree, centrality, clustering</span></div>
        <div class="form-row"><span class="form-label">Regional Analysis</span><select class="form-select" data-param="gt_do_regions"><option value="true" selected>Yes</option><option value="false">No</option></select><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">tumor vs tissue metrics</span></div>
        <div class="form-row"><span class="form-label">Boundary Analysis</span><select class="form-select" data-param="gt_do_boundary"><option value="true" selected>Yes</option><option value="false">No</option></select><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">crossing interactions</span></div>
        <div class="form-row"><span class="form-label">Distance Pairs</span><select class="form-select" data-param="gt_do_distance"><option value="true">Yes</option><option value="false" selected>No</option></select><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">remote coupled pairs</span></div>
        <div class="form-row"><span class="form-label">Dynamics</span><select class="form-select" data-param="gt_do_dynamics"><option value="true">Yes</option><option value="false" selected>No</option></select><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">temporal evolution</span></div>
        <div class="form-row"><span class="form-label">Comparative</span><select class="form-select" data-param="gt_do_comparative"><option value="true">Yes</option><option value="false" selected>No</option></select><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">cross-network comparison</span></div>
        `);
    }

    if (moduleType === 'immunia' && id === 'gt-advanced') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Advanced Parameters</p>
        <div class="form-row"><span class="form-label">Distance Mode</span><select class="form-select" data-param="distance_mode">
            <option value="remote" selected>Remote (far apart)</option>
            <option value="nearby">Nearby (close together)</option>
        </select></div>
        <div class="form-row"><span class="form-label">Min Distance</span><input class="form-input" data-param="gt_min_distance" type="number" step="10" value="250" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px (remote mode)</span></div>
        <div class="form-row"><span class="form-label">Max Distance</span><input class="form-input" data-param="gt_max_distance" type="number" step="10" value="100" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px (nearby mode)</span></div>
        <div class="form-row"><span class="form-label">Max Pairs</span><input class="form-input" data-param="gt_max_pairs" type="number" step="1" value="10" style="width:70px"></div>
        <div class="form-row"><span class="form-label">Min Overlap</span><input class="form-input" data-param="gt_min_overlap" type="number" step="5" value="20" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        `);
    }

    // ── IMMUNIA: PLACEHOLDER STEPS ─────────
    if (moduleType === 'immunia' && id === 'ia-placeholder') {
        return wrap(`
        <div style="text-align:center;padding:20px 0">
            <div style="font-size:32px;margin-bottom:12px">🔮</div>
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Integrated Analysis</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin:12px 0;line-height:1.6">Cross-step integration combining Keller-Segel chemotactic predictions, particle tracking behavioral metrics, and graph theory network structure into unified biological insights.</p>
            <div style="margin:16px 0;padding:10px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);font-size:var(--fs-xs);color:var(--text-tertiary);text-align:left;line-height:1.8">
                <b style="color:var(--brand-accent)">Planned Features:</b><br>
                • KS prediction vs PT measured behavior correlation<br>
                • Graph centrality vs spatial proximity to tumor<br>
                • Motion class distribution per network community<br>
                • Eulerian field ↔ graph metric spatial correlation<br>
                • Multi-dataset comparative analysis
            </div>
            <span style="display:inline-block;padding:4px 12px;border-radius:12px;background:var(--surface-3);color:var(--text-tertiary);font-size:var(--fs-xs);font-weight:600">Coming Soon</span>
        </div>
        `);
    }

    if (moduleType === 'immunia' && id === 'te-placeholder') {
        return wrap(`
        <div style="text-align:center;padding:20px 0">
            <div style="font-size:32px;margin-bottom:12px">🔬</div>
            <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Track Examiner</p>
            <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin:12px 0;line-height:1.6">Interactive single-track inspector. Click any NK cell trajectory to see its full behavioral profile across all analysis steps.</p>
            <div style="margin:16px 0;padding:10px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);font-size:var(--fs-xs);color:var(--text-tertiary);text-align:left;line-height:1.8">
                <b style="color:var(--brand-accent)">Planned Features:</b><br>
                • Click-to-select track on movie overlay<br>
                • Per-track MSD curve, speed profile, angle changes<br>
                • Tumor contact timeline with before/after metrics<br>
                • Signal association partners + coupling strength<br>
                • Graph neighbors + network position<br>
                • Comparison with population statistics
            </div>
            <span style="display:inline-block;padding:4px 12px;border-radius:12px;background:var(--surface-3);color:var(--text-tertiary);font-size:var(--fs-xs);font-weight:600">Coming Soon</span>
        </div>
        `);
    }

    // ── IMMUNIA: PARTICLE TRACKING PANELS ─────
    if (moduleType === 'immunia' && id === 'pt-motion') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Motion Classification</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Classify cell motion based on MSD analysis: diffusive, directed, confined, or anomalous.</p>
        <div class="form-row"><span class="form-label">Analysis Mode</span><select class="form-select" data-param="pt_analysis_mode">
            <option value="auto" selected>Auto (detect from data)</option>
            <option value="basic">Basic (motion only)</option>
            <option value="spatial">Spatial (with masks)</option>
            <option value="enhanced">Enhanced (with CCM)</option>
        </select></div>
        <div class="form-row"><span class="form-label">Directed Threshold</span><input class="form-input" data-param="directed_threshold" type="number" step="0.05" value="0.7" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">directionality ratio</span></div>
        <div class="form-row"><span class="form-label">Diffusion Thresholds</span><input class="form-input" data-param="diff_thresholds" type="text" value="0.01,0.05,0.1" style="width:120px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">μm²/min</span></div>
        <div class="form-row"><span class="form-label">MSD R² Threshold</span><input class="form-input" data-param="msd_r_squared_threshold" type="number" step="0.05" value="0.7" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">fit quality</span></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Cells with directionality > threshold are classified as directed movers. Diffusion thresholds separate confined, diffusive, and super-diffusive.</p>
        `);
    }

    if (moduleType === 'immunia' && id === 'pt-spatial') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Spatial Analysis</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Analyze cell behavior relative to tumor regions, tissue boundaries, and other spatial features.</p>
        <div class="form-row"><span class="form-label">Pixel Size</span><input class="form-input" data-param="pt_pixel_to_um" type="number" step="0.01" value="0.65" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">μm/px</span></div>
        <div class="form-row"><span class="form-label">Time Interval</span><input class="form-input" data-param="pt_frame_to_min" type="number" step="0.1" value="3.0" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">min/frame</span></div>
        <div class="form-row"><span class="form-label">Tumor Scale Factor</span><input class="form-input" data-param="scale_factor" type="number" step="0.1" value="1.3" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">boundary expansion</span></div>
        <div class="form-row"><span class="form-label">CCM Significance</span><input class="form-input" data-param="ccm_significance_threshold" type="number" step="0.05" value="0.3" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">ρ threshold</span></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Scale factor expands tumor contours for interaction zone detection. CCM threshold used when association results are available.</p>
        `);
    }

    if (moduleType === 'immunia' && id === 'pt-advanced') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Advanced Settings</p>
        <div class="form-row"><span class="form-label">Min Track Length</span><input class="form-input" data-param="pt_min_track_length" type="number" step="1" value="4" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        <div class="form-row"><span class="form-label">Max Frame Gap</span><input class="form-input" data-param="max_frame_gap" type="number" step="1" value="5" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames</span></div>
        <div class="form-row"><span class="form-label">MSD Fit Fraction</span><input class="form-input" data-param="msd_fit_fraction" type="number" step="0.05" value="0.33" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">of track length</span></div>
        <div class="form-row"><span class="form-label">Revisit Min Gap</span><input class="form-input" data-param="revisit_min_gap" type="number" step="1" value="3" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">frames between visits</span></div>
        <div class="form-row"><span class="form-label">Min Samples</span><input class="form-input" data-param="min_samples_for_stats" type="number" step="1" value="5" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">for statistics</span></div>
        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">MSD Curves</div>
        <div class="form-row"><span class="form-label">Track IDs</span><input class="form-input" data-param="msd_track_ids" type="text" value="" placeholder="e.g. 5,12,27" style="width:120px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">comma-separated (empty = auto)</span></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Leave empty to auto-select the 5 most diverse tracks. Specify particle IDs for specific MSD curves.</p>
        `);
    }

    // ── IMMUNIA: KELLER-SEGEL PANELS ──────────
    if (moduleType === 'immunia' && id === 'ks-source') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Chemoattractant Source</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Define where the chemoattractant signal originates — the tumor-tissue interface or entire tumor bulk.</p>
        <div class="form-row"><span class="form-label">Source Type</span><select class="form-select" data-param="source_type">
            <option value="interface" selected>Interface (tumor boundary)</option>
            <option value="tumor">Tumor (entire region)</option>
        </select></div>
        <div class="form-row"><span class="form-label">Source Strength</span><input class="form-input" data-param="source_strength" type="number" step="1" value="10" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">intensity multiplier</span></div>
        <div class="form-row"><span class="form-label">Tumor Expansion</span><input class="form-input" data-param="tumor_expansion_percent" type="number" step="1" value="10" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">% radius expansion</span></div>
        <div class="form-row"><span class="form-label">Enforce Tissue Mask</span><select class="form-select" data-param="enforce_tissue_mask">
            <option value="true" selected>Yes</option>
            <option value="false">No</option>
        </select></div>
        <div class="form-row"><span class="form-label">Analysis Modes</span><select class="form-select" data-param="analysis_modes">
            <option value="steady_state" selected>Steady State only</option>
            <option value="both">Steady State + Transient</option>
        </select></div>
        <div class="form-row"><span class="form-label">Initial Condition N₀</span><select class="form-select" data-param="n0_source">
            <option value="cumulative" selected>Cumulative Presence (all frames)</option>
            <option value="first_frames">First N Frames</option>
            <option value="uniform">Uniform (tissue-wide)</option>
        </select></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px"><strong>Interface:</strong> chemoattractant released at tumor-tissue boundary. <strong>Tumor:</strong> entire tumor region as source. Expansion grows the integration region around each tumor for validation.</p>
        `);
    }

    if (moduleType === 'immunia' && id === 'ks-pde') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">PDE Parameters</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Keller-Segel model: D<sub>C</sub>∇²C + S − μC = 0 (chemoattractant) and N = N₀·exp(χ/D<sub>N</sub>·C) (cell density).</p>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:8px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">Chemoattractant</div>
        <div class="form-row"><span class="form-label">D<sub>C</sub> (diffusion)</span><input class="form-input" data-param="D_C" type="number" step="10" value="100" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px²/step</span></div>
        <div class="form-row"><span class="form-label">μ (degradation)</span><input class="form-input" data-param="mu" type="number" step="0.01" value="0.1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">1/step</span></div>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#ffa726;text-transform:uppercase;letter-spacing:1px">Cell Response</div>
        <div class="form-row"><span class="form-label">χ (chemotaxis)</span><input class="form-input" data-param="chi" type="number" step="0.5" value="5.0" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">sensitivity</span></div>
        <div class="form-row"><span class="form-label">D<sub>N</sub> (cell diffusion)</span><input class="form-input" data-param="D_N" type="number" step="0.1" value="1.0" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px²/step</span></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">χ/D<sub>N</sub> ratio controls accumulation strength. Higher χ = stronger chemotaxis. Higher D<sub>N</sub> = more diffuse cells.</p>
        `);
    }

    if (moduleType === 'immunia' && id === 'ks-solver') {
        return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:6px">Solver Settings</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:10px">Numerical solver parameters for the PDE solution.</p>
        <div class="form-row"><span class="form-label">dx (spatial step)</span><input class="form-input" data-param="dx" type="number" step="0.1" value="1.0" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">px</span></div>
        <div class="form-row"><span class="form-label">dt (time step)</span><input class="form-input" data-param="ks_dt" type="number" step="0.001" value="0.01" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">stability: dt < dx²/4D</span></div>
        <div class="form-row"><span class="form-label">Max Iterations</span><input class="form-input" data-param="max_iter" type="number" step="1000" value="10000" style="width:80px"></div>
        <div class="form-row"><span class="form-label">Tolerance</span><input class="form-input" data-param="tolerance" type="number" step="0.0000001" value="0.000001" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">convergence</span></div>

        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);padding:5px 10px;margin:12px -12px 8px;font-size:var(--fs-xs);font-weight:700;color:#42a5f5;text-transform:uppercase;letter-spacing:1px">Transient (if enabled)</div>
        <div class="form-row"><span class="form-label">T<sub>max</sub></span><input class="form-input" data-param="T_max" type="number" step="10" value="100" style="width:70px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">time steps</span></div>
        <div class="form-row"><span class="form-label">dt (transient)</span><input class="form-input" data-param="transient_dt" type="number" step="0.001" value="0.01" style="width:70px"></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">Stability: dt must be < dx²/(4·D<sub>C</sub>). With defaults: 0.01 < 1/(4·100) = 0.0025 — adjust dt or D<sub>C</sub> if solver diverges.</p>
        `);
    }

    if (id === 'channel-setup') return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Channel Names</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Name each channel for plots and reports. Type a custom name or select from common proteins.</p>
        <div class="form-row"><span class="form-label">Channel 1</span><input class="form-input" data-param="ch1_name" list="protein-list" placeholder="e.g. Vinculin" style="width:120px" onkeydown="handleProteinTab(event,this)"></div>
        <div class="form-row"><span class="form-label">Channel 2</span><input class="form-input" data-param="ch2_name" list="protein-list" placeholder="e.g. pFAK" style="width:120px" onkeydown="handleProteinTab(event,this)"></div>
        <div class="form-row"><span class="form-label">Channel 3</span><input class="form-input" data-param="ch3_name" list="protein-list" placeholder="e.g. Biosensor" style="width:120px" onkeydown="handleProteinTab(event,this)"></div>
        <div class="form-row"><span class="form-label">Channel 4</span><input class="form-input" data-param="ch4_name" list="protein-list" placeholder="(optional)" style="width:120px" onkeydown="handleProteinTab(event,this)"></div>
        <datalist id="protein-list">
            <option value="Vinculin"><option value="pFAK"><option value="Paxillin"><option value="Talin">
            <option value="Zyxin"><option value="FAK"><option value="α-Actinin"><option value="Tensin">
            <option value="Integrin β1"><option value="Integrin β3"><option value="VASP"><option value="Kindlin">
            <option value="ILK"><option value="Actin"><option value="Myosin II"><option value="RhoA">
            <option value="Rac1"><option value="Cdc42"><option value="Src"><option value="p130Cas">
            <option value="Biosensor"><option value="FRET"><option value="mCherry"><option value="GFP">
            <option value="Beads"><option value="Phase"><option value="DIC"><option value="Brightfield">
            <option value="Dead Cells"><option value="Tumor Cells"><option value="NK Cells"><option value="T Cells">
            <option value="Macrophages"><option value="Target Cells"><option value="Effector Cells">
            <option value="PI"><option value="Sytox Green"><option value="CellTracker Green"><option value="CellTracker Red">
        </datalist>
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-top:14px;margin-bottom:4px">Optical Settings</p>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">Select fluorophore to auto-fill wavelengths from lookup table.</p>
        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:6px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">Channel 1</div>
        <div class="form-row"><span class="form-label">Fluorophore</span><select class="form-select" data-param="ch1_fluor" style="width:110px" onchange="autoFillWavelengths(this,1)"><option value="">— select —</option><option>GFP</option><option>EGFP</option><option>mEmerald</option><option>YFP</option><option>EYFP</option><option>mVenus</option><option>CFP</option><option>ECFP</option><option>mCerulean</option><option>BFP</option><option>EBFP</option><option>RFP</option><option>DsRed</option><option>mCherry</option><option>tdTomato</option><option>mStrawberry</option><option>mRFP</option><option>Alexa 488</option><option>Alexa 546</option><option>Alexa 568</option><option>Alexa 594</option><option>Alexa 647</option><option>DAPI</option><option>Hoechst</option><option>Other</option></select></div>
        <div class="form-row"><span class="form-label">Emission λ</span><input class="form-input" data-param="ch1_emission" id="ch1_emission" type="number" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">nm</span></div>
        <div class="form-row"><span class="form-label">Excitation λ</span><input class="form-input" data-param="ch1_excitation" id="ch1_excitation" type="number" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">nm</span></div>
        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:10px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">Channel 2</div>
        <div class="form-row"><span class="form-label">Fluorophore</span><select class="form-select" data-param="ch2_fluor" style="width:110px" onchange="autoFillWavelengths(this,2)"><option value="">— select —</option><option>GFP</option><option>EGFP</option><option>mEmerald</option><option>YFP</option><option>EYFP</option><option>mVenus</option><option>CFP</option><option>ECFP</option><option>mCerulean</option><option>BFP</option><option>EBFP</option><option>RFP</option><option>DsRed</option><option>mCherry</option><option>tdTomato</option><option>mStrawberry</option><option>mRFP</option><option>Alexa 488</option><option>Alexa 546</option><option>Alexa 568</option><option>Alexa 594</option><option>Alexa 647</option><option>DAPI</option><option>Hoechst</option><option>Other</option></select></div>
        <div class="form-row"><span class="form-label">Emission λ</span><input class="form-input" data-param="ch2_emission" id="ch2_emission" type="number" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">nm</span></div>
        <div class="form-row"><span class="form-label">Excitation λ</span><input class="form-input" data-param="ch2_excitation" id="ch2_excitation" type="number" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">nm</span></div>
        <div style="background:linear-gradient(180deg,var(--surface-3) 0%,var(--surface-2) 100%);border-bottom:1px solid rgba(0,0,0,.25);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);padding:5px 10px;margin:10px -12px 6px;font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px">Channel 3</div>
        <div class="form-row"><span class="form-label">Fluorophore</span><select class="form-select" data-param="ch3_fluor" style="width:110px" onchange="autoFillWavelengths(this,3)"><option value="">— select —</option><option>GFP</option><option>EGFP</option><option>mEmerald</option><option>YFP</option><option>EYFP</option><option>mVenus</option><option>CFP</option><option>ECFP</option><option>mCerulean</option><option>BFP</option><option>EBFP</option><option>RFP</option><option>DsRed</option><option>mCherry</option><option>tdTomato</option><option>mStrawberry</option><option>mRFP</option><option>Alexa 488</option><option>Alexa 546</option><option>Alexa 568</option><option>Alexa 594</option><option>Alexa 647</option><option>DAPI</option><option>Hoechst</option><option>Other</option></select></div>
        <div class="form-row"><span class="form-label">Emission λ</span><input class="form-input" data-param="ch3_emission" id="ch3_emission" type="number" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">nm</span></div>
        <div class="form-row"><span class="form-label">Excitation λ</span><input class="form-input" data-param="ch3_excitation" id="ch3_excitation" type="number" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">nm</span></div>`);

    if (id === 'metadata') return wrap(`
        <p style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary);margin-bottom:10px">Imaging Parameters</p>
        <div class="form-row"><span class="form-label">Pixel Size</span><input class="form-input" data-param="pixel_size_um" type="number" step="0.001" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">μm/px</span></div>
        <div class="form-row"><span class="form-label">Time Interval</span><input class="form-input" data-param="t_interval" type="number" step="0.1" style="width:80px"><span style="font-size:var(--fs-xs);color:var(--text-tertiary)">sec</span></div>
        <div class="form-row"><span class="form-label">Numerical Aperture</span><input class="form-input" data-param="numerical_aperture" type="number" step="0.01" placeholder="1.49" style="width:80px"></div>
        <div class="form-row"><span class="form-label">Camera Bit Depth</span><select class="form-select" data-param="camera_bit_depth"><option value="16">16-bit</option><option value="12">12-bit</option><option value="8">8-bit</option></select></div>
        <div class="form-row"><span class="form-label">Imaging Mode</span><select class="form-select" data-param="imaging_mode"><option>TIRF</option><option>Widefield</option><option>Confocal</option><option>Spinning Disk</option></select></div>
        <div class="form-row"><span class="form-label">Notes</span><input class="form-input" data-param="notes" placeholder="Optional notes..." style="width:100%"></div>
        <p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">PSF sigma is auto-derived from NA + emission wavelength + pixel size.</p>`);

    if (id.endsWith('-params') || id === 'params') return wrap(`
        <p style="font-size:var(--fs-sm);color:var(--text-tertiary)">Parameters for this step will be customized per module type.</p>`);

    return `<p class="placeholder-text">Select an item from the tree</p>`;
}

// ═════════════════════════════════════════════
// RIGHT PANEL — Open Modules List
// ═════════════════════════════════════════════

function _formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
}

function _formatDate(isoStr) {
    if (!isoStr) return '—';
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
         + ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function _propRow(label, value, copyable) {
    const copyBtn = copyable ? `<span onclick="navigator.clipboard.writeText('${value.replace(/'/g, "\\'")}');updateStatus('Copied!')" style="cursor:pointer;opacity:.4;margin-left:4px" title="Copy">📋</span>` : '';
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:3px 0;border-bottom:1px solid var(--surface-2)">
        <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">${label}</span>
        <span style="font-size:var(--fs-xs);color:var(--text-secondary);font-family:var(--font-mono);max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:right" title="${value}">${value}${copyBtn}</span>
    </div>`;
}

async function updatePropertiesPanel(pipelineIdOverride) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const el = document.getElementById('propsContent');
    if (!el) return;

    // Determine pipeline from override or active subtab
    const sub = ws.subtabs.get(ws.activeSubtab);
    const pid = pipelineIdOverride || sub?.pipelineId;
    if (!pid) {
        el.innerHTML = '<p class="placeholder-text">Select a module to view properties</p>';
        return;
    }

    const pipeline = ws.pipelines.get(pid);
    const pName = pipeline?.name || pid;
    const pType = pipeline?.type?.toUpperCase() || '—';
    const stepCount = pipeline?.steps?.length || 0;
    const currentStep = sub?.stepId || '—';

    // Show immediate info first (no API call needed)
    el.innerHTML = `
        <div style="padding:2px 0">
            <div style="font-weight:700;margin-bottom:2px;font-size:var(--fs-sm)">${pName}</div>
            <div style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">${pType} · ${stepCount} steps · ${currentStep}</div>
            ${_propRow('Created', '...')}
            ${_propRow('Modified', '...')}
            ${_propRow('Folder Size', '...')}
            ${_propRow('Cache', '...')}
            ${_propRow('Location', '...')}
            <div style="margin-top:8px">
                <button class="btn btn-default" onclick="deletePipeline('${pid}')" style="color:var(--status-error);font-size:var(--fs-xs)">Delete Pipeline</button>
            </div>
        </div>`;

    // Fetch full metadata from backend
    if (!state._projectOpen) return;
    const res = await api(`pipeline/${ws.id}/${pid}/info`);
    if (!res.success) return;
    const d = res.data;

    el.innerHTML = `
        <div style="padding:2px 0">
            <div style="font-weight:700;margin-bottom:2px;font-size:var(--fs-sm)">${pName}</div>
            <div style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:8px">${pType} · ${stepCount} steps · ${currentStep}</div>
            ${_propRow('Created', _formatDate(d.created))}
            ${_propRow('Modified', _formatDate(d.last_modified))}
            ${_propRow('Folder Size', _formatBytes(d.total_size) + ` (${d.file_count} files)`)}
            ${_propRow('Cache', d.cache_size > 0 ? _formatBytes(d.cache_size) + ` (${d.cache_files} stacks)` : 'Empty')}
            ${_propRow('Location', d.path, true)}
            ${_propRow('Project Root', d.project_root, true)}
            ${d.step_sizes ? `
                <div style="margin-top:8px;font-size:var(--fs-xs);color:var(--text-tertiary);font-weight:600;margin-bottom:4px">Per-Step Sizes</div>
                ${Object.entries(d.step_sizes).map(([step, size]) =>
                    _propRow(step, _formatBytes(size))
                ).join('')}
            ` : ''}
            <div style="margin-top:8px">
                <button class="btn btn-default" onclick="deletePipeline('${pid}')" style="color:var(--status-error);font-size:var(--fs-xs)">Delete Pipeline</button>
            </div>
        </div>`;
}

function updateOpenModulesList() {
    const ws = getActiveWorkspace();
    const c = document.getElementById('openModulesList');
    if (!ws || !c) return;
    if (ws.type === 'codechat') return;
    const mods = [...ws.subtabs.values()].filter(s => s.type === 'module');
    if (mods.length === 0) { c.innerHTML = '<p class="placeholder-text">No modules open</p>'; return; }
    c.innerHTML = mods.map(s => `
        <div class="open-module-item ${s.id === ws.activeSubtab ? 'active' : ''}" onclick="switchSubtab('${s.id}')">
            <span class="open-module-dot" style="background:${getAccent(s.moduleType)}"></span>
            <span class="open-module-label">${s.label}</span>
            <span class="open-module-close" onclick="closeSubtab('${s.id}',event)">×</span>
        </div>`).join('');
}

// ═════════════════════════════════════════════
// DRAG & DROP
// ═════════════════════════════════════════════

function startDrag(e, type) { e.dataTransfer.setData('text/plain', type); }
function handleCanvasDrop(e) {
    e.preventDefault();
    const type = e.dataTransfer.getData('text/plain');
    const rect = e.currentTarget.getBoundingClientRect();
    const ws = getActiveWorkspace();
    const pos = findNearestFreeCell(ws, e.clientX - rect.left, e.clientY - rect.top);
    createPipeline(type, pos.x, pos.y);
}
function createPipelineOnCanvas(type) {
    createPipeline(type);
}

const GRID_X = 260;
const GRID_Y = 300;
const NODE_W = 220;
const PAD_X = (GRID_X - NODE_W) / 2;
const PAD_Y = 20;

function snapToGrid(v, axis) {
    const g = axis === 'y' ? GRID_Y : GRID_X;
    const pad = axis === 'y' ? PAD_Y : PAD_X;
    return Math.round(v / g) * g + pad;
}

function isPositionOccupied(ws, x, y, excludePid) {
    // Check if any pipeline overlaps this position (bounding box)
    for (const [pid, p] of ws.pipelines) {
        if (pid === excludePid) continue;
        if (Math.abs(p.x - x) < GRID_X * 0.8 && Math.abs(p.y - y) < GRID_Y * 0.8) return true;
    }
    return false;
}

function findNearestFreeCell(ws, rawX, rawY, excludePid) {
    const snappedX = snapToGrid(rawX, 'x');
    const snappedY = snapToGrid(rawY, 'y');
    if (!isPositionOccupied(ws, snappedX, snappedY, excludePid)) {
        return { x: snappedX, y: snappedY };
    }
    // Search nearby cells in expanding radius
    for (let r = 1; r < 10; r++) {
        for (let dx = -r; dx <= r; dx++) {
            for (let dy = -r; dy <= r; dy++) {
                if (Math.abs(dx) !== r && Math.abs(dy) !== r) continue;
                const nx = snappedX + dx * GRID_X;
                const ny = snappedY + dy * GRID_Y;
                if (nx < 0 || ny < 0) continue;
                if (!isPositionOccupied(ws, nx, ny, excludePid)) {
                    return { x: nx, y: ny };
                }
            }
        }
    }
    return { x: snappedX, y: snappedY };
}

function showCanvasGrid(show) {
    const cv = document.querySelector('.canvas-view');
    if (cv) cv.classList.toggle('show-grid', show);
}

function makeDraggable(el, canvas) {
    if (!el) return;
    let dragging = false, ox, oy;
    el.addEventListener('mousedown', e => {
        if (e.target.closest('.pipeline-step') || e.target.closest('[onclick]')) return;
        dragging = true; ox = e.clientX - el.offsetLeft; oy = e.clientY - el.offsetTop;
        el.style.zIndex = 100; e.preventDefault();
        showCanvasGrid(true);
    });
    document.addEventListener('mousemove', e => {
        if (!dragging) return;
        const ws = getActiveWorkspace();
        const pid = el.id.replace('node-', '');
        const pos = findNearestFreeCell(ws, e.clientX - ox, e.clientY - oy, pid);
        el.style.left = Math.max(0, pos.x) + 'px';
        el.style.top = Math.max(0, pos.y) + 'px';
    });
    document.addEventListener('mouseup', () => {
        if (!dragging) return; dragging = false; el.style.zIndex = '';
        showCanvasGrid(false);
        const ws = getActiveWorkspace(); if (!ws) return;
        const pid = el.id.replace('node-', '');
        const p = ws.pipelines.get(pid);
        if (p) {
            p.x = parseInt(el.style.left);
            p.y = parseInt(el.style.top);
            // Sync position to backend
            if (state._projectOpen) {
                api(`pipeline/${ws.id}/${pid}/position`, 'POST', { x: p.x, y: p.y });
            }
        }
    });
}

// ═════════════════════════════════════════════
// COLUMN RESIZER (inside module view)
// ═════════════════════════════════════════════

function initColResize(e, resizer) {
    e.preventDefault();
    const prev = resizer.previousElementSibling;
    const startX = e.clientX;
    const startW = prev.offsetWidth;
    resizer.classList.add('active');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';

    const move = e2 => {
        const delta = e2.clientX - startX;
        const minW = parseInt(getComputedStyle(prev).minWidth) || 100;
        const maxW = parseInt(getComputedStyle(prev).maxWidth) || 600;
        prev.style.width = Math.max(minW, Math.min(maxW, startW + delta)) + 'px';
    };
    const up = () => {
        resizer.classList.remove('active');
        document.body.style.cursor = ''; document.body.style.userSelect = '';
        document.removeEventListener('mousemove', move);
        document.removeEventListener('mouseup', up);
    };
    document.addEventListener('mousemove', move);
    document.addEventListener('mouseup', up);
}

// ═════════════════════════════════════════════
// PANEL RESIZER (global left/right)
// ═════════════════════════════════════════════

function initResizers() {
    setupResizer('leftResizer', 'leftPanel', 'left');
    setupResizer('rightResizer', 'rightPanel', 'right');
}

function setupResizer(rid, pid, side) {
    const r = document.getElementById(rid);
    const p = document.getElementById(pid);
    if (!r || !p) return;
    let active = false, sx, sw;
    r.addEventListener('mousedown', e => {
        active = true; sx = e.clientX; sw = p.offsetWidth;
        r.classList.add('active'); document.body.style.cursor = 'col-resize'; document.body.style.userSelect = 'none'; e.preventDefault();
    });
    document.addEventListener('mousemove', e => {
        if (!active) return;
        const d = side === 'left' ? e.clientX - sx : sx - e.clientX;
        p.style.width = Math.max(parseInt(getComputedStyle(p).minWidth), Math.min(parseInt(getComputedStyle(p).maxWidth), sw + d)) + 'px';
    });
    document.addEventListener('mouseup', () => {
        if (!active) return; active = false; r.classList.remove('active');
        document.body.style.cursor = ''; document.body.style.userSelect = '';
    });
}

// ═════════════════════════════════════════════
// HELPERS
// ═════════════════════════════════════════════

function toggleCat(h) { h.querySelector('.cat-arrow').classList.toggle('open'); h.nextElementSibling.classList.toggle('open'); }
function getActiveWorkspace() { return state.workspaces.get(state.activeWorkspace) || null; }
function updateStatus(t) { const el = document.getElementById('statusText'); if (el) el.textContent = t; }

function isStepOpen(pid, stepId) {
    const ws = getActiveWorkspace(); if (!ws) return false;
    for (const s of ws.subtabs.values()) { if (s.pipelineId === pid && s.stepId === stepId) return true; }
    return false;
}

function getAccent(type) {
    return { fastia:'var(--accent-fastia)', immunia:'var(--accent-immunia)', cornealia:'var(--accent-cornealia)', cornealia_batch:'var(--accent-cornealia)', cellfade:'var(--accent-cellfade)', cellvisia:'var(--accent-cellvisia)' }[type] || 'var(--accent-generic)';
}

// ═════════════════════════════════════════════
// PIPELINE DEFINITIONS
// ═════════════════════════════════════════════

function getPipelineDef(type) {
    const d = {
        fastia: { name:'FASTIA', short:'FASTIA', icon: ICONS.fastia(14), iconLg: ICONS.fastia(18), steps: [
            { id:'import', name:'1. Movie Import' },
            { id:'detection', name:'2. FA Detection' },
            { id:'tracking', name:'3. FA Tracking' },
            { id:'classification', name:'4. FA Classification' },
            { id:'kinetics', name:'5. Kinetic Analysis' },
            { id:'association', name:'6. Association & Edge Analysis' },
            { id:'examination', name:'7. FA Examination' },
        ]},
        immunia: { name:'IMMUNIA', short:'IMMUNIA', icon: ICONS.immunia(14), iconLg: ICONS.immunia(18), steps: [
            { id:'import', name:'1. Movie Import' },
            { id:'segment', name:'2. Segmentation' },
            { id:'track', name:'3. Cell Tracking' },
            { id:'signal_association', name:'4. Signal Association' },
            { id:'keller_segel', name:'5. Keller-Segel' },
            { id:'particle_tracking', name:'6. Particle Tracking' },
            { id:'graph_theory', name:'7. Graph Theory' },
            { id:'integrated_analysis', name:'8. Integrated Analysis' },
            { id:'track_examiner', name:'9. Track Examiner' },
        ]},
        cornealia: { name:'Cornealia', short:'CORN', icon:'👁', iconLg:'👁', steps: [
            { id:'import', name:'1. Image Import' },
            { id:'segmentation', name:'2. Cell Segmentation' },
            { id:'morphometry', name:'3. Morphometric Analysis' },
        ]},
        cornealia_batch: { name:'Cornealia Batch', short:'CRNB', icon:'👁', iconLg:'👁', steps: [
            { id:'batch_setup', name:'1. Batch Setup' },
            { id:'batch_run', name:'2. Run Batch' },
            { id:'batch_results', name:'3. Results & Export' },
        ]},
        cellfade: { name:'CellFADE', short:'CFADE', icon:'🧫', iconLg:'🧫', steps: [
            { id:'import', name:'1. Data Import' },
            { id:'detection', name:'2. FA Detection (DL)' },
            { id:'analysis', name:'3. Analysis' },
        ]},
        cellvisia: { name:'CellVisia', short:'CVIS', icon: ICONS.cellvisia(14), iconLg: ICONS.cellvisia(18), steps: [
            { id:'source', name:'0. Source' },
            { id:'scope', name:'1. Scope' },
            { id:'imgproc', name:'2. Image Processing' },
            { id:'segment', name:'3. Segmentation' },
            { id:'advanced', name:'4. Advanced' },
            { id:'measure', name:'5. Measurement' },
            { id:'export', name:'6. Export' },
        ]},
        associa: { name:'Associa', short:'ASOC', icon: ICONS.associa(14), iconLg: ICONS.associa(18), steps: [
            { id:'source', name:'0. Source' },
            { id:'association', name:'1. Association' },
            { id:'preprocess', name:'2. Pre-processing' },
            { id:'surrogate', name:'3. Surrogate' },
            { id:'results', name:'4. Results' },
            { id:'export', name:'5. Export' },
        ]},
        cellade: { name:'CellADE', short:'CADE', icon: ICONS.cellade(14), iconLg: ICONS.cellade(18), steps: [
            { id:'source', name:'0. Source' },
            { id:'params', name:'1. Parameters' },
            { id:'run', name:'2. Run' },
            { id:'results', name:'3. Results' },
            { id:'export', name:'4. Export' },
        ]},
        cellfade: { name:'CellFADE', short:'CFDE', icon: ICONS.cellfade(14), iconLg: ICONS.cellfade(18), steps: [
            { id:'source', name:'0. Source' },
            { id:'params', name:'1. Parameters' },
            { id:'run', name:'2. Run' },
            { id:'results', name:'3. Results' },
            { id:'export', name:'4. Export' },
        ]},
        annotade: { name:'AnnotADE', short:'ANNT', icon: ICONS.annotade(14), iconLg: ICONS.annotade(18), steps: [
            { id:'source', name:'0. Source' },
            { id:'tools', name:'1. Tools' },
            { id:'assists', name:'2. Assists' },
            { id:'export', name:'3. Export' },
        ]},
    };
    return d[type] || { name:type, short:type.substring(0,4).toUpperCase(), icon:'📦', iconLg:'📦', steps:[] };
}

function getStepDef(moduleType, stepId) {
    const p = getPipelineDef(moduleType);
    // Module-level tab (no specific step) — used by standalone modules
    if (stepId == null) return { name: p.name, icon: p.icon };
    const s = p.steps.find(s => s.id === stepId);
    return { name: s ? s.name : stepId, icon: p.icon };
}

// ═════════════════════════════════════════════
// API HELPERS
// ═════════════════════════════════════════════

async function api(endpoint, method = 'GET', body = null) {
    const opts = { method, headers: {} };
    if (body) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(body);
    }
    const res = await fetch(`/api/${endpoint}`, opts);
    const data = await res.json();
    if (!data.success) {
        console.error(`API error [${endpoint}]:`, data.error);
        updateStatus(`❌ ${data.error}`);
    }
    return data;
}

// ═════════════════════════════════════════════
// SYSTEM MONITOR — Toolbar Gauges
// ═════════════════════════════════════════════

let _sysMonitorInterval = null;

function initGauges() {
    // Inject gauges into toolbar
    const toolbar = document.querySelector('.toolbar');
    if (!toolbar) return;

    const spacer = toolbar.querySelector('.toolbar-spacer');
    if (!spacer) return;

    // Create gauge container — insert after spacer (right side)
    const container = document.createElement('div');
    container.id = 'sysGauges';
    container.className = 'toolbar-gauges';
    container.innerHTML = `<div class="gauge-pair">
        ${buildGaugeSVG('cpu', 'CPU')}
        ${buildGaugeSVG('ram', 'RAM')}
    </div>`;

    spacer.parentNode.insertBefore(container, spacer.nextSibling);
    startSystemMonitor();
}

function buildGaugeSVG(id, label) {
    // LED bar: 10 segments that fill and change color based on usage
    let segs = '';
    for (let i = 0; i < 10; i++) {
        segs += `<div class="led-seg" id="${id}Seg${i}"></div>`;
    }
    return `<div class="led-gauge">
        <span class="led-label">${label}</span>
        <div class="led-bar-wrap">
            <div class="led-bar">${segs}</div>
            <div class="led-app-marker" id="${id}AppMarker"></div>
        </div>
        <span class="led-val" id="${id}GaugeVal">--</span>
    </div>`;
}

function describeArc() { /* legacy — unused */ }

function setNeedle() { /* legacy — unused */ }

function updateLedBar(id, sysPct, appPct) {
    const filled = Math.round(sysPct / 10);
    for (let i = 0; i < 10; i++) {
        const seg = document.getElementById(`${id}Seg${i}`);
        if (!seg) continue;
        if (i < filled) {
            seg.classList.add('on');
            if (i < 4) { seg.style.background = '#27ae60'; seg.style.boxShadow = '0 0 3px #27ae60'; }
            else if (i < 7) { seg.style.background = '#f39c12'; seg.style.boxShadow = '0 0 3px #f39c12'; }
            else { seg.style.background = '#e74c3c'; seg.style.boxShadow = '0 0 3px #e74c3c'; }
        } else {
            seg.classList.remove('on');
            seg.style.background = 'rgba(255,255,255,.08)';
            seg.style.boxShadow = 'none';
        }
    }

    // CelLAB app marker — small triangle under the bar at the app usage position
    const marker = document.getElementById(`${id}AppMarker`);
    if (marker && appPct !== undefined) {
        const pos = Math.min(appPct, 100) / 100 * 100;
        marker.style.left = `${pos}%`;
        marker.style.display = appPct > 0 ? 'block' : 'none';
    }
}

function startSystemMonitor() {
    if (_sysMonitorInterval) return;
    updateSystemMonitor();
    _sysMonitorInterval = setInterval(updateSystemMonitor, 3000);
}

async function updateSystemMonitor() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (!data.success || !data.data.system) return;

        const sys = data.data.system;

        // CPU LED bar — system total + CelLAB marker
        updateLedBar('cpu', sys.cpu_percent, sys.cellab_cpu || 0);
        const cpuVal = document.getElementById('cpuGaugeVal');
        if (cpuVal) {
            const appCpu = Math.round(sys.cellab_cpu || 0);
            cpuVal.innerHTML = `<span style="color:rgba(255,255,255,.7)">${Math.round(sys.cpu_percent)}%</span><span style="color:#3498db;font-size:8px;font-weight:800"> ${appCpu}%</span>`;
        }

        // RAM LED bar — system total + CelLAB marker
        updateLedBar('ram', sys.ram_percent, sys.cellab_ram_percent || 0);
        const ramVal = document.getElementById('ramGaugeVal');
        if (ramVal) {
            const appRam = Math.round(sys.cellab_ram_percent || 0);
            ramVal.innerHTML = `<span style="color:rgba(255,255,255,.7)">${Math.round(sys.ram_percent)}%</span><span style="color:#3498db;font-size:8px;font-weight:800"> ${appRam}%</span>`;
        }
    } catch (e) { /* silent */ }
}

// Initialize gauges on page load
document.addEventListener('DOMContentLoaded', initGauges);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    const tag = e.target.tagName;
    const inInput = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';

    // Ctrl+` — toggle console
    if (e.key === '`' && e.ctrlKey) { e.preventDefault(); _findOrCreateCodeChat(); return; }
    // Ctrl+S — save project
    if (e.key === 's' && e.ctrlKey && !e.shiftKey) { e.preventDefault(); saveProject(); return; }
    // Ctrl+Shift+N — new project
    if (e.key === 'N' && e.ctrlKey && e.shiftKey) { e.preventDefault(); newProject(); return; }
    // Ctrl+Shift+O — open project
    if (e.key === 'O' && e.ctrlKey && e.shiftKey) { e.preventDefault(); openProject(); return; }
    // F5 — run current step
    if (e.key === 'F5' && !e.ctrlKey) { e.preventDefault(); shortcutRunCurrentStep(); return; }
    // Ctrl+Shift+G — new Git terminal
    if (e.key === 'G' && e.ctrlKey && e.shiftKey) { e.preventDefault(); _findOrCreateCodeChat(); addConsoleTab('git').then(() => { _renderCodeChatTabs(); _renderCodeChatBody(); }); return; }
    // Ctrl+Shift+T — new Python terminal
    if (e.key === 'T' && e.ctrlKey && e.shiftKey) { e.preventDefault(); _findOrCreateCodeChat(); addConsoleTab('shared').then(() => { _renderCodeChatTabs(); _renderCodeChatBody(); }); return; }
    // Ctrl+Shift+E — toggle left panel (toolbox)
    if (e.key === 'E' && e.ctrlKey && e.shiftKey) { e.preventDefault(); shortcutToggleLeftPanel(); return; }
    // Ctrl+Shift+H — toggle version control panel
    if (e.key === 'H' && e.ctrlKey && e.shiftKey) { e.preventDefault(); toggleVersionPanel(); return; }
    // Ctrl+Shift+B — toggle console (alternate)
    if (e.key === 'B' && e.ctrlKey && e.shiftKey) { e.preventDefault(); _findOrCreateCodeChat(); return; }
    // Escape — close dialogs/menus
    if (e.key === 'Escape') { hideContextMenu(); closeModals(); return; }
    // Ctrl+Shift+/ — show shortcuts help
    if (e.key === '?' && e.ctrlKey && e.shiftKey) { e.preventDefault(); showShortcutsHelp(); return; }
});

function shortcutRunCurrentStep() {
    const ws = getActiveWorkspace();
    if (!ws) { updateStatus('No workspace active'); return; }
    const sub = ws.subtabs.get(ws.activeSubtab);
    if (!sub || sub.type !== 'module') { updateStatus('Open a module step first'); return; }
    doRunAnalysis(sub.moduleType, sub.stepId);
}

function shortcutToggleLeftPanel() {
    const lp = document.querySelector('.left-panel');
    if (!lp) return;
    if (lp.style.display === 'none') {
        lp.style.display = '';
        updateStatus('Toolbox shown');
    } else {
        lp.style.display = 'none';
        updateStatus('Toolbox hidden');
    }
}

function closeModals() {
    const overlays = document.querySelectorAll('.modal-overlay, #saveAsOverlay');
    overlays.forEach(o => o.remove());
    // Close browser overlay if open
    const browser = document.getElementById('browserOverlay');
    if (browser) browser.style.display = 'none';
}

function showShortcutsHelp() {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

    overlay.innerHTML = `
        <div class="modal-dialog" style="width:420px">
            <div class="modal-header">⌨ Keyboard Shortcuts</div>
            <div class="modal-body" style="padding:16px">
                <table class="shortcuts-table">
                    <tr class="shortcut-section"><td colspan="2">General</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>S</kbd></td><td>Save project</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd></td><td>New project</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>O</kbd></td><td>Open project</td></tr>
                    <tr><td><kbd>Escape</kbd></td><td>Close dialogs & menus</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>/</kbd></td><td>Show this help</td></tr>
                    <tr class="shortcut-section"><td colspan="2">Analysis</td></tr>
                    <tr><td><kbd>F5</kbd></td><td>Run current step</td></tr>
                    <tr class="shortcut-section"><td colspan="2">Console</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>\`</kbd></td><td>Toggle console</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>T</kbd></td><td>New Python terminal</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>G</kbd></td><td>New Git terminal</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd></td><td>Toggle console (alt)</td></tr>
                    <tr><td><kbd>↑</kbd> / <kbd>↓</kbd></td><td>Command history (in console)</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>L</kbd></td><td>Clear console (in console)</td></tr>
                    <tr class="shortcut-section"><td colspan="2">Panels</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>E</kbd></td><td>Toggle toolbox panel</td></tr>
                    <tr><td><kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>H</kbd></td><td>Toggle version history</td></tr>
                </table>
                <div style="text-align:right;margin-top:14px">
                    <button class="btn btn-default" onclick="this.closest('.modal-overlay').remove()">Close</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

// ═════════════════════════════════════════════
// STARTUP DIALOG
// ═════════════════════════════════════════════

function showStartupDialog() {
    document.getElementById('startupOverlay').style.display = 'flex';
    document.getElementById('startupBody').innerHTML = `
        <div class="startup-buttons">
            <button class="startup-btn" onclick="showNewProjectForm()">
                <div class="startup-btn-icon">+</div>
                <div class="startup-btn-label">New Project</div>
                <div class="startup-btn-desc">Create a new analysis project</div>
            </button>
            <button class="startup-btn" onclick="showOpenProjectForm()">
                <div class="startup-btn-icon">📂</div>
                <div class="startup-btn-label">Open Project</div>
                <div class="startup-btn-desc">Open an existing .cellab project</div>
            </button>
        </div>`;
}

function hideStartupDialog() {
    document.getElementById('startupOverlay').style.display = 'none';
}

function showNewProjectForm() {
    document.getElementById('startupBody').innerHTML = `
        <div class="form-group">
            <label class="form-group-label">Project Name</label>
            <input class="form-input" id="newProjectName" placeholder="e.g., FAK_Experiment_2026" style="width:100%;height:28px">
        </div>
        <div class="form-group">
            <label class="form-group-label">Author</label>
            <input class="form-input" id="newProjectAuthor" placeholder="Your name" style="width:100%;height:28px">
        </div>
        <div class="form-group">
            <label class="form-group-label">Description (optional)</label>
            <input class="form-input" id="newProjectDesc" placeholder="Brief description" style="width:100%;height:28px">
        </div>
        <div class="form-group">
            <label class="form-group-label">Save Location</label>
            <div style="display:flex;gap:6px">
                <input class="form-input" id="newProjectRoot" placeholder="Type path or click Browse..." style="flex:1;height:28px">
                <button class="btn btn-default" onclick="browseForFolder('newProjectRoot')">Browse</button>
            </div>
        </div>
        <div style="display:flex;gap:6px;margin-top:16px;justify-content:flex-end">
            <button class="btn btn-default" onclick="showStartupDialog()">Back</button>
            <button class="btn btn-primary" onclick="doCreateProject()">Create Project</button>
        </div>`;
    setTimeout(() => document.getElementById('newProjectName').focus(), 100);
}

function showOpenProjectForm() {
    state._openMode = true;
    browseForFolder('_openProject', '.cellab');
}

async function doCreateProject() {
    const name = document.getElementById('newProjectName').value.trim();
    const root = document.getElementById('newProjectRoot').value.trim();
    const author = document.getElementById('newProjectAuthor').value.trim();
    const desc = document.getElementById('newProjectDesc').value.trim();

    if (!name) { alert('Please enter a project name.'); return; }
    if (!root) { alert('Please select a save location.'); return; }

    updateStatus('Creating project...');
    const res = await api('project/create', 'POST', {
        root: root + '/' + name,
        name: name,
        author: author,
        description: desc,
    });

    if (res.success) {
        state._projectOpen = true;
        hideStartupDialog();
        await loadProjectState();
        updateStatus(`Project created: ${name}`);
    }
}

async function doOpenProject(path) {
    updateStatus('Opening project...');
    const res = await api('project/open', 'POST', { path: path });

    if (res.success) {
        state._projectOpen = true;
        hideStartupDialog();
        restoreFromState(res.data);
        updateStatus(`Opened: ${res.data.project.name}`);
    }
}

// ═════════════════════════════════════════════
// FILE BROWSER
// ═════════════════════════════════════════════

let _browserCallback = null;
let _browserCurrentPath = '';
let _browserSelectedPath = '';
let _browserFilter = '';
let _browserMode = 'folder'; // 'folder' or 'file'

async function browseForFolder(inputId, filter) {
    const isOpen = inputId === '_openProject';
    const mode = isOpen ? 'file' : 'folder';
    const title = isOpen ? 'Open CelLAB Project' : 'Select Folder';

    const body = { mode, title };
    if (isOpen) {
        body.filetypes = [['CelLAB Projects', '*.cellab'], ['All Files', '*.*']];
    }

    try {
        const res = await fetch('/api/browse_open', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!data.success || !data.path) return; // cancelled

        if (isOpen) {
            doOpenProject(data.path);
        } else {
            const el = document.getElementById(inputId);
            if (el) el.value = data.path;
        }
    } catch (e) {
        updateStatus(`Browse error: ${e.message}`);
    }
}

function getDefaultBrowsePath() {
    if (navigator.platform.startsWith('Win')) return 'C:/Users/' + (navigator.userAgent.match(/Windows NT/) ? '' : '');
    return '/home';
}

function closeBrowser() {
    document.getElementById('browserOverlay').style.display = 'none';
}

function browserGo() {
    const path = document.getElementById('browserPathInput').value.trim();
    if (path) loadBrowserPath(path);
}

async function loadBrowserPath(path) {
    _browserCurrentPath = path;
    _browserSelectedPath = '';
    document.getElementById('browserPathInput').value = path;
    document.getElementById('browserSelected').textContent =
        _browserMode === 'folder' ? `Current: ${path}` : '';
    document.getElementById('browserList').innerHTML = '<p class="placeholder-text">Loading...</p>';

    const res = await api('browse', 'POST', {
        path: path,
        filter: _browserFilter,
    });

    if (!res.success) {
        document.getElementById('browserList').innerHTML =
            `<p class="placeholder-text" style="color:var(--status-error)">${res.error}</p>`;
        return;
    }

    const items = res.data.items || [];
    const list = document.getElementById('browserList');

    if (items.length === 0) {
        list.innerHTML = '<p class="placeholder-text">Empty folder</p>';
        return;
    }

    list.innerHTML = items.map(item => {
        const icon = item.is_dir ? '📁' : '📄';
        const size = item.is_dir ? '' : formatBytes(item.size_bytes || 0);
        const isCellab = item.name.endsWith('.cellab') && !item.is_dir;
        // Escape backslashes and quotes for safe inline JS
        const safePath = item.path.replace(/\\/g, '/');
        return `<div class="browser-item ${isCellab ? 'cellab-file' : ''}"
                     data-path="${safePath}" data-isdir="${item.is_dir}"
                     onclick="browserSelect(this)"
                     ondblclick="browserDblClick(this)">
            <span class="browser-item-icon">${icon}</span>
            <span class="browser-item-name">${item.name}</span>
            <span class="browser-item-size">${size}</span>
        </div>`;
    }).join('');
}

function browserSelect(el) {
    document.querySelectorAll('.browser-item').forEach(i => i.classList.remove('selected'));
    el.classList.add('selected');
    _browserSelectedPath = el.dataset.path;
    document.getElementById('browserSelected').textContent = _browserSelectedPath;
}

function browserDblClick(el) {
    const path = el.dataset.path;
    const isDir = el.dataset.isdir === 'true';
    if (isDir) {
        loadBrowserPath(path);
    } else if (path.endsWith('.cellab')) {
        closeBrowser();
        if (_browserCallback) _browserCallback(path);
    }
}

function browserUp() {
    const parts = _browserCurrentPath.replace(/\\/g, '/').split('/').filter(Boolean);
    if (parts.length > 1) {
        parts.pop();
        let newPath = parts.join('/');
        // Windows drive root needs trailing slash
        if (newPath.length === 2 && newPath[1] === ':') newPath += '/';
        loadBrowserPath(newPath);
    }
}

function browserConfirm() {
    let path;
    if (_browserMode === 'folder') {
        // For folder selection: use selected folder or current directory
        path = _browserSelectedPath || _browserCurrentPath;
    } else {
        // For file selection: must have selected a file
        path = _browserSelectedPath;
        if (!path) {
            alert('Please select a file.');
            return;
        }
    }
    closeBrowser();
    if (_browserCallback) _browserCallback(path);
}

function formatBytes(bytes) {
    if (bytes === 0) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

// ═════════════════════════════════════════════
// SAVE / LOAD / CLOSE PROJECT
// ═════════════════════════════════════════════

async function saveProject() {
    // Save GUI state first
    const guiState = buildGuiState();
    await api('gui/state', 'POST', guiState);
    // Then save project
    const res = await api('project/save', 'POST');
    if (res.success) updateStatus('Project saved');
}

async function loadProjectState() {
    const res = await api('project/state', 'GET');
    if (res.success) {
        restoreFromState(res.data);
    }
}

function buildGuiState() {
    const ws = getActiveWorkspace();
    return {
        active_workspace: state.activeWorkspace,
        left_panel_width: document.getElementById('leftPanel')?.offsetWidth || 240,
        right_panel_width: document.getElementById('rightPanel')?.offsetWidth || 200,
        collapsed_groups: [...state.collapsedGroups],
        focused_groups: [...state.focusedGroups.entries()],
        workspace_states: buildWorkspaceStates(),
    };
}

function buildWorkspaceStates() {
    const out = {};
    for (const [wsId, ws] of state.workspaces) {
        out[wsId] = {
            active_subtab_type: ws.subtabs.get(ws.activeSubtab)?.type || 'canvas',
            active_subtab_pipeline: ws.subtabs.get(ws.activeSubtab)?.pipelineId || null,
            active_subtab_step: ws.subtabs.get(ws.activeSubtab)?.stepId || null,
            open_subtabs: [...ws.subtabs.values()]
                .filter(s => s.type === 'module')
                .map(s => ({ pipelineId: s.pipelineId, stepId: s.stepId })),
        };
    }
    return out;
}

function restoreFromState(fullState) {
    // Clear current state
    state.workspaces.clear();
    state.wsCounter = 0;
    state.moduleCounter = 0;
    state.subtabCounter = 0;
    state.collapsedGroups.clear();

    const proj = fullState.project;
    const gui = fullState.gui_state || {};

    // Restore collapsed groups
    (gui.collapsed_groups || []).forEach(g => state.collapsedGroups.add(g));

    // Restore focused groups
    state.focusedGroups.clear();
    (gui.focused_groups || []).forEach(([k, v]) => state.focusedGroups.set(k, v));

    // Restore workspaces
    for (const wsData of fullState.workspaces) {
        state.wsCounter++;
        const wsId = wsData.id || `ws-${state.wsCounter}`;

        // Create canvas subtab
        state.subtabCounter++;
        const canvasSubId = `subtab-${state.subtabCounter}`;

        const ws = {
            id: wsId,
            name: wsData.name,
            type: 'workspace',
            subtabs: new Map(),
            pipelines: new Map(),
            activeSubtab: canvasSubId,
        };

        ws.subtabs.set(canvasSubId, {
            id: canvasSubId, type: 'canvas', label: 'Home',
            icon: '◈', pipelineId: null, stepId: null, closeable: false,
        });

        // Restore pipelines
        for (const pData of wsData.pipelines || []) {
            state.moduleCounter++;
            const pid = pData.id;
            const def = getPipelineDef(pData.type);

            ws.pipelines.set(pid, {
                id: pid,
                type: pData.type,
                name: pData.name,
                shortName: pid,
                steps: def.steps.map(s => ({
                    ...s,
                    status: pData.steps?.[s.id]?.status || 'idle',
                })),
                x: pData.canvas_position?.x || 0,
                y: pData.canvas_position?.y || 0,
            });
        }

        // On reopen: only Canvas/Home is open. User opens steps manually.

        state.workspaces.set(wsId, ws);
    }

    // Set active workspace
    if (gui.active_workspace && state.workspaces.has(gui.active_workspace)) {
        state.activeWorkspace = gui.active_workspace;
    } else {
        state.activeWorkspace = state.workspaces.keys().next().value;
    }

    // Update status bar
    document.getElementById('statusWorkspace').textContent =
        state.workspaces.get(state.activeWorkspace)?.name || '';

    renderAll();
    updateStatus(`Loaded: ${proj.name}`);
}

// ═════════════════════════════════════════════
// WIRE GUI ACTIONS TO API
// ═════════════════════════════════════════════

// Sync pipeline creation to backend after GUI creates it
async function syncPipelineToBackend(ws, pipeline) {
    if (!state._projectOpen) return;
    await api('pipeline/create', 'POST', {
        workspace_id: ws.id,
        type: pipeline.type,
        name: pipeline.name,
        pipeline_id: pipeline.id,
    });
    await api(`pipeline/${ws.id}/${pipeline.id}/position`, 'POST', {
        x: pipeline.x, y: pipeline.y,
    });
}

// ═════════════════════════════════════════════
// PARAMS AUTO-SAVE (debounced)
// ═════════════════════════════════════════════

let _saveTimer = null;

function debouncedSaveParams(formEl) {
    if (_saveTimer) clearTimeout(_saveTimer);
    _saveTimer = setTimeout(() => saveFormParams(formEl), 800);
}

function collectFormParams(formEl) {
    const params = {};
    formEl.querySelectorAll('[data-param]').forEach(el => {
        const key = el.dataset.param;
        if (el.type === 'number') params[key] = parseFloat(el.value) || 0;
        else if (el.type === 'checkbox') params[key] = el.checked;
        else params[key] = el.value;
    });
    return params;
}

function saveFormParams(formEl) {
    if (!state._projectOpen) return;
    const moduleType = formEl.dataset.module;
    const stepId = formEl.dataset.step;
    const section = formEl.dataset.section;
    const params = collectFormParams(formEl);

    // Find which workspace and pipeline this belongs to
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    if (!sub || sub.type !== 'module') return;

    const pipelineId = sub.pipelineId;

    // Save to backend — we namespace by section so all sections accumulate
    api(`step/${ws.id}/${pipelineId}/${stepId}/params`, 'POST', {
        params: { [section]: params },
    });

    updateStatus(`Saved ${section} params`);
}

function populateFormFromParams(formEl, savedParams) {
    if (!savedParams) return;
    const section = formEl.dataset.section;
    const sectionParams = savedParams[section] || {};

    formEl.querySelectorAll('[data-param]').forEach(el => {
        const key = el.dataset.param;
        if (key in sectionParams) {
            if (el.type === 'checkbox') el.checked = sectionParams[key];
            else el.value = sectionParams[key];
        }
    });
}

// ═════════════════════════════════════════════
// LOAD PARAMS FROM BACKEND (on tab open)
// ═════════════════════════════════════════════

async function loadParamsForModule(wsId, pipelineId, stepId) {
    if (!state._projectOpen) return null;
    const res = await api(`step/${wsId}/${pipelineId}/${stepId}/params`);
    if (res.success) return res.data;
    return null;
}

async function populateModuleSettings(subId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub || sub.type !== 'module') return;

    // CellVisia uses 'cellvisia' as virtual step; others use sub.stepId
    const effectiveStep = sub.moduleType === 'cellvisia' ? 'cellvisia'
        : sub.moduleType === 'cellade' ? 'cellade'
        : sub.moduleType === 'associa' ? 'associa'
        : sub.moduleType === 'cellfade' ? 'cellfade'
        : sub.moduleType === 'annotade' ? 'annotade'
        : sub.stepId;
    const saved = await loadParamsForModule(ws.id, sub.pipelineId, effectiveStep);
    if (!saved) return;

    // Store on subtab for later use
    sub._loadedParams = saved;

    // CellVisia: trigger full backend + frontend restore
    if (sub.moduleType === 'cellvisia' && !sub._cvLoadInfo) {
        const cv = saved.cellvisia;
        if (cv?.cvState?.filePath) {
            sub._cvState = cv.cvState;
            sub._cvRestoreAttempted = false;
            cvRestoreState();
        }
    }

    // CellADE: restore state
    if (sub.moduleType === 'cellade' && !sub._cdState?.filePath) {
        if (saved._cdState?.filePath) {
            sub._cdState = saved._cdState;
        }
    }

    // Associa: restore state
    if (sub.moduleType === 'associa' && !sub._asState?.filePath) {
        if (saved._asState?.filePath) {
            sub._asState = saved._asState;
        }
    }

    // CellFADE: restore state
    if (sub.moduleType === 'cellfade' && !sub._cfState?.filePath) {
        if (saved._cfState?.filePath) {
            sub._cfState = saved._cfState;
        }
    }

    // AnnotADE: restore state
    if (sub.moduleType === 'annotade' && !sub._anState?.filePath) {
        if (saved._anState?.filePath) {
            sub._anState = saved._anState;
        }
    }

    // Populate current form if visible
    const form = document.querySelector(`#settingsBody-${subId} .settings-form`);
    if (form) populateFormFromParams(form, saved);
}

// Map plotter output filenames back to plot type IDs
const PLOT_FILENAME_MAP = {
    // Cornealia — single image plotter
    '01_segmentation_overview': 'segmentation',
    '02_radial_distribution':   'radial_distribution',
    '03_potential_Vr':          'potential',
    '04_morse_fit':             'fitting',
    '04_quadratic_fit':         'fitting',
    '05_comprehensive':         'comprehensive',
    '06_publication_gr':        'publication_gr',
    '07_publication_vr':        'publication_vr',
    'pipeline_figure':          'pipeline_figure',
    // Cornealia — batch plotter
    '01_distributions':         'distributions',
    '01_K_um_histogram':        'histogram',
    '02_as_vs_bs_boxplots':     'as_vs_bs_boxplots',
    '03_as_vs_bs_scatter':      'as_vs_bs_scatter',
    '04_as_vs_bs_histograms':   'as_vs_bs_histograms',
    '07_validation_scatter':    'validation_scatter',
    '08_validation_bland_altman': 'validation_bland_altman',
    '06_K_um_deep_dive':        'deep_dive',
    'fig2_as_vs_bs_boxplots':   'pub_boxplots',
    'fig3_K_deep_dive':         'pub_K_deep_dive',
    'fig4_validation':          'pub_validation',
    'fig6_K_independence':      'pub_K_independence',
    // FASTIA — import
    'frame_montage':            'frame_montage',
    // FASTIA — detection
    'detection_montage':        'detection_montage',
    'cellmask_montage':         'cellmask_montage',
    // FASTIA — tracking
    'track_length_distribution': 'track_length_dist',
    'track_displacement':       'track_displacement',
    'track_lifetime_map':       'track_lifetime_map',
    'track_summary':            'track_summary',
    // FASTIA — classification
    'group_distribution':       'group_distribution',
    'feature_heatmap':          'feature_heatmap',
    'discriminability':         'discriminability',
    'class_summary':            'class_summary',
    // FASTIA — kinetics
    'rate_distributions':       'rate_distributions',
    'rates_by_group':           'rates_by_group',
    'assembly_vs_disassembly':  'assembly_vs_disassembly',
    'time_to_peak':             'time_to_peak',
    'rate_quality':             'rate_quality',
    'fa_area_distribution':     'fa_area_distribution',
    'intensity_spaghetti_start':'intensity_spaghetti',
    'intensity_spaghetti_peak': 'intensity_spaghetti_peak',
    // Association: handled by runs-based discovery, not file-based
    // IMMUNIA — segmentation
    'seg_overview':       'seg_overview',
    'seg_masks_frame':    'seg_masks_frame',
    'seg_composite':      'seg_composite',
    'seg_timeline':       'seg_timeline',
    'seg_area_timeline':  'seg_area_timeline',
    // IMMUNIA — tracking
    'trajectories':       'trajectories',
    'trajectories_with_quality': 'trajectories_with_quality',
    'track_length':       'track_length',
    'velocity_dist':      'velocity_dist',
    'msd':                'msd',
    'enhanced_histograms':'enhanced_histograms',
    'quality_dashboard':  'quality_dashboard',
    'spatial_metrics':    'spatial_metrics',
    'trajectory_animation': 'trajectory_animation',
    // IMMUNIA — signal association (per-run, not file-based)
    // IMMUNIA — particle tracking
    'motion_dynamics':   'motion_dynamics',
    'spatial_tumor':     'spatial_tumor',
    'before_after':      'before_after',
    'pt_motion_classes': 'pt_motion_classes',
    'pt_msd':            'pt_msd',
    'pt_speed_dist':     'pt_speed_dist',
    'pt_spatial':        'pt_spatial',
    'pt_params_tumor':   'pt_params_tumor',
    'pt_params_tissue':  'pt_params_tissue',
    'pt_revisit':        'pt_revisit',
    'pt_contact_entry':  'pt_contact_entry',
    'pt_msd_curves':     'pt_msd_curves',
    'pt_eulerian':       'pt_eulerian',
    'pt_eulerian_tumor': 'pt_eulerian_tumor',
    'pt_gr_fields':      'pt_gr_fields',
    'pt_gr_heatmap':     'pt_gr_heatmap',
    // IMMUNIA — keller-segel
    'ks_fields':        'ks_fields',
    'ks_correlation':   'ks_correlation',
    'ks_density':       'ks_density',
    'ks_presence':      'ks_presence',
    'ks_overlay':       'ks_overlay',
    // IMMUNIA — graph theory
    'gt_comprehensive':     'gt_comprehensive',
    'gt_metrics':           'gt_metrics',
    'gt_regions':           'gt_regions',
    'gt_boundary':          'gt_boundary',
    'gt_distance_pairs':    'gt_distance_pairs',
    'gt_metric_fields':     'gt_metric_fields',
    'gt_node_distributions':'gt_node_distributions',
    'gt_comparative':       'gt_comparative',
    'comprehensive':      'comprehensive',
    'influence_matrix':   'influence_matrix',
    'distribution':       'distribution',
    'significance':       'significance',
    'comparison':         'comparison',
};

// For filenames with frame suffixes (e.g. detection_frame_0, track_trajectories_5)
const PLOT_PREFIX_MAP = {
    'detection_frame':   'detection_frame',
    'cellmask_frame':    'cellmask_frame',
    'track_trajectories': 'track_trajectories',
    'indiv_track':       'indiv_track',
    'exam_detail':       'exam_detail',
    'exam_dynamic':      'exam_dynamic',
};

async function discoverExistingResults(subId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub || sub.type !== 'module') return;
    if (!state._projectOpen) return;
    if (!stepHasResults(sub.moduleType, sub.stepId)) return;

    // Always re-discover from disk (results may change between saves/refreshes)
    sub.insertedResults = [];

    // Association: skip standard file discovery, use runs-based discovery only
    if (sub.moduleType === 'fastia' && sub.stepId === 'association') {
        discoverAssociationRuns(sub);
        return;
    }
    if (sub.moduleType === 'immunia' && sub.stepId === 'signal_association') {
        discoverIMMUNIAAssocRuns(sub);
        return;
    }
    if (sub.moduleType === 'immunia' && sub.stepId === 'graph_theory') {
        discoverGTRuns(sub);
        return;
    }

    // Get existing result files from backend
    const res = await api(`step/${ws.id}/${sub.pipelineId}/${sub.stepId}/results`);
    const files = (res.success && res.data.length) ? res.data : [];

    // For batch_results, also check batch_run step
    if (sub.moduleType === 'cornealia_batch' && sub.stepId === 'batch_results') {
        const runRes = await api(`step/${ws.id}/${sub.pipelineId}/batch_run/results`);
        if (runRes.success && runRes.data.length) {
            files.push(...runRes.data);
        }
    }

    if (files.length === 0) return;

    // Discover batch CSV
    const csvFiles = files.filter(r => r.name === 'batch_results.csv');
    if (csvFiles.length > 0 && !sub.insertedResults.find(r => r.plotType === 'batch_table')) {
        sub.insertedResults.push({
            plotType: 'batch_table', label: 'Results Table', icon: '📊',
            url: '_table_', status: 'done',
        });
    }

    // Discover plot images
    const images = files.filter(r => 
        ['.png', '.jpg'].includes(r.type) && 
        r.relative.replace(/\\/g, '/').startsWith('plots/')
    );

    // Also discover video files
    const videos = files.filter(r =>
        ['.mp4', '.webm', '.avi'].includes(r.type) &&
        r.relative.replace(/\\/g, '/').startsWith('plots/')
    );

    const available = getAvailablePlots(sub.moduleType, sub.stepId);

    // Process videos first (they take priority over static previews)
    for (const vid of videos) {
        const baseName = vid.name.replace(/\.(mp4|webm|avi)$/i, '');
        const plotType = PLOT_FILENAME_MAP[baseName];
        if (!plotType) continue;
        const plotDef = available.find(p => p.id === plotType);
        if (!plotDef) continue;
        if (sub.insertedResults.find(r => r.plotType === plotType)) continue;
        sub.insertedResults.push({
            plotType, label: plotDef.label, icon: plotDef.icon,
            url: vid.url, status: 'done',
        });
    }

    for (const img of images) {
        const baseName = img.name.replace(/\.(png|jpg|jpeg)$/i, '');

        // Exact match first
        let plotType = PLOT_FILENAME_MAP[baseName];
        let plotDef = null;
        let isPrefix = false;

        // Prefix match for frame-numbered files (e.g. detection_frame_0, indiv_track_39)
        if (!plotType) {
            for (const [prefix, pType] of Object.entries(PLOT_PREFIX_MAP)) {
                if (baseName.startsWith(prefix)) {
                    plotType = baseName;  // Use full name as plotType (unique per file)
                    isPrefix = true;
                    break;
                }
            }
        }

        if (!plotType) continue;

        // For prefix matches (individual tracks, frame plots), build plotDef dynamically
        if (isPrefix) {
            if (baseName.startsWith('indiv_track_')) {
                const trackNum = baseName.replace('indiv_track_', '');
                plotDef = { id: plotType, label: `Track ${trackNum}`, icon: '🔬' };
            } else if (baseName.startsWith('exam_detail_')) {
                const trackNum = baseName.replace('exam_detail_', '');
                plotDef = { id: plotType, label: `Track ${trackNum}`, icon: '🔬' };
            } else if (baseName.startsWith('track_trajectories_')) {
                const frameNum = baseName.replace('track_trajectories_', '');
                plotDef = { id: plotType, label: `Trajectories (f${frameNum})`, icon: '🖼' };
            } else if (baseName.startsWith('detection_frame_')) {
                const frameNum = baseName.replace('detection_frame_', '');
                plotDef = { id: plotType, label: `Detection (f${frameNum})`, icon: '🖼' };
            } else if (baseName.startsWith('cellmask_frame_')) {
                const frameNum = baseName.replace('cellmask_frame_', '');
                plotDef = { id: plotType, label: `Cell Mask (f${frameNum})`, icon: '🖼' };
            }
        } else {
            plotDef = available.find(p => p.id === plotType);
        }

        if (!plotDef) continue;

        // Skip if already discovered
        if (sub.insertedResults.find(r => r.plotType === plotType)) continue;

        sub.insertedResults.push({
            plotType: plotType,
            label: plotDef.label,
            icon: plotDef.icon,
            url: img.url,
            status: 'done',
        });
    }

    // Discover dynamic viewer markers (.json files in plots/)
    const jsonFiles = files.filter(r =>
        r.type === '.json' &&
        r.relative.replace(/\\/g, '/').startsWith('plots/') &&
        r.name.startsWith('exam_dynamic_')
    );
    for (const jf of jsonFiles) {
        const trackNum = jf.name.replace('exam_dynamic_', '').replace('.json', '');
        const plotType = `exam_dynamic_${trackNum}`;
        if (sub.insertedResults.find(r => r.plotType === plotType)) continue;
        sub.insertedResults.push({
            plotType: plotType,
            label: `Track ${trackNum} 🔍`,
            icon: '🔍',
            url: null,
            status: 'done',
            isDynamic: true,
            trackId: parseInt(trackNum),
        });
    }

    // Re-render tree if we added anything
    if (sub.insertedResults.length > 0) {
        renderModuleTree(sub);
    }
}

// ═════════════════════════════════════════════
// RUN ANALYSIS
// ═════════════════════════════════════════════

function renderPipelineBoard(board) {
    const icons = { idle: '⚪', running: '🟡', done: '🟢', failed: '🔴', skipped: '⚫', locked: '🔒' };
    // Use ordered step IDs from the board
    const orderedIds = ['load', 'preprocess', 'segment', 'metrics', 'gr', 'quality', 'fitting', 'force'];
    let html = `<div class="pipeline-board">`;
    html += `<div class="pb-header">Pipeline Status — ${board.completed}/${board.total} complete</div>`;

    let stepNum = 0;
    for (const stepId of orderedIds) {
        const step = board.steps[stepId];
        if (!step) continue;
        stepNum++;

        const status = step.status || 'idle';
        const icon = icons[status] || '⚪';
        const timeStr = step.time != null && status === 'done' ? `<span class="pb-time">${step.time}s</span>` : '';
        const errorStr = step.error ? `<span class="pb-error">${step.error}</span>` : '';

        let outputsStr = '';
        if (step.outputs && Object.keys(step.outputs).length > 0 && status === 'done') {
            outputsStr = Object.entries(step.outputs)
                .map(([k, v]) => `<span class="pb-val"><span class="pb-key">${k}</span>${v}</span>`)
                .join('');
        }

        html += `<div class="pb-step pb-${status}">`;
        html += `<span class="pb-num">${stepNum}</span>`;
        html += `<span class="pb-icon">${icon}</span>`;
        html += `<span class="pb-name">${step.name}</span>`;
        html += timeStr;
        html += `<span class="pb-outputs">${outputsStr}</span>`;
        html += errorStr;
        html += `</div>`;
    }

    html += `</div>`;
    return html;
}

function renderBatchBoard(b) {
    const isDone = b.status === 'done';
    const pct = b.pct || 0;
    const barColor = isDone ? 'var(--status-ok)' : b.failed > 0 ? 'var(--status-warning)' : 'var(--brand-accent)';

    // Format time
    const fmtTime = (s) => {
        if (s == null || s === 0) return '0s';
        if (s < 60) return `${Math.round(s)}s`;
        if (s < 3600) return `${Math.floor(s/60)}m ${Math.round(s%60)}s`;
        return `${Math.floor(s/3600)}h ${Math.floor((s%3600)/60)}m`;
    };

    let html = `<div class="batch-board">`;
    html += `<div class="bb-header">${isDone ? '✅ Batch Complete' : '⏳ Batch Processing'}</div>`;

    // Progress bar
    html += `<div class="bb-progress-bar"><div class="bb-progress-fill" style="width:${pct}%;background:${barColor}"></div></div>`;

    // Stats grid
    html += `<div class="bb-stats">`;
    html += `<div class="bb-stat"><span class="bb-stat-val">${b.completed}</span><span class="bb-stat-label">/ ${b.total}</span></div>`;
    html += `<div class="bb-stat bb-stat-ok"><span class="bb-stat-val">${b.succeeded}</span><span class="bb-stat-label">succeeded</span></div>`;
    html += `<div class="bb-stat bb-stat-fail"><span class="bb-stat-val">${b.failed}</span><span class="bb-stat-label">failed</span></div>`;
    html += `<div class="bb-stat"><span class="bb-stat-val">${fmtTime(b.elapsed)}</span><span class="bb-stat-label">elapsed</span></div>`;
    if (!isDone) {
        html += `<div class="bb-stat"><span class="bb-stat-val">${fmtTime(b.eta)}</span><span class="bb-stat-label">remaining</span></div>`;
        html += `<div class="bb-stat"><span class="bb-stat-val">${b.rate}</span><span class="bb-stat-label">img/s</span></div>`;
    }
    html += `</div>`;

    // Current image
    if (!isDone && b.current_image) {
        html += `<div class="bb-current">📷 ${b.current_image}</div>`;
    }

    // Summary stats (only when done)
    if (isDone && (b.K_mean || b.n_cells_mean)) {
        html += `<div class="bb-summary">`;
        if (b.K_mean !== 'N/A') html += `<span class="bb-summary-item">K̄ = ${b.K_mean}</span>`;
        if (b.K_std !== 'N/A') html += `<span class="bb-summary-item">σ(K) = ${b.K_std}</span>`;
        if (b.n_cells_mean !== 'N/A') html += `<span class="bb-summary-item">n̄_cells = ${b.n_cells_mean}</span>`;
        html += `</div>`;
    }

    html += `</div>`;
    return html;
}

function _persistRunLog(sub, moduleType, stepId, html) {
    if (!sub) return;
    if (!sub._runLogs) sub._runLogs = {};
    sub._runLogs[`${moduleType}-${stepId}`] = html;
    // Also update DOM if visible
    const el = document.getElementById(`runLog-${moduleType}-${stepId}`);
    if (el) el.innerHTML = html;
}

async function _loadSavedRunLog(sub, moduleType, stepId) {
    // Try loading run_log.json from the results dir
    if (!sub || !sub.pipelineId) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    try {
        const res = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/${stepId}/results/run_log.json`);
        if (res.ok) {
            const data = await res.json();
            if (data.log_html) {
                if (!sub._runLogs) sub._runLogs = {};
                const key = `${moduleType}-${stepId}`;
                // Only restore if no in-memory state yet
                if (!sub._runLogs[key]) {
                    sub._runLogs[key] = data.log_html;
                    const el = document.getElementById(`runLog-${moduleType}-${stepId}`);
                    if (el) el.innerHTML = data.log_html;
                }
            }
        }
    } catch (e) { /* no saved log, fine */ }
}

async function doRunAnalysis(moduleType, stepId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    if (!sub) return;
    const pipelineId = sub.pipelineId;

    // ── Collect current form params before running ──
    _collectCurrentParams(ws);

    // ── Merge all local params across tree items into one object ──
    const allParams = {};
    if (sub._localParams) {
        for (const [itemId, params] of Object.entries(sub._localParams)) {
            Object.assign(allParams, params);
        }
    }

    // Get pipeline name for task manager
    const pipeline = ws.pipelines.get(pipelineId);
    const pipelineName = pipeline?.name || pipelineId;

    // Create task
    const task = createTask(pipelineName, stepId, pipelineId, stepId);
    const taskKey = `${ws.id}/${pipelineId}/${stepId}`;

    // Initialize run log with progress bar
    let logHtml = `
        <div style="color:var(--status-running);margin-bottom:6px">▶ Starting ${stepId}...</div>
        <div class="run-progress-bar"><div class="run-progress-fill" id="runProgressFill-${moduleType}-${stepId}" style="width:0%"></div></div>
        <div id="runProgressLabel-${moduleType}-${stepId}" style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:4px;max-height:200px;overflow-y:auto">Initializing...</div>
    `;
    _persistRunLog(sub, moduleType, stepId, logHtml);

    // Update step status on canvas
    updateStepStatus(pipelineId, stepId, 'running');
    updateStatus(`Running ${moduleType} → ${stepId}...`);

    // Enable stop button
    const stopBtn = document.getElementById(`stopBtn-${moduleType}-${stepId}`);
    if (stopBtn) { stopBtn.disabled = false; stopBtn.style.opacity = ''; stopBtn.style.cursor = ''; stopBtn.style.color = 'var(--status-error)'; }

    // Fire the run request (returns immediately with task_key)
    const startRes = await api(`step/${ws.id}/${pipelineId}/${stepId}/run`, 'POST', allParams);

    if (!startRes.success) {
        logHtml += `<div style="color:var(--status-error)">✗ Failed to start: ${startRes.error}</div>`;
        _persistRunLog(sub, moduleType, stepId, logHtml);
        updateStepStatus(pipelineId, stepId, 'error');
        completeTask(task.id, 'error', startRes.error);
        return;
    }

    if (startRes.data.status === 'already_running') {
        logHtml += `<div style="color:var(--status-warning)">⚠ Already running</div>`;
        _persistRunLog(sub, moduleType, stepId, logHtml);
        return;
    }

    // ── Poll for progress ──
    const pollInterval = 400; // ms
    const poll = async () => {
        try {
            const res = await fetch('/api/tasks/progress', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: taskKey}),
            });
            const data = (await res.json()).data;

            if (data.done && data.result) {
                // ── COMPLETED / CANCELLED / ERROR ──
                const result = data.result;
                const outputs = result.outputs || {};

                // Disable stop button
                const _stopBtn = document.getElementById(`stopBtn-${moduleType}-${stepId}`);
                if (_stopBtn) { _stopBtn.disabled = true; _stopBtn.style.opacity = '0.4'; _stopBtn.style.cursor = 'default'; _stopBtn.style.color = ''; }

                // Update progress bar
                const fillEl = document.getElementById(`runProgressFill-${moduleType}-${stepId}`);
                const labelEl = document.getElementById(`runProgressLabel-${moduleType}-${stepId}`);

                if (result.status === 'cancelled') {
                    if (fillEl) fillEl.style.background = 'var(--status-warning)';
                    if (labelEl) labelEl.textContent = outputs.message || 'Cancelled';
                    logHtml += `<div style="color:var(--status-warning);margin-top:6px">⏹ Cancelled</div>`;
                    if (outputs.message) logHtml += `<div style="opacity:.7">${outputs.message}</div>`;
                    _persistRunLog(sub, moduleType, stepId, logHtml);
                    updateStepStatus(pipelineId, stepId, 'error');
                    updateStatus(`⏹ ${moduleType} → ${stepId}: cancelled`);
                    completeTask(task.id, 'error', 'Cancelled by user', result.log || '');
                } else if (result.status !== 'error') {
                    if (fillEl) fillEl.style.width = '100%';
                    if (labelEl) labelEl.textContent = outputs.message || 'Done';
                    logHtml += `<div style="color:var(--status-ok);margin-top:6px">✓ Completed</div>`;
                    logHtml += `<div style="opacity:.5">${result.results_dir || ''}</div>`;

                    // Render pipeline status board if available
                    if (outputs.batch_board) {
                        logHtml += renderBatchBoard(outputs.batch_board);
                    } else if (outputs.pipeline_board) {
                        logHtml += renderPipelineBoard(outputs.pipeline_board);
                    } else {
                        for (const [k, v] of Object.entries(outputs)) {
                            if (k !== 'message' && k !== 'plots' && k !== 'pipeline_board') {
                                logHtml += `<div style="opacity:.7">${k}: ${v}</div>`;
                            }
                        }
                    }
                    _persistRunLog(sub, moduleType, stepId, logHtml);
                    updateStepStatus(pipelineId, stepId, 'done');
                    updateStatus(`Done: ${moduleType} → ${stepId}`);
                    completeTask(task.id, 'done', null, result.log || '');
                    // Invalidate this step's existing plots + downstream
                    invalidateStaleResults(ws, pipelineId, stepId, moduleType);
                    loadAvailableResults(ws.id, pipelineId, stepId, moduleType, true);
                    // Discover association runs
                    if (stepId === 'association') {
                        sub._resultsDiscovered = false;
                        setTimeout(() => discoverAssociationRuns(sub), 500);
                    }
                    if (stepId === 'signal_association' && moduleType === 'immunia') {
                        setTimeout(() => discoverIMMUNIAAssocRuns(sub), 500);
                    }
                    if (stepId === 'graph_theory' && moduleType === 'immunia') {
                        setTimeout(() => discoverGTRuns(sub), 500);
                    }
                } else {
                    if (fillEl) fillEl.style.width = '100%';
                    if (fillEl) fillEl.style.background = 'var(--status-error)';
                    const errMsg = result.error_msg || 'Unknown error';
                    if (labelEl) labelEl.textContent = errMsg;
                    logHtml += `<div style="color:var(--status-error);margin-top:6px">✗ Error: ${errMsg}</div>`;
                    _persistRunLog(sub, moduleType, stepId, logHtml);
                    updateStepStatus(pipelineId, stepId, 'error');
                    updateStatus(`❌ ${moduleType} → ${stepId}`);
                    completeTask(task.id, 'error', errMsg, result.log || '');
                }

                // Save to backend for cross-session persistence
                _saveRunLogToBackend(ws.id, pipelineId, stepId, logHtml);
                return; // Stop polling
            }

            // ── IN PROGRESS ──
            if (data.progress) {
                const p = data.progress;
                const fillEl = document.getElementById(`runProgressFill-${moduleType}-${stepId}`);
                const labelEl = document.getElementById(`runProgressLabel-${moduleType}-${stepId}`);
                if (fillEl) fillEl.style.width = `${p.pct || 0}%`;

                // Render pipeline board or batch board if available (real-time)
                if (p.batch_board && labelEl) {
                    labelEl.innerHTML = renderBatchBoard(p.batch_board);
                } else if (p.pipeline_board && labelEl) {
                    labelEl.innerHTML = renderPipelineBoard(p.pipeline_board);
                } else if (labelEl) {
                    const newMsg = `${p.phase || ''}: ${p.message || ''} (${Math.round(p.pct || 0)}%)`;
                    if (!labelEl._lastMsg || labelEl._lastMsg !== newMsg) {
                        labelEl._lastMsg = newMsg;
                        const line = document.createElement('div');
                        line.textContent = newMsg;
                        labelEl.appendChild(line);
                        while (labelEl.children.length > 15) labelEl.removeChild(labelEl.firstChild);
                        labelEl.scrollTop = labelEl.scrollHeight;
                    }
                }
                updateStatus(`${moduleType} → ${stepId}: ${p.message || ''} ${Math.round(p.pct || 0)}%`);
            }

            // Continue polling
            setTimeout(poll, pollInterval);
        } catch (err) {
            // Network error — retry
            setTimeout(poll, pollInterval * 2);
        }
    };

    // Start polling after a short delay
    setTimeout(poll, pollInterval);
}

async function _saveRunLogToBackend(wsId, pipelineId, stepId, logHtml) {
    try {
        await fetch(`/api/step/${wsId}/${pipelineId}/${stepId}/run_log`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({log_html: logHtml}),
        });
    } catch (e) { /* best-effort */ }
}

function doResetParams(moduleType, stepId) {
    updateStatus(`Reset params for ${stepId}: TODO`);
}

async function doStopAnalysis(moduleType, stepId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    if (!sub) return;
    const taskKey = `${ws.id}/${sub.pipelineId}/${stepId}`;

    updateStatus(`Stopping ${moduleType} → ${stepId}...`);
    try {
        const res = await fetch('/api/tasks/cancel', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key: taskKey}),
        });
        const data = await res.json();
        if (data.data?.cancelled) {
            updateStatus(`⏹ Stopping ${stepId} after current frame...`);
        }
    } catch (e) {
        updateStatus(`❌ Failed to stop: ${e.message}`);
    }
}

// ── Generic status box persistence ──────────
function _setStatusBox(boxId, html) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (sub) {
        if (!sub._statusBoxes) sub._statusBoxes = {};
        sub._statusBoxes[boxId] = html;
    }
    const el = document.getElementById(boxId);
    if (el) el.innerHTML = html;
}

function _restoreStatusBoxes(sub, ...boxIds) {
    if (!sub?._statusBoxes) return;
    for (const id of boxIds) {
        const saved = sub._statusBoxes[id];
        if (saved) {
            const el = document.getElementById(id);
            if (el) el.innerHTML = saved;
        }
    }
}

function updateStepStatus(pipelineId, stepId, newStatus) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const pipeline = ws.pipelines.get(pipelineId);
    if (!pipeline) return;
    const step = pipeline.steps.find(s => s.id === stepId);
    if (step) step.status = newStatus;
    // Re-render canvas if we're on it
    const activeSub = ws.subtabs.get(ws.activeSubtab);
    if (activeSub?.type === 'canvas') renderViewport();
}

// ═════════════════════════════════════════════
// RESULTS LOADING
// ═════════════════════════════════════════════

// ═════════════════════════════════════════════
// ANSYS-STYLE UPSTREAM/DOWNSTREAM INVALIDATION
// ═════════════════════════════════════════════

// Pipeline step ordering — downstream depends on upstream
const STEP_ORDER = {
    fastia: ['import', 'detection', 'tracking', 'classification', 'kinetics', 'association', 'examination'],
    cornealia: ['import', 'segmentation', 'morphometry'],
    cornealia_batch: ['batch_setup', 'batch_run', 'batch_results'],
    immunia: ['segment', 'track', 'signal_association', 'keller_segel', 'particle_tracking', 'graph_theory', 'integrated_analysis', 'track_examiner'],
};

function invalidateStaleResults(ws, pipelineId, completedStepId, moduleType) {
    /**
     * When a step completes:
     * 1. Mark THIS step's existing plots as stale (data changed, plots are outdated)
     * 2. Mark all DOWNSTREAM steps' plots as stale
     * 3. Re-render affected trees
     */
    const order = STEP_ORDER[moduleType] || [];
    const completedIdx = order.indexOf(completedStepId);
    if (completedIdx < 0) return;

    // Steps to invalidate: this step + all downstream
    const stepsToInvalidate = order.slice(completedIdx);

    let changed = false;
    for (const [subId, sub] of ws.subtabs) {
        if (sub.type !== 'module' || sub.pipelineId !== pipelineId) continue;
        if (!stepsToInvalidate.includes(sub.stepId)) continue;
        if (!sub.insertedResults || sub.insertedResults.length === 0) continue;

        for (const r of sub.insertedResults) {
            if (r.status === 'done') {
                r.status = 'stale';
                r.url = null;  // Force re-generation on click
                changed = true;
            }
        }

        // Also clear _resultsDiscovered so discovery runs fresh next time
        sub._resultsDiscovered = false;

        renderModuleTree(sub);
    }

    if (changed) {
        console.log(`Invalidated results for ${stepsToInvalidate.join(', ')} (pipeline ${pipelineId})`);
    }
}


async function loadAvailableResults(wsId, pipelineId, stepId, moduleType, autoShow) {
    if (!state._projectOpen) return;
    const res = await api(`step/${wsId}/${pipelineId}/${stepId}/results`);
    if (!res.success || !res.data.length) return;

    const listEl = document.getElementById(`resultsList-${moduleType}-${stepId}`);

    // Group: images vs data files
    const images = res.data.filter(r => ['.png', '.jpg', '.jpeg', '.svg'].includes(r.type));
    const dataFiles = res.data.filter(r => ['.json', '.csv', '.pkl'].includes(r.type));

    if (listEl) {
        let html = '';
        if (images.length) {
            html += `<p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:4px">Plots:</p>`;
            html += images.map(r => `
                <button class="btn btn-default" style="justify-content:flex-start" onclick="showResultImage('${r.url}','${r.name}')">
                    🖼 ${r.name}
                </button>`).join('');
        }
        if (dataFiles.length) {
            html += `<p style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px;margin-bottom:4px">Data:</p>`;
            html += dataFiles.map(r => `
                <button class="btn btn-default" style="justify-content:flex-start">
                    📄 ${r.name} <span style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-left:auto">${formatBytes(r.size_bytes)}</span>
                </button>`).join('');
        }
        listEl.innerHTML = html;
    }

    // Auto-show last image in Graphics column
    if (autoShow && images.length > 0) {
        showResultImage(images[images.length - 1].url, images[images.length - 1].name);
    }
}

function showResultImage(url, name) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) { console.error('showResultImage: no sub'); return; }
    const gfxId = `graphicsBody-${sub.id}`;
    const gfx = document.getElementById(gfxId);
    console.log(`showResultImage: url=${url}, gfxId=${gfxId}, found=${!!gfx}`);
    if (gfx) {
        gfx.style.background = 'var(--surface-0)';
        const isVideo = url.match(/\.(mp4|webm|avi|mov)$/i);
        const content = isVideo
            ? `<div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000">
                   <video id="resultVideo" src="${url}" loop style="max-width:100%;max-height:100%"></video>
               </div>
               <div style="display:flex;align-items:center;gap:8px;padding:4px 10px;background:var(--surface-2);border-top:1px solid var(--surface-3);flex-shrink:0">
                   <button onclick="var v=document.getElementById('resultVideo');if(v.paused){v.play();this.textContent='⏸'}else{v.pause();this.textContent='▶'}" style="background:var(--brand-accent);border:none;color:#fff;cursor:pointer;font-size:11px;padding:3px 10px;border-radius:var(--r-sm);font-weight:700">▶</button>
                   <button onclick="var v=document.getElementById('resultVideo');v.currentTime=0;v.play();this.previousElementSibling.textContent='⏸'" style="background:none;border:1px solid var(--chrome-border);color:var(--text-secondary);cursor:pointer;font-size:11px;padding:3px 8px;border-radius:var(--r-sm)">⏮</button>
                   <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Speed:</span>
                   <select onchange="document.getElementById('resultVideo').playbackRate=parseFloat(this.value)" style="font-size:var(--fs-xs);background:var(--surface-1);color:var(--text-secondary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:1px 4px">
                       <option value="0.25">0.25×</option><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="4">4×</option>
                   </select>
                   <div style="flex:1"></div>
                   <a href="${url}" download style="font-size:var(--fs-xs);color:var(--text-tertiary);text-decoration:none">💾 Save</a>
               </div>`
            : `<div style="flex:1;display:flex;align-items:center;justify-content:center;padding:8px;overflow:auto">
                   <img src="${url}" style="max-width:100%;max-height:100%;object-fit:contain;border-radius:4px" alt="${name}"
                        onerror="console.error('IMG load failed:', '${url}')">
               </div>`;
        gfx.innerHTML = `
            <div style="width:100%;height:100%;display:flex;flex-direction:column;overflow:hidden">
                <div style="padding:6px 10px;font-size:var(--fs-xs);color:var(--text-tertiary);border-bottom:1px solid var(--surface-3);flex-shrink:0">${name}</div>
                ${content}
            </div>`;
    } else {
        console.error('showResultImage: element not found:', gfxId);
    }
    updateStatus(`Showing: ${name}`);
}

// ═════════════════════════════════════════════
// MULTI-CHANNEL MOVIE PLAYER (FIJI-style)
// ═════════════════════════════════════════════

let _moviePlayerState = null;
let _frameCache = new Map(); // frame_key → data:image URI
const PRELOAD_AHEAD = 8;

function _frameCacheKey(frame, channel, channels) {
    const bc = (_moviePlayerState?.bcManual) ? `${_moviePlayerState.vmin}_${_moviePlayerState.vmax}` : '';
    const fid = _moviePlayerState?.featureId || '';
    return `${fid}_${frame}_${channel}_${channels || ''}_${bc}`;
}

function _displayFrame(imageSrc) {
    const img = document.getElementById('movieFrameImg');
    const placeholder = document.getElementById('moviePlaceholder');
    if (img) {
        // Skip if already showing this exact image (prevents blink)
        if (img.src === imageSrc) return;
        img.src = imageSrc;
        img.style.display = '';
    }
    if (placeholder) placeholder.style.display = 'none';
}

function _preloadFrames(startFrame) {
    if (!_moviePlayerState) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    const pid = _moviePlayerState.pipelineId;
    const stepId = _moviePlayerState.stepId || 'import';
    const mode = _moviePlayerState.displayMode || 'composite';
    const visibleChannels = _moviePlayerState.channels
        .map((ch, i) => ch.visible ? ch.idx : -1).filter(i => i >= 0);
    const channelParam = mode === 'single' ? (visibleChannels[0] || 0) : -1;
    const channelsStr = mode === 'composite' ? visibleChannels.join(',') : '';

    for (let offset = 1; offset <= PRELOAD_AHEAD; offset++) {
        const f = (startFrame + offset) % _moviePlayerState.totalFrames;
        const key = _frameCacheKey(f, channelParam, channelsStr);
        if (_frameCache.has(key)) continue;
        _frameCache.set(key, 'loading'); // prevent duplicate requests
        let url = `/api/step/${ws.id}/${pid}/${stepId}/preview_frame?frame=${f}&channel=${channelParam}`;
        if (channelsStr && mode === 'composite') url += `&channels=${channelsStr}`;
        if (_moviePlayerState.bcManual) url += `&vmin=${_moviePlayerState.vmin}&vmax=${_moviePlayerState.vmax}`;
        fetch(url).then(r => r.json()).then(data => {
            if (data.success) _frameCache.set(key, data.image);
            else _frameCache.delete(key);
        }).catch(() => _frameCache.delete(key));
    }
}

function emissionToRGB(nm) {
    // Map emission wavelength to display color (simplified visible spectrum)
    if (!nm || nm < 380) return '#ffffff';
    if (nm < 440) return '#8b00ff'; // violet
    if (nm < 470) return '#0044ff'; // blue
    if (nm < 500) return '#00ccff'; // cyan
    if (nm < 520) return '#00ff00'; // green
    if (nm < 545) return '#aaff00'; // yellow-green
    if (nm < 575) return '#ffff00'; // yellow
    if (nm < 600) return '#ff8800'; // orange
    if (nm < 640) return '#ff0000'; // red
    if (nm < 700) return '#cc0000'; // deep red
    return '#880044'; // far red / near-IR
}

function showCellVisiaPlayer() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) return;
    const info = sub._cvLoadInfo;
    if (!info) return;

    const nCh = info.n_channels || 1;
    const totalFrames = info.n_frames || 1;
    const defaultColors = ['#00ff00', '#ff0000', '#42a5f5', '#ffa726', '#e040fb', '#ffffff'];
    const origInfo = sub._cvOriginalInfo || info;
    const origNCh = origInfo?.n_channels || nCh;
    const isInputMode = _cvActiveGfxTab === 'input';
    const keepIndices = isInputMode
        ? Array.from({length: nCh}, (_, i) => i)  // Input: all channels, sequential
        : (sub._cvState?.scopeKeepChannels || Array.from({length: origNCh}, (_, i) => i));
    const chNames = sub._cvState?.channelNames || [];
    const channels = [];
    for (let seqIdx = 0; seqIdx < nCh; seqIdx++) {
        const origIdx = keepIndices[seqIdx] ?? seqIdx;
        const name = chNames[origIdx] || `Ch ${origIdx}`;
        channels.push({ name, color: defaultColors[origIdx % defaultColors.length], emNm: 0, visible: true, idx: seqIdx });
    }

    if (_moviePlayerState?.playTimer) clearInterval(_moviePlayerState.playTimer);
    _moviePlayerState = {
        frame: 0, totalFrames, playing: false, channels, playTimer: null,
        pipelineId: sub.pipelineId, stepId: null, displayMode: 'composite', bcManual: false,
        cvMode: true, featureId: sub._cvLoadInfo?.feature_id || sub._cvFeatureIds?.meta || null,
    };

    gfx.style.background = 'var(--surface-0)';
    gfx.innerHTML = `
        <div class="movie-player" style="display:flex;flex-direction:column;height:100%;font-family:var(--font-ui)">
            <div style="display:flex;align-items:center;gap:4px;padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);flex-shrink:0;flex-wrap:wrap">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-right:4px">Channels</span>
                ${channels.map((ch, i) => `
                    <button class="movie-ch-btn" id="chBtn${i}" onclick="toggleMovieChannel(${i})" style="display:flex;align-items:center;gap:4px;padding:3px 8px;border-radius:var(--r-sm);border:1px solid ${ch.color}40;background:${ch.color}15;color:${ch.color};font-size:var(--fs-xs);font-weight:600;cursor:pointer;transition:all .12s">
                        <span style="width:8px;height:8px;border-radius:50%;background:${ch.color};flex-shrink:0"></span>
                        ${ch.name}
                    </button>
                `).join('')}
                <div style="flex:1"></div>
                <select style="font-size:var(--fs-xs);background:var(--surface-1);color:var(--text-secondary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:2px 6px" onchange="setMovieDisplayMode(this.value)">
                    <option value="composite">Composite</option>
                    <option value="single">Single Channel</option>
                </select>
            </div>
            <div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;background:#000;transform:translateZ(0)" id="movieCanvas"
                 onmousedown="cvToolMouseDown(event)" onmousemove="cvToolMouseMove(event)" onmouseup="cvToolMouseUp(event)"
                 oncontextmenu="event.preventDefault()">
                <img id="movieFrameImg" style="width:100%;height:100%;object-fit:contain;display:none;backface-visibility:hidden">
                <svg id="cvToolOverlay" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10"></svg>
                <div id="moviePlaceholder" style="color:rgba(255,255,255,.3);font-size:var(--fs-sm);text-align:center">
                    <div style="font-size:32px;margin-bottom:8px;opacity:.4">🔬</div>
                    <div>Loading first frame...</div>
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:0;flex-shrink:0;background:linear-gradient(180deg,var(--surface-2),var(--surface-1));border-top:1px solid rgba(255,255,255,.04)">
                <div style="padding:6px 10px 2px;display:flex;align-items:center;gap:8px">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono);min-width:32px" id="movieFrameNum">0</span>
                    <input type="range" min="0" max="${totalFrames - 1}" value="0" style="flex:1;accent-color:var(--brand-accent);height:4px" id="movieSlider" oninput="seekMovieFrame(parseInt(this.value))">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">${totalFrames - 1}</span>
                </div>
                <div style="padding:2px 10px 6px;display:flex;align-items:center;gap:6px">
                    <button onclick="movieStepBack()" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:12px;padding:2px 4px">⏮</button>
                    <button onclick="toggleMoviePlay()" id="moviePlayBtn" style="background:var(--brand-accent);border:none;color:#fff;cursor:pointer;font-size:11px;padding:3px 10px;border-radius:var(--r-sm);font-weight:700">▶</button>
                    <button onclick="movieStepForward()" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:12px;padding:2px 4px">⏭</button>
                    <div style="flex:1"></div>
                    <select id="movieSpeed" style="font-size:var(--fs-xs);background:var(--surface-1);color:var(--text-secondary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:1px 4px">
                        <option value="500">2 fps</option><option value="200">5 fps</option><option value="100" selected>10 fps</option><option value="50">20 fps</option><option value="33">30 fps</option>
                    </select>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">Frame <span id="movieFrameInfo">0</span>/${totalFrames}</span>
                </div>
            </div>
        </div>`;
    setTimeout(() => _autoLoadFirstFrame(), 100);
}

// ═════════════════════════════════════════════
// CELLVISIA — CANVAS TOOL SYSTEM
// ═════════════════════════════════════════════
// Tool follows tree selection. Selecting a Crop feature activates the
// crop tool; selecting anything else reverts to view-only (pan/zoom).

let _cvToolState = { tool: null, dragging: false, startX: 0, startY: 0, curX: 0, curY: 0 };
let _cvRebuilding = false; // lock to prevent frame requests during rebuild
let _cvActiveGfxTab = 'graphics'; // which tab is active: input|graphics|tables|figures

// Map feature types to canvas tools
const CV_TOOL_MAP = { crop: 'rect' };

function _cvActiveTool() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?.activeTreeItem || !sub?.cvFeatures) return null;
    const feat = sub.cvFeatures.find(f => f.id === sub.activeTreeItem.id);
    if (!feat) return null;
    return CV_TOOL_MAP[feat.type] || null;
}

function _screenToImageCoords(e) {
    const img = document.getElementById('movieFrameImg');
    if (!img || !img.naturalWidth) return null;
    const rect = img.getBoundingClientRect();
    // object-fit:contain — image is centered with aspect ratio preserved
    const imgAspect = img.naturalWidth / img.naturalHeight;
    const boxAspect = rect.width / rect.height;
    let renderW, renderH, offsetX, offsetY;
    if (imgAspect > boxAspect) {
        renderW = rect.width;
        renderH = rect.width / imgAspect;
        offsetX = 0;
        offsetY = (rect.height - renderH) / 2;
    } else {
        renderH = rect.height;
        renderW = rect.height * imgAspect;
        offsetX = (rect.width - renderW) / 2;
        offsetY = 0;
    }
    const scaleX = img.naturalWidth / renderW;
    const scaleY = img.naturalHeight / renderH;
    const px = (e.clientX - rect.left - offsetX) * scaleX;
    const py = (e.clientY - rect.top - offsetY) * scaleY;
    return { x: Math.round(px), y: Math.round(py), scaleX, scaleY, offsetX, offsetY, renderW, renderH, rect };
}

function cvToolMouseDown(e) {
    if (e.button !== 0) return; // left click only
    const tool = _cvActiveTool();
    if (!tool) return;
    const coords = _screenToImageCoords(e);
    if (!coords || coords.x < 0 || coords.y < 0) return;
    _cvToolState = { tool, dragging: true, startX: coords.x, startY: coords.y, curX: coords.x, curY: coords.y, screenEvent: e };
    e.preventDefault();
}

function cvToolMouseMove(e) {
    if (!_cvToolState.dragging) return;
    const coords = _screenToImageCoords(e);
    if (!coords) return;
    _cvToolState.curX = Math.max(0, coords.x);
    _cvToolState.curY = Math.max(0, coords.y);
    if (_cvToolState.tool === 'rect') _cvDrawToolOverlay();
}

function cvToolMouseUp(e) {
    if (!_cvToolState.dragging) return;
    _cvToolState.dragging = false;
    const coords = _screenToImageCoords(e);
    if (coords) {
        _cvToolState.curX = Math.max(0, coords.x);
        _cvToolState.curY = Math.max(0, coords.y);
    }
    if (_cvToolState.tool === 'rect') _cvFinalizeCropRect();
}

function _cvDrawToolOverlay() {
    const svg = document.getElementById('cvToolOverlay');
    if (!svg) return;
    const img = document.getElementById('movieFrameImg');
    if (!img || !img.naturalWidth) return;

    const s = _cvToolState;
    const imgRect = img.getBoundingClientRect();
    const svgRect = svg.getBoundingClientRect();
    const imgAspect = img.naturalWidth / img.naturalHeight;
    const boxAspect = imgRect.width / imgRect.height;
    let renderW, renderH, offsetX, offsetY;
    if (imgAspect > boxAspect) {
        renderW = imgRect.width; renderH = imgRect.width / imgAspect;
        offsetX = 0; offsetY = (imgRect.height - renderH) / 2;
    } else {
        renderH = imgRect.height; renderW = imgRect.height * imgAspect;
        offsetX = (imgRect.width - renderW) / 2; offsetY = 0;
    }

    // Convert image coords back to SVG/screen coords
    const sx = renderW / img.naturalWidth;
    const sy = renderH / img.naturalHeight;
    const x1 = Math.min(s.startX, s.curX) * sx + offsetX;
    const y1 = Math.min(s.startY, s.curY) * sy + offsetY;
    const w = Math.abs(s.curX - s.startX) * sx;
    const h = Math.abs(s.curY - s.startY) * sy;

    svg.innerHTML = `
        <rect x="${x1}" y="${y1}" width="${w}" height="${h}"
              fill="rgba(33,150,243,0.15)" stroke="#2196f3" stroke-width="2" stroke-dasharray="6,3"/>
        <text x="${x1 + 4}" y="${y1 - 6}" fill="#2196f3" font-size="11" font-family="var(--font-mono)">
            ${Math.abs(Math.round(s.curX - s.startX))} × ${Math.abs(Math.round(s.curY - s.startY))} px
        </text>
    `;
}

function _cvFinalizeCropRect() {
    const s = _cvToolState;
    const x = Math.min(s.startX, s.curX);
    const y = Math.min(s.startY, s.curY);
    const w = Math.abs(s.curX - s.startX);
    const h = Math.abs(s.curY - s.startY);
    if (w < 2 || h < 2) return; // too small, ignore

    // Find the active Crop feature and populate its params
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?.activeTreeItem || !sub?.cvFeatures) return;
    const feat = sub.cvFeatures.find(f => f.id === sub.activeTreeItem.id && f.type === 'crop');
    if (!feat) return;

    feat.params.x = Math.round(x);
    feat.params.y = Math.round(y);
    feat.params.w = Math.round(w);
    feat.params.h = Math.round(h);

    // Update the settings form if visible
    const form = document.querySelector(`#settingsBody-${sub.id} .settings-form`);
    if (form) {
        const setVal = (key, val) => { const el = form.querySelector(`[data-param="${key}"]`); if (el) el.value = val; };
        setVal('x', feat.params.x);
        setVal('y', feat.params.y);
        setVal('w', feat.params.w);
        setVal('h', feat.params.h);
    }

    updateStatus(`Crop ROI: ${feat.params.x},${feat.params.y} → ${feat.params.w}×${feat.params.h} px`);
}

function showMoviePlayer() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) return;

    // Get channel names from local params, then backend params as fallback
    let importParams = sub._localParams?.['channel-setup'] || {};

    // If local params are empty, try backend-loaded params
    if (Object.keys(importParams).length === 0 && sub._loadedParams) {
        // Backend params may be nested under a section key
        for (const [k, v] of Object.entries(sub._loadedParams)) {
            if (typeof v === 'object' && (v.dead_channel_idx !== undefined || v.ch1_name !== undefined)) {
                importParams = v;
                break;
            }
        }
        // Or flat at top level
        if (sub._loadedParams.dead_channel_idx !== undefined || sub._loadedParams.ch1_name !== undefined) {
            importParams = sub._loadedParams;
        }
    }

    console.log('[MoviePlayer] moduleType:', sub.moduleType, 'importParams:', JSON.stringify(importParams));
    const channels = [];

    if (sub.moduleType === 'immunia') {
        // IMMUNIA: role-based channels with explicit indices
        const roles = [
            { param: 'dead_channel_name', idxParam: 'dead_channel_idx', fallback: 'Dead Cells', color: '#ef5350' },
            { param: 'tumor_channel_name', idxParam: 'tumor_channel_idx', fallback: 'Target Cells', color: '#66bb6a' },
            { param: 'tissue_channel_name', idxParam: 'tissue_channel_idx', fallback: 'Substrate', color: '#42a5f5' },
            { param: 'nk_channel_name', idxParam: 'nk_channel_idx', fallback: 'Effector Cells', color: '#ffa726' },
        ];
        for (const r of roles) {
            const rawIdx = importParams[r.idxParam];
            const idx = (rawIdx !== undefined && rawIdx !== '') ? parseInt(rawIdx) : roles.indexOf(r);
            const name = importParams[r.param] || r.fallback;
            console.log(`[MoviePlayer] Role ${r.fallback}: idx=${idx} (raw=${rawIdx}), name=${name}`);
            channels.push({ name, color: r.color, emNm: 0, visible: true, idx });
        }
    } else {
        // FASTIA: sequential channels with fluorophore lookup
        for (let i = 1; i <= 4; i++) {
            const name = importParams[`ch${i}_name`];
            if (!name) continue;
            const fluor = importParams[`ch${i}_fluor`] || '';
            const emManual = parseFloat(importParams[`ch${i}_emission`]) || 0;
            const emFromDB = FLUOROPHORE_DB[fluor]?.em || 0;
            const emNm = emManual || emFromDB;
            const color = emissionToRGB(emNm);
            channels.push({ name, color, emNm, visible: true, idx: i-1 });
        }
    }
    if (channels.length === 0) {
        channels.push({ name: 'Channel 1', color: '#00ff00', emNm: 509, visible: true, idx: 0 });
        channels.push({ name: 'Channel 2', color: '#ff0000', emNm: 610, visible: true, idx: 1 });
    }

    // Get metadata
    const metaParams = sub._localParams?.['metadata'] || {};
    const movieInfo = sub._movieInfo || {};
    const totalFrames = movieInfo.n_frames || 75;

    // Clear any existing play timer before resetting state
    if (_moviePlayerState?.playTimer) {
        clearInterval(_moviePlayerState.playTimer);
    }

    _moviePlayerState = { frame: 0, totalFrames, playing: false, channels, playTimer: null, pipelineId: sub.pipelineId, stepId: 'import', displayMode: 'composite', bcManual: false };

    gfx.style.background = 'var(--surface-0)';
    gfx.innerHTML = `
        <div class="movie-player" style="display:flex;flex-direction:column;height:100%;font-family:var(--font-ui)">
            <!-- Channel controls bar -->
            <div style="display:flex;align-items:center;gap:4px;padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);flex-shrink:0;flex-wrap:wrap">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-right:4px">Channels</span>
                ${channels.map((ch, i) => `
                    <button class="movie-ch-btn" id="chBtn${i}" onclick="toggleMovieChannel(${i})" style="display:flex;align-items:center;gap:4px;padding:3px 8px;border-radius:var(--r-sm);border:1px solid ${ch.color}40;background:${ch.color}15;color:${ch.color};font-size:var(--fs-xs);font-weight:600;cursor:pointer;transition:all .12s" title="${ch.emNm ? ch.emNm + ' nm' : 'Unknown'}">
                        <span style="width:8px;height:8px;border-radius:50%;background:${ch.color};flex-shrink:0"></span>
                        ${ch.name}
                    </button>
                `).join('')}
                <div style="flex:1"></div>
                <select style="font-size:var(--fs-xs);background:var(--surface-1);color:var(--text-secondary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:2px 6px" onchange="setMovieDisplayMode(this.value)">
                    <option value="composite">Composite</option>
                    <option value="single">Single Channel</option>
                    <option value="split">Split View</option>
                </select>
            </div>

            <!-- Frame display area -->
            <div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;background:#000" id="movieCanvas">
                <img id="movieFrameImg" style="width:100%;height:100%;object-fit:contain;display:none">
                <div id="moviePlaceholder" style="color:rgba(255,255,255,.3);font-size:var(--fs-sm);text-align:center">
                    <div style="font-size:32px;margin-bottom:8px;opacity:.4">🎬</div>
                    <div>Load a movie to preview</div>
                    <div style="font-size:var(--fs-xs);margin-top:4px;opacity:.6">${channels.map(c => c.name).join(' · ')}</div>
                </div>
            </div>

            <!-- Transport controls -->
            <div style="display:flex;flex-direction:column;gap:0;flex-shrink:0;background:linear-gradient(180deg,var(--surface-2),var(--surface-1));border-top:1px solid rgba(255,255,255,.04)">
                <!-- Frame slider -->
                <div style="padding:6px 10px 2px;display:flex;align-items:center;gap:8px">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono);min-width:32px" id="movieFrameNum">0</span>
                    <input type="range" min="0" max="${totalFrames - 1}" value="0" style="flex:1;accent-color:var(--brand-accent);height:4px" id="movieSlider" oninput="seekMovieFrame(parseInt(this.value))">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">${totalFrames - 1}</span>
                </div>
                <!-- Play controls -->
                <div style="padding:2px 10px 6px;display:flex;align-items:center;gap:6px">
                    <button onclick="movieStepBack()" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:12px;padding:2px 4px" title="Previous frame">⏮</button>
                    <button onclick="toggleMoviePlay()" id="moviePlayBtn" style="background:var(--brand-accent);border:none;color:#fff;cursor:pointer;font-size:11px;padding:3px 10px;border-radius:var(--r-sm);font-weight:700" title="Play/Pause">▶</button>
                    <button onclick="movieStepForward()" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:12px;padding:2px 4px" title="Next frame">⏭</button>
                    <div style="flex:1"></div>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Speed:</span>
                    <select id="movieSpeed" style="font-size:var(--fs-xs);background:var(--surface-1);color:var(--text-secondary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:1px 4px">
                        <option value="500">2 fps</option>
                        <option value="200">5 fps</option>
                        <option value="100" selected>10 fps</option>
                        <option value="50">20 fps</option>
                        <option value="33">30 fps</option>
                    </select>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">
                        Frame <span id="movieFrameInfo">0</span>/${totalFrames}
                        ${metaParams.t_interval ? ` · <span id="movieTimeInfo">0.0</span>s` : ''}
                    </span>
                </div>
            </div>
        </div>`;

    updateStatus(`Movie viewer: ${channels.map(c => c.name).join(', ')} · ${totalFrames} frames`);

    // Auto-load first frame from backend
    setTimeout(() => _autoLoadFirstFrame(), 100);
}

// ═════════════════════════════════════════════
// MOVIE PLAYER — BRIGHTNESS & CONTRAST
// ═════════════════════════════════════════════

let _bcDebounce = null;

function updateBCSliderFromRange(which) {
    const slider = document.getElementById(which === 'min' ? 'bcMin' : 'bcMax');
    const box = document.getElementById(which === 'min' ? 'bcMinBox' : 'bcMaxBox');
    if (slider && box) box.value = slider.value;
    _triggerBCUpdate();
}

function updateBCSliderFromBox(which) {
    const box = document.getElementById(which === 'min' ? 'bcMinBox' : 'bcMaxBox');
    const slider = document.getElementById(which === 'min' ? 'bcMin' : 'bcMax');
    if (box && slider) slider.value = box.value;
    _triggerBCUpdate();
}

function _triggerBCUpdate() {
    const minEl = document.getElementById('bcMin');
    const maxEl = document.getElementById('bcMax');
    if (!minEl || !maxEl) return;
    let vmin = parseInt(minEl.value) || 0;
    let vmax = parseInt(maxEl.value) || 65535;
    if (vmin >= vmax) { vmax = vmin + 1; maxEl.value = vmax; document.getElementById('bcMaxBox').value = vmax; }
    if (_bcDebounce) clearTimeout(_bcDebounce);
    _bcDebounce = setTimeout(() => {
        if (_moviePlayerState) {
            _moviePlayerState.vmin = vmin;
            _moviePlayerState.vmax = vmax;
            _moviePlayerState.bcManual = true;
            _frameCache.clear();
            seekMovieFrame(_moviePlayerState.frame);
        }
    }, 150);
}

function updateBCDisplay() { _triggerBCUpdate(); }

async function autoBrightContrast(mode) {
    if (!_moviePlayerState) return;
    const minEl = document.getElementById('bcMin');
    const maxEl = document.getElementById('bcMax');
    if (!minEl || !maxEl) return;

    if (mode === 'reset') {
        minEl.value = 0;
        maxEl.value = parseInt(maxEl.max) || 65535;
        const minBox = document.getElementById('bcMinBox');
        const maxBox = document.getElementById('bcMaxBox');
        if (minBox) minBox.value = 0;
        if (maxBox) maxBox.value = maxEl.value;
        _moviePlayerState.bcManual = false;
        _frameCache.clear();
        seekMovieFrame(_moviePlayerState.frame);
        return;
    }

    const ws = getActiveWorkspace();
    if (!ws) return;
    const pid = _moviePlayerState.pipelineId;
    const stepId = _moviePlayerState.stepId || 'import';
    const frame = _moviePlayerState.frame || 0;

    // Build channel param based on what's currently visible
    const visibleCh = _moviePlayerState.channels
        .map(ch => ch.visible ? ch.idx : -1).filter(i => i >= 0);
    const chParam = visibleCh.length === 1 ? visibleCh[0] : -1;
    const chStr = visibleCh.join(',');

    try {
        let url = `/api/step/${ws.id}/${pid}/${stepId}/preview_frame?frame=${frame}&channel=${chParam}&stats=1`;
        if (chParam === -1 && chStr) url += `&channels=${chStr}`;
        const res = await fetch(url);
        const data = await res.json();
        if (data.success && data.stats) {
            if (mode === 'percentile') {
                minEl.value = Math.floor(data.stats.p05 || 0);
                maxEl.value = Math.ceil(data.stats.p995 || 65535);
            }
            _moviePlayerState.vmin = parseInt(minEl.value);
            _moviePlayerState.vmax = parseInt(maxEl.value);
            _moviePlayerState.bcManual = true;
            const minBox = document.getElementById('bcMinBox');
            const maxBox = document.getElementById('bcMaxBox');
            if (minBox) minBox.value = minEl.value;
            if (maxBox) maxBox.value = maxEl.value;
            _frameCache.clear();
            seekMovieFrame(_moviePlayerState.frame);
        }
    } catch (e) {
        console.error('Auto B&C error:', e);
    }
}

function toggleMovieChannel(idx) {
    if (!_moviePlayerState) return;
    _frameCache.clear();
    const ch = _moviePlayerState.channels[idx];
    ch.visible = !ch.visible;
    const btn = document.getElementById(`chBtn${idx}`);
    if (btn) {
        btn.style.opacity = ch.visible ? '1' : '.3';
        btn.style.background = ch.visible ? `${ch.color}15` : 'transparent';
        btn.style.borderStyle = ch.visible ? 'solid' : 'dashed';
    }
    if (_moviePlayerState.displayMode === 'single') {
        _moviePlayerState.channels.forEach((c, i) => {
            c.visible = (i === idx);
            const b = document.getElementById(`chBtn${i}`);
            if (b) {
                b.style.opacity = c.visible ? '1' : '.3';
                b.style.background = c.visible ? `${c.color}15` : 'transparent';
                b.style.borderStyle = c.visible ? 'solid' : 'dashed';
            }
        });
    }
    seekMovieFrame(_moviePlayerState.frame);
}

function seekMovieFrame(frame) {
    if (!_moviePlayerState) return;
    if (_cvRebuilding) return; // block during rebuild
    _moviePlayerState.frame = frame;
    const numEl = document.getElementById('movieFrameNum');
    const infoEl = document.getElementById('movieFrameInfo');
    if (numEl) numEl.textContent = frame;
    if (infoEl) infoEl.textContent = frame;

    // Build channel parameter based on display mode and visibility
    const mode = _moviePlayerState.displayMode || 'composite';
    const visibleChannels = _moviePlayerState.channels
        .map((ch, i) => ch.visible ? ch.idx : -1)
        .filter(i => i >= 0);

    let channelParam = -1;
    if (mode === 'single') {
        channelParam = visibleChannels.length > 0 ? visibleChannels[0] : 0;
    }
    const channelsStr = mode === 'composite' ? visibleChannels.join(',') : '';
    const cacheKey = _frameCacheKey(frame, channelParam, channelsStr);

    // Check cache first
    const cached = _frameCache.get(cacheKey);
    if (cached && cached !== 'loading') {
        _displayFrame(cached);
        // Preload ahead
        if (_moviePlayerState.playing) _preloadFrames(frame);
        return;
    }

    // Fetch from backend
    const ws = getActiveWorkspace();
    if (!ws) return;
    const pid = _moviePlayerState.pipelineId;
    const stepId = _moviePlayerState.stepId || 'import';
    let url;
    if (_moviePlayerState.cvMode) {
        url = `/api/cellvisia/${ws.id}/${pid}/preview_frame?frame=${frame}&channel=${channelParam}`;
        if (_moviePlayerState.featureId) url += `&feature_id=${_moviePlayerState.featureId}`;
    } else {
        url = `/api/step/${ws.id}/${pid}/${stepId}/preview_frame?frame=${frame}&channel=${channelParam}`;
    }
    if (channelsStr && mode === 'composite') url += `&channels=${channelsStr}`;
    if (_moviePlayerState.bcManual) url += `&vmin=${_moviePlayerState.vmin}&vmax=${_moviePlayerState.vmax}`;

    fetch(url)
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
            // Cache the result
            _frameCache.set(cacheKey, data.image);
            _displayFrame(data.image);
            if (data.n_frames && data.n_frames !== _moviePlayerState.totalFrames) {
                _moviePlayerState.totalFrames = data.n_frames;
                const slider = document.getElementById('movieSlider');
                if (slider) slider.max = data.n_frames - 1;
            }
            // Preload ahead while playing
            if (_moviePlayerState.playing) _preloadFrames(frame);
        })
        .catch(() => {});
}

function _autoLoadFirstFrame() {
    if (!_moviePlayerState) return;
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const pid = sub.pipelineId;
    const stepId = 'import';
    let url;
    if (_moviePlayerState.cvMode) {
        url = `/api/cellvisia/${ws.id}/${pid}/preview_frame?frame=0&channel=-1&stats=1`;
        if (_moviePlayerState.featureId) url += `&feature_id=${_moviePlayerState.featureId}`;
    } else {
        url = `/api/step/${ws.id}/${pid}/${stepId}/preview_frame?frame=0&channel=-1&stats=1`;
    }
    fetch(url)
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                const canvas = document.getElementById('movieCanvas');
                if (canvas) canvas.innerHTML = `<div style="color:rgba(255,255,255,.3);font-size:var(--fs-sm);text-align:center;padding:20px"><div style="font-size:24px;margin-bottom:8px;opacity:.4">📁</div>${data.error || 'Select a movie file first'}</div>`;
                return;
            }
            _displayFrame(data.image);
            _moviePlayerState.totalFrames = data.n_frames || 75;
            _moviePlayerState.stepId = stepId;
            _moviePlayerState.pipelineId = pid;
            // Set B&C slider max from actual data range (don't trigger manual mode)
            if (data.stats) {
                const maxVal = Math.ceil(data.stats.max || 65535);
                const minSlider = document.getElementById('bcMin');
                const maxSlider = document.getElementById('bcMax');
                const minBox = document.getElementById('bcMinBox');
                const maxBox = document.getElementById('bcMaxBox');
                if (minSlider) { minSlider.max = maxVal; minSlider.value = 0; }
                if (maxSlider) { maxSlider.max = maxVal; maxSlider.value = maxVal; }
                if (minBox) { minBox.max = maxVal; minBox.value = 0; }
                if (maxBox) { maxBox.max = maxVal; maxBox.value = maxVal; }
            }
            // Update slider + frame count display
            const slider = document.getElementById('movieSlider');
            if (slider) {
                slider.max = _moviePlayerState.totalFrames - 1;
                const maxLabel = slider.parentElement?.lastElementChild;
                if (maxLabel) maxLabel.textContent = _moviePlayerState.totalFrames - 1;
            }
            // Update "Frame 0/N" text
            const infoSpans = document.querySelectorAll('#movieFrameInfo');
            infoSpans.forEach(s => {
                const parent = s.parentElement;
                if (parent) parent.innerHTML = parent.innerHTML.replace(/\/\d+/, '/' + _moviePlayerState.totalFrames);
            });
            // Store movie info on subtab
            const sub2 = ws?.subtabs.get(ws?.activeSubtab);
            if (sub2) sub2._movieInfo = { n_frames: data.n_frames, n_channels: data.n_channels, shape: data.shape };
            const shape = data.shape || [];
            updateStatus(`Movie loaded: ${shape.join('×')} — ${data.n_frames} frames, ${data.n_channels} channels`);
        })
        .catch(() => {});
}

function toggleMoviePlay() {
    if (!_moviePlayerState) return;
    _moviePlayerState.playing = !_moviePlayerState.playing;
    const btn = document.getElementById('moviePlayBtn');
    if (_moviePlayerState.playing) {
        if (btn) btn.textContent = '⏸';
        // Start preloading ahead
        _preloadFrames(_moviePlayerState.frame);
        const speed = parseInt(document.getElementById('movieSpeed')?.value || '100');
        _moviePlayerState.playTimer = setInterval(() => {
            _moviePlayerState.frame = (_moviePlayerState.frame + 1) % _moviePlayerState.totalFrames;
            const slider = document.getElementById('movieSlider');
            if (slider) slider.value = _moviePlayerState.frame;
            seekMovieFrame(_moviePlayerState.frame);
        }, speed);
    } else {
        if (btn) btn.textContent = '▶';
        clearInterval(_moviePlayerState.playTimer);
    }
}

function movieStepForward() {
    if (!_moviePlayerState) return;
    _moviePlayerState.frame = Math.min(_moviePlayerState.frame + 1, _moviePlayerState.totalFrames - 1);
    document.getElementById('movieSlider').value = _moviePlayerState.frame;
    seekMovieFrame(_moviePlayerState.frame);
}

function movieStepBack() {
    if (!_moviePlayerState) return;
    _moviePlayerState.frame = Math.max(_moviePlayerState.frame - 1, 0);
    document.getElementById('movieSlider').value = _moviePlayerState.frame;
    seekMovieFrame(_moviePlayerState.frame);
}

function setMovieDisplayMode(mode) {
    if (!_moviePlayerState) return;
    _moviePlayerState.displayMode = mode;
    _frameCache.clear(); // mode change invalidates cache
    // In single mode, only show first visible channel
    if (mode === 'single') {
        const firstVisible = _moviePlayerState.channels.findIndex(c => c.visible);
        _moviePlayerState.channels.forEach((c, i) => {
            c.visible = (i === (firstVisible >= 0 ? firstVisible : 0));
            const btn = document.getElementById(`chBtn${i}`);
            if (btn) {
                btn.style.opacity = c.visible ? '1' : '.3';
                btn.style.background = c.visible ? `${c.color}15` : 'transparent';
                btn.style.borderStyle = c.visible ? 'solid' : 'dashed';
            }
        });
    } else if (mode === 'composite') {
        // Re-enable all channels
        _moviePlayerState.channels.forEach((c, i) => {
            c.visible = true;
            const btn = document.getElementById(`chBtn${i}`);
            if (btn) {
                btn.style.opacity = '1';
                btn.style.background = `${c.color}15`;
                btn.style.borderStyle = 'solid';
            }
        });
    }
    seekMovieFrame(_moviePlayerState.frame);
    updateStatus(`Display: ${mode}`);
}

// ═════════════════════════════════════════════
// BATCH TABLE & CSV DOWNLOAD
// ═════════════════════════════════════════════

async function showBatchTable(moduleType, stepId, pipelineIdOverride) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    const pid = pipelineIdOverride || sub?.pipelineId;
    if (!pid) { updateStatus('No pipeline found'); return; }

    // Try batch_results first, then batch_run
    let res = await api(`step/${ws.id}/${pid}/batch_results/table`);
    if (!res.success) {
        res = await api(`step/${ws.id}/${pid}/batch_run/table`);
    }
    if (!res.success) {
        res = await api(`step/${ws.id}/${pid}/${stepId}/table`);
    }

    if (!res.success) {
        updateStatus('No batch results found. Run the batch first.');
        return;
    }

    const { columns, rows, n_rows } = res.data;
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) return;

    // Key columns to show (skip heavy/redundant ones)
    const priorityCols = ['Image_Name', 'n_cells', 'n_interior', 'K', 'K_ds', 'K_Vmin', 'K_gpeak',
                          'r0_fit', 'v_min', 'g_peak', 'reliable', 'R2_damped'];
    const showCols = priorityCols.filter(c => columns.includes(c));
    // Add any remaining scalar columns not in priority
    for (const c of columns) {
        if (!showCols.includes(c) && !['machine_metrics', 'voronoi_metrics', 'dot_centroids'].includes(c)) {
            showCols.push(c);
        }
    }

    // Shorten image_path to just filename
    const displayRows = rows.map(r => {
        const row = { ...r };
        if (row.Image_Name) {
            row.Image_Name = row.Image_Name.replace(/\\/g, '/').split('/').pop();
        }
        return row;
    });

    const tableHtml = `
        <div style="width:100%;height:100%;display:flex;flex-direction:column;overflow:hidden">
            <div style="padding:6px 10px;font-size:var(--fs-sm);font-weight:700;color:var(--text-secondary);border-bottom:2px solid var(--chrome-border);flex-shrink:0;background:var(--surface-1);display:flex;align-items:center;justify-content:space-between">
                <span>Batch Results — ${n_rows} images</span>
                <button class="btn btn-default" onclick="downloadBatchCSV('${moduleType}','${stepId}')" style="height:22px;font-size:var(--fs-xs)">💾 CSV</button>
            </div>
            <div style="flex:1;overflow:auto">
                <table class="batch-table">
                    <thead>
                        <tr>${showCols.map(c => `<th>${c.replace('Image_Name', 'File')}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${displayRows.map(r => `<tr>${showCols.map(c => {
                            let v = r[c];
                            if (v === null || v === undefined) v = '—';
                            else if (typeof v === 'number') v = Number.isInteger(v) ? v : v.toFixed(4);
                            else if (v === true) v = '✓';
                            else if (v === false) v = '✗';
                            const cls = c === 'reliable' ? (r[c] ? 'cell-ok' : 'cell-err') : '';
                            return `<td class="${cls}">${v}</td>`;
                        }).join('')}</tr>`).join('')}
                    </tbody>
                </table>
            </div>
        </div>`;

    gfx.style.background = 'var(--surface-0)';
    gfx.innerHTML = tableHtml;
    updateStatus(`Showing batch results: ${n_rows} images`);
}

function downloadBatchCSV(moduleType, stepId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    if (!sub) return;

    // CSV is in batch_run step results
    const url = `/api/step/${ws.id}/${sub.pipelineId}/batch_run/results/batch_results.csv`;
    const a = document.createElement('a');
    a.href = url;
    a.download = 'batch_results.csv';
    a.click();
}

// ═════════════════════════════════════════════
// ON-DEMAND PLOT GENERATION (ANSYS Insert Result)
// ═════════════════════════════════════════════

async function insertPlot(moduleType, stepId, plotType) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    if (!sub) return;
    const pipelineId = sub.pipelineId;

    // Update status
    const statusEl = document.getElementById(`plotStatus-${sub.activeTreeItem?.id}`);
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-running)">Generating ${plotType}...</span>`;
    updateStatus(`Generating plot: ${plotType}...`);

    // Call backend to generate plot on demand
    const plotBody = { plot_type: plotType };
    // Pass PT-specific params (e.g., track IDs for MSD curves)
    if (stepId === 'particle_tracking' && sub._localParams) {
        const msdIds = sub._localParams['pt-advanced']?.msd_track_ids;
        if (msdIds) plotBody.msd_track_ids = msdIds;
    }
    const res = await api(`step/${ws.id}/${pipelineId}/${stepId}/plot`, 'POST', plotBody);

    if (res.success) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Generated</span>`;
        // Show in Graphics column
        showResultImage(res.data.url, res.data.filename);
        updateStatus(`Showing: ${plotType}`);
    } else {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${res.error}</span>`;
        updateStatus(`❌ ${res.error}`);
    }
}

function loadResult(moduleType, stepId, resultName) {
    // Legacy fallback — try to find matching result file
    showResultImage(``, resultName);
}

// ═════════════════════════════════════════════
// FILE IMPORT (for data import in module settings)
// ═════════════════════════════════════════════

// ── Fluorophore wavelength lookup table (from FPbase / Thermo Fisher) ──
const FLUOROPHORE_DB = {
    'GFP':        { ex: 395, em: 509 },
    'EGFP':       { ex: 488, em: 507 },
    'mEmerald':   { ex: 487, em: 509 },
    'YFP':        { ex: 514, em: 527 },
    'EYFP':       { ex: 514, em: 527 },
    'mVenus':     { ex: 515, em: 528 },
    'CFP':        { ex: 434, em: 477 },
    'ECFP':       { ex: 439, em: 476 },
    'mCerulean':  { ex: 433, em: 475 },
    'BFP':        { ex: 383, em: 448 },
    'EBFP':       { ex: 380, em: 440 },
    'RFP':        { ex: 558, em: 583 },
    'DsRed':      { ex: 558, em: 583 },
    'mCherry':    { ex: 587, em: 610 },
    'tdTomato':   { ex: 554, em: 581 },
    'mStrawberry':{ ex: 574, em: 596 },
    'mRFP':       { ex: 584, em: 607 },
    'Alexa 488':  { ex: 490, em: 525 },
    'Alexa 546':  { ex: 556, em: 573 },
    'Alexa 568':  { ex: 578, em: 603 },
    'Alexa 594':  { ex: 590, em: 617 },
    'Alexa 647':  { ex: 650, em: 668 },
    'DAPI':       { ex: 360, em: 461 },
    'Hoechst':    { ex: 352, em: 461 },
};

function handleProteinTab(e, inputEl) {
    if (e.key !== 'Tab') return;
    const typed = inputEl.value.toLowerCase().trim();
    if (!typed) return; // empty — let Tab move normally

    // Find matching options from the datalist
    const datalist = document.getElementById('protein-list');
    if (!datalist) return;
    const options = [...datalist.options];
    const matches = options.filter(o => o.value.toLowerCase().startsWith(typed));

    if (matches.length > 0) {
        // Auto-complete with first match
        e.preventDefault();
        inputEl.value = matches[0].value;
        inputEl.dispatchEvent(new Event('change', { bubbles: true }));
        // Move focus to next input
        const allInputs = [...inputEl.closest('.settings-form')?.querySelectorAll('input, select') || []];
        const idx = allInputs.indexOf(inputEl);
        if (idx >= 0 && idx < allInputs.length - 1) {
            allInputs[idx + 1].focus();
        }
    }
}

function autoFillWavelengths(selectEl, chIndex) {
    const name = selectEl.value;
    const emInput = document.getElementById(`ch${chIndex}_emission`);
    const exInput = document.getElementById(`ch${chIndex}_excitation`);
    if (!emInput || !exInput) return;
    const db = FLUOROPHORE_DB[name];
    if (db) {
        emInput.value = db.em;
        exInput.value = db.ex;
        // Trigger change events for param saving
        emInput.dispatchEvent(new Event('change', { bubbles: true }));
        exInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

async function selectInputFile(btnEl) {
    const formEl = btnEl.closest('.settings-form');
    const inputEl = formEl?.querySelector('[data-param="input_file"]');

    try {
        const res = await fetch('/api/browse_open', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                mode: 'file',
                title: 'Select Input File',
                filetypes: [['Image Files', '*.tif *.tiff *.nd2 *.czi *.png *.jpg'], ['All Files', '*.*']],
            }),
        });
        const data = await res.json();
        if (!data.success || !data.path) return;

        const path = data.path;

        if (!state._projectOpen) {
            if (inputEl) inputEl.value = path;
            return;
        }

        // Clean downstream results before importing a new file
        const ws = getActiveWorkspace();
        const sub = ws?.subtabs.get(ws?.activeSubtab);
        if (ws && sub) {
            try {
                await api(`pipeline/${ws.id}/${sub.pipelineId}/clean_downstream`, 'POST', {
                    new_file: path,
                });
                console.log('Cleaned downstream before re-import');
            } catch (e) { /* best effort */ }
        }

        // Import data into project
        const importRes = await api('data/import', 'POST', {
            source_path: path,
            mode: 'copy',
        });

        if (importRes.success) {
            if (inputEl) inputEl.value = importRes.data.relative_path;
            updateStatus(`Imported: ${importRes.data.relative_path}`);
            const ws2 = getActiveWorkspace();
            const sub2 = ws2?.subtabs.get(ws2?.activeSubtab);
            if (sub2) {
                if (!sub2._localParams) sub2._localParams = {};
                if (!sub2._localParams['select-movie']) sub2._localParams['select-movie'] = {};
                sub2._localParams['select-movie'].input_file = importRes.data.relative_path;
            }
            if (formEl) debouncedSaveParams(formEl);
        }
    } catch (e) {
        updateStatus(`Browse error: ${e.message}`);
    }
}

async function doDetectionPreview() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    _collectCurrentParams(ws);
    const detParams = sub._localParams?.['fa-det-params'] || {};
    const frameIdx = parseInt(document.getElementById('detPreviewFrameInput')?.value || '0');
    const channel = detParams.detection_channel || 'vinculin';

    _setStatusBox('detPreviewStatus', `<span style="color:var(--status-running)">⏳ Running CellFADE on frame ${frameIdx}...</span>`);

    const detForm = document.querySelector(`[data-section="fa-det-params"]`);
    if (detForm) await saveParamsNow(detForm);

    // Store which subtab this request belongs to (survives tab switches)
    const targetSubId = sub.id;

    try {
        const res = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/detection/preview?frame=${frameIdx}&channel=${channel}`);
        const data = await res.json();

        // Store result on the subtab — persists across tab switches
        const targetSub = ws.subtabs.get(targetSubId);
        if (targetSub) {
            targetSub._detPreviewResult = {
                image: data.success ? data.image : null,
                nFA: data.n_detections || 0,
                frame: frameIdx,
                channel,
                elapsed: data.elapsed,
                warning: data.warning,
                error: data.success ? null : data.error,
            };
        }

        // Update DOM only if we're still on the same tab
        const currentSub = ws.subtabs.get(ws.activeSubtab);
        if (currentSub?.id === targetSubId) {
            if (data.success) {
                _showDetectionGraphics(data.image, data.n_detections, frameIdx, channel, data.warning);
                const nFA = data.n_detections || 0;
                const warning = data.warning ? `<br><span style="color:var(--status-warning)">${data.warning}</span>` : '';
                _setStatusBox('detPreviewStatus', `
                    <span style="color:var(--status-ok)">✓ Detected ${nFA} focal adhesions on frame ${frameIdx}</span><br>
                    <span style="opacity:.7">Channel:</span> ${channel}<br>
                    <span style="opacity:.7">Time:</span> ${data.elapsed || '?'}s${warning}
                `);
                updateStatus(`✅ Detection preview: ${nFA} FAs on frame ${frameIdx}`);
            } else {
                _setStatusBox('detPreviewStatus', `<span style="color:var(--status-error)">✗ ${data.error}</span>`);
                updateStatus(`❌ Detection preview failed`);
            }
        } else {
            // Tab was switched — result is stored, will restore when user comes back
            updateStatus(`✅ Detection done: ${data.n_detections || 0} FAs (frame ${frameIdx}) — switch back to view`);
        }
    } catch (err) {
        _setStatusBox('detPreviewStatus', `<span style="color:var(--status-error)">✗ ${err.message}</span>`);
    }
}

function _showDetectionGraphics(imageSrc, nFA, frameIdx, channel, warning) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) return;

    gfx.style.background = 'var(--surface-0)';
    gfx.innerHTML = `
        <div style="display:flex;flex-direction:column;height:100%">
            <div style="display:flex;align-items:center;gap:6px;padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);flex-shrink:0">
                <span style="font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px">Detection Preview</span>
                <span style="font-size:var(--fs-xs);color:var(--accent-fastia)">Frame ${frameIdx}</span>
                <div style="flex:1"></div>
                <span style="font-size:var(--fs-xs);color:var(--status-ok);font-weight:600">${nFA} FAs detected</span>
            </div>
            <div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000">
                <img src="${imageSrc}" style="max-width:100%;max-height:100%;object-fit:contain" id="detPreviewImg">
            </div>
            ${warning ? `<div style="padding:4px 10px;font-size:var(--fs-xs);color:var(--status-warning);background:var(--surface-1);border-top:1px solid var(--chrome-border)">${warning}</div>` : ''}
        </div>`;
}

function _showDetectionPreviewFrame(frameIdx) {
    // Show the raw frame in a dedicated preview graphics panel
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) return;
    const pid = sub.pipelineId;

    // Build a simple viewer if not already showing one
    if (!document.getElementById('detPreviewImg')) {
        gfx.style.background = 'var(--surface-0)';
        gfx.innerHTML = `
            <div style="display:flex;flex-direction:column;height:100%">
                <div style="display:flex;align-items:center;gap:6px;padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);flex-shrink:0">
                    <span style="font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px">Detection Preview</span>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary)" id="detPreviewFrameLabel">Frame ${frameIdx}</span>
                    <div style="flex:1"></div>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Click 🔍 Detect to run CellFADE</span>
                </div>
                <div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000">
                    <img id="detPreviewImg" style="max-width:100%;max-height:100%;object-fit:contain">
                </div>
            </div>`;
    }

    // Update frame label
    const label = document.getElementById('detPreviewFrameLabel');
    if (label) label.textContent = `Frame ${frameIdx}`;

    // Fetch raw frame
    fetch(`/api/step/${ws.id}/${pid}/import/preview_frame?frame=${frameIdx}&channel=-1`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const img = document.getElementById('detPreviewImg');
                if (img) img.src = data.image;
            }
        }).catch(() => {});
}

// ── CELL SEGMENTATION PREVIEW ─────────────────

function _updateCellSegMethodFields() {
    const method = document.getElementById('cellSegMethodSelect')?.value || 'otsu';
    const otsuEl = document.getElementById('cellSegOtsuFields');
    const manualEl = document.getElementById('cellSegManualFields');
    const minmaxEl = document.getElementById('cellSegMinMaxFields');
    if (otsuEl) otsuEl.style.display = (method === 'otsu' || method === 'min_max') ? '' : 'none';
    if (manualEl) manualEl.style.display = method === 'manual' ? '' : 'none';
    if (minmaxEl) minmaxEl.style.display = method === 'min_max' ? '' : 'none';
}

async function doCellSegPreview() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    _collectCurrentParams(ws);
    const segParams = sub._localParams?.['cell-seg-params'] || {};
    const frameIdx = parseInt(document.getElementById('cellSegPreviewFrameInput')?.value || '0');
    const channel = segParams.seg_channel || 'vinculin';

    _setStatusBox('cellSegPreviewStatus', `<span style="color:var(--status-running)">⏳ Running cell segmentation on frame ${frameIdx}...</span>`);

    const segForm = document.querySelector(`[data-section="cell-seg-params"]`);
    if (segForm) await saveParamsNow(segForm);

    const targetSubId = sub.id;

    try {
        const method = segParams.seg_method || 'otsu';
        const smoothSigma = segParams.smooth_sigma || 5;
        const globalThreshold = segParams.global_threshold !== 'false';
        const keepLargest = segParams.keep_largest !== 'false';

        let url = `/api/step/${ws.id}/${sub.pipelineId}/detection/cell_seg_preview?frame=${frameIdx}&channel=${channel}`;
        url += `&smooth_sigma=${smoothSigma}&method=${method}&global_threshold=${globalThreshold}&keep_largest=${keepLargest}`;
        // Only send manual_threshold when method is manual
        if (method === 'manual') {
            const mt = segParams.manual_threshold;
            if (mt !== undefined && mt !== '') url += `&manual_threshold=${mt}`;
        }
        // Only send intensity range when method is min_max
        if (method === 'min_max') {
            const imin = segParams.intensity_min;
            const imax = segParams.intensity_max;
            if (imin !== undefined && imin !== '' && Number(imin) > 0) url += `&intensity_min=${imin}`;
            if (imax !== undefined && imax !== '' && Number(imax) > 0) url += `&intensity_max=${imax}`;
        }

        const res = await fetch(url);
        const data = await res.json();

        const targetSub = ws.subtabs.get(targetSubId);
        if (targetSub) {
            targetSub._cellSegPreviewResult = {
                image: data.image || null,
                frame: frameIdx,
                info: data.info || '',
                error: data.error || null,
            };
        }

        if (data.success) {
            _showCellSegGraphics(data.image, frameIdx, data.info || '');
            _setStatusBox('cellSegPreviewStatus', `
                <span style="color:var(--status-ok)">✓ Cell segmentation on frame ${frameIdx}</span><br>
                <span style="opacity:.7">${data.info || ''}</span>
            `);
            updateStatus(`✅ Cell segmentation preview done (frame ${frameIdx})`);
        } else {
            _setStatusBox('cellSegPreviewStatus', `<span style="color:var(--status-error)">✗ ${data.error}</span>`);
            updateStatus(`❌ Cell segmentation preview failed`);
        }
    } catch (err) {
        _setStatusBox('cellSegPreviewStatus', `<span style="color:var(--status-error)">✗ ${err.message}</span>`);
    }
}

function _showCellSegGraphics(imageSrc, frameIdx, info) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) return;

    gfx.style.background = 'var(--surface-0)';
    gfx.innerHTML = `
        <div style="display:flex;flex-direction:column;height:100%">
            <div style="display:flex;align-items:center;gap:6px;padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);flex-shrink:0">
                <span style="font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px">Cell Segmentation Preview</span>
                <span style="font-size:var(--fs-xs);color:var(--accent-fastia)">Frame ${frameIdx}</span>
                <div style="flex:1"></div>
                <span style="font-size:var(--fs-xs);color:var(--status-ok);font-weight:600">${info}</span>
            </div>
            <div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000">
                <img src="${imageSrc}" style="max-width:100%;max-height:100%;object-fit:contain" id="cellSegPreviewImg">
            </div>
        </div>`;
}

function _showCellSegPreviewFrame(frameIdx) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) return;
    const pid = sub.pipelineId;

    if (!document.getElementById('cellSegPreviewImg')) {
        gfx.style.background = 'var(--surface-0)';
        gfx.innerHTML = `
            <div style="display:flex;flex-direction:column;height:100%">
                <div style="display:flex;align-items:center;gap:6px;padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);flex-shrink:0">
                    <span style="font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px">Cell Segmentation Preview</span>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary)" id="cellSegPreviewFrameLabel">Frame ${frameIdx}</span>
                    <div style="flex:1"></div>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">Click 🔍 Segment to preview</span>
                </div>
                <div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000">
                    <img id="cellSegPreviewImg" style="max-width:100%;max-height:100%;object-fit:contain">
                </div>
            </div>`;
    }

    const label = document.getElementById('cellSegPreviewFrameLabel');
    if (label) label.textContent = `Frame ${frameIdx}`;

    fetch(`/api/step/${ws.id}/${pid}/import/preview_frame?frame=${frameIdx}&channel=-1`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const img = document.getElementById('cellSegPreviewImg');
                if (img) img.src = data.image;
            }
        }).catch(() => {});
}

let _inspectorData = null; // { df: [{track_id, group, assembly_rate, ...}], filtered: [...] }

async function initTrackInspector() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const statsEl = document.getElementById('inspectorQuickStats');
    const pid = sub.pipelineId;

    // Load df_classified.csv via backend
    try {
        const res = await fetch(`/api/step/${ws.id}/${pid}/classification/results/df_classified.csv`);
        if (!res.ok) {
            if (statsEl) statsEl.innerHTML = `<span style="color:var(--status-warning)">⚠ Run Classification first.</span>`;
            return;
        }
        const csvText = await res.text();

        // Parse CSV
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        const rows = [];
        for (let i = 1; i < lines.length; i++) {
            const vals = lines[i].split(',');
            const row = {};
            headers.forEach((h, j) => row[h.trim()] = vals[j]?.trim() || '');
            rows.push(row);
        }

        _inspectorData = { all: rows, filtered: rows };

        // Populate group filter
        const groupSelect = document.getElementById('inspectorGroupFilter');
        if (groupSelect && rows.length > 0 && rows[0].group !== undefined) {
            const groups = [...new Set(rows.map(r => r.group))].filter(Boolean).sort();
            groupSelect.innerHTML = `<option value="all">All Groups (${rows.length})</option>` +
                groups.map(g => {
                    const n = rows.filter(r => r.group === g).length;
                    return `<option value="${g}">${g} (${n})</option>`;
                }).join('');
        }

        filterInspectorTracks();

        if (statsEl) statsEl.innerHTML = `<span style="color:var(--status-ok)">✓ ${rows.length} classified tracks loaded</span><br>` +
            `<span style="opacity:.7">Select a track and click Inspect.</span>`;

    } catch (e) {
        if (statsEl) statsEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

function filterInspectorTracks() {
    if (!_inspectorData) return;
    const groupVal = document.getElementById('inspectorGroupFilter')?.value || 'all';

    if (groupVal === 'all') {
        _inspectorData.filtered = _inspectorData.all;
    } else {
        _inspectorData.filtered = _inspectorData.all.filter(r => r.group === groupVal);
    }

    const trackSelect = document.getElementById('inspectorTrackSelect');
    if (trackSelect) {
        trackSelect.innerHTML = `<option value="">— ${_inspectorData.filtered.length} tracks —</option>` +
            _inspectorData.filtered.map((r, i) => {
                const tid = r.track_id || i;
                const len = r.track_length || '?';
                const grp = r.group || '';
                return `<option value="${i}">${grp} · Track ${tid} (${len} frames)</option>`;
            }).join('');
    }
}

function onInspectorTrackChange() {
    const select = document.getElementById('inspectorTrackSelect');
    const btn = document.getElementById('inspectBtn');
    const statsEl = document.getElementById('inspectorQuickStats');
    const idx = parseInt(select?.value);

    if (btn) btn.disabled = isNaN(idx);

    if (!isNaN(idx) && _inspectorData?.filtered[idx]) {
        const r = _inspectorData.filtered[idx];
        const asm = parseFloat(r.assembly_rate);
        const dsm = parseFloat(r.disassembly_rate);
        const r2a = parseFloat(r.assembly_r_squared);
        const r2d = parseFloat(r.disassembly_r_squared);
        let html = `<span style="color:var(--accent-fastia);font-weight:600">Track ${r.track_id || idx}</span> · ${r.group || 'N/A'}<br>`;
        html += `<span style="opacity:.7">Length:</span> ${r.track_length || '?'} frames<br>`;
        html += `<span style="opacity:.7">Assembly:</span> ${isNaN(asm) ? 'N/A' : asm.toFixed(4)} min⁻¹`;
        if (!isNaN(r2a)) html += ` (R²=${r2a.toFixed(3)})`;
        html += `<br>`;
        html += `<span style="opacity:.7">Disassembly:</span> ${isNaN(dsm) ? 'N/A' : dsm.toFixed(4)} min⁻¹`;
        if (!isNaN(r2d)) html += ` (R²=${r2d.toFixed(3)})`;
        if (statsEl) statsEl.innerHTML = html;
    }
}

function inspectPrevTrack() {
    const select = document.getElementById('inspectorTrackSelect');
    if (!select) return;
    const cur = parseInt(select.value);
    if (isNaN(cur) || cur <= 0) return;
    select.value = cur - 1;
    onInspectorTrackChange();
    inspectSelectedTrack();
}

function inspectNextTrack() {
    const select = document.getElementById('inspectorTrackSelect');
    if (!select || !_inspectorData) return;
    const cur = parseInt(select.value);
    const next = isNaN(cur) ? 0 : cur + 1;
    if (next >= _inspectorData.filtered.length) return;
    select.value = next;
    onInspectorTrackChange();
    inspectSelectedTrack();
}

async function inspectSelectedTrack() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub || !_inspectorData) return;

    const select = document.getElementById('inspectorTrackSelect');
    const idx = parseInt(select?.value);
    if (isNaN(idx)) return;

    const r = _inspectorData.filtered[idx];
    if (!r) return;

    const trackId = parseInt(r.track_id) || idx;
    const pid = sub.pipelineId;

    updateStatus(`Generating fit plot for Track ${trackId}...`);

    // Call backend to generate individual track fit plot
    const res = await api(`step/${ws.id}/${pid}/kinetics/plot`, 'POST', {
        plot_type: 'indiv_track_fit',
        track_index: parseInt(trackId),
    });

    if (res.success) {
        showResultImage(res.data.url, `Track ${trackId} — Kinetic Fit`);
        updateStatus(`✅ Track ${trackId} kinetic fit`);

        // Add to Individual Results if not already there
        if (!sub.insertedResults) sub.insertedResults = [];
        const existingIdx = sub.insertedResults.findIndex(r => r.plotType === `indiv_track_${trackId}`);
        if (existingIdx >= 0) {
            sub.insertedResults[existingIdx].url = res.data.url;
            sub.insertedResults[existingIdx].status = 'done';
        } else {
            sub.insertedResults.push({
                plotType: `indiv_track_${trackId}`,
                label: `Track ${trackId} (${r.group || '?'})`,
                icon: '🔬',
                url: res.data.url,
                status: 'done',
            });
        }
        renderModuleTree(sub);
    } else {
        updateStatus(`❌ ${res.error}`);
    }
}

function showClassificationResultsPanel() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const statusEl = document.getElementById('classResultsStatus');
    if (!statusEl) return;

    const pid = sub.pipelineId;
    api(`step/${ws.id}/${pid}/classification/results`)
        .then(res => {
            if (res.success && res.data.length) {
                const csvFiles = res.data.filter(f => f.name.endsWith('.csv'));
                const npyFiles = res.data.filter(f => f.name.endsWith('.npy'));
                const csvNames = csvFiles.map(f => f.name).join(', ');
                let html = `<span style="color:var(--status-ok)">✓ Classification results found</span><br>`;
                html += `<span style="opacity:.7">Files: ${csvNames}</span><br>`;

                // Try to read df_classified summary
                const classified = csvFiles.find(f => f.name === 'df_classified.csv');
                if (classified) {
                    html += `<span style="opacity:.7">${(classified.size_bytes / 1024).toFixed(0)} KB classified data</span><br>`;
                }
                html += `<span style="opacity:.7">Use Insert Results to generate plots.</span>`;
                statusEl.innerHTML = html;
            } else {
                statusEl.innerHTML = `<span style="color:var(--status-warning)">⚠ No classification results. Run Classification first.</span>`;
            }
        })
        .catch(() => {
            statusEl.innerHTML = `<span style="color:var(--status-error)">✗ Cannot check results</span>`;
        });
}

function showTrackingResultsPanel() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const statusEl = document.getElementById('trackResultsStatus');
    if (!statusEl) return;

    const pid = sub.pipelineId;
    const channel = sub?._localParams?.['track-params']?.detection_channel ||
                    sub?._localParams?.['fa-det-params']?.detection_channel || 'vinculin';
    // Probe frame 0 of tracking overlay
    fetch(`/api/step/${ws.id}/${pid}/tracking/results_frame?frame=0&channel=${channel}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Tracking results found</span><br>` +
                    `<span style="opacity:.7">${data.n_tracks} tracks · ${data.n_active} active on frame 0</span><br>` +
                    `<span style="opacity:.7">Click Render to pre-compute all frames.</span>`;
            } else {
                statusEl.innerHTML = `<span style="color:var(--status-warning)">⚠ ${data.error || 'No results'}</span>`;
            }
        })
        .catch(() => {
            statusEl.innerHTML = `<span style="color:var(--status-error)">✗ Cannot reach server</span>`;
        });
}

async function renderTrackingOverlay() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const pid = sub.pipelineId;
    const nFrames = sub._movieInfo?.n_frames || 91;
    const channel = sub?._localParams?.['track-params']?.detection_channel ||
                    sub?._localParams?.['fa-det-params']?.detection_channel || 'vinculin';

    const btn = document.getElementById('renderTrackBtn');
    const progressDiv = document.getElementById('trackRenderProgress');
    const fillEl = document.getElementById('trackRenderFill');
    const labelEl = document.getElementById('trackRenderLabel');
    const statusEl = document.getElementById('trackResultsStatus');

    if (btn) { btn.disabled = true; btn.textContent = '⏳ Rendering...'; }
    if (progressDiv) progressDiv.style.display = '';

    let rendered = 0;
    const t0 = performance.now();

    for (let f = 0; f < nFrames; f++) {
        try {
            await fetch(`/api/step/${ws.id}/${pid}/tracking/results_frame?frame=${f}&channel=${channel}`);
        } catch (e) { /* skip */ }

        rendered = f + 1;
        const pct = Math.round(rendered / nFrames * 100);
        if (fillEl) fillEl.style.width = `${pct}%`;
        if (labelEl) labelEl.textContent = `Frame ${rendered}/${nFrames} (${pct}%)`;
    }

    const elapsed = ((performance.now() - t0) / 1000).toFixed(1);

    if (btn) { btn.disabled = false; btn.textContent = '🎬 Render Trajectories'; }
    if (fillEl) fillEl.style.width = '100%';
    if (fillEl) fillEl.style.background = 'var(--status-ok)';
    if (labelEl) labelEl.textContent = `Done — ${nFrames} frames in ${elapsed}s`;
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ All ${nFrames} frames cached</span><br>` +
        `<span style="opacity:.7">${elapsed}s render time</span>`;

    // Auto-launch player
    showTrackingResultsPlayer();
    updateStatus(`✅ Trajectories rendered: ${nFrames} frames`);
}

let _trackResultsFrame = 0, _trackResultsPlaying = false, _trackResultsTimer = null, _trackResultsPid = '', _trackResultsTotal = 0;

function showTrackingResultsPlayer() {
    if (_trackResultsTimer) {
        clearInterval(_trackResultsTimer);
        _trackResultsTimer = null;
        _trackResultsPlaying = false;
    }

    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) return;

    const nFrames = sub._movieInfo?.n_frames || 91;
    const pid = sub.pipelineId;

    gfx.style.background = 'var(--surface-0)';
    gfx.innerHTML = `
        <div class="movie-player" style="display:flex;flex-direction:column;height:100%;font-family:var(--font-ui)">
            <div style="display:flex;align-items:center;gap:6px;padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);flex-shrink:0">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-weight:700;text-transform:uppercase;letter-spacing:.5px">Trajectory Overlay</span>
                <span style="font-size:var(--fs-xs);color:var(--accent-fastia);font-weight:600" id="trackResFACount"></span>
            </div>
            <div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000" id="movieCanvas">
                <img id="movieFrameImg" style="width:100%;height:100%;object-fit:contain;display:none">
                <div id="moviePlaceholder" style="color:rgba(255,255,255,.3);font-size:var(--fs-sm);text-align:center">
                    <div style="font-size:32px;margin-bottom:8px;opacity:.4">📈</div>
                    <div>Loading trajectories...</div>
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:0;flex-shrink:0;background:linear-gradient(180deg,var(--surface-2),var(--surface-1));border-top:1px solid rgba(255,255,255,.04)">
                <div style="padding:6px 10px 2px;display:flex;align-items:center;gap:8px">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono);min-width:32px" id="trackResFrameNum">0</span>
                    <input type="range" min="0" max="${nFrames - 1}" value="0" style="flex:1;accent-color:var(--accent-fastia);height:4px" id="trackResSlider" oninput="_seekTrackResults(parseInt(this.value))">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">${nFrames - 1}</span>
                </div>
                <div style="padding:2px 10px 6px;display:flex;align-items:center;gap:6px">
                    <button onclick="_trackResultsStep(-1)" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:12px;padding:2px 4px">⏮</button>
                    <button onclick="_toggleTrackResultsPlay()" id="trackResPlayBtn" style="background:var(--accent-fastia);border:none;color:#fff;cursor:pointer;font-size:11px;padding:3px 10px;border-radius:var(--r-sm);font-weight:700">▶</button>
                    <button onclick="_trackResultsStep(1)" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:12px;padding:2px 4px">⏭</button>
                    <div style="flex:1"></div>
                    <select id="trackResSpeed" style="font-size:var(--fs-xs);background:var(--surface-1);color:var(--text-secondary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:1px 4px">
                        <option value="200">5 fps</option>
                        <option value="100" selected>10 fps</option>
                        <option value="50">20 fps</option>
                    </select>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">Frame <span id="trackResFrameInfo">0</span>/${nFrames}</span>
                </div>
            </div>
        </div>`;

    _trackResultsFrame = 0;
    _trackResultsPlaying = false;
    _trackResultsPid = pid;
    _trackResultsTotal = nFrames;
    _seekTrackResults(0);
}

function _seekTrackResults(frame) {
    _trackResultsFrame = frame;
    const numEl = document.getElementById('trackResFrameNum');
    const infoEl = document.getElementById('trackResFrameInfo');
    if (numEl) numEl.textContent = frame;
    if (infoEl) infoEl.textContent = frame;
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    const channel = sub?._localParams?.['fa-det-params']?.detection_channel || 'vinculin';
    fetch(`/api/step/${ws.id}/${_trackResultsPid}/tracking/results_frame?frame=${frame}&channel=${channel}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                _displayFrame(data.image);
                const faEl = document.getElementById('trackResFACount');
                if (faEl) faEl.textContent = `${data.n_active} active tracks`;
            }
        }).catch(err => {
            console.error('_seekTrackResults error:', err);
        });
}

function _trackResultsStep(dir) {
    _trackResultsFrame = Math.max(0, Math.min(_trackResultsFrame + dir, _trackResultsTotal - 1));
    const slider = document.getElementById('trackResSlider');
    if (slider) slider.value = _trackResultsFrame;
    _seekTrackResults(_trackResultsFrame);
}

function _toggleTrackResultsPlay() {
    _trackResultsPlaying = !_trackResultsPlaying;
    const btn = document.getElementById('trackResPlayBtn');
    if (_trackResultsPlaying) {
        if (btn) btn.textContent = '⏸';
        const speed = parseInt(document.getElementById('trackResSpeed')?.value || '100');
        _trackResultsTimer = setInterval(() => {
            const slider = document.getElementById('trackResSlider');
            if (!slider) {
                clearInterval(_trackResultsTimer);
                _trackResultsPlaying = false;
                return;
            }
            _trackResultsFrame = (_trackResultsFrame + 1) % _trackResultsTotal;
            slider.value = _trackResultsFrame;
            _seekTrackResults(_trackResultsFrame);
        }, speed);
    } else {
        if (btn) btn.textContent = '▶';
        clearInterval(_trackResultsTimer);
    }
}

function showDetectionResultsPanel() {
    // Check if detection results exist and update the status box
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const statusEl = document.getElementById('renderStatus');
    if (!statusEl) return;

    // Check if results exist via a quick probe of frame 0
    const pid = sub.pipelineId;
    const channel = sub?._localParams?.['fa-det-params']?.detection_channel || 'vinculin';
    fetch(`/api/step/${ws.id}/${pid}/detection/results_frame?frame=0&channel=${channel}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const nFrames = sub._movieInfo?.n_frames || '?';
                statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Detection results found</span><br>` +
                    `<span style="opacity:.7">${data.n_fa} FAs on frame 0 · ${nFrames} frames total</span>`;
            } else {
                statusEl.innerHTML = `<span style="color:var(--status-warning)">⚠ ${data.error || 'No results yet'}</span>`;
            }
        })
        .catch(() => {
            statusEl.innerHTML = `<span style="color:var(--status-error)">✗ Cannot reach server</span>`;
        });
}

let _renderAbort = false;

async function renderDetectionOverlay() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const pid = sub.pipelineId;
    const nFrames = sub._movieInfo?.n_frames || 91;
    const channel = sub?._localParams?.['fa-det-params']?.detection_channel || 'vinculin';

    // Show progress, disable button
    const btn = document.getElementById('renderOverlayBtn');
    const progressDiv = document.getElementById('renderProgress');
    const fillEl = document.getElementById('renderProgressFill');
    const labelEl = document.getElementById('renderProgressLabel');
    const statusEl = document.getElementById('renderStatus');

    if (btn) { btn.disabled = true; btn.textContent = '⏳ Rendering...'; }
    if (progressDiv) progressDiv.style.display = '';
    _renderAbort = false;

    let rendered = 0;
    let totalFAs = 0;
    const t0 = performance.now();

    for (let f = 0; f < nFrames; f++) {
        if (_renderAbort) break;

        try {
            const res = await fetch(`/api/step/${ws.id}/${pid}/detection/results_frame?frame=${f}&channel=${channel}`);
            const data = await res.json();
            if (data.success) {
                totalFAs += data.n_fa || 0;
            }
        } catch (e) { /* skip frame */ }

        rendered = f + 1;
        const pct = Math.round(rendered / nFrames * 100);
        if (fillEl) fillEl.style.width = `${pct}%`;
        if (labelEl) labelEl.textContent = `Frame ${rendered}/${nFrames} (${pct}%)`;
    }

    const elapsed = ((performance.now() - t0) / 1000).toFixed(1);

    if (btn) { btn.disabled = false; btn.textContent = '🎬 Render Overlay'; }

    if (_renderAbort) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-warning)">⏹ Stopped after ${rendered} frames</span>`;
        if (labelEl) labelEl.textContent = `Stopped at ${rendered}/${nFrames}`;
    } else {
        if (fillEl) fillEl.style.width = '100%';
        if (fillEl) fillEl.style.background = 'var(--status-ok)';
        if (labelEl) labelEl.textContent = `Done — ${nFrames} frames in ${elapsed}s`;
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ All ${nFrames} frames cached</span><br>` +
            `<span style="opacity:.7">${totalFAs.toLocaleString()} total FAs · ${elapsed}s · avg ${(totalFAs / nFrames).toFixed(0)} FAs/frame</span>`;

        // Auto-launch the video player in graphics panel
        showDetectionResultsPlayer();
        updateStatus(`✅ Overlay rendered: ${nFrames} frames, ${totalFAs.toLocaleString()} FAs`);
    }
}

function showDetectionResultsPlayer() {
    // Clear any orphaned play timer from a previous view
    if (_detResultsTimer) {
        clearInterval(_detResultsTimer);
        _detResultsTimer = null;
        _detResultsPlaying = false;
    }

    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) { console.error('showDetectionResultsPlayer: no sub'); return; }
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfx) { console.error('showDetectionResultsPlayer: no gfx panel'); return; }

    const movieInfo = sub._movieInfo || {};
    const nFrames = movieInfo.n_frames || 91;
    const pid = sub.pipelineId;
    console.log(`showDetectionResultsPlayer: pid=${pid}, nFrames=${nFrames}, wsId=${ws.id}`);

    // Check if detection results exist
    gfx.style.background = 'var(--surface-0)';
    gfx.innerHTML = `
        <div class="movie-player" style="display:flex;flex-direction:column;height:100%;font-family:var(--font-ui)">
            <div style="display:flex;align-items:center;gap:6px;padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);box-shadow:inset 0 1px 0 rgba(255,255,255,.03);flex-shrink:0">
                <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-weight:700;text-transform:uppercase;letter-spacing:.5px">Detection Overlay</span>
                <span style="font-size:var(--fs-xs);color:var(--accent-fastia);font-weight:600" id="detResFACount"></span>
                <div style="flex:1"></div>
                <select style="font-size:var(--fs-xs);background:var(--surface-1);color:var(--text-secondary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:2px 6px" onchange="_detResultsMode=this.value;_seekDetResults(_detResultsFrame)">
                    <option value="overlay">Overlay</option>
                    <option value="labels">Labels Only</option>
                </select>
            </div>
            <div style="flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#000" id="movieCanvas">
                <img id="movieFrameImg" style="width:100%;height:100%;object-fit:contain;display:none">
                <div id="moviePlaceholder" style="color:rgba(255,255,255,.3);font-size:var(--fs-sm);text-align:center">
                    <div style="font-size:32px;margin-bottom:8px;opacity:.4">🔬</div>
                    <div>Run Full Stack first to view detection results</div>
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:0;flex-shrink:0;background:linear-gradient(180deg,var(--surface-2),var(--surface-1));border-top:1px solid rgba(255,255,255,.04)">
                <div style="padding:6px 10px 2px;display:flex;align-items:center;gap:8px">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono);min-width:32px" id="detResFrameNum">0</span>
                    <input type="range" min="0" max="${nFrames - 1}" value="0" style="flex:1;accent-color:var(--accent-fastia);height:4px" id="detResSlider" oninput="_seekDetResults(parseInt(this.value))">
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">${nFrames - 1}</span>
                </div>
                <div style="padding:2px 10px 6px;display:flex;align-items:center;gap:6px">
                    <button onclick="_detResultsStep(-1)" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:12px;padding:2px 4px">⏮</button>
                    <button onclick="_toggleDetResultsPlay()" id="detResPlayBtn" style="background:var(--accent-fastia);border:none;color:#fff;cursor:pointer;font-size:11px;padding:3px 10px;border-radius:var(--r-sm);font-weight:700">▶</button>
                    <button onclick="_detResultsStep(1)" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:12px;padding:2px 4px">⏭</button>
                    <div style="flex:1"></div>
                    <select id="detResSpeed" style="font-size:var(--fs-xs);background:var(--surface-1);color:var(--text-secondary);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:1px 4px">
                        <option value="200">5 fps</option>
                        <option value="100" selected>10 fps</option>
                        <option value="50">20 fps</option>
                    </select>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary);font-family:var(--font-mono)">Frame <span id="detResFrameInfo">0</span>/${nFrames}</span>
                </div>
            </div>
        </div>`;

    // Try loading first frame overlay
    _detResultsFrame = 0;
    _detResultsMode = 'overlay';
    _detResultsPlaying = false;
    _detResultsPid = pid;
    _detResultsTotal = nFrames;
    _seekDetResults(0);
}

let _detResultsFrame = 0, _detResultsMode = 'overlay', _detResultsPlaying = false, _detResultsTimer = null, _detResultsPid = '', _detResultsTotal = 0;

function _seekDetResults(frame) {
    _detResultsFrame = frame;
    const numEl = document.getElementById('detResFrameNum');
    const infoEl = document.getElementById('detResFrameInfo');
    if (numEl) numEl.textContent = frame;
    if (infoEl) infoEl.textContent = frame;
    const ws = getActiveWorkspace();
    if (!ws) { console.error('_seekDetResults: no workspace'); return; }
    if (!_detResultsPid) { console.error('_seekDetResults: no pipeline ID'); return; }
    // Fetch pre-computed detection overlay frame (fast — reads saved results)
    const sub = ws.subtabs.get(ws.activeSubtab);
    const channel = sub?._localParams?.['fa-det-params']?.detection_channel || 'vinculin';
    const url = `/api/step/${ws.id}/${_detResultsPid}/detection/results_frame?frame=${frame}&channel=${channel}`;
    console.log('_seekDetResults fetching:', url);
    fetch(url)
        .then(r => r.json())
        .then(data => {
            console.log('_seekDetResults response:', data.success, 'has_image:', !!data.image, 'error:', data.error, 'n_fa:', data.n_fa);
            if (data.success) {
                _displayFrame(data.image);
                const faEl = document.getElementById('detResFACount');
                if (faEl) faEl.textContent = `${data.n_fa} FAs`;
            } else if (data.error) {
                console.error('results_frame error:', data.error);
                const ph = document.getElementById('moviePlaceholder');
                if (ph) { ph.style.display = ''; ph.querySelector('div:last-child').textContent = data.error; }
            }
        }).catch(err => {
            console.error('_seekDetResults fetch error:', err, 'url:', url);
        });
}

function _detResultsStep(dir) {
    _detResultsFrame = Math.max(0, Math.min(_detResultsFrame + dir, _detResultsTotal - 1));
    const slider = document.getElementById('detResSlider');
    if (slider) slider.value = _detResultsFrame;
    _seekDetResults(_detResultsFrame);
}

function _toggleDetResultsPlay() {
    _detResultsPlaying = !_detResultsPlaying;
    const btn = document.getElementById('detResPlayBtn');
    if (_detResultsPlaying) {
        if (btn) btn.textContent = '⏸';
        const speed = parseInt(document.getElementById('detResSpeed')?.value || '100');
        _detResultsTimer = setInterval(() => {
            // Auto-stop if player elements are gone (user navigated away)
            const slider = document.getElementById('detResSlider');
            if (!slider) {
                clearInterval(_detResultsTimer);
                _detResultsPlaying = false;
                return;
            }
            _detResultsFrame = (_detResultsFrame + 1) % _detResultsTotal;
            slider.value = _detResultsFrame;
            _seekDetResults(_detResultsFrame);
        }, speed);
    } else {
        if (btn) btn.textContent = '▶';
        clearInterval(_detResultsTimer);
    }
}

async function cvPersistState(sub) {
    if (!sub || !state._projectOpen) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    const payload = {
        cvState: sub._cvState || {},
        cvLoadInfo: sub._cvLoadInfo || null,
        cvOriginalInfo: sub._cvOriginalInfo || null,
        cvFeatureIds: sub._cvFeatureIds || null,
        cvScopeIds: sub._cvScopeIds || null,
        cvFeatures: (sub.cvFeatures || []).map(f => ({
            id: f.id, type: f.type, group: f.group, label: f.label,
            icon: f.icon, params: f.params, suppressed: f.suppressed,
            frozen: f.frozen || false, _status: f._status || 'ok',
            _backendId: f._backendId || null,
        })),
    };
    try {
        await fetch(`/api/step/${ws.id}/${sub.pipelineId}/cellvisia/params`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ params: { cellvisia: payload } }),
        });
    } catch (e) { console.warn('[CellVisia] persist failed:', e); }
}

async function cvRestoreState() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub || !state._projectOpen) return false;
    if (sub._cvLoadInfo) return true;
    if (sub._cvRestoreAttempted) return false;
    sub._cvRestoreAttempted = true;
    try {
        const res = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/cellvisia/params`);
        const data = await res.json();
        const saved = data?.data?.cellvisia || data?.cellvisia;
        if (!saved?.cvState?.filePath) return false;

        sub._cvState = saved.cvState;
        sub._cvLoadInfo = saved.cvLoadInfo;
        sub._cvOriginalInfo = saved.cvOriginalInfo || saved.cvLoadInfo;
        sub._cvFeatureIds = saved.cvFeatureIds;
        sub._cvScopeIds = saved.cvScopeIds || {};

        // Reconstruct backend — re-run load (creates Source chain)
        const loadRes = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/load`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: saved.cvState.filePath, format: saved.cvState.format || 'auto' }),
        });
        const loadData = await loadRes.json();
        if (!loadData.success) return false;

        sub._cvLoadInfo = loadData;
        if (!sub._cvOriginalInfo) sub._cvOriginalInfo = loadData;
        sub._cvFeatureIds = { load: loadData.load_id, channel: loadData.channel_id, meta: loadData.meta_id };

        // Re-apply channel assignment
        if (saved.cvState.channelNames && sub._cvFeatureIds.channel) {
            await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${sub._cvFeatureIds.channel}/params`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ channel_names: saved.cvState.channelNames, channel_roles: saved.cvState.channelRoles || [] }),
            });
        }
        // Re-apply metadata
        if (sub._cvFeatureIds.meta) {
            const mp = {};
            if (saved.cvState.pixel_size_um) mp.pixel_size_um = saved.cvState.pixel_size_um;
            if (saved.cvState.dt_s) mp.dt_s = saved.cvState.dt_s;
            if (saved.cvState.dz_um) mp.dz_um = saved.cvState.dz_um;
            if (Object.keys(mp).length) {
                await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${sub._cvFeatureIds.meta}/params`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(mp),
                });
            }
        }

        // Restore scope fixed settings (channels, temporal, format)
        sub._cvScopeIds = {};
        const sc = saved.cvState;
        if (sc.scopeKeepChannels) {
            const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ feature_type: 'channel_select', params: { keep: sc.scopeKeepChannels.join(',') } }),
            });
            const d = await r.json();
            if (d.success) sub._cvScopeIds.channels = d.backend_id;
        }
        if (sc.scopeFrameStart !== undefined || sc.scopeFrameEnd !== undefined) {
            const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ feature_type: 'frame_range', params: { start: sc.scopeFrameStart || 0, end: sc.scopeFrameEnd ?? -1 } }),
            });
            const d = await r.json();
            if (d.success) sub._cvScopeIds.frameRange = d.backend_id;
        }
        if (sc.scopeSubsample > 1) {
            const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ feature_type: 'frame_subsample', params: { every: sc.scopeSubsample } }),
            });
            const d = await r.json();
            if (d.success) sub._cvScopeIds.subsample = d.backend_id;
        }
        if (sc.scopeBitDepth) {
            const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ feature_type: 'bit_depth', params: { target: sc.scopeBitDepth } }),
            });
            const d = await r.json();
            if (d.success) sub._cvScopeIds.bitDepth = d.backend_id;
        }

        // Restore inserted features (Scope, Pre-processing, etc.)
        if (saved.cvFeatures?.length) {
            sub.cvFeatures = [];
            for (const sf of saved.cvFeatures) {
                // Re-add to backend engine (chains after current terminal)
                const addRes = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ feature_type: sf.type, params: sf.params, suppressed: sf.suppressed || false }),
                });
                const addData = await addRes.json();
                sf._backendId = addData.success ? addData.backend_id : null;
                sub.cvFeatures.push(sf);
            }
            // Update feature counter so new inserts don't collide
            const maxId = Math.max(0, ...sub.cvFeatures.map(f => parseInt(f.id.replace('cvf-','')) || 0));
            _cvFeatureCounter = Math.max(_cvFeatureCounter, maxId);
        }

        showCellVisiaPlayer();
        renderModuleTree(sub);
        await cvRefreshViewer();
        updateStatus('✅ CellVisia state restored');
        return true;
    } catch (e) { console.warn('[CellVisia] restore failed:', e); return false; }
}

async function cvRefreshViewer() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    try {
        const res = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/evaluate`);
        const evalData = await res.json();
        if (evalData.success) {
            const prevNFrames = sub._cvLoadInfo?.n_frames;
            const prevNCh = sub._cvLoadInfo?.n_channels;
            sub._cvLoadInfo = { ...sub._cvLoadInfo, ...evalData };

            if (prevNFrames !== evalData.n_frames || prevNCh !== evalData.n_channels) {
                showCellVisiaPlayer();
            } else if (_moviePlayerState && _cvActiveGfxTab !== 'input') {
                // Only update featureId if not viewing Input
                _moviePlayerState.featureId = evalData.feature_id;
                _frameCache.clear();
                seekMovieFrame(_moviePlayerState.frame || 0);
            }
        }
    } catch (e) { console.warn('[CellVisia] refresh failed:', e); }
}

async function cvRebuildPipeline() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._cvState?.filePath) return false;
    const sc = sub._cvState;

    // Stop player immediately to prevent stale feature_id requests
    if (_moviePlayerState?.playTimer) {
        clearInterval(_moviePlayerState.playTimer);
        _moviePlayerState.playing = false;
        _moviePlayerState.playTimer = null;
    }
    _cvRebuilding = true;

    // 1. Rebuild Source chain
    const loadRes = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/load`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ path: sc.filePath, format: sc.format || 'auto' }),
    });
    const loadData = await loadRes.json();
    if (!loadData.success) { console.error('[CellVisia rebuild] load failed:', loadData.error); return false; }
    sub._cvFeatureIds = { load: loadData.load_id, channel: loadData.channel_id, meta: loadData.meta_id };

    // 2. Re-apply channel assignment
    if (sc.channelNames) {
        await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${sub._cvFeatureIds.channel}/params`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ channel_names: sc.channelNames, channel_roles: sc.channelRoles || [] }),
        });
    }
    // Re-apply metadata
    const mp = {};
    if (sc.pixel_size_um) mp.pixel_size_um = sc.pixel_size_um;
    if (sc.dt_s) mp.dt_s = sc.dt_s;
    if (sc.dz_um) mp.dz_um = sc.dz_um;
    if (Object.keys(mp).length) {
        await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${sub._cvFeatureIds.meta}/params`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(mp),
        });
    }

    // 3. Scope fixed settings (in order: channels → temporal → format)
    sub._cvScopeIds = {};
    if (sc.scopeKeepChannels && sc.scopeKeepChannels.length > 0) {
        const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ feature_type: 'channel_select', params: { keep: sc.scopeKeepChannels.join(',') } }),
        });
        const d = await r.json();
        if (d.success) sub._cvScopeIds.channels = d.backend_id;
    }
    if (sc.scopeFrameStart !== undefined || sc.scopeFrameEnd !== undefined) {
        const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ feature_type: 'frame_range', params: { start: sc.scopeFrameStart || 0, end: sc.scopeFrameEnd ?? -1 } }),
        });
        const d = await r.json();
        if (d.success) sub._cvScopeIds.frameRange = d.backend_id;
    }
    if (sc.scopeSubsample > 1) {
        const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ feature_type: 'frame_subsample', params: { every: sc.scopeSubsample } }),
        });
        const d = await r.json();
        if (d.success) sub._cvScopeIds.subsample = d.backend_id;
    }
    if (sc.scopeBitDepth) {
        const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ feature_type: 'bit_depth', params: { target: sc.scopeBitDepth } }),
        });
        const d = await r.json();
        if (d.success) sub._cvScopeIds.bitDepth = d.backend_id;
    }

    // 4. Re-add inserted features
    if (sub.cvFeatures?.length) {
        for (const sf of sub.cvFeatures) {
            const r = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ feature_type: sf.type, params: sf.params, suppressed: sf.suppressed || false }),
            });
            const d = await r.json();
            sf._backendId = d.success ? d.backend_id : null;
        }
        // Re-freeze features that were frozen (must happen after all are added & evaluable)
        for (const sf of sub.cvFeatures) {
            if (sf.frozen && sf._backendId) {
                await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${sf._backendId}/freeze`, {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ frozen: true }),
                });
            }
        }
    }

    // 5. Evaluate terminal to get new feature_id + update player state
    try {
        const evalRes = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/evaluate`);
        const evalData = await evalRes.json();
        if (evalData.success) {
            sub._cvLoadInfo = { ...sub._cvLoadInfo, ...evalData };
            if (_moviePlayerState) {
                _moviePlayerState.featureId = evalData.feature_id;
                _moviePlayerState.totalFrames = evalData.n_frames || _moviePlayerState.totalFrames;
                _frameCache.clear();
                seekMovieFrame(_moviePlayerState.frame || 0);
            }
        }
    } catch (e) { console.warn('[CellVisia rebuild] eval failed:', e); }

    _cvRebuilding = false;
    return true;
}

async function cvSaveScopeChannels() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const keep = [];
    document.querySelectorAll('.cv-scope-ch:checked').forEach(el => keep.push(parseInt(el.dataset.ch)));
    if (!sub._cvState) sub._cvState = {};
    sub._cvState.scopeKeepChannels = keep;

    const statusEl = document.getElementById('cvScopeChStatus');
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-running)">⏳ Rebuilding...</span>`;
    await cvRebuildPipeline();
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Keeping channels: ${keep.join(', ')}</span>`;
    cvPersistState(sub);
    updateStatus(`Channels: keeping ${keep.join(', ')}`);
    showCellVisiaPlayer();
}

async function cvSaveScopeTemporal() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    if (!sub._cvState) sub._cvState = {};
    const start = parseInt(document.querySelector('[data-param="scope_frame_start"]')?.value) || 0;
    const end = parseInt(document.querySelector('[data-param="scope_frame_end"]')?.value) ?? -1;
    const every = Math.max(1, parseInt(document.querySelector('[data-param="scope_subsample"]')?.value) || 1);
    sub._cvState.scopeFrameStart = start;
    sub._cvState.scopeFrameEnd = end;
    sub._cvState.scopeSubsample = every;

    const statusEl = document.getElementById('cvScopeTemporalStatus');
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-running)">⏳ Rebuilding...</span>`;
    await cvRebuildPipeline();
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Frames ${start}→${end}, every ${every}</span>`;
    cvPersistState(sub);
    updateStatus(`Temporal: frames ${start}→${end}, every ${every}`);
    showCellVisiaPlayer();
}

async function cvSaveScopeFormat() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    if (!sub._cvState) sub._cvState = {};
    const bitDepth = document.querySelector('[data-param="scope_bit_depth"]')?.value || '';
    const axesOrder = document.querySelector('[data-param="scope_axes_order"]')?.value || '';
    const deinterleaveN = parseInt(document.querySelector('[data-param="scope_deinterleave"]')?.value) || 0;
    sub._cvState.scopeBitDepth = bitDepth;
    sub._cvState.scopeAxesOrder = axesOrder;
    sub._cvState.scopeDeinterleave = deinterleaveN;

    const statusEl = document.getElementById('cvScopeFormatStatus');
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-running)">⏳ Rebuilding...</span>`;
    await cvRebuildPipeline();
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Applied</span>`;
    cvPersistState(sub);
    updateStatus('Format settings applied');
    showCellVisiaPlayer();
}

// ── Graphics / Tables / Figures tab switching ────────────────────────────────

function cvSwitchGfxTab(subId, tab) {
    const tabs = {
        input:    document.getElementById(`gfxTabInput-${subId}`),
        graphics: document.getElementById(`gfxTabGraphics-${subId}`),
        tables:   document.getElementById(`gfxTabTables-${subId}`),
        figures:  document.getElementById(`gfxTabFigures-${subId}`),
    };
    const gfxBody = document.getElementById(`graphicsBody-${subId}`);
    const tablesBody = document.getElementById(`tablesBody-${subId}`);
    const figuresBody = document.getElementById(`figuresBody-${subId}`);

    // Visual tab state
    for (const [key, el] of Object.entries(tabs)) {
        if (!el) continue;
        const active = key === tab;
        el.style.borderBottomColor = active ? 'var(--brand-accent)' : 'transparent';
        el.style.color = active ? 'var(--text-secondary)' : 'var(--text-tertiary)';
        el.style.opacity = active ? '1' : '.6';
    }

    // Show/hide bodies — Input and Graphics share graphicsBody
    _cvActiveGfxTab = tab;
    const showPlayer = tab === 'input' || tab === 'graphics';
    if (gfxBody) gfxBody.style.display = showPlayer ? '' : 'none';
    if (tablesBody) tablesBody.style.display = tab === 'tables' ? '' : 'none';
    if (figuresBody) figuresBody.style.display = tab === 'figures' ? '' : 'none';

    // Swap featureId for Input vs Graphics
    if (showPlayer && _moviePlayerState?.cvMode) {
        const ws = getActiveWorkspace();
        const sub = ws?.subtabs.get(subId);
        if (sub) {
            if (tab === 'input') {
                // Input: show original image with ALL channels
                const origInfo = sub._cvOriginalInfo || sub._cvLoadInfo;
                const origNCh = origInfo?.n_channels || 1;
                const currentNCh = _moviePlayerState.channels?.length || 0;
                const metaFid = sub._cvFeatureIds?.meta || null;
                if (currentNCh !== origNCh) {
                    // Rebuild player with original channel count
                    const saved = sub._cvLoadInfo;
                    sub._cvLoadInfo = { ...origInfo, feature_id: metaFid };
                    showCellVisiaPlayer();
                    sub._cvLoadInfo = saved;
                } else {
                    _moviePlayerState.featureId = metaFid;
                    _frameCache.clear();
                    seekMovieFrame(_moviePlayerState.frame || 0);
                }
            } else if (tab === 'graphics') {
                // Graphics: show pipeline terminal with selected channels
                const pipelineNCh = sub._cvLoadInfo?.n_channels || 1;
                const currentNCh = _moviePlayerState.channels?.length || 0;
                const newFid = sub._cvLoadInfo?.feature_id || sub._cvFeatureIds?.meta || null;
                if (currentNCh !== pipelineNCh) {
                    showCellVisiaPlayer();
                } else {
                    _moviePlayerState.featureId = newFid;
                    _frameCache.clear();
                    seekMovieFrame(_moviePlayerState.frame || 0);
                }
            }
        }
    }
}

// ── SVG Plotter ─────────────────────────────────────────────────────────────

function cvPlotSVG({ title, xLabel, yLabel, series, width = 600, height = 300, type = 'line' }) {
    // series: [{ name, data: [{x, y}], color }]
    const margin = { top: 30, right: 20, bottom: 40, left: 60 };
    const w = width - margin.left - margin.right;
    const h = height - margin.top - margin.bottom;

    let allX = [], allY = [];
    for (const s of series) { for (const d of s.data) { allX.push(d.x); allY.push(d.y); }}
    const xMin = Math.min(...allX), xMax = Math.max(...allX);
    const yMin = Math.min(0, Math.min(...allY)), yMax = Math.max(...allY) * 1.1 || 1;
    const sx = (v) => margin.left + (v - xMin) / ((xMax - xMin) || 1) * w;
    const sy = (v) => margin.top + h - (v - yMin) / ((yMax - yMin) || 1) * h;

    // Grid lines
    const nTicks = 5;
    let gridLines = '';
    for (let i = 0; i <= nTicks; i++) {
        const yVal = yMin + (yMax - yMin) * i / nTicks;
        const yPos = sy(yVal);
        gridLines += `<line x1="${margin.left}" y1="${yPos}" x2="${width - margin.right}" y2="${yPos}" stroke="rgba(255,255,255,.06)" stroke-width="1"/>`;
        gridLines += `<text x="${margin.left - 8}" y="${yPos + 3}" fill="rgba(255,255,255,.4)" font-size="10" text-anchor="end" font-family="var(--font-mono)">${yVal.toFixed(yVal > 100 ? 0 : 1)}</text>`;
    }
    for (let i = 0; i <= nTicks; i++) {
        const xVal = xMin + (xMax - xMin) * i / nTicks;
        const xPos = sx(xVal);
        gridLines += `<text x="${xPos}" y="${height - 8}" fill="rgba(255,255,255,.4)" font-size="10" text-anchor="middle" font-family="var(--font-mono)">${Number.isInteger(xVal) ? xVal : xVal.toFixed(1)}</text>`;
    }

    // Series
    let seriesSvg = '';
    const colors = ['#42a5f5', '#66bb6a', '#ff7043', '#ab47bc', '#ffa726', '#26c6da'];
    for (let si = 0; si < series.length; si++) {
        const s = series[si];
        const c = s.color || colors[si % colors.length];
        if (type === 'bar') {
            const barW = Math.max(2, w / (s.data.length * series.length) - 1);
            s.data.forEach((d, i) => {
                const bx = sx(d.x) - barW / 2 + si * (barW + 1);
                const bh = h - (sy(d.y) - margin.top);
                seriesSvg += `<rect x="${bx}" y="${sy(d.y)}" width="${barW}" height="${bh}" fill="${c}" opacity="0.8"/>`;
            });
        } else {
            const pts = s.data.map(d => `${sx(d.x)},${sy(d.y)}`).join(' ');
            seriesSvg += `<polyline points="${pts}" fill="none" stroke="${c}" stroke-width="2"/>`;
            if (s.data.length < 50) {
                s.data.forEach(d => {
                    seriesSvg += `<circle cx="${sx(d.x)}" cy="${sy(d.y)}" r="3" fill="${c}"/>`;
                });
            }
        }
    }

    // Legend
    let legend = '';
    if (series.length > 1) {
        series.forEach((s, i) => {
            const c = s.color || colors[i % colors.length];
            legend += `<rect x="${margin.left + i * 100}" y="6" width="12" height="3" fill="${c}"/>`;
            legend += `<text x="${margin.left + i * 100 + 16}" y="11" fill="rgba(255,255,255,.6)" font-size="10">${s.name || `Series ${i+1}`}</text>`;
        });
    }

    return `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:${width}px;height:auto">
        <rect width="${width}" height="${height}" fill="transparent"/>
        ${gridLines}
        <text x="${width/2}" y="${margin.top - 10}" fill="rgba(255,255,255,.7)" font-size="12" text-anchor="middle" font-weight="600">${title || ''}</text>
        <text x="${width/2}" y="${height - 2}" fill="rgba(255,255,255,.35)" font-size="10" text-anchor="middle">${xLabel || ''}</text>
        <text x="12" y="${margin.top + h/2}" fill="rgba(255,255,255,.35)" font-size="10" text-anchor="middle" transform="rotate(-90,12,${margin.top + h/2})">${yLabel || ''}</text>
        ${seriesSvg}
        ${legend}
    </svg>`;
}

// ── Measurement types → output routing ──────────────────────────────────────

const CV_MEASUREMENT_TYPES = new Set([
    'region_props', 'intensity_stats', 'shape_descriptors', 'texture', 'granularity',
    'spatial_stats', 'neighbors', 'image_quality', 'histogram', 'intensity_distribution',
    'plot_profile', 'skeleton_measure', 'calculate_math', 'colocalization',
]);

// Which measurements produce figures (charts)?
const CV_FIGURE_TYPES = new Set([
    'intensity_stats', 'granularity', 'image_quality', 'histogram',
    'intensity_distribution', 'plot_profile',
]);

async function cvShowMeasurementResults(sub, featureId) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    try {
        const res = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/measurements?feature_id=${featureId}`);
        const data = await res.json();
        if (!data.success || !data.measurement) return;

        const m = data.measurement;
        const tablesBody = document.getElementById(`tablesBody-${sub.id}`);
        const figuresBody = document.getElementById(`figuresBody-${sub.id}`);

        // ── Tables ──
        if (m.type === 'table' && m.rows && tablesBody) {
            const cols = m.columns || Object.keys(m.rows[0] || {});
            tablesBody.innerHTML = `
                <div style="padding:8px 12px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--chrome-border);background:var(--surface-2)">
                    <span style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">${m.name || 'Results'}</span>
                    <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">${m.rows.length} rows</span>
                    <span style="flex:1"></span>
                    <button class="btn btn-sm" onclick="cvExportResultsCSV('${sub.id}')" style="font-size:11px;padding:2px 8px">📋 Copy CSV</button>
                </div>
                <div style="overflow:auto;flex:1" id="cvResultsTable-${sub.id}">
                    <table style="width:100%;border-collapse:collapse;font-size:var(--fs-xs);font-family:var(--font-mono)">
                        <thead><tr>${cols.map(c => `<th style="position:sticky;top:0;background:var(--surface-3);padding:4px 8px;text-align:left;border-bottom:1px solid var(--chrome-border);cursor:pointer;white-space:nowrap;color:var(--text-secondary)" onclick="cvSortResultsTable('${sub.id}','${c}')">${c} ↕</th>`).join('')}</tr></thead>
                        <tbody>${m.rows.map((row, ri) => `<tr style="background:${ri % 2 ? 'var(--surface-1)' : 'var(--surface-0)'}">
                            ${cols.map(c => { const v = row[c]; return `<td style="padding:3px 8px;border-bottom:1px solid rgba(255,255,255,.03);white-space:nowrap">${typeof v === 'number' ? (Number.isInteger(v) ? v : v.toFixed(3)) : (v ?? '')}</td>`; }).join('')}
                        </tr>`).join('')}</tbody>
                    </table>
                </div>`;
            tablesBody._cvResultData = { columns: cols, rows: m.rows, name: m.name };
        }

        // ── Figures ──
        if (figuresBody) {
            let figHtml = '';
            if (m.type === 'table' && m.rows && m.rows.length > 0) {
                const cols = m.columns || Object.keys(m.rows[0]);
                const numCols = cols.filter(c => c !== 'frame' && c !== 'label' && typeof m.rows[0][c] === 'number');
                if (numCols.length > 0 && m.rows[0].frame !== undefined) {
                    // Time-series: plot each numeric column vs frame
                    const series = numCols.map(c => ({
                        name: c,
                        data: m.rows.filter(r => r.frame !== undefined).map(r => ({ x: r.frame, y: r[c] || 0 })),
                    }));
                    figHtml = cvPlotSVG({ title: m.name, xLabel: 'Frame', yLabel: '', series, type: 'line' });
                }
            } else if (m.type === 'histogram' && m.per_frame) {
                const fk = Object.keys(m.per_frame)[0];
                if (fk !== undefined) {
                    const h = m.per_frame[fk];
                    const data = h.counts.map((c, i) => ({ x: (h.bin_edges[i] + h.bin_edges[i+1]) / 2, y: c }));
                    figHtml = cvPlotSVG({ title: `${m.name} (frame ${fk})`, xLabel: 'Intensity', yLabel: 'Count', series: [{ name: 'counts', data }], type: 'bar' });
                }
            } else if (m.type === 'profile' && m.per_frame) {
                const fk = Object.keys(m.per_frame)[0];
                if (fk !== undefined) {
                    const prof = m.per_frame[fk];
                    const data = prof.map((v, i) => ({ x: i, y: v }));
                    figHtml = cvPlotSVG({ title: `${m.name} (frame ${fk})`, xLabel: 'Position (px)', yLabel: 'Intensity', series: [{ name: 'profile', data }], type: 'line' });
                }
            }

            if (figHtml) {
                figuresBody.innerHTML = `
                    <div style="padding:8px 12px;border-bottom:1px solid var(--chrome-border);background:var(--surface-2)">
                        <span style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">${m.name || 'Figure'}</span>
                    </div>
                    <div style="padding:16px;display:flex;justify-content:center">${figHtml}</div>`;
            }
        }

        // Auto-switch to appropriate tab
        const hasFigure = CV_FIGURE_TYPES.has(data.measurement_type || '') || figuresBody?.querySelector('svg');
        const hasTable = m.type === 'table' && m.rows?.length > 0;
        if (hasFigure && figuresBody?.querySelector('svg')) {
            cvSwitchGfxTab(sub.id, 'figures');
        } else if (hasTable) {
            cvSwitchGfxTab(sub.id, 'tables');
        }
    } catch (e) {
        console.warn('[CellVisia] measurement fetch failed:', e);
    }
}

function cvSortResultsTable(subId, column) {
    const tablesBody = document.getElementById(`tablesBody-${subId}`);
    if (!tablesBody?._cvResultData) return;
    const d = tablesBody._cvResultData;
    if (!d._sortDir) d._sortDir = {};
    const dir = d._sortDir[column] === 'asc' ? 'desc' : 'asc';
    d._sortDir[column] = dir;
    d.rows.sort((a, b) => {
        const va = a[column], vb = b[column];
        if (typeof va === 'number' && typeof vb === 'number') return dir === 'asc' ? va - vb : vb - va;
        return dir === 'asc' ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
    });
    const cols = d.columns;
    const tableEl = document.getElementById(`cvResultsTable-${subId}`);
    if (tableEl) {
        tableEl.innerHTML = `<table style="width:100%;border-collapse:collapse;font-size:var(--fs-xs);font-family:var(--font-mono)">
            <thead><tr>${cols.map(c => `<th style="position:sticky;top:0;background:var(--surface-3);padding:4px 8px;text-align:left;border-bottom:1px solid var(--chrome-border);cursor:pointer;white-space:nowrap;color:var(--text-secondary)" onclick="cvSortResultsTable('${subId}','${c}')">${c} ${d._sortDir[c] === 'asc' ? '▲' : d._sortDir[c] === 'desc' ? '▼' : '↕'}</th>`).join('')}</tr></thead>
            <tbody>${d.rows.map((row, ri) => `<tr style="background:${ri % 2 ? 'var(--surface-1)' : 'var(--surface-0)'}">
                ${cols.map(c => { const v = row[c]; return `<td style="padding:3px 8px;border-bottom:1px solid rgba(255,255,255,.03);white-space:nowrap">${typeof v === 'number' ? (Number.isInteger(v) ? v : v.toFixed(3)) : (v ?? '')}</td>`; }).join('')}
            </tr>`).join('')}</tbody></table>`;
    }
}

function cvExportResultsCSV(subId) {
    const tablesBody = document.getElementById(`tablesBody-${subId}`);
    if (!tablesBody?._cvResultData) return;
    const d = tablesBody._cvResultData;
    const csv = [d.columns.join(',')].concat(
        d.rows.map(r => d.columns.map(c => r[c] ?? '').join(','))
    ).join('\n');
    navigator.clipboard.writeText(csv).then(() => updateStatus('📋 Results copied to clipboard'));
}

async function cvBrowseSave(btnEl, paramKey, mode, filetypesJson) {
    const input = btnEl.parentElement.querySelector(`[data-param="${paramKey}"]`);
    if (!input) return;
    // Derive initial dir from source path if available
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    const srcPath = sub?._cvState?.filePath || '';
    const initialDir = srcPath ? srcPath.replace(/[/\\][^/\\]*$/, '') : '';

    let filetypes = [['All Files', '*.*']];
    try { filetypes = JSON.parse(filetypesJson.replace(/&quot;/g, '"')); } catch {}

    try {
        const res = await fetch('/api/browse_save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mode, title: mode === 'folder' ? 'Select Output Folder' : 'Save As', initial_dir: initialDir, filetypes }),
        });
        const data = await res.json();
        if (data.success && data.path) {
            input.value = data.path;
            // Trigger onchange so params get saved
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    } catch (e) {
        updateStatus(`Browse error: ${e.message}`);
    }
}

async function cvApplyFeature(featureId) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?.cvFeatures) return;
    const feat = sub.cvFeatures.find(f => f.id === featureId);
    if (!feat) return;

    // Collect params from form
    const form = document.querySelector(`#settingsBody-${sub.id} .settings-form`);
    if (form) {
        const defs = CV_PARAM_DEFS[feat.type] || [];
        form.querySelectorAll('[data-param]').forEach(el => {
            const key = el.dataset.param;
            const def = defs.find(d => d.key === key);
            if (!def) return;
            if (def.type === 'int') feat.params[key] = parseInt(el.value) || 0;
            else if (def.type === 'float') feat.params[key] = parseFloat(el.value) || 0;
            else if (def.type === 'text') {
                const orig = def.fallback;
                if (Array.isArray(orig)) {
                    feat.params[key] = el.value.split(',').map(s => s.trim()).filter(Boolean);
                } else {
                    feat.params[key] = el.value;
                }
            } else {
                feat.params[key] = el.value;
            }
        });
    }

    const statusEl = document.getElementById(`cvFeatureStatus-${featureId}`);
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-running)">⏳ Applying...</span>`;

    try {
        if (feat._backendId) {
            // Incremental: update params on existing backend feature
            const res = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/add_feature`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ feature_type: feat.type, params: feat.params, backend_id: feat._backendId }),
            });
            const data = await res.json();
            if (!data.success) {
                if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
                return;
            }
        } else {
            // New feature: need rebuild to insert into chain
            const ok = await cvRebuildPipeline();
            if (!ok) {
                if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ Rebuild failed</span>`;
                return;
            }
        }

        // Evaluate + update viewer
        if (statusEl) {
            const evalRes = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/evaluate?feature_id=${feat._backendId}`);
            const evalData = await evalRes.json();
            if (evalData.success) {
                statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Applied — ${evalData.axes} ${evalData.shape.join('×')}</span>`;
            } else {
                statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Applied</span>`;
            }
        }
        cvRefreshViewer();

        // Clear crop tool overlay if visible
        const toolOverlay = document.getElementById('cvToolOverlay');
        if (toolOverlay) toolOverlay.innerHTML = '';

        // Auto-show measurement results for measurement ops
        if (CV_MEASUREMENT_TYPES.has(feat.type) && feat._backendId) {
            cvShowMeasurementResults(sub, feat._backendId);
        }
    } catch (err) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${err.message}</span>`;
    }
    cvPersistState(sub);
    updateStatus(`Applied: ${feat.label}`);
}

// ═════════════════════════════════════════════
// ANNOTADE — Annotation Tool
// ═════════════════════════════════════════════

const AN_CLASSES = {
    1: { name:'Cell',           color:[76,175,80]   },
    2: { name:'Nucleus',        color:[66,133,244]  },
    3: { name:'Focal Adhesion', color:[244,67,54]   },
    4: { name:'Boundary',       color:[255,193,7]   },
    5: { name:'Background',     color:[158,158,158] },
};

async function anPersistState(sub) {
    if (!sub || !state._projectOpen) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    try {
        await fetch(`/api/step/${ws.id}/${sub.pipelineId}/annotade/params`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ params: { _anState: sub._anState || {} } }),
        });
    } catch (e) { console.warn('[AnnotADE] persist failed:', e); }
}

async function annotadeBrowse() {
    try {
        const res = await fetch('/api/browse_save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mode: 'file', title: 'Select Image', filetypes: [['TIFF','*.tif'],['PNG','*.png'],['All','*.*']] }),
        });
        const data = await res.json();
        if (data.success && data.path) {
            const input = document.getElementById('anFileInput');
            if (input) input.value = data.path;
        }
    } catch (e) { updateStatus(`Browse error: ${e.message}`); }
}

async function annotadeLoad() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const filePath = document.getElementById('anFileInput')?.value;
    if (!filePath) { updateStatus('Select an image first.'); return; }

    const statusEl = document.getElementById('anLoadStatus');
    if (statusEl) statusEl.innerHTML = 'Loading...';

    try {
        const res = await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/load`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: filePath }),
        });
        const data = await res.json();
        if (data.success) {
            if (!sub._anState) sub._anState = {};
            Object.assign(sub._anState, {
                filePath, filename: data.filename,
                shape: `${data.height}×${data.width}`,
                n_frames: data.n_frames, dtype: data.dtype,
                imgW: data.width, imgH: data.height,
                currentFrame: 0, brightness: 0, contrast: 1.0,
                tool: 'brush', brush_size: 5, class_id: 1,
                loadStatus: `✓ ${data.filename} (${data.n_frames} frames)`,
            });

            // Init per-frame label arrays
            sub._anLabels = {};
            for (let i = 0; i < data.n_frames; i++) {
                sub._anLabels[i] = new Uint16Array(data.height * data.width);
            }

            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">${sub._anState.loadStatus}</span>`;
            updateStatus(`✅ AnnotADE: loaded ${data.filename}`);
            anPersistState(sub);

            if (data.preview) _anInitCanvas(sub, data.preview);
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

// ── Canvas setup ────────────────────────────────

function _anInitCanvas(sub, imageBase64) {
    const gfxBody = document.getElementById(`graphicsBody-${sub.id}`);
    if (!gfxBody) return;
    const { imgW, imgH } = sub._anState;

    gfxBody.innerHTML = `
        <div style="flex:1;position:relative;overflow:auto;background:#111;display:flex;align-items:center;justify-content:center" id="anCanvasWrap-${sub.id}">
            <div style="position:relative;width:${imgW}px;height:${imgH}px" id="anCanvasStack-${sub.id}">
                <canvas id="anCvImg-${sub.id}" width="${imgW}" height="${imgH}" style="position:absolute;top:0;left:0"></canvas>
                <canvas id="anCvLbl-${sub.id}" width="${imgW}" height="${imgH}" style="position:absolute;top:0;left:0;opacity:0.45;cursor:crosshair"
                    onmousedown="_anMD(event,'${sub.id}')" onmousemove="_anMM(event,'${sub.id}')" onmouseup="_anMU(event,'${sub.id}')"
                    onmouseleave="_anMU(event,'${sub.id}')" oncontextmenu="event.preventDefault()"></canvas>
            </div>
        </div>
        <div style="height:24px;background:var(--surface-1);border-top:1px solid var(--chrome-border);display:flex;align-items:center;gap:12px;padding:0 10px;font-size:10px;color:var(--text-tertiary);flex-shrink:0" id="anStatusBar-${sub.id}">
            <span id="anCoord-${sub.id}">—</span>
            <span id="anToolLabel-${sub.id}">Brush (5px)</span>
            <span id="anClassLabel-${sub.id}">Class: 1 — Cell</span>
        </div>`;

    const img = new Image();
    img.onload = () => {
        const ctx = document.getElementById(`anCvImg-${sub.id}`)?.getContext('2d');
        if (ctx) ctx.drawImage(img, 0, 0);
        sub._anImgEl = img;
    };
    img.src = imageBase64;
}

function _anGetSub(subId) {
    const ws = getActiveWorkspace();
    if (!ws) return null;
    for (const [, s] of ws.subtabs) { if (s.id === subId) return s; }
    return null;
}

// ── Mouse handlers ──────────────────────────────

let _anDrawing = false;

function _anMD(e, subId) {
    if (e.button !== 0) return;
    _anDrawing = true;
    const sub = _anGetSub(subId);
    if (!sub) return;
    const { x, y } = _anCanvasXY(e, subId);
    const tool = sub._anState?.tool || 'brush';

    if (tool === 'brush' || tool === 'eraser') {
        _anPaintAt(sub, x, y);
    } else if (tool === 'flood') {
        _anFloodClient(sub, x, y);
        _anDrawing = false;
    }
}

function _anMM(e, subId) {
    const sub = _anGetSub(subId);
    if (!sub) return;
    const { x, y } = _anCanvasXY(e, subId);

    const coord = document.getElementById(`anCoord-${subId}`);
    if (coord) coord.textContent = `(${x}, ${y})`;

    if (_anDrawing) {
        const tool = sub._anState?.tool || 'brush';
        if (tool === 'brush' || tool === 'eraser') {
            _anPaintAt(sub, x, y);
        }
    }
}

function _anMU(e, subId) {
    if (_anDrawing) {
        _anDrawing = false;
        const sub = _anGetSub(subId);
        if (sub) _anSyncLabels(sub);
    }
}

function _anCanvasXY(e, subId) {
    const cv = document.getElementById(`anCvLbl-${subId}`);
    if (!cv) return { x:0, y:0 };
    const rect = cv.getBoundingClientRect();
    const scaleX = cv.width / rect.width;
    const scaleY = cv.height / rect.height;
    return {
        x: Math.floor((e.clientX - rect.left) * scaleX),
        y: Math.floor((e.clientY - rect.top) * scaleY),
    };
}

// ── Paint brush / eraser ────────────────────────

function _anPaintAt(sub, cx, cy) {
    const { imgW, imgH } = sub._anState;
    const frame = sub._anState.currentFrame || 0;
    const labels = sub._anLabels?.[frame];
    if (!labels) return;

    const r = Math.max(1, Math.floor((sub._anState.brush_size || 5) / 2));
    const tool = sub._anState.tool || 'brush';
    const classId = tool === 'eraser' ? 0 : (sub._anState.class_id || 1);

    for (let dy = -r; dy <= r; dy++) {
        for (let dx = -r; dx <= r; dx++) {
            if (dx*dx + dy*dy > r*r) continue;
            const px = cx + dx, py = cy + dy;
            if (px >= 0 && px < imgW && py >= 0 && py < imgH) {
                labels[py * imgW + px] = classId;
            }
        }
    }

    _anRedrawOverlay(sub);
}

// ── Flood fill (client-side) ────────────────────

function _anFloodClient(sub, seedX, seedY) {
    const { imgW, imgH } = sub._anState;
    const frame = sub._anState.currentFrame || 0;
    const labels = sub._anLabels?.[frame];
    if (!labels) return;

    const imgCv = document.getElementById(`anCvImg-${sub.id}`);
    if (!imgCv) return;
    const imgCtx = imgCv.getContext('2d');
    const imgData = imgCtx.getImageData(0, 0, imgW, imgH).data;

    const tolerance = sub._anState.flood_tolerance || 30;
    const classId = sub._anState.class_id || 1;
    const seedVal = imgData[(seedY * imgW + seedX) * 4];
    const low = seedVal - tolerance, high = seedVal + tolerance;

    const visited = new Uint8Array(imgW * imgH);
    const queue = [seedY * imgW + seedX];
    visited[queue[0]] = 1;

    while (queue.length > 0) {
        const idx = queue.shift();
        const val = imgData[idx * 4];
        if (val >= low && val <= high) {
            labels[idx] = classId;
            const y = Math.floor(idx / imgW), x = idx % imgW;
            for (const [dy, dx] of [[-1,0],[1,0],[0,-1],[0,1]]) {
                const ny = y+dy, nx = x+dx;
                if (ny >= 0 && ny < imgH && nx >= 0 && nx < imgW) {
                    const ni = ny * imgW + nx;
                    if (!visited[ni]) { visited[ni] = 1; queue.push(ni); }
                }
            }
        }
    }

    _anRedrawOverlay(sub);
    _anSyncLabels(sub);
    updateStatus(`Flood fill: class ${classId} from (${seedX},${seedY})`);
}

// ── Overlay rendering ───────────────────────────

function _anRedrawOverlay(sub) {
    const cv = document.getElementById(`anCvLbl-${sub.id}`);
    if (!cv) return;
    const ctx = cv.getContext('2d');
    const { imgW, imgH } = sub._anState;
    const frame = sub._anState.currentFrame || 0;
    const labels = sub._anLabels?.[frame];
    if (!labels) return;

    const imgData = ctx.createImageData(imgW, imgH);
    const d = imgData.data;

    for (let i = 0; i < imgW * imgH; i++) {
        const lbl = labels[i];
        if (lbl > 0 && lbl <= 5) {
            const c = AN_CLASSES[lbl].color;
            d[i*4]   = c[0];
            d[i*4+1] = c[1];
            d[i*4+2] = c[2];
            d[i*4+3] = 200;
        }
    }

    ctx.putImageData(imgData, 0, 0);
}

// ── Label sync to backend ───────────────────────

async function _anSyncLabels(sub) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const frame = sub._anState.currentFrame || 0;
    const labels = sub._anLabels?.[frame];
    if (!labels) return;

    const stats = {};
    for (let i = 0; i < labels.length; i++) {
        const v = labels[i];
        if (v > 0) stats[v] = (stats[v] || 0) + 1;
    }
    sub._anState.labelStats = stats;

    try {
        const bytes = new Uint8Array(labels.buffer);
        let b64 = '';
        const chunk = 8192;
        for (let i = 0; i < bytes.length; i += chunk) {
            b64 += String.fromCharCode(...bytes.subarray(i, i + chunk));
        }
        b64 = btoa(b64);
        await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/labels/${frame}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ data: b64 }),
        });
    } catch {}
}

// ── Tool switching ──────────────────────────────

function annotadeSetTool(tool) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._anState) return;
    sub._anState.tool = tool;
    _anUpdateStatusBar(sub);
    updateStatus(`AnnotADE tool: ${tool}`);
}

function _anUpdateStatusBar(sub) {
    const toolEl = document.getElementById(`anToolLabel-${sub.id}`);
    const classEl = document.getElementById(`anClassLabel-${sub.id}`);
    if (toolEl) {
        const t = sub._anState.tool || 'brush';
        const sz = sub._anState.brush_size || 5;
        toolEl.textContent = t === 'brush' ? `Brush (${sz}px)` : t === 'eraser' ? `Eraser (${sz}px)` : t.charAt(0).toUpperCase() + t.slice(1);
    }
    if (classEl) {
        const c = sub._anState.class_id || 1;
        classEl.textContent = `Class: ${c} — ${AN_CLASSES[c]?.name || '?'}`;
    }
}

// ── Frame navigation ────────────────────────────

async function annotadeFrame(delta) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._anState) return;
    const nFrames = sub._anState.n_frames || 1;
    let cur = (sub._anState.currentFrame || 0) + delta;
    cur = Math.max(0, Math.min(cur, nFrames - 1));
    sub._anState.currentFrame = cur;

    try {
        const res = await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/frame/${cur}`);
        const data = await res.json();
        if (data.success && data.preview) {
            const img = new Image();
            img.onload = () => {
                const ctx = document.getElementById(`anCvImg-${sub.id}`)?.getContext('2d');
                if (ctx) ctx.drawImage(img, 0, 0);
                sub._anImgEl = img;
                _anRedrawOverlay(sub);
            };
            img.src = data.preview;
        }
    } catch {}

    const label = document.getElementById('anFrameLabel');
    if (label) label.textContent = `${cur + 1} / ${nFrames}`;
}

async function annotadeDisplay() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._anState?.filePath) return;
    const frame = sub._anState.currentFrame || 0;
    const bEl = document.querySelector('[data-param="brightness"]');
    const cEl = document.querySelector('[data-param="contrast"]');
    const brightness = bEl ? parseInt(bEl.value) : 0;
    const contrast = cEl ? parseInt(cEl.value) / 100 : 1.0;

    try {
        const res = await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/frame/${frame}?brightness=${brightness}&contrast=${contrast}`);
        const data = await res.json();
        if (data.success && data.preview) {
            const img = new Image();
            img.onload = () => {
                const ctx = document.getElementById(`anCvImg-${sub.id}`)?.getContext('2d');
                if (ctx) ctx.drawImage(img, 0, 0);
            };
            img.src = data.preview;
        }
    } catch {}
}

// ── Assist tools (server-side) ──────────────────

async function annotadeOtsu() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._anState?.filePath) { updateStatus('Load an image first.'); return; }
    const frame = sub._anState.currentFrame || 0;

    try {
        const res = await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/assist`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ method: 'otsu', frame }),
        });
        const data = await res.json();
        if (data.success && data.mask_data) {
            _anApplyMask(sub, data.mask_data);
        }
    } catch (e) { updateStatus(`Otsu error: ${e.message}`); }
}

async function annotadeThreshold() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._anState?.filePath) { updateStatus('Load an image first.'); return; }
    const frame = sub._anState.currentFrame || 0;
    const value = parseInt(document.querySelector('[data-param="threshold_value"]')?.value || '128');

    try {
        const res = await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/assist`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ method: 'threshold', frame, value }),
        });
        const data = await res.json();
        if (data.success && data.mask_data) {
            _anApplyMask(sub, data.mask_data);
        }
    } catch (e) { updateStatus(`Threshold error: ${e.message}`); }
}

async function annotadeFCM() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._anState?.filePath) { updateStatus('Load an image first.'); return; }
    const frame = sub._anState.currentFrame || 0;
    const clusters = parseInt(document.querySelector('[data-param="fcm_clusters"]')?.value || '2');

    try {
        const res = await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/assist`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ method: 'fcm', frame, n_clusters: clusters }),
        });
        const data = await res.json();
        if (data.success && data.mask_data) {
            _anApplyMask(sub, data.mask_data);
        }
    } catch (e) { updateStatus(`FCM error: ${e.message}`); }
}

function _anApplyMask(sub, maskB64) {
    const { imgW, imgH } = sub._anState;
    const frame = sub._anState.currentFrame || 0;
    const labels = sub._anLabels?.[frame];
    if (!labels) return;

    const raw = atob(maskB64);
    const classId = sub._anState.class_id || 1;
    for (let i = 0; i < raw.length && i < imgW * imgH; i++) {
        if (raw.charCodeAt(i) > 0) {
            labels[i] = classId;
        }
    }

    _anRedrawOverlay(sub);
    _anSyncLabels(sub);
    updateStatus(`Assist applied (class ${classId})`);
}

// ── Misc ────────────────────────────────────────

async function annotadeClearLabels() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._anState) return;
    const frame = sub._anState.currentFrame || 0;
    if (sub._anLabels?.[frame]) {
        sub._anLabels[frame].fill(0);
    }
    _anRedrawOverlay(sub);
    try {
        await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/clear_labels`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ frame }),
        });
    } catch {}
    updateStatus('Labels cleared.');
}

async function annotadeExport() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._anState?.filePath) { updateStatus('Load an image first.'); return; }
    try {
        const res = await fetch(`/api/annotade/${ws.id}/${sub.pipelineId}/export`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            updateStatus(`✅ Exported: ${data.path}`);
        } else {
            updateStatus(`Export error: ${data.error}`);
        }
    } catch (e) { updateStatus(`Export error: ${e.message}`); }
}
// ═════════════════════════════════════════════
// CELLFADE — FA Detection Module
// ═════════════════════════════════════════════

async function cfPersistState(sub) {
    if (!sub || !state._projectOpen) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    try {
        await fetch(`/api/step/${ws.id}/${sub.pipelineId}/cellfade/params`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ params: { _cfState: sub._cfState || {} } }),
        });
    } catch (e) { console.warn('[CellFADE] persist failed:', e); }
}

async function cellfadeBrowse(inputId) {
    try {
        const res = await fetch('/api/browse_save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mode: 'file', title: 'Select Image', filetypes: [['TIFF','*.tif'],['PNG','*.png'],['All','*.*']] }),
        });
        const data = await res.json();
        if (data.success && data.path) {
            const input = document.getElementById(inputId);
            if (input) input.value = data.path;
        }
    } catch (e) { updateStatus(`Browse error: ${e.message}`); }
}

async function cellfadeLoad() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const filePath = document.getElementById('cfFileInput')?.value;
    if (!filePath) { updateStatus('Select an FA image first.'); return; }

    const statusEl = document.getElementById('cfLoadStatus');
    if (statusEl) statusEl.innerHTML = 'Loading...';

    try {
        const boundaryPath = document.getElementById('cfBoundaryInput')?.value || '';
        const res = await fetch(`/api/cellfade/${ws.id}/${sub.pipelineId}/load`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ fa_path: filePath, boundary_path: boundaryPath }),
        });
        const data = await res.json();
        if (data.success) {
            if (!sub._cfState) sub._cfState = {};
            sub._cfState.filePath = filePath;
            sub._cfState.boundaryPath = boundaryPath;
            sub._cfState.shape = data.shape;
            sub._cfState.vmin = data.vmin;
            sub._cfState.vmax = data.vmax;
            sub._cfState.hasBoundary = data.has_boundary;
            sub._cfState.loadStatus = `✓ ${data.shape}${data.has_boundary ? ' + boundary' : ''}`;
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">${sub._cfState.loadStatus}</span>`;
            updateStatus(`✅ CellFADE: loaded ${data.shape}`);
            cfPersistState(sub);

            if (data.preview) {
                const gfxBody = document.getElementById(`graphicsBody-${sub.id}`);
                if (gfxBody) {
                    gfxBody.innerHTML = `<div style="flex:1;display:flex;align-items:center;justify-content:center;background:#000">
                        <img src="${data.preview}" style="max-width:100%;max-height:100%;object-fit:contain">
                    </div>`;
                }
            }
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

async function cellfadeRun() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._cfState?.filePath) { updateStatus('Load an FA image first.'); return; }

    const statusEl = document.getElementById('cfRunStatus');
    if (statusEl) statusEl.innerHTML = 'Running CellFADE...';

    let savedParams = {};
    try {
        const pRes = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/cellfade/params`);
        const pData = await pRes.json();
        if (pData.success && pData.params) {
            for (const section of Object.values(pData.params)) {
                if (typeof section === 'object') Object.assign(savedParams, section);
            }
        }
    } catch {}

    try {
        const res = await fetch(`/api/cellfade/${ws.id}/${sub.pipelineId}/run`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ params: savedParams }),
        });
        const data = await res.json();
        if (data.success) {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ ${data.n_final} FAs · ${data.n_seeds} seeds · ${data.elapsed_s}s</span>`;
            updateStatus(`✅ CellFADE: ${data.n_final} FAs`);
            sub._cfState.lastRun = { n_final: data.n_final, n_seeds: data.n_seeds, elapsed_s: data.elapsed_s };
            cfPersistState(sub);

            const bodyEl = document.getElementById(`settingsBody-${sub.id}`);
            if (bodyEl && sub.activeTreeItem?.id === 'cf-run') {
                bodyEl.innerHTML = renderSettingsContent(sub.moduleType, sub.stepId, sub.activeTreeItem);
            }
            renderModuleTree(sub);

            if (data.overlay) {
                const gfxBody = document.getElementById(`graphicsBody-${sub.id}`);
                if (gfxBody) {
                    gfxBody.innerHTML = `<div style="flex:1;display:flex;align-items:center;justify-content:center;background:#000">
                        <img src="${data.overlay}" style="max-width:100%;max-height:100%;object-fit:contain">
                    </div>`;
                }
            }
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

// ═════════════════════════════════════════════
// CELLADE — Cell Segmentation Module
// ═════════════════════════════════════════════

async function cdPersistState(sub) {
    if (!sub || !state._projectOpen) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    try {
        await fetch(`/api/step/${ws.id}/${sub.pipelineId}/cellade/params`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ params: { _cdState: sub._cdState || {} } }),
        });
    } catch (e) { console.warn('[CellADE] persist failed:', e); }
}

async function cdRestoreState(sub) {
    if (!sub || sub._cdState?.filePath) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    try {
        const res = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/cellade/params`);
        const data = await res.json();
        if (data.success && data.params?._cdState) {
            sub._cdState = data.params._cdState;
        }
    } catch {}
}

async function asPersistState(sub) {
    if (!sub || !state._projectOpen) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    try {
        await fetch(`/api/step/${ws.id}/${sub.pipelineId}/associa/params`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ params: { _asState: sub._asState || {} } }),
        });
    } catch (e) { console.warn('[Associa] persist failed:', e); }
}

async function asRestoreState(sub) {
    if (!sub || sub._asState?.filePath) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    try {
        const res = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/associa/params`);
        const data = await res.json();
        if (data.success && data.params?._asState) {
            sub._asState = data.params._asState;
        }
    } catch {}
}

async function celladeBrowseImage() {
    try {
        const res = await fetch('/api/browse_save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mode: 'file', title: 'Select Image', filetypes: [['TIFF','*.tif'],['PNG','*.png'],['JPEG','*.jpg'],['All','*.*']] }),
        });
        const data = await res.json();
        if (data.success && data.path) {
            const input = document.getElementById('cdFileInput');
            if (input) input.value = data.path;
        }
    } catch (e) { updateStatus(`Browse error: ${e.message}`); }
}

async function celladeBrowseGT() {
    try {
        const res = await fetch('/api/browse_save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mode: 'file', title: 'Select Ground Truth', filetypes: [['TIFF','*.tif'],['PNG','*.png'],['All','*.*']] }),
        });
        const data = await res.json();
        if (data.success && data.path) {
            const input = document.getElementById('cdGtInput');
            if (input) input.value = data.path;
        }
    } catch (e) { updateStatus(`Browse error: ${e.message}`); }
}

async function celladeLoadImage() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const filePath = document.getElementById('cdFileInput')?.value;
    if (!filePath) { updateStatus('Select an image first.'); return; }

    const statusEl = document.getElementById('cdLoadStatus');
    if (statusEl) statusEl.innerHTML = 'Loading...';

    try {
        const res = await fetch(`/api/cellade/${ws.id}/${sub.pipelineId}/load`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ file_path: filePath }),
        });
        const data = await res.json();
        if (data.success) {
            if (!sub._cdState) sub._cdState = {};
            sub._cdState.filePath = filePath;
            sub._cdState.shape = data.shape;
            sub._cdState.dtype = data.dtype;
            sub._cdState.vmin = data.vmin;
            sub._cdState.vmax = data.vmax;
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ ${data.shape} · ${data.dtype}</span>`;
            updateStatus(`✅ CellADE: loaded ${data.shape}`);
            cdPersistState(sub);

            // Show preview in Graphics tab
            if (data.preview) {
                const gfxBody = document.getElementById(`graphicsBody-${sub.id}`);
                if (gfxBody) {
                    gfxBody.innerHTML = `<div style="flex:1;display:flex;align-items:center;justify-content:center;background:#000">
                        <img src="${data.preview}" style="max-width:100%;max-height:100%;object-fit:contain">
                    </div>`;
                }
            }
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

async function celladeLoadGT() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const filePath = document.getElementById('cdGtInput')?.value;
    if (!filePath) return;

    try {
        const res = await fetch(`/api/cellade/${ws.id}/${sub.pipelineId}/load_gt`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ file_path: filePath }),
        });
        const data = await res.json();
        const statusEl = document.getElementById('cdGtStatus');
        if (data.success) {
            if (!sub._cdState) sub._cdState = {};
            sub._cdState.gtPath = filePath;
            sub._cdState.gtCells = data.n_cells;
            sub._cdState.gtStatus = `✓ ${data.n_cells} cells`;
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ ${data.n_cells} ground truth cells</span>`;
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) { updateStatus(`GT load error: ${e.message}`); }
}

async function celladeRun() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._cdState?.filePath) { updateStatus('Load an image first.'); return; }

    const statusEl = document.getElementById('cdRunStatus');
    if (statusEl) statusEl.innerHTML = 'Running CellADE pipeline...';

    // Collect params from saved settings
    let savedParams = {};
    try {
        const pRes = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/cellade/params`);
        const pData = await pRes.json();
        if (pData.success && pData.params) {
            for (const section of Object.values(pData.params)) {
                if (typeof section === 'object') Object.assign(savedParams, section);
            }
        }
    } catch {}

    try {
        const res = await fetch(`/api/cellade/${ws.id}/${sub.pipelineId}/run`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ params: savedParams }),
        });
        const data = await res.json();
        if (data.success) {
            const metricsHtml = data.metrics
                ? `<div style="font-size:var(--fs-xs);padding:6px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);margin-top:8px">
                    <b>F1@0.5:</b> ${data.metrics.F1?.toFixed(3) || '—'} · <b>mAP:</b> ${data.metrics.mAP?.toFixed(3) || '—'} · <b>Regions:</b> ${data.n_regions}</div>`
                : `<div style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-top:8px">${data.n_regions} regions · ${data.elapsed_s}s</div>`;
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ Done — ${data.n_regions} regions in ${data.elapsed_s}s</span>`;
            const metricsEl = document.getElementById('cdRunMetrics');
            if (metricsEl) metricsEl.innerHTML = metricsHtml;
            updateStatus(`✅ CellADE: ${data.n_regions} regions`);
            sub._cdState.lastRun = { n_regions: data.n_regions, elapsed_s: data.elapsed_s, metrics: data.metrics };
            cdPersistState(sub);

            // Re-render settings panel so plot buttons appear
            const bodyEl = document.getElementById(`settingsBody-${sub.id}`);
            if (bodyEl && sub.activeTreeItem?.id === 'cd-run') {
                bodyEl.innerHTML = renderSettingsContent(sub.moduleType, sub.stepId, sub.activeTreeItem);
            }

            // Re-render tree so Results items appear
            renderModuleTree(sub);

            // Show overlay in Graphics tab
            if (data.overlay) {
                const gfxBody = document.getElementById(`graphicsBody-${sub.id}`);
                if (gfxBody) {
                    gfxBody.innerHTML = `<div style="flex:1;display:flex;align-items:center;justify-content:center;background:#000">
                        <img src="${data.overlay}" style="max-width:100%;max-height:100%;object-fit:contain">
                    </div>`;
                }
            }
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

async function celladeExportMask() { updateStatus('Export mask: TODO — connect to backend'); }
async function celladeExportOverlay() { updateStatus('Export overlay: TODO — connect to backend'); }

// ═════════════════════════════════════════════
// ASSOCIA — Signal Coupling Module
// ═════════════════════════════════════════════

async function assocBrowseCSV(btn) {
    try {
        const res = await fetch('/api/browse_save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mode: 'file', title: 'Select Signal CSV', filetypes: [['CSV Files', '*.csv'], ['TSV Files', '*.tsv'], ['All Files', '*.*']] }),
        });
        const data = await res.json();
        if (data.success && data.path) {
            const input = document.getElementById('asFileInput');
            if (input) input.value = data.path;
        }
    } catch (e) { updateStatus(`Browse error: ${e.message}`); }
}

async function assocLoadCSV() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const fileInput = document.getElementById('asFileInput');
    const filePath = fileInput?.value;
    if (!filePath) { updateStatus('Select a CSV file first.'); return; }

    const statusEl = document.getElementById('asLoadStatus');
    if (statusEl) statusEl.innerHTML = 'Loading...';

    try {
        const hasHeader = document.querySelector('[data-param="has_header"]')?.value || 'auto';
        const res = await fetch(`/api/associa/${ws.id}/${sub.pipelineId}/load`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ file_path: filePath, has_header: hasHeader }),
        });
        const data = await res.json();
        if (data.success) {
            if (!sub._asState) sub._asState = {};
            sub._asState.filePath = filePath;
            sub._asState.mode = data.mode;
            sub._asState.nSignals = data.n_signals;
            sub._asState.nSamples = data.n_samples;
            sub._asState.nPairs = data.n_pairs;
            sub._asState.signalNames = data.signal_names;
            const modeStr = data.mode === 'batch'
                ? `Batch: ${data.n_signals} signals · ${data.n_pairs} pairs · ${data.n_samples} samples`
                : `Single: 1 pair · ${data.n_samples} samples`;
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ ${modeStr}</span><br>Signals: ${data.signal_names.join(', ')}`;
            updateStatus(`✅ Associa: loaded ${data.n_signals} signals, ${data.n_pairs} pairs`);
            asPersistState(sub);
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

async function assocRunAnalysis() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._asState?.filePath) { updateStatus('Load signals first.'); return; }

    const statusEl = document.getElementById('asRunStatus');
    if (statusEl) statusEl.innerHTML = 'Running...';

    // Collect config from backend saved params (debouncedSaveParams stores under step='associa')
    let savedParams = {};
    try {
        const pRes = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/associa/params`);
        const pData = await pRes.json();
        if (pData.success && pData.params) {
            // Flatten all sections into one dict
            for (const section of Object.values(pData.params)) {
                if (typeof section === 'object') Object.assign(savedParams, section);
            }
        }
    } catch {}

    const config = {
        stationarizer: {
            method: savedParams.stat_method || 'none',
            bp_low: parseFloat(savedParams.bp_low) || 0.008,
            bp_high: parseFloat(savedParams.bp_high) || 0.25,
            sampling_rate: parseFloat(savedParams.sampling_rate) || sub._asState.samplingRate || 1,
        },
        methods: {
            m_ccm: savedParams.m_ccm === true || savedParams.m_ccm === 'true' || savedParams.m_ccm === undefined,
            m_granger: savedParams.m_granger === true || savedParams.m_granger === 'true',
            m_pearson: savedParams.m_pearson === true || savedParams.m_pearson === 'true',
            m_mi: savedParams.m_mi === true || savedParams.m_mi === 'true',
            m_te: savedParams.m_te === true || savedParams.m_te === 'true',
            ccm_E: parseInt(savedParams.ccm_E) || 2,
            ccm_tau: parseInt(savedParams.ccm_tau) || 1,
            ccm_n_boot: parseInt(savedParams.ccm_n_boot) || 20,
            gc_maxlag: parseInt(savedParams.gc_maxlag) || 5,
            gc_criterion: savedParams.gc_criterion || 'aic',
        },
        surrogate: {
            method: savedParams.surr_method || 'iaaft',
            n: parseInt(savedParams.surr_n) || 100,
            alpha: parseFloat(savedParams.surr_alpha) || 0.05,
        },
    };

    try {
        const res = await fetch(`/api/associa/${ws.id}/${sub.pipelineId}/run`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ config }),
        });
        const data = await res.json();
        if (data.success) {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ ${data.run_id} — ${data.n_pairs} pairs, ${data.n_significant || 0} significant</span>`;
            updateStatus(`✅ Associa run complete: ${data.run_id}`);
            asPersistState(sub);
            // Show results in Tables tab
            if (data.summary) {
                const tablesBody = document.getElementById(`tablesBody-${sub.id}`);
                if (tablesBody && data.summary.rows?.length) {
                    const cols = data.summary.columns;
                    tablesBody.innerHTML = `
                        <div style="padding:8px 12px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--chrome-border);background:var(--surface-2)">
                            <span style="font-size:var(--fs-sm);font-weight:600;color:var(--text-secondary)">Association Results</span>
                            <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">${data.summary.rows.length} rows</span>
                        </div>
                        <div style="overflow:auto;flex:1" id="cvResultsTable-${sub.id}">
                            <table style="width:100%;border-collapse:collapse;font-size:var(--fs-xs);font-family:var(--font-mono)">
                                <thead><tr>${cols.map(c => `<th style="position:sticky;top:0;background:var(--surface-3);padding:4px 8px;text-align:left;border-bottom:1px solid var(--chrome-border);white-space:nowrap;color:var(--text-secondary)">${c}</th>`).join('')}</tr></thead>
                                <tbody>${data.summary.rows.map((row, ri) => `<tr style="background:${ri % 2 ? 'var(--surface-1)' : 'var(--surface-0)'}">
                                    ${cols.map(c => `<td style="padding:3px 8px;border-bottom:1px solid rgba(255,255,255,.03);white-space:nowrap">${typeof row[c] === 'number' ? (Number.isInteger(row[c]) ? row[c] : row[c].toFixed(4)) : (row[c] ?? '')}</td>`).join('')}
                                </tr>`).join('')}</tbody>
                            </table>
                        </div>`;
                    cvSwitchGfxTab(sub.id, 'tables');
                }
            }
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

async function assocExport() {
    updateStatus('Export: TODO — connect to backend');
}

async function doCellVisiaLoad() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const fileInput = document.getElementById('cvFileInput');
    const filePath = fileInput?.value;
    if (!filePath) {
        _setStatusBox('cvLoadStatus', `<span style="color:var(--status-error)">✗ No file selected. Click Browse first.</span>`);
        return;
    }
    _setStatusBox('cvLoadStatus', `<span style="color:var(--status-running)">⏳ Loading image...</span>`);
    try {
        const res = await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/load`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: filePath, format: document.querySelector('[data-param="format"]')?.value || 'auto' }),
        });
        const data = await res.json();
        if (data.success) {
            const shape = data.shape || [];
            const dims = shape.length === 4
                ? `${shape[0]} frames × ${shape[1]} ch × ${shape[2]}×${shape[3]} px`
                : shape.length === 3
                ? `${shape[0]} frames × ${shape[1]}×${shape[2]} px`
                : shape.join(' × ');
            _setStatusBox('cvLoadStatus', `
                <span style="color:var(--status-ok)">✓ Image loaded</span><br>
                <span style="opacity:.7">File:</span> ${filePath.split(/[/\\]/).pop()}<br>
                <span style="opacity:.7">Shape:</span> ${dims}<br>
                <span style="opacity:.7">Axes:</span> ${data.axes}<br>
                <span style="opacity:.7">Frames:</span> ${data.n_frames ?? 1}<br>
                <span style="opacity:.7">Channels:</span> ${data.n_channels ?? 1}<br>
                <span style="opacity:.7">Dtype:</span> ${data.dtype}`);
            // Store feature IDs + image info on the sub-tab
            sub._cvLoadInfo = data;
            sub._cvOriginalInfo = data;  // preserved — never overwritten by evaluate
            sub._cvFeatureIds = { load: data.load_id, channel: data.channel_id, meta: data.meta_id };
            if (!sub._cvState) sub._cvState = {};
            sub._cvState.filePath = filePath;
            sub._cvState.format = document.querySelector('[data-param="format"]')?.value || 'auto';
            sub._cvState.loadStatusHtml = document.getElementById('cvLoadStatus')?.innerHTML || '';
            updateStatus(`✅ CellVisia: loaded ${data.n_frames ?? 1} frames, ${data.n_channels ?? 1} ch`);
            showCellVisiaPlayer();
            cvPersistState(sub);
        } else {
            _setStatusBox('cvLoadStatus', `<span style="color:var(--status-error)">✗ ${data.error}</span>`);
        }
    } catch (err) {
        _setStatusBox('cvLoadStatus', `<span style="color:var(--status-error)">✗ ${err.message}</span>`);
    }
}

async function cvSaveChannelAssignment() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._cvFeatureIds?.channel) return;
    const rows = document.querySelectorAll('.cv-ch-row');
    const names = [], roles = [];
    rows.forEach(row => {
        names.push(row.querySelector('.cv-ch-name')?.value || '');
        roles.push(row.querySelector('.cv-ch-role')?.value || '');
    });
    try {
        await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${sub._cvFeatureIds.channel}/params`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ channel_names: names, channel_roles: roles }),
        });
        if (!sub._cvState) sub._cvState = {};
        sub._cvState.channelNames = names;
        sub._cvState.channelRoles = roles;
        updateStatus('✅ Channel assignment saved');
        cvPersistState(sub);
    } catch (e) { console.error(e); }
}

async function cvSaveMetadata() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub?._cvFeatureIds?.meta) return;
    const params = {};
    const px = document.querySelector('[data-param="pixel_size_um"]')?.value;
    const dt = document.querySelector('[data-param="dt_s"]')?.value;
    const dz = document.querySelector('[data-param="dz_um"]')?.value;
    if (px) params.pixel_size_um = parseFloat(px);
    if (dt) params.dt_s = parseFloat(dt);
    if (dz) params.dz_um = parseFloat(dz);
    try {
        await fetch(`/api/cellvisia/${ws.id}/${sub.pipelineId}/feature/${sub._cvFeatureIds.meta}/params`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(params),
        });
        if (!sub._cvState) sub._cvState = {};
        Object.assign(sub._cvState, params);
        updateStatus('✅ Imaging metadata saved');
        cvPersistState(sub);
    } catch (e) { console.error(e); }
}

async function doImportMovie() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const fileInput = document.getElementById('movieFileInput');
    const filePath = fileInput?.value;

    if (!filePath) {
        _setStatusBox('importStatus', `<span style="color:var(--status-error)">✗ No file selected. Click Browse first.</span>`);
        return;
    }

    _setStatusBox('importStatus', `<span style="color:var(--status-running)">⏳ Loading movie...</span>`);

    // Save params first so backend can find the file
    _collectCurrentParams(ws);
    const bodyEl = document.getElementById(`settingsBody-${sub.id}`);
    const form = bodyEl?.querySelector('.settings-form');
    if (form) await saveParamsNow(form);

    // Fetch first frame to validate + get metadata
    try {
        const res = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/${sub.stepId}/preview_frame?frame=0&channel=-1`);
        const data = await res.json();

        if (data.success) {
            const shape = data.shape || [];
            const dims = shape.length === 4
                ? `${shape[0]} frames × ${shape[1]} channels × ${shape[2]}×${shape[3]} px`
                : shape.length === 3
                ? `${shape[0]} frames × ${shape[1]}×${shape[2]} px (single channel)`
                : shape.join(' × ');

            _setStatusBox('importStatus', `
                <span style="color:var(--status-ok)">✓ Movie loaded successfully</span><br>
                <span style="opacity:.7">File:</span> ${filePath.split(/[/\\]/).pop()}<br>
                <span style="opacity:.7">Shape:</span> ${dims}<br>
                <span style="opacity:.7">Frames:</span> ${data.n_frames}<br>
                <span style="opacity:.7">Channels:</span> ${data.n_channels}
            `);

            // ── Persist file path so it survives tree item switches ──
            if (!sub._localParams) sub._localParams = {};
            if (!sub._localParams['select-movie']) sub._localParams['select-movie'] = {};
            sub._localParams['select-movie'].input_file = filePath;
            sub._localParams['select-movie'].format = form?.querySelector('[data-param="format"]')?.value || 'TIFF Stack';
            // Store movie info for player use
            sub._movieInfo = { n_frames: data.n_frames, n_channels: data.n_channels, shape: data.shape };

            updateStatus(`✅ Movie imported: ${data.n_frames} frames, ${data.n_channels} ch`);
            updateStepStatus(sub.pipelineId, 'import', 'done');
        } else {
            _setStatusBox('importStatus', `<span style="color:var(--status-error)">✗ ${data.error}</span>`);
            updateStatus(`❌ Import failed: ${data.error}`);
        }
    } catch (err) {
        _setStatusBox('importStatus', `<span style="color:var(--status-error)">✗ ${err.message}</span>`);
    }
}

async function saveParamsNow(formEl) {
    if (!formEl || !state._projectOpen) return;
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const section = formEl.dataset.section;
    const params = {};
    formEl.querySelectorAll('[data-param]').forEach(el => {
        if (el.type === 'checkbox') params[el.dataset.param] = el.checked;
        else params[el.dataset.param] = el.value;
    });
    await api(`step/${ws.id}/${sub.pipelineId}/${sub.stepId}/params`, 'POST', { params: { [section]: params } });
}

async function selectBatchFolder(btnEl) {
    const formEl = btnEl.closest('.settings-form');
    const inputEl = formEl?.querySelector('[data-param="batch_folder"]');

    try {
        const res = await fetch('/api/browse_open', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                mode: 'folder',
                title: 'Select Image Folder',
            }),
        });
        const data = await res.json();
        if (!data.success || !data.path) return;

        if (inputEl) inputEl.value = data.path;
        updateStatus(`Batch folder: ${data.path}`);
        if (formEl) debouncedSaveParams(formEl);
    } catch (e) {
        updateStatus(`Browse error: ${e.message}`);
    }
}

// ═════════════════════════════════════════════
// AVAILABLE PLOTS REGISTRY (per package)
// ═════════════════════════════════════════════

function stepHasResults(moduleType, stepId) {
    // Steps that produce plottable/viewable results
    const resultsSteps = {
        cornealia: ['segmentation', 'morphometry'],
        cornealia_batch: ['batch_results'],
        fastia: ['import', 'detection', 'tracking', 'classification', 'kinetics', 'association', 'examination'],
        immunia: ['segment', 'track', 'signal_association', 'keller_segel', 'particle_tracking', 'graph_theory', 'integrated_analysis', 'track_examiner'],
        cellade: [null],  // module-level (stepId=null)
        cellfade: [null],
    };
    return (resultsSteps[moduleType] || []).includes(stepId);
}

function getAvailablePlots(moduleType, stepId) {
    if (moduleType === 'cornealia') {
        if (stepId === 'import') return [
            { id: 'segmentation',    icon: '🖼', label: 'Segmentation Overview' },
        ];
        if (stepId === 'segmentation') return [
            { id: 'segmentation',    icon: '🖼', label: 'Segmentation Overview' },
        ];
        if (stepId === 'morphometry') return [
            { id: 'radial_distribution', icon: '📈', label: 'g(r) — Radial Distribution' },
            { id: 'potential',           icon: '📉', label: 'V(r) — Interaction Potential' },
            { id: 'fitting',            icon: '🔬', label: 'Fitting & Stiffness (K)' },
            { id: 'mechanical_field',   icon: '⚡', label: 'Mechanical State' },
            { id: 'comprehensive',      icon: '📊', label: 'Comprehensive Summary' },
            { id: 'publication_gr',     icon: '📄', label: 'Publication — g(r)' },
            { id: 'publication_vr',     icon: '📄', label: 'Publication — V(r)' },
            { id: 'pipeline_figure',    icon: '🎯', label: 'Pipeline Figure' },
        ];
    }
    if (moduleType === 'cornealia_batch') {
        if (stepId === 'batch_results') return [
            { id: 'batch_table',            icon: '📊', label: 'Results Table' },
            { id: 'distributions',          icon: '📈', label: 'K Distributions' },
            { id: 'histogram',              icon: '📊', label: 'Histogram' },
            { id: 'as_vs_bs_boxplots',      icon: '📦', label: 'AS vs BS — Boxplots' },
            { id: 'as_vs_bs_scatter',       icon: '⚬', label: 'AS vs BS — Scatter' },
            { id: 'as_vs_bs_histograms',    icon: '📊', label: 'AS vs BS — Histograms' },
            { id: 'validation_scatter',     icon: '✓', label: 'Validation Scatter' },
            { id: 'validation_bland_altman', icon: '📉', label: 'Bland-Altman Plot' },
            { id: 'deep_dive',             icon: '🔬', label: 'K Deep Dive' },
            { id: 'pub_boxplots',          icon: '📄', label: 'Publication — Boxplots' },
            { id: 'pub_K_deep_dive',       icon: '📄', label: 'Publication — K Deep Dive' },
            { id: 'pub_validation',        icon: '📄', label: 'Publication — Validation' },
            { id: 'pub_K_independence',    icon: '📄', label: 'Publication — K Independence' },
            { id: 'pub_comprehensive',     icon: '📄', label: 'Publication — Comprehensive' },
        ];
        return [];
    }
    if (moduleType === 'fastia') {
        if (stepId === 'import') return [
            { id: 'frame_montage', icon: '🖼', label: 'Frame Montage' },
        ];
        if (stepId === 'detection') return [
            { id: 'detection_montage',  icon: '🖼', label: 'Detection Montage' },
            { id: 'detection_frame',    icon: '🔬', label: 'Detection Single Frame' },
            { id: 'cellmask_montage',   icon: '🟢', label: 'Cell Mask Montage' },
            { id: 'cellmask_frame',     icon: '🔍', label: 'Cell Mask Single Frame' },
        ];
        if (stepId === 'tracking') return [
            { id: 'track_trajectories',  icon: '🖼', label: 'Trajectories' },
            { id: 'track_length_dist',   icon: '📊', label: 'Track Length Distribution' },
            { id: 'track_displacement',  icon: '📈', label: 'Displacement Analysis' },
            { id: 'track_lifetime_map',  icon: '🗺', label: 'Lifetime Map' },
            { id: 'track_summary',       icon: '📋', label: 'Tracking Summary' },
        ];
        if (stepId === 'classification') return [
            { id: 'group_distribution', icon: '📊', label: 'Group Distribution' },
            { id: 'feature_heatmap',    icon: '📦', label: 'Feature Boxplots by Group' },
            { id: 'discriminability',   icon: '🗺', label: 'Pairwise Effect Sizes' },
            { id: 'class_summary',      icon: '📈', label: 'Effect Size Summary' },
        ];
        if (stepId === 'kinetics') return [
            { id: 'rate_distributions',    icon: '📊', label: 'Rate Distributions' },
            { id: 'rates_by_group',        icon: '📦', label: 'Rates by Group' },
            { id: 'assembly_vs_disassembly', icon: '⚬', label: 'Assembly vs Disassembly' },
            { id: 'time_to_peak',          icon: '📈', label: 'Time to Peak' },
            { id: 'rate_quality',          icon: '✓', label: 'Rate Quality (R²)' },
            { id: 'fa_area_distribution',  icon: '📦', label: 'FA Area Distribution' },
            { id: 'intensity_spaghetti',   icon: '📈', label: 'Intensity Traces (start)' },
            { id: 'intensity_spaghetti_peak', icon: '📈', label: 'Intensity Traces (peak)' },
        ];
        if (stepId === 'association') return [];  // plots handled per-run via right-click
    }
    if (moduleType === 'immunia') {
        if (stepId === 'segment') return [
            { id: 'seg_overview',      icon: '🖼', label: 'Segmentation Overview' },
            { id: 'seg_masks_frame',   icon: '🔬', label: 'Masks — Single Frame' },
            { id: 'seg_composite',     icon: '🎨', label: 'Composite Overlay' },
            { id: 'seg_timeline',      icon: '📈', label: 'Object Count Timeline' },
            { id: 'seg_area_timeline', icon: '📊', label: 'Area % Timeline' },
        ];
        if (stepId === 'track') return [
            { id: 'trajectories',              icon: '🖼', label: 'Trajectory Map' },
            { id: 'trajectories_with_quality', icon: '⭐', label: 'Trajectories + Quality' },
            { id: 'track_length',              icon: '📊', label: 'Track Length Distribution' },
            { id: 'velocity_dist',             icon: '📈', label: 'Velocity Distribution' },
            { id: 'msd',                       icon: '📉', label: 'Mean Squared Displacement' },
            { id: 'enhanced_histograms',       icon: '📊', label: 'Enhanced Histograms' },
            { id: 'quality_dashboard',         icon: '🔬', label: 'Quality Dashboard' },
            { id: 'spatial_metrics',           icon: '🗺', label: 'Spatial Metrics' },
            { id: 'trajectory_animation',      icon: '🎬', label: 'Trajectory Animation (MP4)' },
        ];
        if (stepId === 'signal_association') return [];  // plots handled per-run via right-click
        if (stepId === 'particle_tracking') return [
            { id: 'motion_dynamics',   icon: '📊', label: 'Motion & Dynamics (9-panel)' },
            { id: 'spatial_tumor',     icon: '🗺', label: 'Spatial & Tumor (6-panel)' },
            { id: 'before_after',      icon: '📈', label: 'Before/After Tumor Contact' },
            { id: 'pt_params_tumor',   icon: '🧬', label: 'All Parameters × Tumor' },
            { id: 'pt_params_tissue',  icon: '🧫', label: 'All Parameters × Tissue' },
            { id: 'pt_revisit',        icon: '🔄', label: 'Revisit + Motion Bar' },
            { id: 'pt_contact_entry',  icon: '📋', label: 'Contact Entry Stats' },
            { id: 'pt_msd_curves',    icon: '📐', label: 'MSD Curves (per track)' },
            { id: 'pt_eulerian',      icon: '🌡', label: 'Eulerian Fields (6-panel)' },
            { id: 'pt_eulerian_tumor',icon: '🔬', label: 'Fields vs Tumor Distance' },
            { id: 'pt_gr_fields',     icon: '📡', label: 'g(r) Radial Distribution' },
            { id: 'pt_gr_heatmap',    icon: '🧱', label: 'g(r) Per-Tumor Heatmap' },
            { id: 'pt_motion_classes', icon: '🏃', label: 'Motion Classification' },
            { id: 'pt_msd',            icon: '📉', label: 'MSD Analysis' },
            { id: 'pt_speed_dist',     icon: '⚡', label: 'Speed Distribution' },
            { id: 'pt_spatial',        icon: '🎯', label: 'Spatial Context' },
        ];
        if (stepId === 'keller_segel') return [
            { id: 'ks_fields',         icon: '🗺', label: 'KS Model Fields (5-panel)' },
            { id: 'ks_correlation',    icon: '📈', label: 'Theory vs Measured Correlation' },
            { id: 'ks_density',        icon: '🧫', label: 'Cell Density N(x)' },
            { id: 'ks_presence',       icon: '👁', label: 'Cumulative NK Presence' },
            { id: 'ks_overlay',        icon: '🎨', label: 'Theory vs Measured Overlay' },
        ];
        if (stepId === 'graph_theory') return [
            { id: 'gt_comprehensive',     icon: '📊', label: 'Comprehensive Overview' },
            { id: 'gt_metrics',           icon: '📈', label: 'Network Metrics' },
            { id: 'gt_regions',           icon: '🗺', label: 'Regional Analysis' },
            { id: 'gt_boundary',          icon: '🔀', label: 'Boundary Analysis' },
            { id: 'gt_distance_pairs',    icon: '🔗', label: 'Distance Pairs' },
            { id: 'gt_metric_fields',     icon: '🌡', label: 'Metric Fields' },
            { id: 'gt_node_distributions',icon: '📉', label: 'Node Distributions' },
            { id: 'gt_comparative',       icon: '⚖', label: 'Comparative Summary' },
        ];
    }
    if (moduleType === 'cellade') {
        return [
            { id: 'pipeline', icon: '📊', label: 'Pipeline Overview' },
            { id: 'overlay',  icon: '🖼', label: 'Segmentation Overlay' },
            { id: 'stress',   icon: '🔥', label: 'Stress Map' },
            { id: 'metrics',  icon: '📈', label: 'Evaluation Metrics' },
        ];
    }
    if (moduleType === 'cellfade') {
        return [
            { id: 'debug',     icon: '🔬', label: 'Pipeline Debug (8-panel)' },
            { id: 'result',    icon: '🖼', label: 'Detection Result' },
            { id: 'expansion', icon: '📐', label: 'Expansion Before/After' },
            { id: 'overlay',   icon: '🎯', label: 'FA Overlay' },
        ];
    }
    return [];
}

// ═════════════════════════════════════════════
// CUSTOM RIGHT-CLICK CONTEXT MENU
// ═════════════════════════════════════════════

function initContextMenu() {
    // Disable browser right-click everywhere in CelLAB
    document.addEventListener('contextmenu', (e) => {
        // Let pipeline nodes handle their own right-click
        if (e.target.closest('.pipeline-node')) return;

        // Let result items handle their own right-click
        if (e.target.closest('.result-item')) return;

        // Let association run folders handle their own right-click
        if (e.target.closest('.mtree-run-folder')) return;

        // Let section heads with their own context handler pass through
        if (e.target.closest('.assoc-results-header')) return;

        e.preventDefault();
        hideContextMenu();

        // Only show menu when right-clicking on Results header
        const resultsHeader = e.target.closest('.results-header');
        if (!resultsHeader) return;

        const subId = resultsHeader.dataset.subid;
        const moduleType = resultsHeader.dataset.module;
        const stepId = resultsHeader.dataset.step;
        const section = resultsHeader.dataset.section;
        if (!subId || !moduleType) return;

        // Individual results are added via Track Inspector, not right-click
        if (section === 'individual') return;

        showContextMenu(e.clientX, e.clientY, subId, moduleType, stepId);
    });

    // Close on click anywhere
    document.addEventListener('click', hideContextMenu);
}

function showContextMenu(x, y, subId, moduleType, stepId) {
    hideContextMenu();

    const plots = getAvailablePlots(moduleType, stepId);
    if (plots.length === 0) return;

    // Check which are already inserted
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(subId);
    const inserted = sub?.insertedResults?.map(r => r.plotType) || [];

    const menu = document.createElement('div');
    menu.id = 'cellabContextMenu';
    menu.className = 'cellab-ctx-menu';

    menu.innerHTML = `
        <div class="ctx-item ctx-submenu-trigger">
            <span class="ctx-icon">📊</span>
            <span>Insert Result</span>
            <span class="ctx-arrow">▶</span>
            <div class="ctx-submenu">
                ${plots.map(p => {
                    const already = inserted.includes(p.id);
                    return `<div class="ctx-item ${already ? 'ctx-disabled' : ''}" 
                                 onclick="${already ? '' : `ctxInsertPlot('${moduleType}','${stepId}','${p.id}')`}">
                        <span class="ctx-icon">${p.icon}</span>
                        <span>${p.label}</span>
                        ${already ? '<span class="ctx-check">✓</span>' : ''}
                    </div>`;
                }).join('')}
            </div>
        </div>
        <div class="ctx-separator"></div>
        <div class="ctx-item ctx-disabled">
            <span class="ctx-icon">🗑</span>
            <span>Clear All Results</span>
        </div>
    `;

    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    document.body.appendChild(menu);

    // Keep in viewport
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) menu.style.left = (x - rect.width) + 'px';
    if (rect.bottom > window.innerHeight) menu.style.top = (y - rect.height) + 'px';
}

function hideContextMenu() {
    document.querySelectorAll('.cellab-ctx-menu').forEach(el => el.remove());
    _pendingAIContextItems = [];
}

function ctxInsertPlot(moduleType, stepId, plotType) {
    hideContextMenu();

    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(ws.activeSubtab);
    if (!sub) return;

    // Initialize inserted results array on subtab
    if (!sub.insertedResults) sub.insertedResults = [];

    // Special: batch table
    if (plotType === 'batch_table') {
        const existing = sub.insertedResults.find(r => r.plotType === 'batch_table');
        if (!existing) {
            sub.insertedResults.push({
                plotType: 'batch_table', label: 'Results Table', icon: '📊',
                url: '_table_', status: 'done',
            });
            renderModuleTree(sub);
        }
        selectInsertedResultInTree(sub.id, 'batch_table');
        showBatchTable(moduleType, stepId);
        return;
    }

    // Check if already inserted
    const existing = sub.insertedResults.find(r => r.plotType === plotType);
    if (existing) {
        if (existing.url) {
            showResultImage(existing.url, existing.label);
            selectInsertedResultInTree(sub.id, plotType);
        } else {
            doInsertPlot(sub, moduleType, stepId, plotType);
        }
        return;
    }

    // Add to insertedResults
    const plots = getAvailablePlots(moduleType, stepId);
    const plotDef = plots.find(p => p.id === plotType);
    const label = plotDef ? plotDef.label : plotType;
    const icon = plotDef ? plotDef.icon : '📊';

    sub.insertedResults.push({
        plotType, label, icon, url: null, status: 'generating',
    });

    // Re-render tree to show new item
    renderModuleTree(sub);

    // Generate the plot
    doInsertPlot(sub, moduleType, stepId, plotType);
}

async function doInsertPlot(sub, moduleType, stepId, plotType) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const pipelineId = sub.pipelineId;

    // Find the result entry
    const entry = sub.insertedResults?.find(r => r.plotType === plotType);
    if (entry) entry.status = 'generating';
    renderModuleTree(sub);

    updateStatus(`Generating: ${plotType}...`);

    const plotUrl = `step/${ws.id}/${pipelineId}/${stepId}/plot`;
    console.log(`doInsertPlot: calling ${plotUrl} with plot_type=${plotType}`);

    const res = await api(plotUrl, 'POST', {
        plot_type: plotType,
    });

    console.log('doInsertPlot response:', res.success, res.error);

    if (res.success) {
        if (entry) {
            entry.url = res.data.url;
            entry.status = 'done';
        }
        showResultImage(res.data.url, res.data.filename);
        renderModuleTree(sub);
        selectInsertedResultInTree(sub.id, plotType);
        updateStatus(`✅ ${plotType}`);
    } else {
        if (entry) entry.status = 'error';
        renderModuleTree(sub);
        updateStatus(`❌ Plot error: ${res.error}`);
    }
}

function selectInsertedResultInTree(subId, plotType) {
    // Highlight in tree
    const treeBody = document.querySelector(`#moduleTree-${subId}`);
    if (!treeBody) return;
    treeBody.querySelectorAll('.mtree-item').forEach(i => i.classList.remove('active'));
    const item = treeBody.querySelector(`[data-result="${plotType}"]`);
    if (item) item.classList.add('active');
}

function onInsertedResultClick(subId, plotType) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub) return;

    const entry = sub.insertedResults?.find(r => r.plotType === plotType);
    if (!entry) return;

    selectInsertedResultInTree(subId, plotType);

    // Special: batch table
    if (plotType === 'batch_table') {
        showBatchTable(sub.moduleType, sub.stepId);
        return;
    }

    // Special: association run folder — just show settings panel, no image
    if (plotType.startsWith('run_meta_')) {
        return;
    }

    // Stale results auto-regenerate on click
    if (entry.status === 'stale' || !entry.url) {
        if (plotType.startsWith('exam_detail_')) {
            const tid = parseInt(plotType.replace('exam_detail_', ''));
            examInsertDetailedAnalysis(tid);
        } else if (plotType.startsWith('exam_dynamic_')) {
            const tid = parseInt(plotType.replace('exam_dynamic_', ''));
            examOpenDynamicViewer(tid);
        } else if (plotType.startsWith('indiv_track_')) {
            const tid = parseInt(plotType.replace('indiv_track_', ''));
            inspectSelectedTrack(tid);
        } else {
            doInsertPlot(sub, sub.moduleType, sub.stepId, plotType);
        }
    } else if (plotType.startsWith('exam_dynamic_')) {
        // Dynamic viewers always reopen live (no static URL)
        const tid = parseInt(plotType.replace('exam_dynamic_', ''));
        examOpenDynamicViewer(tid);
    } else {
        showResultImage(entry.url, entry.label);
    }
}

function removeInsertedResult(subId, plotType) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub || !sub.insertedResults) return;

    const entry = sub.insertedResults.find(r => r.plotType === plotType);
    const label = entry?.label || plotType;
    if (!confirm(`Remove "${label}" from results?`)) return;

    sub.insertedResults = sub.insertedResults.filter(r => r.plotType !== plotType);
    renderModuleTree(sub);
    updateStatus(`Removed: ${label}`);

    // Clean up dynamic viewer marker file
    if (plotType.startsWith('exam_dynamic_')) {
        const tid = plotType.replace('exam_dynamic_', '');
        fetch(`/api/step/${ws.id}/${sub.pipelineId}/examination/results/plots/exam_dynamic_${tid}.json`, { method: 'DELETE' }).catch(() => {});
    }
}

// ═════════════════════════════════════════════
// RESULT ITEM CONTEXT MENU (Locate / Save As / Remove)
// ═════════════════════════════════════════════

// Track last right-click position for toast placement
let _lastCtxX = 0, _lastCtxY = 0;

function showResultContextMenu(e, subId, plotType) {
    e.preventDefault();
    e.stopPropagation();
    hideContextMenu();
    _lastCtxX = e.clientX;
    _lastCtxY = e.clientY;

    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub) return;

    const entry = sub.insertedResults?.find(r => r.plotType === plotType);
    if (!entry) return;

    const contextItem = {
        type: 'result',
        label: `${plotType} (${sub.label || sub.pipelineId})`,
        data: `Result plot: ${plotType}, Pipeline: ${sub.pipelineId}, Step: ${sub.stepId}, Status: ${entry.status || 'done'}`,
        actionNew: `askAIAboutPipeline('${sub.pipelineId}','${escapeHtml(sub.label || sub.pipelineId)}','${sub.moduleType || ''}')`,
    };

    const menu = document.createElement('div');
    menu.id = 'cellabContextMenu';
    menu.className = 'cellab-ctx-menu';
    menu.innerHTML = `
        <div class="ctx-item" onclick="locateResult('${subId}','${plotType}')">📂 Locate File</div>
        <div class="ctx-item" onclick="showSaveAsDialog('${subId}','${plotType}')">💾 Save As...</div>
        <div class="ctx-separator"></div>
        ${buildAISubmenu(contextItem)}
        <div class="ctx-separator"></div>
        <div class="ctx-item ctx-danger" onclick="hideContextMenu();removeInsertedResult('${subId}','${plotType}')">🗑 Remove</div>
    `;
    document.body.appendChild(menu);
    menu.style.left = e.clientX + 'px';
    menu.style.top = e.clientY + 'px';

    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) menu.style.left = (e.clientX - rect.width) + 'px';
    if (rect.bottom > window.innerHeight) menu.style.top = (e.clientY - rect.height) + 'px';

    setTimeout(() => document.addEventListener('click', hideContextMenu, { once: true }), 50);
}

function showToast(msg, duration = 3000) {
    const old = document.getElementById('cellabToast');
    if (old) old.remove();
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.id = 'cellabToast';
    toast.textContent = msg;

    // Position near the last right-click, or fall back to top-center
    toast.style.position = 'fixed';
    document.body.appendChild(toast);
    const tw = toast.offsetWidth;
    const th = toast.offsetHeight;
    if (_lastCtxX > 0 && _lastCtxY > 0) {
        let tx = _lastCtxX + 12;
        let ty = _lastCtxY - th - 8;
        if (tx + tw > window.innerWidth) tx = window.innerWidth - tw - 12;
        if (ty < 4) ty = _lastCtxY + 20;
        toast.style.left = tx + 'px';
        toast.style.top = ty + 'px';
        toast.style.transform = 'none';
    }

    setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .3s'; setTimeout(() => toast.remove(), 300); }, duration);
}

async function locateResult(subId, plotType) {
    hideContextMenu();
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub) return;

    const entry = sub.insertedResults?.find(r => r.plotType === plotType);
    if (!entry || !entry.url || entry.url === '_table_') {
        showToast('No file path available for this result');
        return;
    }

    const statusRes = await api('status');
    const projectRoot = statusRes.data?.project_root || '';

    const urlParts = entry.url.split('/results/');
    const relPath = urlParts.length > 1 ? urlParts[1].replace(/\//g, '\\') : '';
    const stepPath = `${sub.pipelineId}\\${sub.stepId}\\results\\${relPath}`;
    const fullPath = `${projectRoot}\\workspaces\\${ws.id}\\${stepPath}`;

    try {
        await navigator.clipboard.writeText(fullPath);
        showToast(`📋 Copied to clipboard: ${fullPath}`, 4000);
    } catch {
        showToast(`📂 ${fullPath}`, 5000);
    }
}

function showSaveAsDialog(subId, plotType) {
    hideContextMenu();
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub) return;

    const entry = sub.insertedResults?.find(r => r.plotType === plotType);
    if (!entry) return;

    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'saveAsOverlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

    overlay.innerHTML = `
        <div class="modal-dialog" style="width:380px">
            <div class="modal-header">💾 Save As — ${entry.label || plotType}</div>
            <div class="modal-body" style="padding:14px;display:flex;flex-direction:column;gap:10px">
                <div class="form-row">
                    <span class="form-label">Format</span>
                    <select class="form-select" id="saveAsFormat" style="max-width:140px">
                        <option value="png" selected>PNG</option>
                        <option value="svg">SVG</option>
                        <option value="jpg">JPG</option>
                        <option value="pdf">PDF</option>
                    </select>
                </div>
                <div class="form-row">
                    <span class="form-label">DPI</span>
                    <select class="form-select" id="saveAsDpi" style="max-width:140px">
                        <option value="150">150 (screen)</option>
                        <option value="300" selected>300 (print)</option>
                        <option value="600">600 (publication)</option>
                    </select>
                </div>
                <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:8px">
                    <button class="btn btn-default" onclick="document.getElementById('saveAsOverlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="doSaveAs('${subId}','${plotType}')">Save</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

async function doSaveAs(subId, plotType) {
    const ws = getActiveWorkspace();
    if (!ws) return;
    const sub = ws.subtabs.get(subId);
    if (!sub) return;

    const fmt = document.getElementById('saveAsFormat').value;
    const dpi = document.getElementById('saveAsDpi').value;

    document.getElementById('saveAsOverlay').remove();
    showToast(`Generating ${plotType} as ${fmt.toUpperCase()} @ ${dpi} DPI...`, 5000);

    const res = await api(`step/${ws.id}/${sub.pipelineId}/${sub.stepId}/export-plot`, 'POST', {
        plot_type: plotType,
        format: fmt,
        dpi: parseInt(dpi),
    });

    if (res.success && res.data.url) {
        const filename = res.data.filename || `${plotType}.${fmt}`;

        try {
            // Fetch the file as blob
            const response = await fetch(res.data.url);
            const blob = await response.blob();

            // Always show OS save dialog via File System Access API
            if (typeof window.showSaveFilePicker === 'function') {
                const mimeMap = { png: 'image/png', jpg: 'image/jpeg', svg: 'image/svg+xml', pdf: 'application/pdf' };
                const extMap = { png: '.png', jpg: '.jpg', svg: '.svg', pdf: '.pdf' };
                const handle = await window.showSaveFilePicker({
                    suggestedName: filename,
                    types: [{
                        description: `${fmt.toUpperCase()} file`,
                        accept: { [mimeMap[fmt] || 'application/octet-stream']: [extMap[fmt] || `.${fmt}`] },
                    }],
                });
                const writable = await handle.createWritable();
                await writable.write(blob);
                await writable.close();
                showToast(`✅ Saved: ${handle.name}`);
            } else {
                // Browser doesn't support File System Access API
                // Enable "Ask where to save" in Chrome: chrome://settings/downloads
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
                showToast(`💡 To choose location: enable "Ask where to save" in Chrome settings`, 5000);
            }
        } catch (e) {
            if (e.name === 'AbortError') return; // user cancelled save dialog
            console.error('Save As error:', e);
            showToast(`❌ Save failed: ${e.message}`, 4000);
        }
    } else {
        showToast(`❌ ${res.error || 'Export failed'}`);
    }
}

// ═════════════════════════════════════════════
// TASK MANAGER
// ═════════════════════════════════════════════

let _tasks = [];  // [{id, pipeline, step, status, cpu, ram, startTime, endTime, error}]
let _taskCounter = 0;
let _taskRefreshInterval = null;

function createTask(pipelineName, stepName, pipelineId, stepId) {
    _taskCounter++;
    const ws = getActiveWorkspace();
    const wsId = ws?.id || '';
    const task = {
        id: _taskCounter,
        pipeline: pipelineName,
        step: stepName,
        pipelineId,
        stepId,
        taskKey: `${wsId}/${pipelineId}/${stepId}`,
        status: 'running',
        cpu: '--',
        ram: '--',
        startTime: Date.now(),
        endTime: null,
        error: null,
        log: '',
        expanded: true,  // auto-expand running tasks
    };
    _tasks.unshift(task);
    refreshTaskManagerIfVisible();
    startTaskLogPolling();
    return task;
}

function completeTask(taskId, status = 'done', error = null, log = '') {
    const task = _tasks.find(t => t.id === taskId);
    if (!task) return;
    task.status = status;
    task.endTime = Date.now();
    task.error = error;
    task.cpu = '--';
    task.ram = '--';
    if (log) task.log = log;
    if (error && !task.log) task.log += `\nError: ${error}`;
    refreshTaskManagerIfVisible();
}

function refreshTaskManagerIfVisible() {
    if (!_taskManagerActive) return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    renderTaskManagerView(document.getElementById('viewport'), ws);
    // Auto-scroll running task logs to bottom
    requestAnimationFrame(() => {
        for (const t of _tasks) {
            if (t.expanded && t.status === 'running') {
                const el = document.getElementById(`tmLog-${t.id}`);
                if (el) el.scrollTop = el.scrollHeight;
            }
        }
    });
}

function formatElapsed(ms) {
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${String(sec).padStart(2, '0')}`;
}

function renderTaskManagerView(vp, ws) {
    const running = _tasks.filter(t => t.status === 'running').length;
    const completed = _tasks.filter(t => t.status === 'done').length;
    const failed = _tasks.filter(t => t.status === 'error').length;

    const statusIcons = { running: '⏳', done: '✅', error: '❌' };

    let tableRows = '';
    if (_tasks.length === 0) {
        tableRows = `<tr><td colspan="7" class="tm-empty">No tasks yet. Run a step to see it here.</td></tr>`;
    } else {
        tableRows = _tasks.map(t => {
            const elapsed = t.endTime ? formatElapsed(t.endTime - t.startTime) : formatElapsed(Date.now() - t.startTime);
            const statusCls = t.status === 'running' ? 'tm-status-running' : t.status === 'error' ? 'tm-status-error' : 'tm-status-done';
            const hasLog = (t.log && t.log.trim().length > 0) || t.status === 'running';
            const expandIcon = hasLog ? (t.expanded ? '▾' : '▸') : '';
            return `<tr class="tm-row ${statusCls}" onclick="toggleTaskLog(${t.id})" style="${hasLog ? 'cursor:pointer' : ''}">
                <td class="tm-cell tm-cell-status"><span class="tm-expand-icon">${expandIcon}</span> ${statusIcons[t.status]} <span class="tm-status-text">${t.status}</span></td>
                <td class="tm-cell">${escapeHtml(t.pipeline)}</td>
                <td class="tm-cell">${escapeHtml(t.step)}</td>
                <td class="tm-cell tm-cell-mono">${t.cpu}</td>
                <td class="tm-cell tm-cell-mono">${t.ram}</td>
                <td class="tm-cell tm-cell-mono">${elapsed}</td>
                <td class="tm-cell tm-cell-actions">${
                    t.status === 'running' ? `<button class="tm-action-btn tm-stop-btn" onclick="event.stopPropagation();stopTask(${t.id})">Stop</button>` :
                    t.status === 'error' ? `<button class="tm-action-btn tm-retry-btn" onclick="event.stopPropagation();retryTask(${t.id})">Retry</button>` : ''
                }</td>
            </tr>${t.expanded && hasLog ? `<tr class="tm-log-row"><td colspan="7"><div class="tm-log-content" id="tmLog-${t.id}">${t.log.trim() ? escapeHtml(t.log) : '<span style="color:var(--text-tertiary)">Waiting for output...</span>'}</div></td></tr>` : ''}`
        }).join('');
    }

    vp.innerHTML = `<div class="tm-view fade-in">
        <div class="tm-header-bar">
            <div class="tm-summary">
                <span class="tm-summary-item"><span class="tm-dot tm-dot-running"></span> Running: ${running}</span>
                <span class="tm-summary-item"><span class="tm-dot tm-dot-done"></span> Completed: ${completed}</span>
                <span class="tm-summary-item"><span class="tm-dot tm-dot-error"></span> Failed: ${failed}</span>
                <span class="tm-summary-item tm-summary-total">Total: ${_tasks.length}</span>
            </div>
            <div class="tm-header-actions">
                <button class="tm-clear-btn" onclick="clearCompletedTasks()">Clear Completed</button>
                <button class="tm-clear-btn" onclick="clearAllTasks()">Clear All</button>
            </div>
        </div>
        <div class="tm-table-wrap">
            <table class="tm-table">
                <thead>
                    <tr>
                        <th class="tm-th" style="width:90px">Status</th>
                        <th class="tm-th">Pipeline</th>
                        <th class="tm-th">Step</th>
                        <th class="tm-th" style="width:60px">CPU</th>
                        <th class="tm-th" style="width:70px">RAM</th>
                        <th class="tm-th" style="width:60px">Time</th>
                        <th class="tm-th" style="width:70px">Action</th>
                    </tr>
                </thead>
                <tbody>${tableRows}</tbody>
            </table>
        </div>
    </div>`;

    // Start refresh interval for running tasks
    if (running > 0 && !_taskRefreshInterval) {
        _taskRefreshInterval = setInterval(() => {
            const hasRunning = _tasks.some(t => t.status === 'running');
            if (!hasRunning) { clearInterval(_taskRefreshInterval); _taskRefreshInterval = null; return; }
            refreshTaskManagerIfVisible();
        }, 1000);
    }
}

function clearCompletedTasks() {
    _tasks = _tasks.filter(t => t.status === 'running');
    refreshTaskManagerIfVisible();
}

function toggleTaskLog(taskId) {
    const task = _tasks.find(t => t.id === taskId);
    if (!task) return;
    if (!task.log?.trim() && task.status !== 'running') return;
    task.expanded = !task.expanded;
    refreshTaskManagerIfVisible();
}

function clearAllTasks() {
    if (_tasks.some(t => t.status === 'running')) {
        if (!confirm('There are running tasks. Clear all anyway?')) return;
    }
    _tasks = [];
    refreshTaskManagerIfVisible();
}

async function stopTask(taskId) {
    const task = _tasks.find(t => t.id === taskId);
    if (!task) return;

    // Call backend to cancel the running thread
    if (task.taskKey) {
        try {
            await fetch('/api/tasks/cancel', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: task.taskKey}),
            });
        } catch (e) { /* best effort */ }
    }

    // Hide any visible stop button
    const parts = task.taskKey?.split('/') || [];
    if (parts.length === 3) {
        // Try to determine moduleType from pipelineId
        const pid = parts[1];
        const stepId = parts[2];
        const moduleType = pid.replace(/-\d+$/, '').replace(/_/g, '');
        const stopBtn = document.getElementById(`stopBtn-${moduleType}-${stepId}`);
        if (stopBtn) { stopBtn.disabled = true; stopBtn.style.opacity = '0.4'; stopBtn.style.cursor = 'default'; stopBtn.style.color = ''; }
    }

    completeTask(taskId, 'error', 'Stopped by user');
    updateStatus('⏹ Task stopped');
}

function retryTask(taskId) {
    const task = _tasks.find(t => t.id === taskId);
    if (!task) return;
    // Re-run the step
    doRunAnalysis(task.pipelineId.split('-').slice(0, -1).join('-').replace(/_/g, ''), task.stepId);
}

let _taskManagerActive = false;

function openTaskManager() {
    _taskManagerActive = !_taskManagerActive;
    const btn = document.getElementById('tmToolbarBtn');
    if (btn) btn.classList.toggle('active', _taskManagerActive);

    // Hide side panels for full-width view
    const rp = document.querySelector('.right-panel');
    const rr = document.getElementById('rightResizer');
    if (_taskManagerActive) {
        if (rp) rp.style.display = 'none';
        if (rr) rr.style.display = 'none';
    } else {
        if (rp) rp.style.display = '';
        if (rr) rr.style.display = '';
    }

    renderViewport();
    renderLeftPanel();
}

let _logPollInterval = null;

function startTaskLogPolling() {
    if (_logPollInterval) return;
    _logPollInterval = setInterval(pollRunningTaskLogs, 1000);
}

async function pollRunningTaskLogs() {
    const running = _tasks.filter(t => t.status === 'running');
    if (running.length === 0) {
        clearInterval(_logPollInterval);
        _logPollInterval = null;
        return;
    }

    // Kill zombie tasks older than 6 hours
    const now = Date.now();
    for (const task of running) {
        if (now - task.startTime > 6 * 60 * 60 * 1000) {
            task.status = 'error';
            task.error = 'Timed out (zombie)';
            task.endTime = now;
        }
    }

    // Only poll logs for up to 2 tasks to avoid flooding connections
    const toCheck = running.filter(t => t.status === 'running').slice(0, 2);
    let changed = false;
    for (const task of toCheck) {
        if (!task.taskKey) continue;
        try {
            const res = await api('tasks/log', 'POST', { key: task.taskKey });
            if (res.success && res.data.log && res.data.log !== task.log) {
                task.log = res.data.log;
                changed = true;
            }
        } catch (e) { /* silent */ }
    }
    if (changed) refreshTaskManagerIfVisible();
}

// ═════════════════════════════════════════════
// DROPDOWN MENUS
// ═════════════════════════════════════════════

// ═════════════════════════════════════════════
// ASSOCIATION — EDGE ANALYSIS
// ═════════════════════════════════════════════

async function _loadEdgeStatus() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const el = document.getElementById('edgeAnalysisStatus');
    if (!el) return;

    try {
        const res = await fetch(`/api/step/${ws.id}/${sub.pipelineId}/association/results/edge_analysis_summary.json`);
        if (res.ok) {
            const data = await res.json();
            const d = data.fa_edge_distribution || {};
            el.innerHTML = `<span style="color:var(--status-ok)">✓ Edge analysis available</span><br>`
                + `Sectors: ${data.num_sectors} · ${data.n_protruding}P / ${data.n_retracting}R / ${data.n_steady}S<br>`
                + `FAs mapped: ${data.n_fa_mapped}<br>`
                + `FA distribution: ${d.protruding || 0} protruding, ${d.retracting || 0} retracting, ${d.steady || 0} steady<br>`
                + `<span style="opacity:.5">Time: ${data.elapsed_s?.toFixed(1) || '?'}s</span>`;
        } else {
            el.innerHTML = 'No edge analysis yet. Click Run Edge Analysis.';
        }
    } catch (e) {
        el.innerHTML = 'No edge analysis yet. Click Run Edge Analysis.';
    }
}

async function runEdgeAnalysis() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const el = document.getElementById('edgeAnalysisStatus');
    if (el) el.innerHTML = '<span style="color:var(--status-running)">⏳ Running edge analysis...</span>';

    // Collect params
    const bodyEl = document.getElementById(`settingsBody-${ws.activeSubtab}`);
    const params = {};
    if (bodyEl) {
        bodyEl.querySelectorAll('[data-param]').forEach(e => { params[e.dataset.param] = e.value; });
    }

    try {
        const res = await api(`step/${ws.id}/${sub.pipelineId}/association/edge_analysis`, 'POST', params);
        if (res.success) {
            const d = res.data;
            if (el) el.innerHTML = `<span style="color:var(--status-ok)">✓ Done in ${d.elapsed_s?.toFixed(1) || '?'}s</span><br>`
                + `Sectors: ${d.num_sectors} · ${d.n_protruding}P / ${d.n_retracting}R / ${d.n_steady}S<br>`
                + `FAs mapped: ${d.n_fa_mapped}`;
            updateStatus('✓ Edge analysis complete');
        } else {
            if (el) el.innerHTML = `<span style="color:var(--status-error)">❌ ${res.error}</span>`;
        }
    } catch (e) {
        if (el) el.innerHTML = `<span style="color:var(--status-error)">❌ ${e.message}</span>`;
    }
}


// ═════════════════════════════════════════════
// ASSOCIATION — RUNS DISCOVERY
// ═════════════════════════════════════════════

async function discoverAssociationRuns(sub) {
    if (!sub || sub.stepId !== 'association') return;
    const ws = getActiveWorkspace();
    if (!ws) return;

    const res = await api(`step/${ws.id}/${sub.pipelineId}/association/runs`);
    if (!res.success || !res.data.runs) return;

    const runs = res.data.runs;
    if (!sub.insertedResults) sub.insertedResults = [];

    // Clear old run items
    sub.insertedResults = sub.insertedResults.filter(r => !r._isRun && !r._runId);

    for (const run of runs) {
        const runId = run.run_id || run.run_dir;
        // Add run header
        sub.insertedResults.push({
            plotType: `run_meta_${runId}`,
            label: run.label || runId,
            icon: '📁',
            group: 'Runs',
            _isRun: true,
            _runId: runId,
            _runMeta: run,
            status: 'done',
            url: null,  // no image URL — handled by settings panel
        });

        // Add existing plots as children
        for (const plotFile of (run.plot_files || [])) {
            const baseName = plotFile.replace(/\.(png|jpg)$/i, '');
            const plotUrl = `/api/step/${ws.id}/${sub.pipelineId}/association/results/runs/${runId}/plots/${plotFile}`;
            let label = baseName.replace(/_/g, ' ');
            let icon = '📊';
            if (baseName.includes('significance')) { label = 'Significance Rates'; icon = '📊'; }
            else if (baseName.includes('distributions')) { label = 'Statistic Distributions'; icon = '📦'; }
            else if (baseName.includes('effect_sizes')) { label = 'P-value Distribution'; icon = '📈'; }
            else if (baseName.includes('method_agreement')) { label = 'Method Agreement'; icon = '🗺'; }
            else if (baseName.includes('group_coupling')) { label = 'Coupling by Group'; icon = '🏷'; }
            else if (baseName.startsWith('assoc_track_')) {
                const parts = baseName.replace('assoc_track_', '').split('_');
                label = `Track ${parts[0]}`;
                icon = '🔗';
            }

            sub.insertedResults.push({
                plotType: `${runId}_${baseName}`,
                label: label,
                icon: icon,
                _runId: runId,
                url: plotUrl,
                status: 'done',
            });
        }
    }

    renderModuleTree(sub);
}

function showAssocRunContextMenu(event, subId, runId) {
    event.preventDefault();
    event.stopPropagation();
    hideContextMenu();
    _lastRightClickPos = { x: event.clientX, y: event.clientY };
    const menu = document.createElement('div');
    menu.id = 'cellabContextMenu';
    menu.className = 'cellab-ctx-menu';
    menu.innerHTML = `
        <div class="ctx-item" onclick="insertAssociationRunPlot('${runId}','assoc_significance');hideContextMenu()"><span class="ctx-icon">📊</span><span>Significance Rates</span></div>
        <div class="ctx-item" onclick="insertAssociationRunPlot('${runId}','assoc_distributions');hideContextMenu()"><span class="ctx-icon">📦</span><span>Statistic Distributions</span></div>
        <div class="ctx-item" onclick="insertAssociationRunPlot('${runId}','assoc_effect_sizes');hideContextMenu()"><span class="ctx-icon">📈</span><span>P-value Distribution</span></div>
        <div class="ctx-item" onclick="insertAssociationRunPlot('${runId}','assoc_method_agreement');hideContextMenu()"><span class="ctx-icon">🗺</span><span>Method Agreement</span></div>
        <div class="ctx-item" onclick="insertAssociationRunPlot('${runId}','assoc_group_coupling');hideContextMenu()"><span class="ctx-icon">🏷</span><span>Coupling by Group</span></div>
        <div class="ctx-separator"></div>
        <div class="ctx-item ctx-danger" onclick="deleteAssociationRun('${runId}');hideContextMenu()"><span class="ctx-icon">🗑</span><span>Delete Run</span></div>
    `;
    menu.style.cssText = `position:fixed;left:${event.clientX}px;top:${event.clientY}px;z-index:10000`;
    document.body.appendChild(menu);
    setTimeout(() => document.addEventListener('click', hideContextMenu, { once: true }), 30);
}

function showAssocEdgePlotsMenu(event, subId) {
    event.preventDefault();
    event.stopPropagation();
    hideContextMenu();
    _lastRightClickPos = { x: event.clientX, y: event.clientY };
    const menu = document.createElement('div');
    menu.id = 'cellabContextMenu';
    menu.className = 'cellab-ctx-menu';
    menu.innerHTML = `
        <div class="ctx-item" onclick="insertEdgePlot('edge_velocity_heatmap');hideContextMenu()"><span class="ctx-icon">📊</span><span>Edge Velocity Heatmap</span></div>
        <div class="ctx-item" onclick="insertEdgePlot('edge_motion_map');hideContextMenu()"><span class="ctx-icon">🌊</span><span>Edge Motion Map</span></div>
    `;
    menu.style.cssText = `position:fixed;left:${event.clientX}px;top:${event.clientY}px;z-index:10000`;
    document.body.appendChild(menu);
}

async function insertEdgePlot(plotType) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    updateStatus(`Generating ${plotType}...`);
    try {
        const res = await api(`step/${ws.id}/${sub.pipelineId}/association/edge_plot`, 'POST', { plot_type: plotType });
        if (res.success && res.data.url) {
            showResultImage(res.data.url, plotType);
            if (!sub.insertedResults) sub.insertedResults = [];
            const itemId = `edge_${res.data.filename?.replace(/\.png$/, '') || plotType}`;
            if (!sub.insertedResults.find(r => r.plotType === itemId)) {
                sub.insertedResults.push({ plotType: itemId, label: plotType === 'edge_velocity_heatmap' ? 'Edge Velocity Heatmap' : 'Edge Motion Map', icon: plotType === 'edge_velocity_heatmap' ? '📊' : '🌊', _isEdge: true, url: res.data.url, status: 'done' });
                renderModuleTree(sub);
            }
        }
    } catch (e) { updateStatus(`❌ ${e.message}`); }
}

async function deleteAssociationRun(runId) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    if (!confirm(`Delete run ${runId}?`)) return;
    const res = await api(`step/${ws.id}/${sub.pipelineId}/association/runs/${runId}`, 'DELETE');
    if (res.success) { sub.insertedResults = (sub.insertedResults || []).filter(r => r._runId !== runId); renderModuleTree(sub); updateStatus(`Deleted: ${runId}`); }
}

async function insertAssociationRunPlot(runId, plotType) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    updateStatus(`Generating ${plotType}...`);
    try {
        const res = await api(`step/${ws.id}/${sub.pipelineId}/association/runs/${runId}/plot`, 'POST', { plot_type: plotType });
        if (res.success && res.data.url) {
            showResultImage(res.data.url, `${plotType} (${runId})`);
            if (!sub.insertedResults) sub.insertedResults = [];
            const itemId = `${runId}_${res.data.filename?.replace(/\.png$/, '') || plotType}`;
            if (!sub.insertedResults.find(r => r.plotType === itemId)) {
                let label = plotType.replace('assoc_', '').replace(/_/g, ' ');
                label = label.charAt(0).toUpperCase() + label.slice(1);
                sub.insertedResults.push({ plotType: itemId, label, icon: '📊', _runId: runId, url: res.data.url, status: 'done' });
                renderModuleTree(sub);
            }
        }
    } catch (err) { updateStatus(`❌ ${err.message}`); }
}

// ═════════════════════════════════════════════
// IMMUNIA — Signal Association Run Functions
// ═════════════════════════════════════════════

async function discoverIMMUNIAAssocRuns(sub) {
    if (!sub || sub.stepId !== 'signal_association') return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    const res = await api(`step/${ws.id}/${sub.pipelineId}/signal_association/runs`);
    if (!res.success || !res.data.runs) return;
    const runs = res.data.runs;
    if (!sub.insertedResults) sub.insertedResults = [];
    sub.insertedResults = sub.insertedResults.filter(r => !r._isRun && !r._runId);
    for (const run of runs) {
        const runId = run.run_id || run.run_dir;
        sub.insertedResults.push({ plotType: `run_meta_${runId}`, label: run.label || runId, icon: '📁', group: 'Runs', _isRun: true, _runId: runId, _runMeta: run, status: 'done', url: null });
        for (const plotFile of (run.plot_files || [])) {
            const baseName = plotFile.replace(/\.(png|jpg)$/i, '');
            const plotUrl = `/api/step/${ws.id}/${sub.pipelineId}/signal_association/results/runs/${runId}/plots/${plotFile}`;
            let label = baseName.replace(/_/g, ' '), icon = '📊';
            if (baseName.includes('comprehensive')) { label = 'Comprehensive'; icon = '📊'; }
            else if (baseName.includes('influence_matrix')) { label = 'Influence Matrix'; icon = '🗺'; }
            else if (baseName.includes('distribution')) { label = 'ρ Distribution'; icon = '📈'; }
            else if (baseName.includes('significance')) { label = 'Significance'; icon = '🎯'; }
            else if (baseName.includes('comparison')) { label = 'Strength vs Sig'; icon = '⚬'; }
            sub.insertedResults.push({ plotType: `${runId}_${baseName}`, label, icon, _runId: runId, url: plotUrl, status: 'done' });
        }
    }
    renderModuleTree(sub);
}

async function insertIMMUNIAAssocRunPlot(runId, plotType) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    updateStatus(`Generating ${plotType}...`);
    const res = await api(`step/${ws.id}/${sub.pipelineId}/signal_association/runs/${runId}/plot`, 'POST', { plot_type: plotType });
    if (res.success) { showResultImage(res.data.url, res.data.filename || plotType); setTimeout(() => discoverIMMUNIAAssocRuns(sub), 500); }
    else { updateStatus(`Plot error: ${res.error}`); }
}

async function deleteIMMUNIAAssocRun(subId, runId) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(subId);
    if (!sub) return;
    if (!confirm(`Delete run ${runId}?`)) return;
    const res = await api(`step/${ws.id}/${sub.pipelineId}/signal_association/runs/${runId}`, 'DELETE');
    if (res.success) { updateStatus(`Deleted: ${runId}`); discoverIMMUNIAAssocRuns(sub); }
}

function showIMMUNIAAssocRunMenu(event, subId, runId) {
    event.preventDefault();
    event.stopPropagation();
    hideContextMenu();
    const menu = document.createElement('div');
    menu.id = 'cellabContextMenu';
    menu.className = 'cellab-ctx-menu';
    menu.innerHTML = `
        <div class="ctx-item" onclick="insertIMMUNIAAssocRunPlot('${runId}','comprehensive');hideContextMenu()"><span class="ctx-icon">📊</span><span>Comprehensive (6-panel)</span></div>
        <div class="ctx-item" onclick="insertIMMUNIAAssocRunPlot('${runId}','influence_matrix');hideContextMenu()"><span class="ctx-icon">🗺</span><span>Influence Matrix</span></div>
        <div class="ctx-item" onclick="insertIMMUNIAAssocRunPlot('${runId}','distribution');hideContextMenu()"><span class="ctx-icon">📈</span><span>ρ Distribution</span></div>
        <div class="ctx-item" onclick="insertIMMUNIAAssocRunPlot('${runId}','significance');hideContextMenu()"><span class="ctx-icon">🎯</span><span>Significance Analysis</span></div>
        <div class="ctx-item" onclick="insertIMMUNIAAssocRunPlot('${runId}','comparison');hideContextMenu()"><span class="ctx-icon">⚬</span><span>Strength vs Significance</span></div>
        <div class="ctx-sep"></div>
        <div class="ctx-item ctx-danger" onclick="deleteIMMUNIAAssocRun('${subId}','${runId}');hideContextMenu()"><span class="ctx-icon">🗑</span><span>Delete Run</span></div>
    `;
    menu.style.cssText = `position:fixed;left:${event.clientX}px;top:${event.clientY}px;z-index:10000`;
    document.body.appendChild(menu);
    setTimeout(() => document.addEventListener('click', hideContextMenu, { once: true }), 30);
}

// ═════════════════════════════════════════════
// GRAPH THEORY — Run Management
// ═════════════════════════════════════════════

async function _loadGTAssocRuns() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    const pid = sub.pipelineId;
    const res = await api(`step/${ws.id}/${pid}/signal_association/runs`);
    const container = document.getElementById('gtAssocRunsList');
    if (!container) return;
    if (!res.success || !res.data.runs || res.data.runs.length === 0) {
        container.innerHTML = '<span style="font-size:var(--fs-xs);color:var(--status-error)">No association runs found.</span>';
        return;
    }
    const runs = res.data.runs;
    const saved = sub._localParams?.['gt-networks']?.gt_selected_runs || 'all';
    const selectedSet = saved === 'all' ? null : new Set(saved.split(','));
    let html = '<div style="display:flex;gap:4px;margin-bottom:6px">' +
        '<button class="btn btn-default" onclick="_gtSelectAll(true)" style="font-size:10px;padding:2px 6px">All</button>' +
        '<button class="btn btn-default" onclick="_gtSelectAll(false)" style="font-size:10px;padding:2px 6px">None</button></div>';
    for (const run of runs) {
        const rid = run.run_id || run.run_dir;
        const checked = selectedSet === null || selectedSet.has(rid) ? 'checked' : '';
        const cfg = run.config || {};
        const stats = run.statistics || {};
        const methodKey = Object.keys(stats)[0] || cfg.method || '?';
        const s = stats[methodKey] || {};
        html += `<label style="display:flex;align-items:center;gap:6px;font-size:var(--fs-xs);padding:5px 8px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);cursor:pointer">
            <input type="checkbox" class="gtRunCheck" value="${rid}" ${checked} onchange="_gtUpdateSelection()">
            <span style="font-weight:600;color:var(--text-primary)">${(cfg.method||'?').toUpperCase()}</span>
            <span style="color:var(--text-tertiary)">· ${cfg.signal_type||'?'} · ${s.n_pairs||'?'} pairs</span>
            <span style="color:var(--text-tertiary);font-size:9px;margin-left:auto">${rid.replace('run_','')}</span>
        </label>`;
    }
    container.innerHTML = html;
}
function _gtSelectAll(checked) {
    document.querySelectorAll('.gtRunCheck').forEach(c => c.checked = checked);
    _gtUpdateSelection();
}
function _gtUpdateSelection() {
    const checks = document.querySelectorAll('.gtRunCheck');
    const selected = Array.from(checks).filter(c => c.checked).map(c => c.value);
    const input = document.getElementById('gtSelectedRuns');
    if (input) input.value = selected.length === checks.length ? 'all' : selected.join(',');
}

async function discoverGTRuns(sub) {
    if (!sub || sub.stepId !== 'graph_theory') return;
    const ws = getActiveWorkspace();
    if (!ws) return;
    const res = await api(`step/${ws.id}/${sub.pipelineId}/graph_theory/runs`);
    if (!res.success || !res.data.runs) return;
    if (!sub.insertedResults) sub.insertedResults = [];
    sub.insertedResults = sub.insertedResults.filter(r => !r._isRun && !r._runId);
    for (const run of res.data.runs) {
        const runId = run.run_id || run.run_dir;
        sub.insertedResults.push({ plotType: `run_meta_${runId}`, label: run.label || runId, icon: '📁', group: 'Runs', _isRun: true, _runId: runId, _runMeta: run, status: 'done', url: null });
        for (const pf of (run.plot_files || [])) {
            const bn = pf.replace(/\.(png|jpg)$/i, '');
            sub.insertedResults.push({ plotType: `${runId}_${bn}`, label: bn.replace(/_/g, ' '), icon: '📊', _runId: runId, url: `/api/step/${ws.id}/${sub.pipelineId}/graph_theory/results/runs/${runId}/plots/${pf}`, status: 'done' });
        }
    }
    renderModuleTree(sub);
}

async function insertGTRunPlot(runId, plotType) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;
    updateStatus(`Generating ${plotType}...`);
    const res = await api(`step/${ws.id}/${sub.pipelineId}/graph_theory/runs/${runId}/plot`, 'POST', { plot_type: plotType });
    if (res.success) {
        showResultImage(res.data.url, res.data.filename || plotType);
        setTimeout(() => discoverGTRuns(sub), 500);
    } else {
        updateStatus(`Plot error: ${res.error}`);
    }
}

async function deleteGTRun(subId, runId) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(subId);
    if (!sub) return;
    if (!confirm(`Delete GT run ${runId}?`)) return;
    const res = await api(`step/${ws.id}/${sub.pipelineId}/graph_theory/runs/${runId}`, 'DELETE');
    if (res.success) {
        updateStatus(`Deleted: ${runId}`);
        discoverGTRuns(sub);
    }
}

// ═════════════════════════════════════════════
// ASSOCIATION — PAIR SELECTION
// ═════════════════════════════════════════════

let _assocData = {
    channelNames: [],
    tracks: null,       // from df_classified.csv
    filteredIndices: [], // track indices matching group filter
};

async function initAssocPairSelection() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const wsId = ws.id;
    const pid = sub.pipelineId;

    // Read saved state from local params
    const saved = sub._localParams?.['assoc-pairs'] || {};
    const savedChannels = saved.selected_channels || 'all';
    const savedRunMode = saved.assoc_run_mode || 'all';
    const savedGroupFilter = saved.assoc_group_filter || 'all';
    const savedTrackId = saved.assoc_single_track_id || '';

    // Load channel names from import params
    try {
        const paramRes = await api(`step/${wsId}/${pid}/import/params`);
        if (paramRes.success) {
            for (const [sk, sv] of Object.entries(paramRes.data)) {
                if (typeof sv === 'object' && sv.ch1_name) {
                    _assocData.channelNames = [];
                    for (let i = 1; i <= 4; i++) {
                        const name = sv[`ch${i}_name`];
                        if (name) _assocData.channelNames.push(name);
                    }
                    break;
                }
            }
        }
    } catch(e) {}

    // Build channel checkboxes and restore checked state
    const checksEl = document.getElementById('assocChannelChecks');
    if (checksEl && _assocData.channelNames.length > 0) {
        const chColors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12'];
        const savedSet = savedChannels === 'all' ? null : new Set(savedChannels.split(','));

        checksEl.innerHTML = _assocData.channelNames.map((name, i) => {
            const color = chColors[i % chColors.length];
            const checked = savedSet === null || savedSet.has(String(i));
            return `<label style="display:flex;align-items:center;gap:4px;font-size:var(--fs-xs);cursor:pointer;padding:4px 10px;border-radius:4px;border:1px solid ${color}40;background:${color}15">
                <input type="checkbox" ${checked ? 'checked' : ''} onchange="assocSaveChannelState()" data-ch-idx="${i}" style="margin:0">
                <span style="color:${color};font-weight:600">${name}</span>
            </label>`;
        }).join('');
    } else if (checksEl) {
        checksEl.innerHTML = '<span style="color:var(--status-warning)">No channels found. Run Movie Import first.</span>';
    }

    // Restore run mode
    const runModeEl = document.getElementById('assocRunMode');
    if (runModeEl) runModeEl.value = savedRunMode;
    assocToggleTrackSelector();

    // Load classification data for track selector
    try {
        const csvRes = await fetch(`/api/step/${wsId}/${pid}/classification/results/df_classified.csv`);
        if (csvRes.ok) {
            const text = await csvRes.text();
            const lines = text.trim().split('\n');
            const headers = lines[0].split(',').map(h => h.trim());
            _assocData.tracks = [];
            for (let i = 1; i < lines.length; i++) {
                const vals = lines[i].split(',');
                const row = {};
                headers.forEach((h, j) => row[h] = vals[j]?.trim() || '');
                _assocData.tracks.push(row);
            }

            // Populate group filter and restore selection
            const groups = [...new Set(_assocData.tracks.map(t => t.group))].sort();
            const gf = document.getElementById('assocGroupFilter');
            if (gf) {
                gf.innerHTML = `<option value="all">All Groups (${_assocData.tracks.length})</option>` +
                    groups.map(g => {
                        const cnt = _assocData.tracks.filter(t => t.group === g).length;
                        return `<option value="${g}">${g} (${cnt})</option>`;
                    }).join('');
                gf.value = savedGroupFilter;
            }

            assocFilterTracks();

            // Restore selected track
            if (savedTrackId) {
                const trackSel = document.getElementById('assocTrackSelect');
                if (trackSel) {
                    for (let i = 0; i < trackSel.options.length; i++) {
                        if (trackSel.options[i].value === savedTrackId) {
                            trackSel.selectedIndex = i;
                            break;
                        }
                    }
                }
            }
        }
    } catch(e) {}

    assocUpdatePairPreview();
    assocUpdateStats();
}

function assocSaveChannelState() {
    // Save checked channel indices to hidden input
    const indices = [];
    document.querySelectorAll('#assocChannelChecks input[type=checkbox]').forEach(cb => {
        if (cb.checked) indices.push(cb.dataset.chIdx);
    });
    const hidden = document.getElementById('assocSelectedChannels');
    if (hidden) hidden.value = indices.length === _assocData.channelNames.length ? 'all' : indices.join(',');
    assocUpdatePairPreview();
}

function assocUpdatePairPreview() {
    const checked = [];
    document.querySelectorAll('#assocChannelChecks input:checked').forEach(cb => {
        const idx = parseInt(cb.dataset.chIdx);
        checked.push({ idx, name: _assocData.channelNames[idx] });
    });

    // Form all pairs from checked channels
    const pairs = [];
    for (let i = 0; i < checked.length; i++) {
        for (let j = i + 1; j < checked.length; j++) {
            pairs.push(`${checked[i].name} ↔ ${checked[j].name}`);
        }
    }

    const el = document.getElementById('assocPairPreview');
    if (el) {
        if (pairs.length === 0) {
            el.innerHTML = '<span style="color:var(--status-warning)">Select ≥2 channels to form pairs.</span>';
        } else {
            el.innerHTML = `<span style="color:var(--status-ok)">${pairs.length} pair${pairs.length > 1 ? 's' : ''}:</span> ` +
                pairs.map(p => `<span style="color:var(--brand-accent)">${p}</span>`).join(' · ');
        }
    }

    assocUpdateStats();
}

function assocToggleTrackSelector() {
    const mode = document.getElementById('assocRunMode')?.value || 'all';
    const sel = document.getElementById('assocTrackSelector');
    if (sel) sel.style.display = mode === 'single' ? 'block' : 'none';
    assocUpdateStats();
}

function assocFilterTracks() {
    const groupVal = document.getElementById('assocGroupFilter')?.value || 'all';
    const minLen = parseInt(document.querySelector('[data-param="min_track_length"]')?.value || 10);

    if (!_assocData.tracks) return;

    _assocData.filteredIndices = [];
    _assocData.tracks.forEach((t, i) => {
        const len = parseInt(t.track_length || 0);
        if (len < minLen) return;
        if (groupVal !== 'all' && t.group !== groupVal) return;
        _assocData.filteredIndices.push(i);
    });

    // Update track dropdown
    const sel = document.getElementById('assocTrackSelect');
    if (sel) {
        sel.innerHTML = _assocData.filteredIndices.map(i => {
            const t = _assocData.tracks[i];
            const tid = parseInt(t.track_id);
            return `<option value="${tid}">${t.group} · Track ${tid} (${t.track_length}f)</option>`;
        }).join('');
    }

    const countEl = document.getElementById('assocTrackCount');
    if (countEl) countEl.textContent = `${_assocData.filteredIndices.length} tracks`;

    assocUpdateStats();
}

function assocStepTrack(delta) {
    const sel = document.getElementById('assocTrackSelect');
    if (!sel || sel.options.length === 0) return;
    sel.selectedIndex = Math.max(0, Math.min(sel.options.length - 1, sel.selectedIndex + delta));
}

function assocUpdateStats() {
    const el = document.getElementById('assocPairStats');
    if (!el) return;

    const nChecked = document.querySelectorAll('#assocChannelChecks input:checked').length;
    const nPairs = nChecked * (nChecked - 1) / 2;
    const mode = document.getElementById('assocRunMode')?.value || 'all';
    const nTracks = mode === 'single' ? 1 : (_assocData.filteredIndices?.length || 0);
    const nTotal = nTracks * nPairs;

    if (nPairs === 0) {
        el.innerHTML = '<span style="color:var(--status-warning)">Select ≥2 channels</span>';
    } else if (nTracks === 0) {
        el.innerHTML = '<span style="color:var(--status-warning)">No tracks match filters</span>';
    } else {
        el.innerHTML = `${nTracks} track${nTracks > 1 ? 's' : ''} × ${nPairs} pair${nPairs > 1 ? 's' : ''} = <span style="color:var(--brand-accent);font-weight:700">${nTotal} analyses</span>`;
    }
}


// ═════════════════════════════════════════════
// FA EXAMINATION — INTERACTIVE CANVAS
// ═════════════════════════════════════════════

const EXAM_GROUP_COLORS = {
    'G1': '#3498db', 'G2': '#2ecc71', 'G3': '#1abc9c', 'G4': '#9b59b6', 'G5': '#34495e',
    'G6': '#e67e22', 'G7': '#e74c3c', 'G8': '#f39c12', 'G9': '#95a5a6',
};

let _exam = {
    tracks: null,        // array from df_classified.csv
    frame: 0,
    totalFrames: 91,
    channel: 0,          // channel index
    channelNames: [],
    nChannels: 1,
    playing: false,
    playTimer: null,
    playSpeed: 50,
    selectedTrackId: null,
    imgW: 512, imgH: 512,
    wsId: null, pid: null,
};

async function initExaminationCanvas() {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    _exam.wsId = ws.id;
    _exam.pid = sub.pipelineId;
    _exam.frame = 0;

    // Populate graphics panel with interactive canvas
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (gfx) {
        gfx.innerHTML = `
            <div id="examCanvasWrap" style="position:relative;width:100%;height:100%;background:#0a0a0a;overflow:hidden;display:flex;align-items:center;justify-content:center">
                <img id="examCellImg" style="max-width:100%;max-height:100%;object-fit:contain;image-rendering:auto;display:block" draggable="false">
                <div id="examFAOverlay" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none"></div>
                <div id="examCanvasLegend" style="position:absolute;top:8px;right:8px;background:rgba(0,0,0,.75);padding:6px 10px;border-radius:6px;font-size:10px;line-height:1.6;pointer-events:none;z-index:50;backdrop-filter:blur(4px)"></div>
            </div>`;
    }

    const statsEl = document.getElementById('examStats');

    // Load metadata via preview_frame (returns JSON with base64)
    try {
        const metaRes = await fetch(`/api/step/${_exam.wsId}/${_exam.pid}/import/preview_frame?frame=0&channel=0`);
        const meta = await metaRes.json();
        if (meta.success) {
            _exam.totalFrames = meta.n_frames || 91;
            _exam.nChannels = meta.n_channels || 1;
            _exam.imgW = meta.shape?.[meta.shape.length - 1] || 512;
            _exam.imgH = meta.shape?.[meta.shape.length - 2] || 512;

            const slider = document.getElementById('examFrameSlider');
            if (slider) { slider.max = _exam.totalFrames - 1; slider.value = 0; }
            document.getElementById('examFrameTotal').textContent = `/ ${_exam.totalFrames}`;

            // Show first frame immediately
            const img = document.getElementById('examCellImg');
            if (img && meta.image) img.src = meta.image;
        }
    } catch(e) { console.warn('Exam: metadata load failed', e); }

    // Get channel names from import params
    try {
        const paramRes = await api(`step/${_exam.wsId}/${_exam.pid}/import/params`);
        if (paramRes.success) {
            const p = paramRes.data;
            _exam.channelNames = [];
            for (const [sk, sv] of Object.entries(p)) {
                if (typeof sv === 'object' && sv.ch1_name) {
                    for (let i = 1; i <= 4; i++) {
                        const name = sv[`ch${i}_name`];
                        if (name) _exam.channelNames.push(name);
                    }
                    break;
                }
            }
        }
    } catch(e) {}

    // Build channel buttons
    const chBtns = document.getElementById('examChannelBtns');
    if (chBtns) {
        let names = _exam.channelNames.length > 0
            ? _exam.channelNames
            : Array.from({length: _exam.nChannels}, (_, i) => `Ch ${i}`);
        chBtns.innerHTML = names.map((n, i) =>
            `<button class="btn ${i === 0 ? 'btn-primary' : 'btn-default'}" onclick="examSwitchChannel(${i})" id="examChBtn${i}" style="font-size:var(--fs-xs);padding:4px 8px">${n}</button>`
        ).join('');
    }

    // Load track/classification data
    try {
        const csvRes = await fetch(`/api/step/${_exam.wsId}/${_exam.pid}/classification/results/df_classified.csv`);
        if (csvRes.ok) {
            const text = await csvRes.text();
            const lines = text.trim().split('\n');
            const headers = lines[0].split(',').map(h => h.trim());
            _exam.tracks = [];
            for (let i = 1; i < lines.length; i++) {
                const vals = lines[i].split(',');
                const row = {};
                headers.forEach((h, j) => row[h] = vals[j]?.trim() || '');
                _exam.tracks.push(row);
            }
        }
    } catch(e) {}

    // Load frame_data (per-frame track positions)
    try {
        const fdRes = await api(`step/${_exam.wsId}/${_exam.pid}/examination/frame_data`, 'POST', {});
        if (fdRes.success) {
            _exam.frameData = fdRes.data.frame_data;
            _exam.totalFrames = fdRes.data.n_frames || _exam.totalFrames;
            const slider = document.getElementById('examFrameSlider');
            if (slider) slider.max = _exam.totalFrames - 1;
            document.getElementById('examFrameTotal').textContent = `/ ${_exam.totalFrames}`;
            const nTracks = fdRes.data.n_tracks || (_exam.tracks?.length || 0);
            if (statsEl) statsEl.innerHTML = `<span style="color:var(--status-ok)">✓ ${nTracks} tracks · ${_exam.totalFrames} frames</span>`;

            // Build group checkboxes from actual data
            const allGroups = new Set();
            for (const fkey of Object.keys(_exam.frameData)) {
                for (const t of _exam.frameData[fkey]) {
                    if (t.group) allGroups.add(t.group);
                }
            }
            const sortedGroups = [...allGroups].sort();
            const ALL_GROUPS = ['G1','G2','G3','G4','G5','G6','G7','G8','G9'];
            const groupsInData = new Set();
            for (const fkey of Object.keys(_exam.frameData)) {
                for (const t of _exam.frameData[fkey]) {
                    if (t.group) groupsInData.add(t.group);
                }
            }
            const checksEl = document.getElementById('examGroupChecks');
            const legendEl = document.getElementById('examGroupLegend');
            const GROUP_NAMES = {
                'G1': 'NAs turn-over', 'G2': 'NAs maturing', 'G3': 'NAs advancing',
                'G4': 'NAs retracting', 'G5': 'NAs stable', 'G6': 'FAs retracting',
                'G7': 'FAs stable edge', 'G8': 'FAs stable inside', 'G9': 'Noise',
            };
            if (checksEl) {
                checksEl.innerHTML = ALL_GROUPS.map(g => {
                    const color = EXAM_GROUP_COLORS[g] || '#95a5a6';
                    const inData = groupsInData.has(g);
                    return `<label style="display:flex;align-items:center;gap:2px;font-size:var(--fs-xs);cursor:pointer;padding:2px 6px;border-radius:3px;border:1px solid ${color}40;background:${color}15;${inData ? '' : 'opacity:0.4'}">
                        <input type="checkbox" ${inData ? 'checked' : ''} onchange="examUpdateOverlay()" data-group="${g}" style="margin:0">
                        <span style="color:${color};font-weight:600">${g}</span>
                    </label>`;
                }).join('');
            }
            if (legendEl) {
                legendEl.innerHTML = ALL_GROUPS.map(g => {
                    const color = EXAM_GROUP_COLORS[g] || '#95a5a6';
                    const name = GROUP_NAMES[g] || g;
                    const inData = groupsInData.has(g);
                    return `<span style="display:flex;align-items:center;gap:3px;${inData ? '' : 'opacity:0.35'}"><span style="width:8px;height:8px;border-radius:50%;background:${color};flex-shrink:0"></span>${g}: ${name}${inData ? '' : ' (0)'}</span>`;
                }).join('');
            }
        }
    } catch(e) { console.warn('Exam: frame_data load failed', e); }

    // Show overlay for frame 0
    examUpdateOverlay();
}

async function examShowFrame(f) {
    _exam.frame = f;
    const label = document.getElementById('examFrameLabel');
    if (label) label.textContent = f;
    const slider = document.getElementById('examFrameSlider');
    if (slider) slider.value = f;

    // Fetch cell image (returns JSON with base64)
    try {
        const res = await fetch(`/api/step/${_exam.wsId}/${_exam.pid}/import/preview_frame?frame=${f}&channel=${_exam.channel}`);
        const data = await res.json();
        if (data.success && data.image) {
            const img = document.getElementById('examCellImg');
            if (img) {
                img.src = data.image;
                // Update overlay after image loads (need dimensions for positioning)
                img.onload = () => examUpdateOverlay();
            }
        }
    } catch(e) {
        console.warn('Exam: frame load failed', e);
    }
}

function examUpdateOverlay() {
    const overlay = document.getElementById('examFAOverlay');
    const img = document.getElementById('examCellImg');
    if (!overlay || !img || !_exam.frameData) return;

    const circleSize = parseInt(document.getElementById('examCircleSize')?.value || 12);
    const minLife = parseInt(document.getElementById('examMinLife')?.value || 3);
    const showLabels = document.getElementById('examShowLabels')?.checked || false;

    document.getElementById('examCircleVal').textContent = circleSize;
    document.getElementById('examMinLifeVal').textContent = minLife;

    // Get enabled groups from checkboxes
    const enabledGroups = new Set();
    document.querySelectorAll('#examGroupChecks input[type="checkbox"]').forEach(cb => {
        if (cb.checked) enabledGroups.add(cb.dataset.group);
    });
    const hasAnyGroupChecked = enabledGroups.size > 0;

    // If user re-enables any group, clear isolation mode
    if (hasAnyGroupChecked && _exam.isolatedTrackId != null) {
        _exam.isolatedTrackId = null;
    }

    // Get image position within wrapper (object-fit: contain centering)
    const wrap = document.getElementById('examCanvasWrap');
    if (!wrap) return;

    const wrapRect = wrap.getBoundingClientRect();
    const imgRect = img.getBoundingClientRect();
    const offX = imgRect.left - wrapRect.left;
    const offY = imgRect.top - wrapRect.top;
    const scaleX = imgRect.width / _exam.imgW;
    const scaleY = imgRect.height / _exam.imgH;

    // Get active tracks for this frame
    const frameKey = String(_exam.frame);
    const activeTracks = _exam.frameData[frameKey] || [];

    // Build track lookup for lifetime filtering
    const trackLookup = {};
    if (_exam.tracks) {
        for (const t of _exam.tracks) {
            trackLookup[parseInt(t.track_id)] = t;
        }
    }

    let html = '';
    let visCount = 0;

    for (const at of activeTracks) {
        const tid = at.track_id;
        const info = trackLookup[tid] || {};
        const lifetime = parseInt(info.track_length || at.lifetime || 1);
        const group = info.group || at.group || 'G9';

        // Filters
        if (lifetime < minLife && tid !== _exam.isolatedTrackId) continue;
        if (_exam.isolatedTrackId != null) {
            // Isolation mode: show only the searched track
            if (tid !== _exam.isolatedTrackId) continue;
        } else if (hasAnyGroupChecked && !enabledGroups.has(group)) {
            continue;
        }

        const color = EXAM_GROUP_COLORS[group] || '#95a5a6';
        const cx = offX + at.cx * scaleX;
        const cy = offY + at.cy * scaleY;
        const isSelected = _exam.selectedTrackId === tid;
        const r = circleSize / 2;

        html += `<div class="exam-fa-dot${isSelected ? ' exam-fa-selected' : ''}" style="left:${cx - r}px;top:${cy - r}px;width:${circleSize}px;height:${circleSize}px;border-color:${color};background:${color}33" data-tid="${tid}" onclick="event.stopPropagation();examSelectTrack(${tid})" oncontextmenu="event.preventDefault();event.stopPropagation();examFAContextMenu(event,${tid})" title="Track ${tid} · ${group} · ${lifetime}f">`;
        if (showLabels) html += `<span>${tid}</span>`;
        html += `</div>`;
        visCount++;
    }

    overlay.innerHTML = html;
    overlay.style.pointerEvents = 'auto';

    // Update stats
    const statsEl = document.getElementById('examStats');
    if (statsEl && _exam.frameData) {
        const total = _exam.tracks?.length || 0;
        const active = activeTracks.length;
        statsEl.innerHTML = `Frame ${_exam.frame} · Active: ${active} · Visible: ${visCount} · Total: ${total}`;
    }

    // Update canvas legend (always show all 9 groups)
    const canvasLegend = document.getElementById('examCanvasLegend');
    if (canvasLegend) {
        const ALL_GROUPS = ['G1','G2','G3','G4','G5','G6','G7','G8','G9'];
        const GROUP_NAMES = {
            'G1': 'NAs turn-over', 'G2': 'NAs maturing', 'G3': 'NAs advancing',
            'G4': 'NAs retracting', 'G5': 'NAs stable', 'G6': 'FAs retracting',
            'G7': 'FAs stable edge', 'G8': 'FAs stable inside', 'G9': 'Noise',
        };
        if (_exam.isolatedTrackId != null && !hasAnyGroupChecked) {
            canvasLegend.innerHTML = `<span style="color:#f1c40f">◉ Track ${_exam.isolatedTrackId} (isolated)</span>`;
        } else {
            canvasLegend.innerHTML = ALL_GROUPS.map(g => {
                const color = EXAM_GROUP_COLORS[g] || '#95a5a6';
                const active = enabledGroups.has(g);
                return `<div style="display:flex;align-items:center;gap:5px;${active ? '' : 'opacity:0.25'}"><span style="width:8px;height:8px;border-radius:50%;background:${color};flex-shrink:0"></span><span style="color:${color}">${g}</span><span style="color:#999">${GROUP_NAMES[g] || ''}</span></div>`;
            }).join('');
        }
    }
}

function examSelectTrack(tid) {
    _exam.selectedTrackId = tid;
    examUpdateOverlay();

    const info = _exam.tracks?.find(t => parseInt(t.track_id) === tid);
    const infoEl = document.getElementById('examSelectedInfo');
    if (infoEl && info) {
        const asm = parseFloat(info.assembly_rate);
        const dsm = parseFloat(info.disassembly_rate);
        infoEl.style.display = 'block';
        infoEl.innerHTML = `
            <span style="font-weight:700;color:var(--brand-accent)">Track ${tid}</span> · ${info.group || '?'}<br>
            Length: ${info.track_length || '?'} frames (${info.start_frame}→${info.end_frame})<br>
            Assembly: ${isNaN(asm) ? 'N/A' : asm.toFixed(4)} min⁻¹<br>
            Disassembly: ${isNaN(dsm) ? 'N/A' : dsm.toFixed(4)} min⁻¹<br>
            Area: ${parseFloat(info.mean_area || 0).toFixed(3)} μm² · Edge: ${parseFloat(info.mean_edge_distance || 0).toFixed(1)} μm
            <div style="margin-top:6px;display:flex;gap:4px">
                <button class="btn btn-primary" onclick="examInsertDetailedAnalysis(${tid})" style="font-size:var(--fs-xs);padding:4px 10px">🔬 Static Analysis</button>
                <button class="btn btn-default" onclick="examOpenDynamicViewer(${tid})" style="font-size:var(--fs-xs);padding:4px 10px">🔍 Dynamic Viewer</button>
            </div>
        `;
    } else if (infoEl) {
        infoEl.style.display = 'none';
    }
}

function examSwitchChannel(idx) {
    _exam.channel = idx;
    // Update button states
    for (let i = 0; i < _exam.nChannels; i++) {
        const btn = document.getElementById(`examChBtn${i}`);
        if (btn) { btn.className = i === idx ? 'btn btn-primary' : 'btn btn-default'; }
    }
    examShowFrame(_exam.frame);
}

function examTogglePlay() {
    const btn = document.getElementById('examPlayBtn');
    if (_exam.playing) {
        clearTimeout(_exam.playTimer);
        _exam.playing = false;
        if (btn) btn.textContent = '▶ Play';
    } else {
        _exam.playSpeed = parseInt(document.getElementById('examSpeed')?.value || 50);
        _exam.playing = true;
        if (btn) btn.textContent = '⏸ Stop';
        examPlayNextFrame();
    }
}

async function examPlayNextFrame() {
    if (!_exam.playing) return;
    _exam.frame = (_exam.frame + 1) % _exam.totalFrames;
    await examShowFrame(_exam.frame);
    if (_exam.playing) {
        _exam.playTimer = setTimeout(examPlayNextFrame, _exam.playSpeed);
    }
}

async function examStepFrame(delta) {
    const f = Math.max(0, Math.min(_exam.totalFrames - 1, _exam.frame + delta));
    await examShowFrame(f);
}

async function examSeekFrame(val) {
    await examShowFrame(parseInt(val));
}

function examSetSpeed() {
    _exam.playSpeed = parseInt(document.getElementById('examSpeed')?.value || 50);
    // Speed change takes effect on next frame naturally (setTimeout-based)
}

function examSearchTrack() {
    const raw = document.getElementById('examSearchTrack')?.value?.trim();
    if (!raw) return;
    const tid = parseInt(raw);
    if (isNaN(tid)) { updateStatus('Enter a valid track ID'); return; }

    if (!_exam.frameData) { updateStatus('No frame data loaded'); return; }

    // Find first frame where this track appears
    let firstFrame = -1;
    for (let f = 0; f < _exam.totalFrames; f++) {
        const tracks = _exam.frameData[String(f)];
        if (!tracks) continue;
        if (tracks.find(t => t.track_id === tid)) {
            firstFrame = f;
            break;
        }
    }

    if (firstFrame < 0) {
        updateStatus(`Track ${tid} not found in any frame`);
        return;
    }

    // Deselect all group checkboxes → isolates this track visually
    document.querySelectorAll('#examGroupChecks input').forEach(c => c.checked = false);

    // Select this track and jump to its first frame
    _exam.selectedTrackId = tid;
    _exam.isolatedTrackId = tid;  // special flag: show only this track regardless of filters
    examShowFrame(firstFrame);
    examSelectTrack(tid);
    updateStatus(`Track ${tid} isolated · frame ${firstFrame}`);
}


// ═════════════════════════════════════════════
// FA EXAMINATION — DYNAMIC VIEWER
// ═════════════════════════════════════════════

let _dynViewer = {
    trackId: null,
    frameData: null,   // array of {frame, cx, cy, intensity, area_um2}
    frameIdx: 0,       // index into frameData (not absolute frame number)
    zoom: 4,
    channel: 0,
    imgW: 512, imgH: 512,
    playing: false,
    playTimer: null,
};

async function examOpenDynamicViewer(tid) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    // If this track's viewer is already open, don't reload
    if (_dynViewer.trackId === tid && document.getElementById('dynCanvas')) {
        return;
    }

    const info = _exam.tracks?.find(t => parseInt(t.track_id) === tid);
    const group = info?.group || '?';
    const plotType = `exam_dynamic_${tid}`;

    // Register in tree if not already there
    if (!sub.insertedResults) sub.insertedResults = [];
    let entry = sub.insertedResults.find(r => r.plotType === plotType);
    if (!entry) {
        entry = {
            plotType: plotType,
            label: `Track ${tid} (${group}) 🔍`,
            icon: '🔍',
            url: null,
            status: 'done',
            isDynamic: true,
            trackId: tid,
        };
        sub.insertedResults.push(entry);
        renderModuleTree(sub);
    }

    // Save marker file for cross-session persistence
    try {
        await api(`step/${ws.id}/${sub.pipelineId}/examination/save_dynamic_marker`, 'POST', {
            track_id: tid, group: group,
        });
    } catch(e) {}

    // Clear panel cache when switching to a different track
    _dynViewer._panelCache = {};
    _dynViewer._loadingKey = null;

    // Load and show the viewer
    await _examLoadDynamicViewer(tid, group, sub);
}

async function _examLoadDynamicViewer(tid, group, sub) {
    _dynViewer.trackId = tid;
    _dynViewer.frameIdx = 0;
    _dynViewer.channel = _exam.channel || 0;

    // Ensure exam state is initialized
    const ws = getActiveWorkspace();
    if (!_exam.wsId) {
        _exam.wsId = ws?.id;
        _exam.pid = sub?.pipelineId;
    }
    // Also store on _dynViewer for self-sufficient panel updates
    _dynViewer.wsId = _exam.wsId || ws?.id;
    _dynViewer.pid = _exam.pid || sub?.pipelineId;

    // Load per-frame track data from backend
    updateStatus(`Loading dynamic viewer for Track ${tid}...`);
    const res = await api(`step/${_dynViewer.wsId}/${_dynViewer.pid}/examination/track_frames`, 'POST', { track_id: tid });
    if (!res.success) { updateStatus(`❌ ${res.error}`); return; }

    _dynViewer.frameData = res.data.frame_data;
    _dynViewer.imgW = res.data.img_width;
    _dynViewer.imgH = res.data.img_height;

    // Load channel names if not yet loaded
    if (!_exam.channelNames || _exam.channelNames.length === 0) {
        try {
            const paramRes = await api(`step/${_dynViewer.wsId}/${_dynViewer.pid}/import/params`);
            if (paramRes.success) {
                for (const [sk, sv] of Object.entries(paramRes.data)) {
                    if (typeof sv === 'object' && sv.ch1_name) {
                        _exam.channelNames = [];
                        for (let i = 1; i <= 4; i++) {
                            const name = sv[`ch${i}_name`];
                            if (name) _exam.channelNames.push(name);
                        }
                        break;
                    }
                }
            }
        } catch(e) {}
    }

    // Build channel buttons
    let chNames = _exam.channelNames.length > 0
        ? _exam.channelNames
        : Array.from({length: _exam.nChannels}, (_, i) => `Ch ${i}`);
    const chBtnsHtml = chNames.map((n, i) =>
        `<button class="btn ${i === _dynViewer.channel ? 'btn-primary' : 'btn-default'}" onclick="dynSwitchChannel(${i})" id="dynChBtn${i}" style="font-size:10px;padding:3px 8px">${n}</button>`
    ).join('');

    // Render zoomed canvas + controls in SETTINGS panel (middle column)
    const bodyEl = document.getElementById(`settingsBody-${sub.id}`);
    if (bodyEl) {
        bodyEl.innerHTML = `
        <div style="padding:0">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                <button class="btn btn-default" onclick="dynBackToOverview()" style="font-size:10px;padding:3px 8px">← Overview</button>
                <span style="font-weight:700;color:var(--brand-accent);font-size:var(--fs-sm)">🔍 Track ${tid}</span>
                <span style="color:var(--text-tertiary);font-size:var(--fs-xs)">${group} · ${_dynViewer.frameData.length}f</span>
            </div>
            <div style="background:#1a1a1a;border:1px solid #333;border-radius:6px;overflow:hidden;display:flex;align-items:center;justify-content:center;height:280px;margin-bottom:8px">
                <canvas id="dynCanvas" style="image-rendering:pixelated" width="270" height="270"></canvas>
            </div>
            <div style="display:flex;gap:4px;align-items:center;margin-bottom:6px">
                <button class="btn btn-primary" id="dynPlayBtn" onclick="dynTogglePlay()" style="min-width:50px;font-size:10px;padding:2px 6px">▶ Play</button>
                <button class="btn btn-default" onclick="dynStep(-1)" style="font-size:10px;padding:2px 4px">◀</button>
                <button class="btn btn-default" onclick="dynStep(1)" style="font-size:10px;padding:2px 4px">▶</button>
                <input type="range" id="dynFrameSlider" min="0" max="${_dynViewer.frameData.length - 1}" value="0" style="flex:1" oninput="dynSeek(this.value)">
                <span style="font-size:10px;color:var(--text-tertiary);min-width:30px" id="dynFrameInfo">${_dynViewer.frameData[0]?.frame || 0}</span>
            </div>
            <div style="display:flex;gap:3px;align-items:center;margin-bottom:6px">
                <span style="font-size:10px;color:var(--text-tertiary)">Zoom:</span>
                ${[1,2,4,8].map(z => `<button class="btn ${z === _dynViewer.zoom ? 'btn-primary' : 'btn-default'}" onclick="dynSetZoom(${z})" id="dynZoom${z}" style="font-size:9px;padding:2px 6px;min-width:28px">${z}×</button>`).join('')}
            </div>
            <div style="display:flex;gap:3px;align-items:center;margin-bottom:6px;flex-wrap:wrap">
                <span style="font-size:10px;color:var(--text-tertiary)">Channel:</span>
                ${chBtnsHtml}
            </div>
            <div id="dynStats" style="font-size:10px;font-family:var(--font-mono);color:var(--text-tertiary);padding:6px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-sm);line-height:1.6;margin-bottom:6px">
                Loading...
            </div>
            <button class="btn btn-primary" onclick="examInsertDetailedAnalysis(${tid})" style="font-size:10px;padding:4px 8px;width:100%">🔬 Generate Static Analysis</button>
        </div>`;
    }

    // Render montage (top) + timeseries (bottom) STACKED in graphics panel
    const gfx = document.getElementById(`graphicsBody-${sub.id}`);
    if (gfx) {
        // Try saved images first for instant display after refresh
        const savedMontageUrl = `/api/step/${_dynViewer.wsId}/${_dynViewer.pid}/examination/results/plots/exam_dynamic_${tid}_montage_ch${_dynViewer.channel}_z${_dynViewer.zoom}.jpg`;
        const savedTsUrl = `/api/step/${_dynViewer.wsId}/${_dynViewer.pid}/examination/results/plots/exam_dynamic_${tid}_timeseries.jpg`;

        gfx.innerHTML = `
        <div style="display:flex;flex-direction:column;height:100%;gap:6px;padding:6px;overflow-y:auto;background:#0f0f0f">
            <div style="flex-shrink:0">
                <img id="dynMontage" src="${savedMontageUrl}" style="width:100%;border-radius:6px;display:block" draggable="false"
                     onerror="this.removeAttribute('src');this.alt='Generating montage...'">
            </div>
            <div style="flex-shrink:0">
                <img id="dynTimeseries" src="${savedTsUrl}" style="width:100%;border-radius:6px;display:block" draggable="false"
                     onerror="this.removeAttribute('src');this.alt='Generating timeseries...'">
            </div>
        </div>`;
    }

    // Load panels from backend
    dynLoadPanels(tid, _dynViewer.channel);

    // Show first frame
    dynShowFrame(0);
    updateStatus(`Dynamic viewer: Track ${tid}`);
}

async function dynShowFrame(idx) {
    if (!_dynViewer.frameData || idx < 0 || idx >= _dynViewer.frameData.length) return;
    _dynViewer.frameIdx = idx;

    const fd = _dynViewer.frameData[idx];
    const absFrame = fd.frame;

    // Update slider + info
    const slider = document.getElementById('dynFrameSlider');
    if (slider) slider.value = idx;
    const info = document.getElementById('dynFrameInfo');
    if (info) info.textContent = `Frame ${absFrame} (${idx + 1}/${_dynViewer.frameData.length})`;

    // Update stats
    const statsEl = document.getElementById('dynStats');
    if (statsEl) {
        statsEl.innerHTML = `
            <div>Frame: <span style="color:var(--brand-accent)">${absFrame}</span></div>
            <div>Position: <span style="color:var(--brand-accent)">(${fd.cx}, ${fd.cy})</span></div>
            <div>Intensity: <span style="color:var(--brand-accent)">${fd.intensity.toFixed(1)}</span></div>
            <div>Area: <span style="color:var(--brand-accent)">${fd.area_um2.toFixed(3)} μm²</span></div>
        `;
    }

    // Fetch full frame image
    try {
        const wsId = _dynViewer.wsId || _exam.wsId;
        const pid = _dynViewer.pid || _exam.pid;
        const res = await fetch(`/api/step/${wsId}/${pid}/import/preview_frame?frame=${absFrame}&channel=${_dynViewer.channel}`);
        const data = await res.json();
        if (data.success && data.image) {
            dynDrawCrop(data.image, fd.cx, fd.cy);
        }
    } catch(e) { console.warn('dynShowFrame failed', e); }
}

function dynDrawCrop(base64Src, cx, cy) {
    const canvas = document.getElementById('dynCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const img = new Image();
    img.onload = () => {
        const zoom = _dynViewer.zoom;
        const cropW = Math.floor(_dynViewer.imgW / zoom);
        const cropH = Math.floor(_dynViewer.imgH / zoom);

        // Center crop on centroid
        let sx = Math.round(cx - cropW / 2);
        let sy = Math.round(cy - cropH / 2);
        sx = Math.max(0, Math.min(sx, _dynViewer.imgW - cropW));
        sy = Math.max(0, Math.min(sy, _dynViewer.imgH - cropH));

        // Canvas display size
        const displaySize = 400;
        canvas.width = displaySize;
        canvas.height = displaySize;
        canvas.style.width = displaySize + 'px';
        canvas.style.height = displaySize + 'px';

        // Scale source coords to image dimensions in the base64
        const scaleX = img.width / _dynViewer.imgW;
        const scaleY = img.height / _dynViewer.imgH;

        ctx.imageSmoothingEnabled = zoom <= 2;
        ctx.clearRect(0, 0, displaySize, displaySize);
        ctx.drawImage(img,
            sx * scaleX, sy * scaleY, cropW * scaleX, cropH * scaleY,
            0, 0, displaySize, displaySize);

        // Draw crosshair at FA centroid
        const drawCx = ((cx - sx) / cropW) * displaySize;
        const drawCy = ((cy - sy) / cropH) * displaySize;
        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(drawCx, 0); ctx.lineTo(drawCx, displaySize);
        ctx.moveTo(0, drawCy); ctx.lineTo(displaySize, drawCy);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw circle at centroid
        ctx.beginPath();
        ctx.arc(drawCx, drawCy, 12, 0, Math.PI * 2);
        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 2;
        ctx.stroke();
    };
    img.src = base64Src;
}

function dynSetZoom(z) {
    _dynViewer.zoom = z;
    [1,2,4,8].forEach(zz => {
        const btn = document.getElementById(`dynZoom${zz}`);
        if (btn) btn.className = zz === z ? 'btn btn-primary' : 'btn btn-default';
    });
    dynShowFrame(_dynViewer.frameIdx);
    // Reload montage at new zoom level
    dynLoadPanels(_dynViewer.trackId, _dynViewer.channel);
}

async function dynLoadPanels(tid, channel) {
    const cacheKey = `${tid}_${channel}_${_dynViewer.zoom}`;

    // Skip if already loading same request
    if (_dynViewer._loadingKey === cacheKey) return;

    // Use cache if available
    if (_dynViewer._panelCache && _dynViewer._panelCache[cacheKey]) {
        const cached = _dynViewer._panelCache[cacheKey];
        const montageImg = document.getElementById('dynMontage');
        const tsImg = document.getElementById('dynTimeseries');
        if (montageImg) montageImg.src = cached.montage;
        if (tsImg) tsImg.src = cached.timeseries;
        return;
    }

    _dynViewer._loadingKey = cacheKey;

    const montageImg = document.getElementById('dynMontage');
    const tsImg = document.getElementById('dynTimeseries');
    if (montageImg) montageImg.style.opacity = '0.4';
    if (tsImg) tsImg.style.opacity = '0.4';

    const wsId = _dynViewer.wsId || _exam.wsId;
    const pid = _dynViewer.pid || _exam.pid;
    if (!wsId || !pid) { console.warn('dynLoadPanels: no wsId/pid'); return; }

    const res = await api(`step/${wsId}/${pid}/examination/dynamic_panels`, 'POST', {
        track_id: tid,
        channel: channel,
        zoom: _dynViewer.zoom,
    });

    // Only apply if this is still the latest request
    if (_dynViewer._loadingKey !== cacheKey) return;
    _dynViewer._loadingKey = null;

    if (res.success) {
        if (montageImg) { montageImg.src = res.data.montage; montageImg.style.opacity = '1'; }
        if (tsImg) { tsImg.src = res.data.timeseries; tsImg.style.opacity = '1'; }
        _dynViewer.montageFrames = res.data.montage_frames;

        // Cache result
        if (!_dynViewer._panelCache) _dynViewer._panelCache = {};
        _dynViewer._panelCache[cacheKey] = { montage: res.data.montage, timeseries: res.data.timeseries };
    } else {
        if (montageImg) montageImg.style.opacity = '1';
        if (tsImg) tsImg.style.opacity = '1';
    }
}

function dynSwitchChannel(idx) {
    _dynViewer.channel = idx;
    const n = _exam.channelNames.length || _exam.nChannels;
    for (let i = 0; i < n; i++) {
        const btn = document.getElementById(`dynChBtn${i}`);
        if (btn) btn.className = i === idx ? 'btn btn-primary' : 'btn btn-default';
    }
    dynShowFrame(_dynViewer.frameIdx);
    // Reload montage for new channel
    dynLoadPanels(_dynViewer.trackId, idx);
}

function dynStep(delta) {
    const next = Math.max(0, Math.min(_dynViewer.frameData.length - 1, _dynViewer.frameIdx + delta));
    dynShowFrame(next);
}

function dynSeek(val) {
    dynShowFrame(parseInt(val));
}

function dynTogglePlay() {
    const btn = document.getElementById('dynPlayBtn');
    if (_dynViewer.playing) {
        clearTimeout(_dynViewer.playTimer);
        _dynViewer.playing = false;
        if (btn) btn.textContent = '▶ Play';
    } else {
        _dynViewer.playing = true;
        if (btn) btn.textContent = '⏸ Stop';
        dynPlayNext();
    }
}

async function dynPlayNext() {
    if (!_dynViewer.playing) return;
    const next = _dynViewer.frameIdx + 1;
    if (next >= _dynViewer.frameData.length) {
        // Loop back
        await dynShowFrame(0);
    } else {
        await dynShowFrame(next);
    }
    if (_dynViewer.playing) {
        _dynViewer.playTimer = setTimeout(dynPlayNext, 150);
    }
}

function dynBackToOverview() {
    if (_dynViewer.playing) {
        clearTimeout(_dynViewer.playTimer);
        _dynViewer.playing = false;
    }
    // Re-initialize the overview canvas
    initExaminationCanvas();
}


function examFAContextMenu(e, tid) {
    // Remove any existing context menu
    const old = document.getElementById('examCtxMenu');
    if (old) old.remove();

    const info = _exam.tracks?.find(t => parseInt(t.track_id) === tid);
    const group = info?.group || '?';

    const menu = document.createElement('div');
    menu.id = 'examCtxMenu';
    menu.style.cssText = `position:fixed;left:${e.clientX}px;top:${e.clientY}px;background:var(--surface-1);border:1px solid var(--chrome-border);border-radius:var(--r-sm);padding:4px 0;z-index:9999;box-shadow:0 4px 16px rgba(0,0,0,.4);min-width:180px`;
    menu.innerHTML = `
        <div style="padding:4px 12px;font-size:var(--fs-xs);color:var(--text-tertiary);border-bottom:1px solid var(--chrome-border)">Track ${tid} · ${group}</div>
        <div class="ctx-item" style="padding:6px 12px;cursor:pointer;font-size:var(--fs-sm)" onmouseover="this.style.background='var(--surface-2)'" onmouseout="this.style.background=''" onclick="document.getElementById('examCtxMenu').remove();examInsertDetailedAnalysis(${tid})">
            🔬 Insert Static Analysis
        </div>
        <div class="ctx-item" style="padding:6px 12px;cursor:pointer;font-size:var(--fs-sm)" onmouseover="this.style.background='var(--surface-2)'" onmouseout="this.style.background=''" onclick="document.getElementById('examCtxMenu').remove();examOpenDynamicViewer(${tid})">
            🔍 Open Dynamic Viewer
        </div>
        <div style="border-top:1px solid var(--chrome-border)"></div>
        <div class="ctx-item" style="padding:6px 12px;cursor:pointer;font-size:var(--fs-sm)" onmouseover="this.style.background='var(--surface-2)'" onmouseout="this.style.background=''" onclick="document.getElementById('examCtxMenu').remove();examSelectTrack(${tid})">
            📌 Select Track
        </div>
    `;
    document.body.appendChild(menu);

    // Close on click anywhere
    const closer = (ev) => {
        if (!menu.contains(ev.target)) { menu.remove(); document.removeEventListener('click', closer); }
    };
    setTimeout(() => document.addEventListener('click', closer), 10);
}

async function examInsertDetailedAnalysis(tid) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) return;

    const info = _exam.tracks?.find(t => parseInt(t.track_id) === tid);
    const group = info?.group || '?';
    const plotType = `exam_detail_${tid}`;

    // Check if already exists
    if (!sub.insertedResults) sub.insertedResults = [];
    const existing = sub.insertedResults.find(r => r.plotType === plotType);
    if (existing && existing.status === 'done' && existing.url) {
        // Already exists — just show it
        showResultImage(existing.url, `Track ${tid} (${group}) — Detailed Analysis`);
        return;
    }

    updateStatus(`Generating detailed analysis for Track ${tid}...`);

    // Call backend
    const res = await api(`step/${ws.id}/${sub.pipelineId}/examination/plot`, 'POST', {
        plot_type: 'exam_detailed',
        track_id: tid,
    });

    if (res.success) {
        showResultImage(res.data.url, `Track ${tid} (${group}) — Detailed Analysis`);
        updateStatus(`✅ Track ${tid} detailed analysis`);

        // Add or update in tree
        const existIdx = sub.insertedResults.findIndex(r => r.plotType === plotType);
        const entry = {
            plotType: plotType,
            label: `Track ${tid} (${group})`,
            icon: '🔬',
            url: res.data.url,
            status: 'done',
        };
        if (existIdx >= 0) {
            sub.insertedResults[existIdx] = entry;
        } else {
            sub.insertedResults.push(entry);
        }
        renderModuleTree(sub);
    } else {
        updateStatus(`❌ ${res.error}`);
    }
}


const MENUS = {
    file: [
        { label: 'New Project', shortcut: 'Ctrl+Shift+N', action: 'newProject()' },
        { label: 'Open Project', shortcut: 'Ctrl+Shift+O', action: 'openProject()' },
        { sep: true },
        { label: 'Save', shortcut: 'Ctrl+S', action: 'saveProject()' },
        { label: 'Save As...', action: 'saveProjectAs()' },
        { sep: true },
        { label: 'Close Project', action: 'closeProject()' },
        { sep: true },
        { label: 'Clean Unused Data...', action: 'cleanUnusedData()' },
    ],
    view: [
        { label: 'Toggle Toolbox', shortcut: 'Ctrl+Shift+E', action: 'shortcutToggleLeftPanel()' },
        { label: 'Toggle Properties', action: 'toggleRightPanel()' },
        { sep: true },
        { label: 'Toggle Console', shortcut: 'Ctrl+`', action: 'toggleConsole()' },
        { label: 'Toggle CelLAB Git', shortcut: 'Ctrl+Shift+H', action: 'toggleVersionPanel()' },
        { sep: true },
        { label: '☀ Light Theme', action: "setTheme('light')" },
        { label: '🌙 Dark Theme', action: "setTheme('dark')" },
        { sep: true },
        { label: 'Reset Layout', action: 'resetLayout()' },
    ],
    tools: [
        { label: 'Python Console (Shared)', shortcut: 'Ctrl+Shift+T', action: 'openSharedConsole()' },
        { label: 'Python Console (Isolated)', action: 'openIsolatedConsole()' },
        { label: 'Git Terminal', shortcut: 'Ctrl+Shift+G', action: 'openGitConsole()' },
        { sep: true },
        { label: 'CellIntella (Shared)', action: 'togglecinteliaPanel()' },
        { label: 'CellIntella (Fresh)', action: 'opencinteliaFresh()' },
        { sep: true },
        { label: 'Task Manager', action: 'openTaskManager()' },
        { label: 'Package Manager', action: 'openPackageManager()' },
    ],
    extensions: [
        { label: 'No extensions installed', disabled: true },
        { sep: true },
        { label: 'Extension Marketplace...', disabled: true },
    ],
    help: [
        { label: 'Keyboard Shortcuts', shortcut: 'Ctrl+Shift+/', action: 'showShortcutsHelp()' },
        { sep: true },
        { label: 'Documentation', disabled: true },
        { label: 'About CelLAB', action: 'showAbout()' },
        { sep: true },
        { label: '📖 Cite CelLAB', action: 'showCiteDialog()' },
        { label: '☕ Buy Us a Coffee', action: 'showSupportDialog()' },
        { sep: true },
        { label: '🧩 Embed Your Package', action: 'showHelpLink("embed")' },
        { label: '🤝 Collaboration Request', action: 'showHelpLink("collab")' },
        { label: '🐛 Report an Error', action: 'showHelpLink("bug")' },
        { label: '💡 Suggest an Improvement', action: 'showHelpLink("feature")' },
    ],
};

let _activeMenu = null;

function initMenuBar() {
    document.querySelectorAll('.menu-item[data-menu]').forEach(item => {
        const menuId = item.dataset.menu;
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            if (_activeMenu === menuId) { closeMenu(); return; }
            openMenu(menuId, item);
        });
        item.addEventListener('mouseenter', () => {
            if (_activeMenu && _activeMenu !== menuId) openMenu(menuId, item);
        });
    });
}

function openMenu(menuId, anchor) {
    closeMenu();
    const items = MENUS[menuId];
    if (!items) return;

    _activeMenu = menuId;
    anchor.classList.add('active');

    const dropdown = document.createElement('div');
    dropdown.id = 'menuDropdown';
    dropdown.className = 'menu-dropdown';

    dropdown.innerHTML = items.map(item => {
        if (item.sep) return '<div class="menu-sep"></div>';
        const cls = item.disabled ? 'menu-dd-item disabled' : 'menu-dd-item';
        return `<div class="${cls}" ${item.action && !item.disabled ? `onclick="closeMenu();${item.action}"` : ''}>
            <span class="menu-dd-label">${item.label}</span>
            ${item.shortcut ? `<span class="menu-dd-shortcut">${item.shortcut}</span>` : ''}
        </div>`;
    }).join('');

    document.body.appendChild(dropdown);
    const rect = anchor.getBoundingClientRect();
    dropdown.style.left = rect.left + 'px';
    dropdown.style.top = rect.bottom + 'px';

    // Bounds check
    const ddRect = dropdown.getBoundingClientRect();
    if (ddRect.right > window.innerWidth) dropdown.style.left = (window.innerWidth - ddRect.width - 4) + 'px';

    setTimeout(() => document.addEventListener('click', closeMenu, { once: true }), 30);
}

function closeMenu() {
    _activeMenu = null;
    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
    const dd = document.getElementById('menuDropdown');
    if (dd) dd.remove();
}

// Menu action helpers
function saveProjectAs() { updateStatus('Save As: TODO — use File > Save As in future'); }
function closeProject() {
    if (!confirm('Close current project?')) return;
    api('project/close', 'POST', {}).then(() => { location.reload(); });
}

async function cleanUnusedData() {
    if (!state._projectOpen) {
        updateStatus('No project open');
        return;
    }
    if (!confirm('This will permanently delete data files in data/ that are not referenced by any pipeline.\n\nContinue?')) return;

    updateStatus('Scanning for unused data files...');
    const res = await api('data/clean_unused', 'POST', {});
    if (res.success) {
        const d = res.data;
        if (d.n_deleted === 0) {
            updateStatus('No unused data files found');
        } else {
            const names = d.deleted.map(f => `${f.name} (${f.size_mb} MB)`).join('\n');
            updateStatus(`✅ Cleaned ${d.n_deleted} files (${d.total_mb} MB)`);
            alert(`Cleaned ${d.n_deleted} unused data files:\n\n${names}\n\nTotal freed: ${d.total_mb} MB`);
        }
    }
}
function _findOrCreateCodeChat() {
    let ccWs = [...state.workspaces.values()].find(w => w.type === 'codechat');
    if (!ccWs) { createCodeChat(); ccWs = [...state.workspaces.values()].find(w => w.type === 'codechat'); }
    else { switchWorkspace(ccWs.id); }
    return ccWs;
}

function _findOrCreateCodeChat() {
    let ccWs = [...state.workspaces.values()].find(w => w.type === 'codechat');
    if (!ccWs) { createCodeChat(); ccWs = [...state.workspaces.values()].find(w => w.type === 'codechat'); }
    else { switchWorkspace(ccWs.id); }
    return ccWs;
}
function openSharedConsole() { _findOrCreateCodeChat(); _addCodeChatTab('shared'); }
function openIsolatedConsole() { _findOrCreateCodeChat(); _addCodeChatTab('isolated'); }
function openGitConsole() { _findOrCreateCodeChat(); _addCodeChatTab('git'); }
function opencinteliaFresh() { _findOrCreateCodeChat(); _addCodeChatTab('cellintella_fresh'); }
const openCellIntellaFresh = opencinteliaFresh;

function showPipelineContextMenu(e, pipeline) {
    e.preventDefault();
    e.stopPropagation();
    hideContextMenu();

    const contextItem = {
        type: 'pipeline',
        label: pipeline.name,
        data: `Pipeline: ${pipeline.name} (type: ${pipeline.type}), ID: ${pipeline.id}`,
        actionNew: `askAIAboutPipeline('${pipeline.id}','${escapeHtml(pipeline.name)}','${pipeline.type}')`,
    };

    const menu = document.createElement('div');
    menu.className = 'cellab-ctx-menu';
    menu.style.left = e.clientX + 'px';
    menu.style.top = e.clientY + 'px';
    menu.innerHTML = `
        ${buildAISubmenu(contextItem)}
        <div class="ctx-submenu-trigger">
            <div class="ctx-item"><span>📄</span> Generate Report <span style="float:right;opacity:.4">▸</span></div>
            <div class="ctx-submenu">
                <div class="ctx-item" onclick="hideContextMenu();generateReport('${pipeline.id}','md')">
                    <span>📝</span> Markdown (.md)
                </div>
                <div class="ctx-item" onclick="hideContextMenu();generateReport('${pipeline.id}','pdf')">
                    <span>📕</span> PDF (.pdf)
                </div>
                <div class="ctx-item" onclick="hideContextMenu();generateReport('${pipeline.id}','docx')">
                    <span>📘</span> Word (.docx)
                </div>
            </div>
        </div>
        <div class="ctx-separator"></div>
        <div class="ctx-item ctx-danger" onclick="hideContextMenu();deletePipeline('${pipeline.id}',event)">
            <span>🗑</span> Delete Pipeline
        </div>
    `;
    document.body.appendChild(menu);

    // Bound-check
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) menu.style.left = (e.clientX - rect.width) + 'px';
    if (rect.bottom > window.innerHeight) menu.style.top = (e.clientY - rect.height) + 'px';

    setTimeout(() => document.addEventListener('click', hideContextMenu, { once: true }), 10);
}

function askAIAboutPipeline(pipelineId, pipelineName, pipelineType) {
    // Remove existing mini-chat
    const old = document.getElementById('aiMiniChat');
    if (old) old.remove();

    const ws = getActiveWorkspace();
    if (!ws) return;

    const scope = {
        level: 'pipeline',
        wsId: ws.id,
        pipelineId: pipelineId,
        pipelineName: pipelineName,
        pipelineType: pipelineType,
    };

    // Position near the pipeline node
    const node = document.getElementById(`node-${pipelineId}`);
    let left = 200, top = 100;
    if (node) {
        const rect = node.getBoundingClientRect();
        left = Math.min(rect.right + 10, window.innerWidth - 340);
        top = Math.max(rect.top, 40);
    }

    const chat = document.createElement('div');
    chat.id = 'aiMiniChat';
    chat.className = 'ai-mini-chat';
    chat.style.left = left + 'px';
    chat.style.top = top + 'px';
    chat.innerHTML = `
        <div class="ai-mini-header" onmousedown="aiMiniDragStart(event)">
            <span>🤖 ${escapeHtml(pipelineName)}</span>
            <button class="ai-mini-close" onclick="document.getElementById('aiMiniChat').remove()">✕</button>
        </div>
        <div class="ai-mini-body" id="aiMiniBody">
            <div class="ai-mini-msg ai-mini-ai">📌 Context: ${escapeHtml(pipelineName)} (${escapeHtml(pipelineType)})</div>
        </div>
        <div class="ai-mini-input-row">
            <input class="ai-mini-input" id="aiMiniInput" type="text"
                   placeholder="Ask about this pipeline..."
                   onkeydown="if(event.key==='Enter')aiMiniSend()"
                   spellcheck="false" autocomplete="off">
            <button class="ai-mini-send" onclick="aiMiniSend()">➤</button>
        </div>
    `;
    chat.dataset.scope = JSON.stringify(scope);
    document.body.appendChild(chat);
    document.getElementById('aiMiniInput')?.focus();
}

async function aiMiniSend() {
    const input = document.getElementById('aiMiniInput');
    const body = document.getElementById('aiMiniBody');
    const chat = document.getElementById('aiMiniChat');
    if (!input || !body || !chat) return;

    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    // Handle /config command
    if (msg === '/config') {
        try {
            const res = await api('cellintella/config', 'GET');
            if (res.success) {
                const c = res.data;
                body.innerHTML += `<div class="ai-mini-msg ai-mini-ai">⚙ n_ctx=${c.n_ctx}, threads=${c.n_threads}, KV=${c.kv_cache_mb}MB, model=${c.model_mb}MB<br>Use: /config n_ctx 8192</div>`;
            }
        } catch(e) { body.innerHTML += `<div class="ai-mini-msg ai-mini-ai" style="color:#f38ba8">Error: ${e.message}</div>`; }
        body.scrollTop = body.scrollHeight;
        return;
    }
    if (msg.startsWith('/config ')) {
        const parts = msg.replace('/config ', '').trim().split(/\s+/);
        if (parts.length >= 2 && ['n_ctx','n_threads','timeout'].includes(parts[0])) {
            const bdy = {}; bdy[parts[0]] = parseInt(parts[1]);
            body.innerHTML += `<div class="ai-mini-msg ai-mini-ai">⏳ Reloading with ${parts[0]}=${parts[1]}...</div>`;
            body.scrollTop = body.scrollHeight;
            try {
                const res = await api('cellintella/config', 'POST', bdy);
                if (res.success && res.data.reloaded) {
                    body.innerHTML += `<div class="ai-mini-msg ai-mini-ai">✅ Reloaded. n_ctx=${res.data.n_ctx}, KV=${res.data.kv_cache_mb}MB</div>`;
                }
            } catch(e) { body.innerHTML += `<div class="ai-mini-msg ai-mini-ai" style="color:#f38ba8">${e.message}</div>`; }
            body.scrollTop = body.scrollHeight;
            return;
        }
    }
    if (msg === '/help') {
        body.innerHTML += `<div class="ai-mini-msg ai-mini-ai">/config — show settings<br>/config n_ctx 8192 — resize context<br>/help — this message</div>`;
        body.scrollTop = body.scrollHeight;
        return;
    }

    input.disabled = true;

    body.innerHTML += `<div class="ai-mini-msg ai-mini-user">${escapeHtml(msg)}</div>`;
    body.innerHTML += `<div class="ai-mini-msg ai-mini-ai ai-mini-thinking" id="aiMiniThinking">⏳ Thinking...</div>`;
    body.scrollTop = body.scrollHeight;

    try {
        const scope = JSON.parse(chat.dataset.scope || '{}');
        const res = await api('cellintella/query', 'POST', {
            message: msg,
            scope,
            accumulated_context: buildAIContextText('mini-chat'),
        });
        const el = document.getElementById('aiMiniThinking');
        if (el) el.remove();

        if (res.success && res.data.response) {
            body.innerHTML += `<div class="ai-mini-msg ai-mini-ai">${escapeHtml(res.data.response).replace(/\n/g, '<br>')}</div>`;
        } else {
            body.innerHTML += `<div class="ai-mini-msg ai-mini-ai" style="color:#f38ba8">${escapeHtml(res.error || 'No response')}</div>`;
        }
    } catch (e) {
        const el = document.getElementById('aiMiniThinking');
        if (el) el.remove();
        body.innerHTML += `<div class="ai-mini-msg ai-mini-ai" style="color:#f38ba8">Error: ${e.message}</div>`;
    }

    body.scrollTop = body.scrollHeight;
    input.disabled = false;
    input.focus();
}

// Draggable mini-chat
let _aiMiniDrag = null;
function aiMiniDragStart(e) {
    const chat = document.getElementById('aiMiniChat');
    if (!chat) return;
    _aiMiniDrag = { el: chat, startX: e.clientX - chat.offsetLeft, startY: e.clientY - chat.offsetTop };
    document.addEventListener('mousemove', aiMiniDragMove);
    document.addEventListener('mouseup', aiMiniDragEnd);
    e.preventDefault();
}
function aiMiniDragMove(e) {
    if (!_aiMiniDrag) return;
    _aiMiniDrag.el.style.left = (e.clientX - _aiMiniDrag.startX) + 'px';
    _aiMiniDrag.el.style.top = (e.clientY - _aiMiniDrag.startY) + 'px';
}
function aiMiniDragEnd() {
    _aiMiniDrag = null;
    document.removeEventListener('mousemove', aiMiniDragMove);
    document.removeEventListener('mouseup', aiMiniDragEnd);
}
function openPackageManager() { updateStatus('Package Manager: TODO'); }

function setTheme(theme) {
    if (theme === 'light') {
        document.body.classList.add('light-theme');
    } else {
        document.body.classList.remove('light-theme');
    }
    localStorage.setItem('cellab-theme', theme);
    updateStatus(`Theme: ${theme === 'light' ? '☀ Light' : '🌙 Dark'}`);
}

// Restore theme on load
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('cellab-theme');
    if (saved === 'light') document.body.classList.add('light-theme');
});

async function generateReport(pipelineId, format) {
    const ws = getActiveWorkspace();
    if (!ws) return;

    showToast(`📄 Generating ${format.toUpperCase()} report...`);
    updateStatus(`Generating ${format} report for ${pipelineId}...`);

    try {
        const res = await api('report/generate', 'POST', {
            ws_id: ws.id,
            pipeline_id: pipelineId,
            format: format,
        });

        if (res.success) {
            const data = res.data;
            const note = data.note || '';
            const path = data.path || '';
            const dir = data.dir || '';

            updateStatus(`✅ Report saved: ${path}`);

            // Show success dialog with open option
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
            const dialog = document.createElement('div');
            dialog.className = 'modal-dialog';
            dialog.style.width = '420px';
            dialog.innerHTML = `
                <div class="modal-header">📄 Report Generated</div>
                <div class="modal-body" style="padding:16px">
                    <div style="margin-bottom:12px;font-size:var(--fs-sm)">
                        <strong>Format:</strong> ${data.format?.toUpperCase() || format.toUpperCase()}<br>
                        <strong>Path:</strong> <span style="font-family:var(--font-mono);font-size:11px;word-break:break-all">${escapeHtml(path)}</span>
                        ${note ? `<br><br><span style="color:#fab387;font-size:11px">⚠ ${escapeHtml(note)}</span>` : ''}
                    </div>
                    <div style="display:flex;gap:8px;justify-content:flex-end">
                        <button class="btn btn-default" id="reportCloseBtn">Close</button>
                        <button class="btn btn-primary" id="reportOpenBtn">📂 Open Folder</button>
                    </div>
                </div>
            `;
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);
            document.getElementById('reportCloseBtn').onclick = () => overlay.remove();
            document.getElementById('reportOpenBtn').onclick = () => { openReportDir(dir); overlay.remove(); };
        } else {
            showToast(`❌ ${res.error}`);
            updateStatus(`❌ Report failed: ${res.error}`);
        }
    } catch (e) {
        showToast(`❌ ${e.message}`);
        updateStatus(`❌ Report error: ${e.message}`);
    }
}

async function openReportDir(dir) {
    try {
        await api('report/open', 'POST', { dir });
    } catch(e) { /* silent */ }
}
function toggleRightPanel() {
    const rp = document.querySelector('.right-panel');
    if (!rp) return;
    if (rp.style.display === 'none') { rp.style.display = ''; updateStatus('Properties shown'); }
    else { rp.style.display = 'none'; updateStatus('Properties hidden'); }
}
function stopCurrentTask() { updateStatus('Stop: no running tasks'); }
function showAbout() {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    overlay.innerHTML = `
        <div class="modal-dialog" style="width:360px;text-align:center">
            <div class="modal-header">About CelLAB</div>
            <div class="modal-body" style="padding:20px">
                <div style="font-size:24px;margin-bottom:8px">🔬</div>
                <div style="font-size:16px;font-weight:800;margin-bottom:4px">CelLAB</div>
                <div style="font-size:12px;color:var(--text-tertiary);margin-bottom:12px">Cellular Analysis Workbench</div>
                <div style="font-size:var(--fs-sm);margin-bottom:4px">Version 3.1.11</div>
                <div style="font-size:var(--fs-xs);color:var(--text-tertiary)">Han Mechanobiology Lab — Michigan Tech</div>
                <div style="font-size:var(--fs-xs);color:var(--text-tertiary);margin-bottom:16px">Majid R.</div>
                <button class="btn btn-default" onclick="this.closest('.modal-overlay').remove()">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

function showCiteDialog() {
    const citation = `Rostam, M. (2026). CelLAB: A Cellular Analysis Workbench for\nQuantitative Cell Biology. Han Mechanobiology Lab,\nMichigan Technological University.\nhttps://github.com/MAjidROSTAM/CelLAB`;
    const bibtex = `@software{cellab2026,
  author = {Rostam, Majid},
  title = {CelLAB: Cellular Analysis Workbench},
  year = {2026},
  url = {https://github.com/MAjidROSTAM/CelLAB},
  institution = {Han Mechanobiology Lab, Michigan Tech}
}`;
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    overlay.innerHTML = `
        <div class="modal-dialog" style="width:480px">
            <div class="modal-header">📖 Cite CelLAB</div>
            <div class="modal-body" style="padding:20px">
                <div style="font-size:var(--fs-sm);color:var(--text-secondary);margin-bottom:12px">
                    If CelLAB contributes to your research, please cite us. It helps sustain the project.
                </div>
                <div style="font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);margin-bottom:4px;text-transform:uppercase;letter-spacing:1px">Plain Text</div>
                <pre style="background:var(--surface-0);border:1px solid var(--chrome-border-strong);border-radius:var(--r-sm);padding:10px;font-size:var(--fs-xs);font-family:var(--font-mono);white-space:pre-wrap;color:var(--text-primary);margin-bottom:12px;cursor:pointer" onclick="navigator.clipboard.writeText(this.textContent);showToast('📋 Citation copied!')" title="Click to copy">${citation}</pre>
                <div style="font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);margin-bottom:4px;text-transform:uppercase;letter-spacing:1px">BibTeX</div>
                <pre style="background:var(--surface-0);border:1px solid var(--chrome-border-strong);border-radius:var(--r-sm);padding:10px;font-size:var(--fs-xs);font-family:var(--font-mono);white-space:pre-wrap;color:var(--text-primary);margin-bottom:16px;cursor:pointer" onclick="navigator.clipboard.writeText(this.textContent);showToast('📋 BibTeX copied!')" title="Click to copy">${bibtex}</pre>
                <div style="display:flex;gap:8px;justify-content:flex-end">
                    <button class="btn btn-default" onclick="this.closest('.modal-overlay').remove()">Close</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

function showSupportDialog() {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    overlay.innerHTML = `
        <div class="modal-dialog" style="width:400px;text-align:center">
            <div class="modal-header">☕ Support Our Research</div>
            <div class="modal-body" style="padding:24px">
                <div style="font-size:32px;margin-bottom:12px">☕</div>
                <div style="font-size:var(--fs-md);font-weight:700;margin-bottom:8px">Buy Us a Coffee</div>
                <div style="font-size:var(--fs-sm);color:var(--text-secondary);margin-bottom:16px;line-height:1.6">
                    CelLAB is free and open-source, built by researchers for researchers.<br>
                    Your support helps us maintain and improve the platform.
                </div>
                <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:16px">
                    <a href="https://buymeacoffee.com/" target="_blank" style="display:flex;align-items:center;justify-content:center;gap:8px;padding:10px 16px;background:var(--surface-3);border:1px solid var(--chrome-border-strong);border-radius:var(--r-md);color:var(--text-primary);text-decoration:none;font-size:var(--fs-sm);font-weight:600;transition:all .12s" onmouseover="this.style.background='var(--surface-4)'" onmouseout="this.style.background='var(--surface-3)'">
                        ☕ Buy Me a Coffee <span style="font-size:var(--fs-xs);color:var(--text-tertiary)">(coming soon)</span>
                    </a>
                    <a href="https://github.com/MAjidROSTAM/CelLAB" target="_blank" style="display:flex;align-items:center;justify-content:center;gap:8px;padding:10px 16px;background:var(--surface-3);border:1px solid var(--chrome-border-strong);border-radius:var(--r-md);color:var(--text-primary);text-decoration:none;font-size:var(--fs-sm);font-weight:600;transition:all .12s" onmouseover="this.style.background='var(--surface-4)'" onmouseout="this.style.background='var(--surface-3)'">
                        ⭐ Star on GitHub
                    </a>
                </div>
                <div style="font-size:var(--fs-xs);color:var(--text-tertiary)">Han Mechanobiology Lab — Michigan Tech</div>
                <div style="margin-top:12px">
                    <button class="btn btn-default" onclick="this.closest('.modal-overlay').remove()">Close</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

function showHelpLink(type) {
    const items = {
        embed: {
            icon: '🧩', title: 'Embed Your Package',
            desc: 'CelLAB is designed as a modular platform. You can integrate your own analysis pipeline as a CelLAB package — with its own GUI steps, plotters, and documentation.',
            bullets: [
                'Define pipeline steps (Import → Process → Analyze → Export)',
                'Create plotters for your results (batch + single)',
                'Add hierarchical documentation for CellIntella',
                'Publish as a CelLAB extension package',
            ],
            action: 'https://github.com/MAjidROSTAM/CelLAB/issues/new?title=Package+Integration+Request&labels=package',
            actionLabel: '📩 Contact Us About Integration',
        },
        collab: {
            icon: '🤝', title: 'Collaboration Request',
            desc: 'We welcome collaborations with researchers and labs working in cell biology, mechanobiology, image analysis, and related fields.',
            bullets: [
                'Joint development of analysis pipelines',
                'Dataset sharing and validation studies',
                'Method development and publication',
                'Custom CelLAB modules for your workflow',
            ],
            action: 'mailto:mrostam@mtu.edu?subject=CelLAB%20Collaboration%20Request',
            actionLabel: '📧 Send Collaboration Email',
        },
        bug: {
            icon: '🐛', title: 'Report an Error',
            desc: 'Found a bug? Help us improve CelLAB by reporting it. Please include steps to reproduce, error messages, and your system info.',
            bullets: [
                'Describe what you expected vs. what happened',
                'Include the console output (Ctrl+` to open)',
                'Attach screenshots if possible',
                'Mention your OS, Python version, and CelLAB version',
            ],
            action: 'https://github.com/MAjidROSTAM/CelLAB/issues/new?title=Bug+Report&labels=bug',
            actionLabel: '🐛 Open Issue on GitHub',
        },
        feature: {
            icon: '💡', title: 'Suggest an Improvement',
            desc: 'Have an idea to make CelLAB better? We value user feedback — every feature in CelLAB started as a suggestion.',
            bullets: [
                'Describe the problem your idea solves',
                'Explain your ideal workflow',
                'Reference similar features in other tools if helpful',
                'Vote on existing suggestions with 👍',
            ],
            action: 'https://github.com/MAjidROSTAM/CelLAB/issues/new?title=Feature+Request&labels=enhancement',
            actionLabel: '💡 Submit on GitHub',
        },
    };
    const item = items[type];
    if (!item) return;

    const bulletHtml = item.bullets.map(b =>
        `<div style="display:flex;gap:8px;align-items:flex-start;font-size:var(--fs-sm);color:var(--text-secondary);line-height:1.5">
            <span style="color:var(--brand-accent);flex-shrink:0;margin-top:1px">▸</span>${b}
        </div>`
    ).join('');

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    overlay.innerHTML = `
        <div class="modal-dialog" style="width:440px">
            <div class="modal-header">${item.icon} ${item.title}</div>
            <div class="modal-body" style="padding:20px">
                <div style="font-size:var(--fs-sm);color:var(--text-secondary);margin-bottom:14px;line-height:1.6">${item.desc}</div>
                <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:16px;padding:12px;background:var(--surface-0);border:1px solid var(--chrome-border);border-radius:var(--r-md)">
                    ${bulletHtml}
                </div>
                <div style="display:flex;gap:8px;justify-content:flex-end">
                    <button class="btn btn-default" onclick="this.closest('.modal-overlay').remove()">Close</button>
                    <a href="${item.action}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;height:28px;padding:0 12px;background:var(--brand-accent);color:#fff;border-radius:var(--r-sm);font-size:var(--fs-sm);font-weight:600;text-decoration:none;font-family:var(--font-ui)">${item.actionLabel}</a>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

// ═════════════════════════════════════════════
// VERSION CONTROL PANEL
// ═════════════════════════════════════════════

let _vcOpen = false;
let _vcDirty = false;

function toggleVersionPanel() {
    _vcOpen = !_vcOpen;
    let panel = document.getElementById('vcPanel');

    if (!panel) {
        panel = document.createElement('div');
        panel.id = 'vcPanel';
        panel.className = 'vc-panel';
        panel.innerHTML = `
            <div class="vc-header">
                <span class="vc-header-title">⏱ CelLAB Git</span>
                <button class="console-btn" onclick="toggleVersionPanel()" title="Close">✕</button>
            </div>
            <div class="vc-actions">
                <div class="vc-commit-row">
                    <input class="vc-commit-input" id="vcCommitMsg" type="text"
                           placeholder="Commit message..."
                           onkeydown="if(event.key==='Enter')vcDoCommit()"
                           spellcheck="false">
                    <button class="vc-commit-btn" id="vcCommitBtn" onclick="vcDoCommit()">Commit</button>
                </div>
                <div class="vc-btn-row">
                    <button class="vc-action-main" onclick="vcShowStatus()">📊 Status</button>
                    <button class="vc-action-main" onclick="vcRefresh()">🔄 Refresh</button>
                    <button class="vc-action-main" onclick="vcShowTagBox('')">🏷 Tag Latest</button>
                </div>
            </div>
            <div class="vc-info-box" id="vcInfoBox" style="display:none"></div>
            <div class="vc-tag-box" id="vcTagBox" style="display:none">
                <input class="vc-tag-input" id="vcTagInput" type="text" placeholder="Tag name..."
                       onkeydown="if(event.key==='Enter')vcDoTag()" spellcheck="false">
                <button class="vc-tag-btn" onclick="vcDoTag()">Tag</button>
                <button class="vc-tag-cancel" onclick="vcHideTagBox()">✕</button>
            </div>
            <div class="vc-section-label" id="vcTimelineLabel">TIMELINE</div>
            <div class="vc-timeline" id="vcTimeline">
                <div class="vc-loading">Loading history...</div>
            </div>
        `;
        // Insert as sibling of right-panel
        const rightPanel = document.querySelector('.right-panel');
        if (rightPanel) {
            rightPanel.parentNode.insertBefore(panel, rightPanel.nextSibling);
        } else {
            document.body.appendChild(panel);
        }
    }

    panel.classList.toggle('open', _vcOpen);
    if (_vcOpen) vcRefresh();
}

async function vcRefresh() {
    await vcLoadTimeline();
}

async function vcShowStatus() {
    const box = document.getElementById('vcInfoBox');
    if (!box) return;

    box.style.display = 'block';
    box.innerHTML = '<div class="vc-info-loading">Checking status...</div>';

    // Ensure a git session exists
    if (!window._vcGitSession) {
        const r = await api('console/create', 'POST', { type: 'git' });
        if (r.success) window._vcGitSession = r.data.session_id;
    }

    const res = await api('console/exec', 'POST', { code: 'status', session_id: window._vcGitSession });
    if (res.success) {
        const text = res.data.stdout || res.data.stderr || 'No response';
        // Colorize the status output
        let html = escapeHtml(text)
            .replace(/⚠.*$/gm, '<span style="color:#fab387;font-weight:700">$&</span>')
            .replace(/✓.*$/gm, '<span style="color:#a6e3a1;font-weight:700">$&</span>')
            .replace(/(Project|Root|Workspaces|Pipelines|Last commit):?/g, '<span style="font-weight:700;color:var(--text-secondary)">$&</span>');
        box.innerHTML = `<pre class="vc-info-content">${html}</pre>
            <button class="vc-info-close" onclick="document.getElementById('vcInfoBox').style.display='none'">✕</button>`;
    } else {
        box.innerHTML = `<div class="vc-info-content" style="color:var(--status-error)">${res.error}</div>`;
    }
}

async function vcLoadTimeline() {
    const timeline = document.getElementById('vcTimeline');
    if (!timeline) return;

    try {
        const logRes = await api('version/log?max=50', 'GET');

        if (!logRes.success || !logRes.data || logRes.data.length === 0) {
            timeline.innerHTML = '<div class="vc-empty">No commits yet. Make your first commit above.</div>';
            return;
        }

        // Load tags
        let tagMap = {};
        try {
            const tagRes = await api('version/tags', 'GET');
            if (tagRes.success && tagRes.data) {
                for (const t of tagRes.data) {
                    tagMap[t.hash?.substring(0, 8)] = t.name;
                }
            }
        } catch (e) { /* no tags */ }

        timeline.innerHTML = logRes.data.map((entry, idx) => {
            const hash = entry.hash || '';
            const shortHash = hash.substring(0, 8);
            const msg = entry.message || '';
            const ts = entry.timestamp || '';
            const date = ts.substring(0, 10);
            const time = ts.substring(11, 16);
            const tag = tagMap[shortHash];
            const isFirst = idx === 0;

            return `
                <div class="vc-commit ${isFirst ? 'vc-commit-latest' : ''}" data-hash="${hash}">
                    <div class="vc-commit-line">
                        <div class="vc-commit-dot ${isFirst ? 'latest' : ''}"></div>
                        ${idx < logRes.data.length - 1 ? '<div class="vc-commit-connector"></div>' : ''}
                    </div>
                    <div class="vc-commit-body">
                        <div class="vc-commit-msg">${escapeHtml(msg)}</div>
                        <div class="vc-commit-meta">
                            <span class="vc-commit-hash" title="${hash}">${shortHash}</span>
                            <span class="vc-commit-date">${date} ${time}</span>
                            ${tag ? `<span class="vc-tag-badge">${escapeHtml(tag)}</span>` : ''}
                        </div>
                        <div class="vc-commit-actions">
                            <button class="vc-action-btn" onclick="vcShowTagBox('${hash}')" title="Tag this commit">🏷</button>
                            <button class="vc-action-btn" onclick="vcCheckout('${hash}')" title="Revert to this commit">↩</button>
                            ${idx < logRes.data.length - 1 ? `<button class="vc-action-btn" onclick="vcDiff('${hash}','${logRes.data[idx + 1].hash}')" title="Diff with previous">⟷</button>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

    } catch (e) {
        timeline.innerHTML = `<div class="vc-empty">Error loading history: ${e.message}</div>`;
    }
}

async function vcDoCommit() {
    const input = document.getElementById('vcCommitMsg');
    const msg = input?.value?.trim();
    if (!msg) { input?.focus(); return; }

    const btn = document.getElementById('vcCommitBtn');
    btn.textContent = '...';
    btn.disabled = true;

    try {
        const res = await api('version/commit', 'POST', { message: msg, author: 'gui' });
        if (res.success) {
            input.value = '';
            showToast(`✅ Committed: ${res.data.hash?.substring(0, 8)}`, 3000);
            vcSetDirty(false);
            await vcRefresh();
        } else {
            showToast(`❌ ${res.error}`, 3000);
        }
    } catch (e) {
        showToast(`❌ Commit failed: ${e.message}`, 3000);
    } finally {
        btn.textContent = 'Commit';
        btn.disabled = false;
    }
}

let _vcTagTarget = null;

function vcShowTagBox(hash) {
    // If no hash provided, use latest commit
    if (!hash) {
        // Grab from timeline
        const firstCommit = document.querySelector('.vc-commit[data-hash]');
        if (firstCommit) hash = firstCommit.dataset.hash;
        if (!hash) { showToast('No commits to tag', 2000); return; }
    }
    _vcTagTarget = hash;
    const box = document.getElementById('vcTagBox');
    const input = document.getElementById('vcTagInput');
    if (box) box.style.display = 'flex';
    if (input) { input.value = ''; input.focus(); }
}

function vcHideTagBox() {
    const box = document.getElementById('vcTagBox');
    if (box) box.style.display = 'none';
    _vcTagTarget = null;
}

async function vcDoTag() {
    const input = document.getElementById('vcTagInput');
    const tagName = input?.value?.trim();
    if (!tagName || !_vcTagTarget) return;

    try {
        const res = await api('version/tag', 'POST', {
            tag_name: tagName,
            commit_hash: _vcTagTarget
        });
        if (res.success) {
            showToast(`🏷 Tagged: ${tagName}`, 2000);
            vcHideTagBox();
            await vcLoadTimeline();
        } else {
            showToast(`❌ ${res.error}`, 3000);
        }
    } catch (e) {
        showToast(`❌ Tag failed`, 3000);
    }
}

async function vcCheckout(hash) {
    if (!confirm(`Revert all parameters to commit ${hash.substring(0, 8)}?\n\nThis will overwrite current settings.`)) return;

    try {
        const res = await api('version/checkout', 'POST', { commit_hash: hash });
        if (res.success) {
            showToast(`↩ Reverted to ${hash.substring(0, 8)}`, 3000);
            await vcRefresh();
        } else {
            showToast(`❌ ${res.error}`, 3000);
        }
    } catch (e) {
        showToast(`❌ Checkout failed`, 3000);
    }
}

async function vcDiff(hashA, hashB) {
    try {
        const res = await api('version/diff', 'POST', { hash_a: hashA, hash_b: hashB });
        if (res.success) {
            vcShowDiffDialog(hashA, hashB, res.data);
        } else {
            showToast(`❌ ${res.error}`, 3000);
        }
    } catch (e) {
        showToast(`❌ Diff failed`, 3000);
    }
}

function vcShowDiffDialog(hashA, hashB, diff) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

    let diffHtml = '';
    if (diff && typeof diff === 'object') {
        const entries = Object.entries(diff);
        if (entries.length === 0) {
            diffHtml = '<div style="padding:12px;color:var(--text-tertiary)">No differences found</div>';
        } else {
            diffHtml = entries.map(([key, val]) => {
                const content = typeof val === 'object' ? JSON.stringify(val, null, 2) : String(val);
                return `<div class="vc-diff-entry">
                    <div class="vc-diff-path">${escapeHtml(key)}</div>
                    <pre class="vc-diff-content">${escapeHtml(content)}</pre>
                </div>`;
            }).join('');
        }
    } else {
        diffHtml = `<pre class="vc-diff-content">${escapeHtml(JSON.stringify(diff, null, 2))}</pre>`;
    }

    overlay.innerHTML = `
        <div class="modal-dialog" style="width:600px;max-height:70vh">
            <div class="modal-header">⟷ Diff: ${hashA.substring(0, 8)} vs ${hashB.substring(0, 8)}</div>
            <div class="modal-body" style="padding:0;overflow-y:auto;max-height:55vh">
                ${diffHtml}
            </div>
            <div style="padding:10px;text-align:right;border-top:1px solid var(--chrome-border)">
                <button class="btn btn-default" onclick="this.closest('.modal-overlay').remove()">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

function vcSetDirty(dirty) {
    _vcDirty = dirty;
    const dot = document.getElementById('vcDirtyDot');
    if (dot) dot.classList.toggle('visible', dirty);
}

// Periodically check dirty state
async function vcCheckDirty() {
    try {
        const logRes = await api('version/log?max=1', 'GET');
        if (!logRes.success || !logRes.data || logRes.data.length === 0) {
            vcSetDirty(false);
            return;
        }
        // Simple heuristic: we don't have full dirty detection here
        // The git terminal status command does it properly
    } catch (e) { /* silent */ }
}

// ═════════════════════════════════════════════
// PYTHON CONSOLE (REPL)
// ═════════════════════════════════════════════

let _consoleOpen = false;
let _consoleTabs = [];  // [{id, sessionId, type, name, lines: [], history: [], histIdx: -1}]
let _consoleActiveTab = null;
let _consoleTabCounter = 0;
let _cellIntellaModelLoaded = false;

// AI Context Accumulation
// Each CellIntella chat (mini-chat or console tab) can accumulate context items
// Items are sent with every query from that chat
let _aiContextStore = new Map();  // chatId → [{type, label, data}]

function getAIContextForChat(chatId) {
    return _aiContextStore.get(chatId) || [];
}

function addAIContext(chatId, item) {
    if (!_aiContextStore.has(chatId)) _aiContextStore.set(chatId, []);
    const items = _aiContextStore.get(chatId);
    // Avoid duplicates
    if (!items.find(i => i.label === item.label)) {
        items.push(item);
    }
    return items.length;
}

function getOpenAIChats() {
    // Collect all open CellIntella chats (console tabs + mini-chat)
    const chats = [];
    // Console tabs
    for (const tab of _consoleTabs) {
        if (tab.type === 'cellintella' || tab.type === 'cellintella_fresh') {
            chats.push({ id: tab.id, label: tab.name, type: 'console' });
        }
    }
    // Mini-chat
    const mini = document.getElementById('aiMiniChat');
    if (mini) {
        const header = mini.querySelector('.ai-mini-header span');
        chats.push({ id: 'mini-chat', label: header?.textContent || '🤖 Mini Chat', type: 'mini' });
    }
    return chats;
}

function buildAIContextText(chatId) {
    const items = getAIContextForChat(chatId);
    if (items.length === 0) return '';
    let text = '[Accumulated Context]\n';
    for (const item of items) {
        text += `• ${item.label}: ${item.data}\n`;
    }
    return text;
}

let _pendingAIContextItems = [];  // temp storage for menu items

function buildAISubmenu(contextItem) {
    // Store item and reference by index to avoid JSON-in-HTML escaping issues
    const idx = _pendingAIContextItems.length;
    _pendingAIContextItems.push(contextItem);

    const openChats = getOpenAIChats();

    let addToItems = '';
    if (openChats.length > 0) {
        addToItems = openChats.map(c =>
            `<div class="ctx-item" onclick="aiAddContextFromMenu(${idx},'${c.id}')">
                <span style="opacity:.6">→</span> ${escapeHtml(c.label)}
            </div>`
        ).join('');
    }
    addToItems += `<div class="ctx-item" onclick="aiAddContextNewFromMenu(${idx})">
        <span style="opacity:.6">＋</span> New CellIntella tab
    </div>`;

    return `
        <div class="ctx-submenu-trigger">
            <div class="ctx-item"><span>🤖</span> AI <span style="float:right;opacity:.4">▸</span></div>
            <div class="ctx-submenu">
                <div class="ctx-item" onclick="hideContextMenu();${contextItem.actionNew || ''}">
                    <span>💬</span> New Chat
                </div>
                <div class="ctx-separator"></div>
                <div class="ctx-item" style="opacity:.5;font-size:10px;cursor:default;pointer-events:none">📌 ADD TO CONTEXT</div>
                ${addToItems}
            </div>
        </div>
    `;
}

// These grab the item BEFORE hideContextMenu clears the array
function aiAddContextFromMenu(idx, chatId) {
    const item = _pendingAIContextItems[idx];
    hideContextMenu();
    if (item) aiAddContextToChat(chatId, item);
}

function aiAddContextNewFromMenu(idx) {
    const item = _pendingAIContextItems[idx];
    hideContextMenu();
    if (item) aiAddContextNewTab(item);
}

function aiAddContextToChat(chatId, item) {
    const count = addAIContext(chatId, item);
    showToast(`📌 Added "${item.label}" to context (${count} items)`);

    // If it's a console tab, add a visual indicator
    const tab = _consoleTabs.find(t => t.id === chatId);
    if (tab) {
        tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 Context added: ${escapeHtml(item.label)}</span>` });
        renderConsoleBody();
    }

    // If it's the mini-chat, add indicator
    if (chatId === 'mini-chat') {
        const body = document.getElementById('aiMiniBody');
        if (body) {
            body.innerHTML += `<div class="ai-mini-msg ai-mini-ai">📌 Context added: ${escapeHtml(item.label)}</div>`;
            body.scrollTop = body.scrollHeight;
        }
    }
}

function aiAddContextNewTab(item) {
    if (!_consoleOpen) toggleConsole();
    addConsoleTab('cellintella').then(() => {
        // Find the just-created tab
        const tab = _consoleTabs[_consoleTabs.length - 1];
        if (tab && (tab.type === 'cellintella' || tab.type === 'cellintella_fresh')) {
            addAIContext(tab.id, item);
            tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 Context added: ${escapeHtml(item.label)}</span>` });
            renderConsoleBody();
        }
    });
}

const CONSOLE_TYPES = {
    shared:       { label: '🐍 Python',     color: '#89b4fa', prompt: '>>> ', welcome: 'Python (shared namespace) — has access to project, results, all imports' },
    isolated:     { label: '🐍 Python',     color: '#a6e3a1', prompt: '>>> ', welcome: 'Python (isolated) — fresh namespace, import what you need' },
    git:          { label: '📦 CelLAB Git', color: '#fab387', prompt: '$ ',  welcome: 'CelLAB Git — type "help" for available commands' },
    cellintella:      { label: '🤖 CellIntella',    color: '#cba6f7', prompt: '🤖 ', welcome: 'CellIntella (shared memory) — Cell Intelligent Autonomous Interface — conversation history preserved across messages' },
    cellintella_fresh:{ label: '🤖 CellIntella',    color: '#b4befe', prompt: '🤖 ', welcome: 'CellIntella (fresh) — Cell Intelligent Autonomous Interface — no history, fast one-off questions' },
};

function toggleConsole() {
    let panel = document.getElementById('consolePanel');

    if (!panel) {
        panel = document.createElement('div');
        panel.id = 'consolePanel';
        panel.className = 'console-panel';
        panel.innerHTML = `
            <div class="console-resize" onmousedown="initConsoleResize(event)"></div>
            <div class="console-header">
                <div class="console-tabs-row" id="consoleTabsRow"></div>
                <div class="console-header-actions">
                    <span style="font-size:10px;color:rgba(205,214,244,.2);margin-right:4px">Ctrl+\`</span>
                    <button class="console-btn" onclick="consoleCopyAll()" title="Copy all">📋</button>
                    <button class="console-btn" onclick="consoleClear()" title="Clear">🗑</button>
                    <button class="console-btn" onclick="consoleReset()" title="Reset">⟳</button>
                    <button class="console-btn" onclick="consoleShowNS()" title="Variables">≡</button>
                    <span style="width:1px;height:16px;background:rgba(255,255,255,.1);margin:0 4px"></span>
                    <button class="console-btn console-win-btn" onclick="consoleMinimize()" title="Minimize">─</button>
                    <button class="console-btn console-win-btn" id="consoleMaxBtn" onclick="consoleMaximize()" title="Maximize">□</button>
                    <button class="console-btn console-win-btn console-close-btn" onclick="toggleConsole()" title="Close">✕</button>
                </div>
            </div>
            <div class="console-body" id="consoleBody" onclick="document.getElementById('consoleInput')?.focus()"></div>
        `;
        const statusBar = document.querySelector('.status-bar');
        if (statusBar) statusBar.parentNode.insertBefore(panel, statusBar);
        else document.body.appendChild(panel);

        // Create first tab
        addConsoleTab('shared');
    }

    _consoleOpen = !_consoleOpen;
    panel.classList.toggle('open', _consoleOpen);
    if (_consoleOpen) document.getElementById('consoleInput')?.focus();
}

async function addConsoleTab(type, scope = null) {
    let sessionId = null;

    // CellIntella tabs don't need a console session
    if (type === 'cellintella' || type === 'cellintella_fresh') {
        sessionId = `cellintella_${Date.now()}`;
    } else {
        const res = await api('console/create', 'POST', { type });
        if (!res.success) return;
        sessionId = res.data.session_id;
    }

    _consoleTabCounter++;
    const info = CONSOLE_TYPES[type];

    // Build scope-aware name and welcome
    let tabName = `${info.label} ${_consoleTabCounter}`;
    let scopeWelcome = '';
    if (scope && scope.level !== 'none') {
        if (scope.level === 'pipeline' && scope.pipelineName) {
            tabName = `🤖 ${scope.pipelineName}`;
            scopeWelcome = `📌 Context: pipeline "${scope.pipelineName}" (${scope.pipelineType || '?'})`;
        } else if (scope.level === 'workspace') {
            tabName = `🤖 Workspace`;
            scopeWelcome = `📌 Context: workspace "${scope.wsId}"`;
        } else if (scope.level === 'project') {
            tabName = `🤖 Project`;
            scopeWelcome = `📌 Context: entire project`;
        }
    }

    const tab = {
        id: `ctab_${_consoleTabCounter}`,
        sessionId: sessionId,
        type: type,
        name: tabName,
        scope: scope || { level: 'none' },
        lines: [
            { html: `<span class="console-welcome">CelLAB Console — ${info.welcome}</span>` },
            ...(scopeWelcome ? [{ html: `<span class="console-welcome" style="color:#cba6f7">${scopeWelcome}</span>` }] : []),
            ...(type === 'cellintella' || type === 'cellintella_fresh' ? [
                { html: `<span class="console-welcome">⏳ First message takes ~2-3 min to load the model. After that, responses are fast.</span>` },
                { html: `<span class="console-welcome">Powered by Llama 3.2 3B (local, private — no data leaves your machine)</span>` },
            ] : []),
        ],
        history: [],
        histIdx: -1,
    };
    _consoleTabs.push(tab);
    switchConsoleTab(tab.id);
    return tab;
}

function switchConsoleTab(tabId) {
    _consoleActiveTab = tabId;
    renderConsoleTabs();
    renderConsoleBody();
}

function closeConsoleTab(tabId, ev) {
    if (ev) ev.stopPropagation();
    _consoleTabs = _consoleTabs.filter(t => t.id !== tabId);
    if (_consoleActiveTab === tabId) {
        _consoleActiveTab = _consoleTabs.length > 0 ? _consoleTabs[_consoleTabs.length - 1].id : null;
    }
    if (_consoleTabs.length === 0) {
        toggleConsole();
        return;
    }
    renderConsoleTabs();
    renderConsoleBody();
}

function renderConsoleTabs() {
    // If in Code & Chat mode, render there instead
    if ((_getActiveCodeChatWs() !== null)) {
        _renderCodeChatTabs();
        return;
    }
    const row = document.getElementById('consoleTabsRow');
    if (!row) return;

    row.innerHTML = _consoleTabs.map(t => {
        const info = CONSOLE_TYPES[t.type];
        const active = t.id === _consoleActiveTab;
        return `<div class="console-tab ${active ? 'active' : ''}" onclick="switchConsoleTab('${t.id}')" style="background:${active ? info.color : info.color + '33'};color:${active ? '#fff' : 'rgba(255,255,255,.6)'}">
            <span class="console-tab-label">${t.name}</span>
            ${_consoleTabs.length > 1 ? `<span class="console-tab-close" onclick="closeConsoleTab('${t.id}',event)">✕</span>` : ''}
        </div>`;
    }).join('') + `
        <div class="console-add-btn" onclick="showAddTerminalMenu(event)" title="New Terminal">+</div>
    `;
}

function showAddTerminalMenu(e) {
    e.stopPropagation();
    hideContextMenu();
    const menu = document.createElement('div');
    menu.id = 'cellabContextMenu';
    menu.className = 'cellab-ctx-menu';
    menu.innerHTML = `
        <div class="ctx-item" onclick="hideContextMenu();addConsoleTab('shared')"><span style="color:#89b4fa">●</span> Python (Shared)</div>
        <div class="ctx-item" onclick="hideContextMenu();addConsoleTab('isolated')"><span style="color:#a6e3a1">●</span> Python (Isolated)</div>
        <div class="ctx-item" onclick="hideContextMenu();addConsoleTab('git')"><span style="color:#fab387">●</span> CelLAB Git</div>
        <div class="ctx-separator"></div>
        <div class="ctx-item" onclick="hideContextMenu();addConsoleTab('cellintella')"><span style="color:#cba6f7">●</span> CellIntella (Shared)</div>
        <div class="ctx-item" onclick="hideContextMenu();addConsoleTab('cellintella_fresh')"><span style="color:#b4befe">●</span> CellIntella (Fresh)</div>
    `;
    document.body.appendChild(menu);
    const rect = e.target.getBoundingClientRect();
    menu.style.left = rect.left + 'px';
    menu.style.top = (rect.top - menu.offsetHeight - 4) + 'px';
    setTimeout(() => document.addEventListener('click', hideContextMenu, { once: true }), 50);
}

function getActiveConsoleTab() {
    return _consoleTabs.find(t => t.id === _consoleActiveTab);
}

function renderConsoleBody() {
    // If in Code & Chat mode, render there instead
    if ((_getActiveCodeChatWs() !== null)) {
        _renderCodeChatBody();
        return;
    }
    const body = document.getElementById('consoleBody');
    if (!body) return;
    const tab = getActiveConsoleTab();
    if (!tab) { body.innerHTML = ''; return; }

    const info = CONSOLE_TYPES[tab.type];
    body.innerHTML = tab.lines.map(l => `<div class="console-line">${l.html}</div>`).join('')
        + `<div class="console-input-line" id="consoleInputLine">
            <span class="console-prompt" style="color:${info.color}">${info.prompt}</span>
            <input class="console-input" id="consoleInput" type="text"
                   onkeydown="consoleKeyDown(event)" spellcheck="false" autocomplete="off">
        </div>`;
    scrollConsoleToBottom();
    document.getElementById('consoleInput')?.focus();
}

function consoleKeyDown(e) {
    const tab = getActiveConsoleTab();
    if (!tab) return;

    if (e.key === 'Enter') {
        const input = document.getElementById('consoleInput');
        const code = input.value.trim();
        if (!code) return;

        tab.history.push(code);
        tab.histIdx = tab.history.length;

        const info = CONSOLE_TYPES[tab.type];
        tab.lines.push({ html: `<span class="console-prompt-echo" style="color:${info.color}">${info.prompt}</span><span class="console-code">${escapeHtml(code)}</span>` });

        input.value = '';
        renderConsoleBody();
        consoleExec(code);
    }

    if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (tab.histIdx > 0) {
            tab.histIdx--;
            document.getElementById('consoleInput').value = tab.history[tab.histIdx] || '';
        }
    }
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (tab.histIdx < tab.history.length - 1) {
            tab.histIdx++;
            document.getElementById('consoleInput').value = tab.history[tab.histIdx] || '';
        } else {
            tab.histIdx = tab.history.length;
            document.getElementById('consoleInput').value = '';
        }
    }
    if (e.key === 'l' && e.ctrlKey) { e.preventDefault(); consoleClear(); }
}

async function consoleExec(code) {
    const tab = getActiveConsoleTab();
    if (!tab) return;

    // Route CellIntella tabs to AI endpoint
    if (tab.type === 'cellintella' || tab.type === 'cellintella_fresh') {
        await cellIntellaConsoleExec(tab, code);
        return;
    }

    try {
        const res = await api('console/exec', 'POST', { code, session_id: tab.sessionId });

        if (!res.success) {
            tab.lines.push({ html: `<span class="console-err">${escapeHtml(res.error || 'Failed')}</span>` });
            renderConsoleBody(); return;
        }

        const { stdout, stderr, result, magic } = res.data;
        if (magic === 'clear') { consoleClear(); return; }

        if (stdout) tab.lines.push({ html: `<span class="console-out">${escapeHtml(stdout)}</span>` });
        if (result) tab.lines.push({ html: `<span class="console-result">${escapeHtml(result)}</span>` });
        if (stderr) tab.lines.push({ html: `<span class="console-err">${escapeHtml(stderr)}</span>` });
        renderConsoleBody();
    } catch (e) {
        tab.lines.push({ html: `<span class="console-err">Network error: ${e.message}</span>` });
        renderConsoleBody();
    }
}

async function cellIntellaConsoleExec(tab, message) {
    // Magic commands
    if (message === 'clear' || message === 'cls' || message === 'clc') {
        consoleClear(); return;
    }

    // /config command
    if (message.startsWith('/config')) {
        const arg = message.replace('/config', '').trim();
        if (!arg) {
            // Show current config
            try {
                const res = await api('cellintella/config', 'GET');
                if (res.success) {
                    const c = res.data;
                    tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">⚙ CellIntella Config:\n  n_ctx = ${c.n_ctx} tokens (context window)\n  n_threads = ${c.n_threads}\n  KV cache = ${c.kv_cache_mb} MB\n  Model = ${c.model_mb} MB\n  Total RAM ≈ ${c.model_mb + c.kv_cache_mb} MB\n  Loaded: ${c.loaded ? 'yes' : 'no'}\n\nUsage: /config n_ctx 8192</span>` });
                }
            } catch(e) { tab.lines.push({ html: `<span class="console-err">Error: ${e.message}</span>` }); }
        } else {
            // Parse: /config n_ctx 8192
            const parts = arg.split(/\s+/);
            if (parts.length >= 2) {
                const key = parts[0];
                const val = parseInt(parts[1]);
                if (!['n_ctx', 'n_threads', 'timeout'].includes(key) || isNaN(val)) {
                    tab.lines.push({ html: `<span class="console-err">Unknown config: ${key}. Options: n_ctx, n_threads, timeout</span>` });
                } else {
                    tab.lines.push({ html: `<span class="console-out" style="color:#fab387">⏳ Reloading model with ${key}=${val}... (~2 min)</span>` });
                    renderConsoleBody();
                    try {
                        const body = {}; body[key] = val;
                        const res = await api('cellintella/config', 'POST', body);
                        if (res.success && res.data.reloaded) {
                            tab.lines.push({ html: `<span class="console-result" style="color:#a6e3a1">✅ Model reloaded. n_ctx=${res.data.n_ctx}, KV cache=${res.data.kv_cache_mb}MB</span>` });
                        } else {
                            tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">No changes needed.</span>` });
                        }
                    } catch(e) { tab.lines.push({ html: `<span class="console-err">Reload failed: ${e.message}</span>` }); }
                }
            } else {
                tab.lines.push({ html: `<span class="console-err">Usage: /config n_ctx 8192</span>` });
            }
        }
        renderConsoleBody();
        return;
    }

    // /help command
    if (message === '/help') {
        tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">CellIntella Commands:\n  /config          — show model settings\n  /config n_ctx N  — change context window (reloads model)\n  /scope           — show current scope\n  /scope project   — attach entire project context\n  /scope workspace — attach current workspace\n  /scope none      — clear scope\n  /context         — show accumulated context items\n  /context clear   — remove all context items\n  clear            — clear console</span>` });
        renderConsoleBody();
        return;
    }

    // /context command
    if (message.startsWith('/context')) {
        const arg = message.replace('/context', '').trim();
        if (arg === 'clear') {
            _aiContextStore.delete(tab.id);
            tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 Context cleared</span>` });
        } else {
            const items = getAIContextForChat(tab.id);
            if (items.length === 0) {
                tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 No context items. Right-click objects → AI → Add to Context</span>` });
            } else {
                const list = items.map((item, i) => `  ${i+1}. [${item.type}] ${item.label}`).join('\n');
                tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 Context (${items.length} items):\n${escapeHtml(list)}</span>` });
            }
        }
        renderConsoleBody();
        return;
    }

    // /scope command
    if (message.startsWith('/scope')) {
        const arg = message.replace('/scope', '').trim();
        const ws = getActiveWorkspace();
        if (!arg || arg === 'none') {
            tab.scope = { level: 'none' };
            tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 Scope cleared — no context attached</span>` });
        } else if (arg === 'project') {
            tab.scope = { level: 'project' };
            tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 Scope: entire project</span>` });
        } else if (arg === 'workspace') {
            tab.scope = { level: 'workspace', wsId: ws?.id || '' };
            tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 Scope: workspace "${ws?.name || ws?.id}"</span>` });
        } else if (arg === 'help') {
            tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">/scope none — clear context\n/scope project — entire project\n/scope workspace — active workspace\n/scope &lt;pipeline-id&gt; — specific pipeline</span>` });
        } else {
            // Try to find pipeline by id or name
            if (ws) {
                const sub = [...ws.subtabs.values()].find(s => s.pipelineId === arg || (s.label && s.label.toLowerCase().includes(arg.toLowerCase())));
                if (sub) {
                    tab.scope = { level: 'pipeline', wsId: ws.id, pipelineId: sub.pipelineId, pipelineName: sub.label || sub.pipelineId, pipelineType: '' };
                    tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">📌 Scope: pipeline "${sub.label || sub.pipelineId}"</span>` });
                } else {
                    tab.lines.push({ html: `<span class="console-err">Pipeline "${arg}" not found. Try /scope help</span>` });
                }
            }
        }
        renderConsoleBody();
        return;
    }

    // Show thinking indicator
    const info = CONSOLE_TYPES[tab.type];
    tab.lines.push({ html: `<span class="console-out" style="color:rgba(203,166,247,.4);font-style:italic">${_cellIntellaModelLoaded ? '⏳ Thinking...' : '⏳ Loading model & thinking... (~2-3 min first time)'}</span>` });
    renderConsoleBody();

    try {
        const res = await api('cellintella/query', 'POST', {
            message: message,
            session_id: tab.sessionId,
            fresh: tab.type === 'cellintella_fresh',
            scope: tab.scope || { level: 'none' },
            accumulated_context: buildAIContextText(tab.id),
        });

        // Remove thinking indicator (last line)
        tab.lines.pop();

        if (res.success && res.data.response) {
            const text = res.data.response;
            tab.lines.push({ html: `<span class="console-result" style="color:#cba6f7">${escapeHtml(text)}</span>` });
            _cellIntellaModelLoaded = true;
        } else {
            tab.lines.push({ html: `<span class="console-err">${escapeHtml(res.error || 'No response')}</span>` });
        }
    } catch (e) {
        tab.lines.pop(); // remove thinking
        tab.lines.push({ html: `<span class="console-err">Connection error: ${e.message}</span>` });
    }

    renderConsoleBody();
}

function consoleAppend(html) {
    const tab = getActiveConsoleTab();
    if (!tab) return;
    tab.lines.push({ html });
    renderConsoleBody();
}

function scrollConsoleToBottom() {
    const body = document.getElementById('consoleBody');
    if (body) requestAnimationFrame(() => body.scrollTop = body.scrollHeight);
}

function consoleClear() {
    const tab = getActiveConsoleTab();
    if (!tab) return;
    tab.lines = [{ html: '<span class="console-welcome">Console cleared</span>' }];
    renderConsoleBody();
}

async function consoleCopyAll() {
    const tab = getActiveConsoleTab();
    if (!tab) return;
    const text = tab.lines.map(l => {
        const d = document.createElement('div'); d.innerHTML = l.html; return d.textContent;
    }).join('\n');
    try {
        await navigator.clipboard.writeText(text);
        showToast('📋 Copied to clipboard', 2000);
    } catch {
        showToast('Copy failed', 2000);
    }
}

async function consoleReset() {
    const tab = getActiveConsoleTab();
    if (!tab) return;
    await api('console/reset', 'POST', { session_id: tab.sessionId });
    consoleClear();
    consoleAppend('<span class="console-welcome">Namespace reset</span>');
}

async function consoleShowNS() {
    const tab = getActiveConsoleTab();
    if (!tab) return;
    if (tab.type === 'git') {
        consoleAppend('<span class="console-result">Type "help" for available commands</span>');
        return;
    }
    const res = await api(`console/namespace?session_id=${tab.sessionId}`, 'GET');
    if (res.success) {
        const names = Object.entries(res.data).map(([k, t]) => `  ${k}: ${t}`).join('\n');
        consoleAppend(`<span class="console-result">Namespace:\n${escapeHtml(names)}</span>`);
    }
}

let _consolePreMaxH = null;
let _consoleMinimized = false;

function consoleMinimize() {
    const panel = document.getElementById('consolePanel');
    if (!panel) return;
    const body = document.getElementById('consoleBody');
    const resize = panel.querySelector('.console-resize');

    if (_consoleMinimized) {
        body.style.display = '';
        resize.style.display = '';
        panel.style.height = _consolePreMaxH || '30vh';
        panel.style.minHeight = '150px';
        _consoleMinimized = false;
    } else {
        _consolePreMaxH = panel.style.height || '30vh';
        body.style.display = 'none';
        resize.style.display = 'none';
        panel.style.height = 'auto';
        panel.style.minHeight = '0';
        _consoleMinimized = true;
    }
}

function consoleMaximize() {
    const panel = document.getElementById('consolePanel');
    if (!panel) return;
    const btn = document.getElementById('consoleMaxBtn');
    const body = document.getElementById('consoleBody');
    const resize = panel.querySelector('.console-resize');

    if (panel.classList.contains('maximized')) {
        panel.classList.remove('maximized');
        panel.style.height = _consolePreMaxH || '30vh';
        panel.style.maxHeight = '50vh';
        if (btn) btn.textContent = '□';
        body.style.display = '';
        resize.style.display = '';
        _consoleMinimized = false;
    } else {
        _consolePreMaxH = panel.style.height || '30vh';
        panel.classList.add('maximized');
        panel.style.height = '70vh';
        panel.style.maxHeight = '80vh';
        if (btn) btn.textContent = '❐';
        body.style.display = '';
        resize.style.display = '';
        _consoleMinimized = false;
    }
    scrollConsoleToBottom();
}


function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

function initConsoleResize(e) {
    e.preventDefault();
    const panel = document.getElementById('consolePanel');
    if (!panel) return;
    const startY = e.clientY;
    const startH = panel.offsetHeight;
    const handle = e.target;
    handle.classList.add('active');

    const onMove = (ev) => {
        const delta = startY - ev.clientY;
        const newH = Math.max(120, Math.min(500, startH + delta));
        panel.style.height = newH + 'px';
    };
    const onUp = () => {
        handle.classList.remove('active');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
}
function newProject() { showStartupDialog(); }
function openProject() { showOpenProjectForm(); }
let _canvasZoom = 1;

function zoomIn() {
    _canvasZoom = Math.min(3, _canvasZoom + 0.15);
    applyCanvasZoom();
    updateStatus(`Zoom: ${Math.round(_canvasZoom * 100)}%`);
}

function zoomOut() {
    _canvasZoom = Math.max(0.3, _canvasZoom - 0.15);
    applyCanvasZoom();
    updateStatus(`Zoom: ${Math.round(_canvasZoom * 100)}%`);
}

function fitToWindow() {
    _canvasZoom = 1;
    applyCanvasZoom();
    // Center the canvas
    const cv = document.querySelector('.canvas-view');
    if (cv) cv.scrollTo(0, 0);
    updateStatus('Fit to window');
}

function applyCanvasZoom() {
    const cv = document.querySelector('.canvas-view');
    if (!cv) return;
    cv.style.transform = `scale(${_canvasZoom})`;
    cv.style.transformOrigin = 'top left';
}

// Mouse wheel zoom on canvas
document.addEventListener('wheel', (e) => {
    if (!e.ctrlKey) return;
    const cv = document.querySelector('.canvas-view');
    if (!cv || !cv.contains(e.target)) return;
    e.preventDefault();
    if (e.deltaY < 0) { _canvasZoom = Math.min(3, _canvasZoom + 0.1); }
    else { _canvasZoom = Math.max(0.3, _canvasZoom - 0.1); }
    applyCanvasZoom();
    updateStatus(`Zoom: ${Math.round(_canvasZoom * 100)}%`);
}, { passive: false });

function resetLayout() {
    // Restore all panels
    const lp = document.querySelector('.left-panel');
    const rp = document.querySelector('.right-panel');
    const lr = document.getElementById('leftResizer');
    const rr = document.getElementById('rightResizer');
    if (lp) lp.style.display = '';
    if (rp) rp.style.display = '';
    if (lr) lr.style.display = '';
    if (rr) rr.style.display = '';

    // Reset zoom
    _canvasZoom = 1;
    applyCanvasZoom();

    // Close task manager
    _taskManagerActive = false;
    const tmBtn = document.getElementById('tmToolbarBtn');
    if (tmBtn) tmBtn.classList.remove('active');

    // Reset console height
    const cp = document.getElementById('consolePanel');
    if (cp) cp.style.height = '30vh';

    // Close VC panel
    const vp = document.getElementById('vcPanel');
    if (vp) { vp.classList.remove('open'); _vcOpen = false; }

    renderViewport();
    renderLeftPanel();
    updateStatus('Layout reset');
}

// ═════════════════════════════════════════════
// IMMUNIA — SEGMENTATION PREVIEW
// ═════════════════════════════════════════════

function immuniaAssocMethodChanged(method) {
    // No need to hide/show fields — all params stay visible since they're saved
    // regardless and the backend only uses the relevant ones for the selected method
}

function immuniaSegMethodChanged(roleKey, method) {
    const manualFields = document.getElementById(`segManualFields_${roleKey}`);
    const minMaxFields = document.getElementById(`segMinMaxFields_${roleKey}`);
    const factorRow = document.getElementById(`tf_${roleKey}`)?.closest('.form-row');
    if (manualFields) manualFields.style.display = method === 'manual' ? '' : 'none';
    if (minMaxFields) minMaxFields.style.display = method === 'min_max' ? '' : 'none';
    if (factorRow) factorRow.style.display = method === 'manual' ? 'none' : '';
}

async function doImmuniaSegPreview(roleKey) {
    const ws = getActiveWorkspace();
    const sub = ws?.subtabs.get(ws?.activeSubtab);
    if (!sub) { console.error('[SegPreview] No active subtab'); return; }

    const statusEl = document.getElementById(`segPreviewStatus_${roleKey}`);
    const frameEl = document.getElementById(`segPreviewFrame_${roleKey}`);
    const frame = parseInt(frameEl?.value || '0');

    console.log(`[SegPreview] role=${roleKey} frame=${frame} ws=${ws.id} pipeline=${sub.pipelineId}`);
    if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-running)">⏳ Segmenting frame ${frame}...</span>`;

    // Save current params to backend first
    try {
        const form = document.querySelector(`.settings-form[data-section="seg-${roleKey}"]`);
        if (form) {
            console.log('[SegPreview] Saving params...');
            await saveParamsNow(form);
        } else {
            console.warn('[SegPreview] Form not found for section seg-' + roleKey);
        }
    } catch (e) {
        console.warn('[SegPreview] saveParamsNow failed:', e);
    }

    try {
        const url = `/api/immunia/${ws.id}/${sub.pipelineId}/seg_preview`;
        console.log('[SegPreview] Fetching:', url);
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: roleKey, frame: frame })
        });
        const data = await res.json();
        console.log('[SegPreview] Response:', data.success, data.error || '');
        if (data.success) {
            const gfx = document.getElementById(`graphicsBody-${sub.id}`);
            if (gfx) {
                gfx.innerHTML = `
                    <div style="display:flex;flex-direction:column;height:100%">
                        <div style="padding:6px 10px;background:linear-gradient(180deg,var(--surface-3),var(--surface-2));border-bottom:1px solid rgba(0,0,0,.3);flex-shrink:0">
                            <span style="font-size:var(--fs-xs);font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:.5px">${roleKey} Segmentation Preview — Frame ${frame}</span>
                        </div>
                        <div style="flex:1;display:flex;align-items:center;justify-content:center;background:#000;overflow:hidden">
                            <img src="${data.image}" style="max-width:100%;max-height:100%;object-fit:contain">
                        </div>
                        <div style="padding:4px 10px;font-size:var(--fs-xs);color:var(--text-tertiary);background:var(--surface-2)">
                            ${data.info || ''}
                        </div>
                    </div>`;
            }
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-ok)">✓ ${data.info || 'Preview complete'}</span>`;
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${data.error}</span>`;
        }
    } catch (e) {
        console.error('[SegPreview] Error:', e);
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--status-error)">✗ ${e.message}</span>`;
    }
}

// ═════════════════════════════════════════════
// ARISTOLIA — Interactive Learning Platform
// ═════════════════════════════════════════════

function openAristolia() {
    updateStatus('Aristolia — coming soon. "We learn by doing" — Aristotle');
}

function togglecinteliaPanel() {
    let ccWs = null;
    for (const [wsId, ws] of state.workspaces) {
        if (ws.type === 'codechat') { ccWs = ws; break; }
    }
    if (!ccWs) {
        createCodeChat();
        ccWs = [...state.workspaces.values()].find(w => w.type === 'codechat');
    } else {
        switchWorkspace(ccWs.id);
    }
    if (ccWs) {
        const existing = ccWs.consoleTabs.find(t => t.type === 'cellintella');
        if (existing) {
            ccWs.activeConsoleTab = existing.id;
            _renderCodeChatTabs();
            _renderCodeChatBody();
        } else {
            _addCodeChatTab('cellintella');
        }
    }
}

// Alias for renamed HTML references
const toggleCellIntellaPanel = togglecinteliaPanel;

// ═════════════════════════════════════════════
// INIT
// ═════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    console.log('CELLAB Workbench v3.1');
    initResizers();
    initContextMenu();
    initMenuBar();

    // Check if a project is already open on the server
    const res = await api('status');
    if (res.success && res.data.project_open) {
        // Server already has a project — load it
        state._projectOpen = true;
        await loadProjectState();
        hideStartupDialog();
    } else {
        // Show startup dialog
        showStartupDialog();
    }

    updateStatus('Ready — CELLAB v3.1');

    // Create default Code & Chat if none exists (silently, don't switch to it)
    const hasCodeChat = [...state.workspaces.values()].some(w => w.type === 'codechat');
    if (!hasCodeChat) {
        _codeChatCounter++;
        const ccId = `cc-${_codeChatCounter}`;
        const ccInfo = CONSOLE_TYPES['shared'];
        const ccTabId = `cctab_${Date.now()}`;
        const ccWs = {
            id: ccId,
            name: 'Code & Chat',
            type: 'codechat',
            _isDefault: true,
            consoleTabs: [{
                id: ccTabId,
                sessionId: null,
                type: 'shared',
                name: `${ccInfo.label} 1`,
                scope: { level: 'none' },
                lines: [{ html: `<span class="console-welcome">CelLAB Console — ${ccInfo.welcome}</span>` }],
                history: [],
                histIdx: -1,
            }],
            activeConsoleTab: ccTabId,
        };
        state.workspaces.set(ccId, ccWs);
        // Create backend session async (don't block)
        api('console/create', 'POST', { type: 'shared' }).then(res => {
            if (res.success) ccWs.consoleTabs[0].sessionId = res.data.session_id;
        });
        renderWorkspaceTabs();
    }
});
