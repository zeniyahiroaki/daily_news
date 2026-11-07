// Daily News Application Logic

const STORAGE_KEY_THEME = 'dailynews_theme';
const STORAGE_KEY_READ = 'dailynews_read_articles';
const STORAGE_KEY_FAVORITES = 'dailynews_fav_articles';

// アプリケーションステート
let state = {
  allArticles: [],
  genres: [],
  meta: {},
  currentGenre: 'all',
  currentDateFilter: 'today', // 'today' or 'all'
  searchQuery: '',
  readIds: new Set(),
  favoriteIds: new Set()
};

// 1. 初期化
document.addEventListener('DOMContentLoaded', () => {
  initStorage();
  initTheme();
  initPWA();
  initEventListeners();
  loadNewsData();
});

// ローカルストレージの読み込み
function initStorage() {
  try {
    const savedRead = JSON.parse(localStorage.getItem(STORAGE_KEY_READ) || '[]');
    state.readIds = new Set(savedRead);
    const savedFav = JSON.parse(localStorage.getItem(STORAGE_KEY_FAVORITES) || '[]');
    state.favoriteIds = new Set(savedFav);
    updateReadStats();
  } catch (e) {
    console.error('Storage init error:', e);
  }
}

function saveStorage() {
  localStorage.setItem(STORAGE_KEY_READ, JSON.stringify(Array.from(state.readIds)));
  localStorage.setItem(STORAGE_KEY_FAVORITES, JSON.stringify(Array.from(state.favoriteIds)));
  updateReadStats();
}

function updateReadStats() {
  const readStatsElem = document.getElementById('read-stats');
  if (readStatsElem) {
    readStatsElem.textContent = `既読: ${state.readIds.size}件`;
  }
}

// 2. テーマ切り替え (ダークモード)
function initTheme() {
  const savedTheme = localStorage.getItem(STORAGE_KEY_THEME);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add('dark');
    updateThemeIcon(true);
  } else {
    document.documentElement.classList.remove('dark');
    updateThemeIcon(false);
  }

  const themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', toggleTheme);
  }
}

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem(STORAGE_KEY_THEME, isDark ? 'dark' : 'light');
  updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.className = isDark ? 'ph ph-sun text-xl text-yellow-400' : 'ph ph-moon text-xl';
  }
}

// 3. PWAのインストールプロンプト
let deferredPrompt = null;
function initPWA() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => console.log('SW registered:', reg.scope))
      .catch(err => console.warn('SW register error:', err));
  }

  const installBtn = document.getElementById('pwa-install-btn');
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) {
      installBtn.classList.remove('hidden');
      installBtn.classList.add('flex');
    }
  });

  if (installBtn) {
    installBtn.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log('PWA prompt outcome:', outcome);
      deferredPrompt = null;
      installBtn.classList.add('hidden');
    });
  }
}

// 4. イベントリスナーの設定
function initEventListeners() {
  // 日付フィルター切り替え
  const btnToday = document.getElementById('filter-today');
  const btnAll = document.getElementById('filter-all-dates');
  
  if (btnToday && btnAll) {
    btnToday.addEventListener('click', () => {
      state.currentDateFilter = 'today';
      btnToday.className = 'px-3.5 py-1.5 rounded-lg bg-white dark:bg-slate-700 shadow-sm text-slate-900 dark:text-white font-semibold transition';
      btnAll.className = 'px-3.5 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition';
      renderGenreTabs();
      renderArticles();
    });

    btnAll.addEventListener('click', () => {
      state.currentDateFilter = 'all';
      btnAll.className = 'px-3.5 py-1.5 rounded-lg bg-white dark:bg-slate-700 shadow-sm text-slate-900 dark:text-white font-semibold transition';
      btnToday.className = 'px-3.5 py-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition';
      renderGenreTabs();
      renderArticles();
    });
  }

  // 検索
  const searchInput = document.getElementById('search-input');
  const searchClear = document.getElementById('search-clear');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.trim().toLowerCase();
      if (searchClear) {
        searchClear.classList.toggle('hidden', state.searchQuery === '');
      }
      renderArticles();
    });
  }

  if (searchClear) {
    searchClear.addEventListener('click', () => {
      if (searchInput) {
        searchInput.value = '';
        state.searchQuery = '';
        searchClear.classList.add('hidden');
        renderArticles();
      }
    });
  }

  // 既読クリア
  const clearReadBtn = document.getElementById('btn-clear-read');
  if (clearReadBtn) {
    clearReadBtn.addEventListener('click', () => {
      if (confirm('既読状態をリセットしますか？')) {
        state.readIds.clear();
        saveStorage();
        renderArticles();
      }
    });
  }
}

// 5. データの読み込み
async function loadNewsData() {
  try {
    const res = await fetch('./data/news.json?t=' + Date.now());
    if (!res.ok) throw new Error('Failed to load data');
    const data = await res.json();
    
    state.meta = data;
    state.allArticles = data.articles || [];
    state.genres = data.genres || [];

    // ヘッダー情報更新
    const dateElem = document.getElementById('header-date');
    if (dateElem) {
      dateElem.textContent = `${data.target_date} (更新: ${data.generated_at_formatted || '18:00'})`;
    }

    // カウント表示
    const todayCountElem = document.getElementById('today-count');
    if (todayCountElem) todayCountElem.textContent = data.today_articles_count || 0;

    const allCountElem = document.getElementById('all-count');
    if (allCountElem) allCountElem.textContent = data.total_articles || 0;

    renderGenreTabs();
    renderArticles();

  } catch (err) {
    console.error('Error fetching news.json:', err);
    const container = document.getElementById('articles-container');
    if (container) {
      container.innerHTML = `
        <div class="col-span-full py-12 text-center text-red-500">
          <p class="font-bold text-base mb-1">ニュースデータの読み込みに失敗しました</p>
          <p class="text-xs text-slate-500">まだ collector.py が実行されていないか、データが存在しません。</p>
        </div>
      `;
    }
  }
}

// 6. ジャンルタブの描画
function renderGenreTabs() {
  const tabsContainer = document.getElementById('genre-tabs');
  if (!tabsContainer) return;

  tabsContainer.innerHTML = '';

  // お気に入りタブを追加したタブリスト
  const tabs = [
    ...state.genres,
    { id: 'favorites', name: '★ お気に入り' }
  ];

  tabs.forEach(genre => {
    const btn = document.createElement('button');
    const isActive = state.currentGenre === genre.id;
    
    btn.className = `tab-btn px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 transition ${isActive ? 'active' : ''}`;
    
    // カウント（現在の日付フィルターに応じて動的に計算）
    let countBadge = '';
    if (genre.id === 'favorites') {
      countBadge = `<span class="px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300 text-[10px]">${state.favoriteIds.size}</span>`;
    } else {
      const count = getGenreCount(genre.id);
      countBadge = `<span class="opacity-75 text-[10px]">(${count})</span>`;
    }

    btn.innerHTML = `${escapeHtml(genre.name)} ${countBadge}`;
    btn.addEventListener('click', () => {
      state.currentGenre = genre.id;
      renderGenreTabs();
      renderArticles();
    });

    tabsContainer.appendChild(btn);
  });
}

function getGenreCount(genreId) {
  return state.allArticles.filter(art => {
    if (state.currentDateFilter === 'today' && !art.is_today) {
      return false;
    }
    if (genreId !== 'all' && art.genre !== genreId) {
      return false;
    }
    return true;
  }).length;
}

// 7. 記事一覧のフィルタリングと描画
function renderArticles() {
  const container = document.getElementById('articles-container');
  const emptyState = document.getElementById('empty-state');
  if (!container) return;

  // フィルタリング処理
  let filtered = state.allArticles.filter(art => {
    // 1. お気に入りタブ
    if (state.currentGenre === 'favorites') {
      if (!state.favoriteIds.has(art.id)) return false;
    } 
    // 2. 通常ジャンルタブ
    else if (state.currentGenre !== 'all') {
      if (art.genre !== state.currentGenre) return false;
    }

    // 3. 日付フィルター（お気に入りタブ以外）
    if (state.currentGenre !== 'favorites') {
      if (state.currentDateFilter === 'today' && !art.is_today) {
        return false;
      }
    }

    // 4. 検索クエリ
    if (state.searchQuery) {
      const q = state.searchQuery;
      const titleMatch = (art.title || '').toLowerCase().includes(q);
      const summaryMatch = (art.summary || '').toLowerCase().includes(q);
      const mediaMatch = (art.media || '').toLowerCase().includes(q);
      if (!titleMatch && !summaryMatch && !mediaMatch) {
        return false;
      }
    }

    return true;
  });

  // 空表示の判定
  if (filtered.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.classList.remove('hidden');
    return;
  }

  if (emptyState) emptyState.classList.add('hidden');

  // カードHTMLの生成
  container.innerHTML = filtered.map(art => {
    const isRead = state.readIds.has(art.id);
    const isFav = state.favoriteIds.has(art.id);
    const genreColors = getGenreBadgeColor(art.genre);

    // 要約の箇条書き
    let bulletsHtml = '';
    if (art.summary_bullets && art.summary_bullets.length > 0) {
      bulletsHtml = art.summary_bullets.map(b => `
        <li class="flex items-start gap-1.5 text-xs text-slate-600 dark:text-slate-300">
          <span class="text-blue-500 font-bold shrink-0">•</span>
          <span>${escapeHtml(b)}</span>
        </li>
      `).join('');
    } else {
      bulletsHtml = `<li class="text-xs text-slate-500">${escapeHtml(art.summary || '')}</li>`;
    }

    return `
      <article class="news-card rounded-2xl overflow-hidden flex flex-col justify-between ${isRead ? 'is-read' : ''}" data-id="${art.id}">
        <div>
          <!-- Thumbnail & Media Badge -->
          <div class="relative aspect-video w-full overflow-hidden bg-slate-100 dark:bg-slate-800">
            <img src="${escapeHtml(art.thumbnail)}" 
                 alt="${escapeHtml(art.title)}" 
                 class="w-full h-full object-cover transition duration-300 hover:scale-105"
                 loading="lazy"
                 onerror="this.onerror=null; this.src='${escapeHtml(art.default_thumb || './icons/icon.svg')}';">
            
            <!-- Source Tag -->
            <div class="absolute top-3 left-3 flex items-center gap-1.5">
              <span class="px-2 py-0.5 rounded-lg text-[11px] font-semibold bg-slate-900/80 text-white backdrop-blur-sm">
                ${escapeHtml(art.media)}
              </span>
              <span class="px-2 py-0.5 rounded-lg text-[11px] font-semibold ${genreColors} backdrop-blur-sm">
                ${escapeHtml(art.genre_name)}
              </span>
            </div>

            <!-- Favorite Star Button -->
            <button class="btn-fav absolute top-3 right-3 p-2 rounded-xl backdrop-blur-sm transition ${isFav ? 'bg-amber-500 text-white' : 'bg-slate-900/60 text-slate-200 hover:text-white'}" 
                    data-id="${art.id}" aria-label="お気に入りトグル">
              <i class="ph-fill ph-star text-base ${isFav ? 'text-white' : 'text-slate-300'}"></i>
            </button>

            ${art.is_today ? `
              <div class="absolute bottom-2 right-2 px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-600 text-white shadow-sm">
                本日
              </div>
            ` : ''}
          </div>

          <!-- Body Content -->
          <div class="p-4 space-y-3">
            <div class="flex items-center justify-between text-[11px] text-slate-400">
              <span class="flex items-center gap-1">
                <i class="ph ph-clock"></i>
                ${art.published_date} ${art.published_time}
              </span>
              ${isRead ? '<span class="text-slate-400 font-medium">既読</span>' : ''}
            </div>

            <!-- Title -->
            <h2 class="card-title text-sm sm:text-base font-bold text-slate-900 dark:text-white line-clamp-2 hover:text-blue-600 dark:hover:text-blue-400 transition">
              <a href="${escapeHtml(art.url)}" target="_blank" rel="noopener noreferrer" class="article-link" data-id="${art.id}">
                ${escapeHtml(art.title)}
              </a>
            </h2>

            <!-- AI 3-lines summary / Excerpt -->
            <ul class="space-y-1.5 pt-1 border-t border-slate-100 dark:border-slate-800/80">
              ${bulletsHtml}
            </ul>
          </div>
        </div>

        <!-- Footer link button -->
        <div class="p-4 pt-0">
          <a href="${escapeHtml(art.url)}" target="_blank" rel="noopener noreferrer" 
             class="article-link inline-flex items-center justify-between w-full px-3 py-2 text-xs font-semibold rounded-xl bg-slate-100 hover:bg-blue-50 dark:bg-slate-800 dark:hover:bg-slate-700/80 text-slate-700 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400 transition"
             data-id="${art.id}">
            <span>元記事を読む</span>
            <i class="ph ph-arrow-square-out text-sm"></i>
          </a>
        </div>
      </article>
    `;
  }).join('');

  // リンククリック時の既読ハンドラを登録
  document.querySelectorAll('.article-link').forEach(link => {
    link.addEventListener('click', (e) => {
      const artId = e.currentTarget.getAttribute('data-id');
      if (artId) {
        markAsRead(artId);
      }
    });
  });

  // お気に入りトグルハンドラ
  document.querySelectorAll('.btn-fav').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const artId = e.currentTarget.getAttribute('data-id');
      if (artId) {
        toggleFavorite(artId);
      }
    });
  });
}

// 8. 既読とお気に入りの操作
function markAsRead(id) {
  state.readIds.add(id);
  saveStorage();
  const card = document.querySelector(`.news-card[data-id="${id}"]`);
  if (card) {
    card.classList.add('is-read');
  }
}

function toggleFavorite(id) {
  if (state.favoriteIds.has(id)) {
    state.favoriteIds.delete(id);
  } else {
    state.favoriteIds.add(id);
  }
  saveStorage();
  renderGenreTabs(); // お気に入り件数の更新
  renderArticles();
}

// 9. ユーティリティ
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function getGenreBadgeColor(genre) {
  switch (genre) {
    case 'tech':
      return 'bg-purple-900/80 text-purple-200';
    case 'mobile':
      return 'bg-blue-900/80 text-blue-200';
    case 'camera':
      return 'bg-emerald-900/80 text-emerald-200';
    case 'music':
      return 'bg-rose-900/80 text-rose-200';
    case 'car':
      return 'bg-amber-900/80 text-amber-200';
    case 'appliance':
      return 'bg-teal-900/80 text-teal-200';
    default:
      return 'bg-slate-900/80 text-slate-200';
  }
}
