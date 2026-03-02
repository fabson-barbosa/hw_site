import { useCallback, useEffect, useRef, useState } from "react";

const API_BASE = "/api/v1";
const PAGE_SIZE = 20;

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function buildCarsUrl({ year, series, search, skip }) {
  const params = new URLSearchParams({ skip, limit: PAGE_SIZE });
  if (year) params.set("year", year);
  if (series) params.set("series", series);
  if (search) params.set("search", search);
  return `/cars?${params}`;
}

// ---------------------------------------------------------------------------
// Lazy image with skeleton
// ---------------------------------------------------------------------------

function LazyImage({ src, alt, className = "" }) {
  const [status, setStatus] = useState("loading"); // loading | loaded | error
  const imgRef = useRef(null);

  useEffect(() => {
    setStatus("loading");
    if (!src) { setStatus("error"); return; }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && imgRef.current) {
          imgRef.current.src = src;
          observer.disconnect();
        }
      },
      { rootMargin: "200px" }
    );
    if (imgRef.current) observer.observe(imgRef.current);
    return () => observer.disconnect();
  }, [src]);

  return (
    <div className={`car-card__image-wrapper ${className}`}>
      {status === "loading" && <div className="car-card__skeleton" aria-hidden="true" />}
      <img
        ref={imgRef}
        alt={alt}
        onLoad={() => setStatus("loaded")}
        onError={() => setStatus("error")}
        className={status === "loaded" ? "loaded" : "loading"}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Skeleton Card
// ---------------------------------------------------------------------------

function SkeletonCard() {
  return (
    <div className="skeleton-card" aria-hidden="true">
      <div className="skeleton-block" style={{ aspectRatio: "1/1" }} />
      <div style={{ padding: "0.5rem 0.6rem" }}>
        <div className="skeleton-block" style={{ height: "0.75rem", marginBottom: "0.4rem" }} />
        <div className="skeleton-block" style={{ height: "0.65rem", width: "60%" }} />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Car Card
// ---------------------------------------------------------------------------

function CarCard({ car, onClick }) {
  return (
    <article
      className="car-card"
      tabIndex={0}
      role="button"
      aria-label={`Ver detalhes de ${car.name}`}
      onClick={() => onClick(car)}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onClick(car)}
    >
      <LazyImage src={car.image_url} alt={car.name} />
      <div className="car-card__body">
        <p className="car-card__name">{car.name}</p>
        <p className="car-card__meta">
          {[car.year, car.color].filter(Boolean).join(" · ")}
        </p>
        {car.view_count > 0 && (
          <p className="car-card__views" aria-label={`${car.view_count} visualizações`}>
            👁 {car.view_count}
          </p>
        )}
      </div>
    </article>
  );
}

// ---------------------------------------------------------------------------
// Car Detail Modal
// ---------------------------------------------------------------------------

function CarModal({ car, onClose }) {
  // Close on Escape
  useEffect(() => {
    const handler = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const details = [
    ["Série", car.series],
    ["Nº na série", car.series_number],
    ["Ano", car.year],
    ["Cor", car.color],
    ["Tampo", car.tampo],
    ["Base", car.base_color],
    ["Janela", car.window_color],
    ["Interior", car.interior_color],
    ["Roda", car.wheel_type],
    ["Toy #", car.toy_number],
    ["País", car.country],
  ].filter(([, v]) => v);

  return (
    <div
      className="modal-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="modal">
        <button className="modal__close" onClick={onClose} aria-label="Fechar">
          ×
        </button>
        {car.image_url ? (
          <img className="modal__image" src={car.image_url} alt={car.name} loading="lazy" />
        ) : (
          <div className="modal__image" style={{ display: "flex", alignItems: "center", justifyContent: "center", fontSize: "3rem" }}>
            🏎️
          </div>
        )}
        <div className="modal__body">
          <h2 id="modal-title" className="modal__title">{car.name}</h2>
          {details.length > 0 && (
            <table className="modal__details" aria-label="Detalhes do carrinho">
              <tbody>
                {details.map(([label, value]) => (
                  <tr key={label}>
                    <td>{label}</td>
                    <td>{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {car.fandom_url && (
            <a
              className="modal__fandom-link"
              href={car.fandom_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Ver no Fandom Wiki ↗
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Most Viewed Strip
// ---------------------------------------------------------------------------

function MostViewedStrip({ onSelect }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    apiFetch("/cars/most-viewed?limit=10")
      .then(setItems)
      .catch(() => {});
  }, []);

  if (items.length === 0) return null;

  return (
    <section aria-labelledby="most-viewed-heading">
      <h2 id="most-viewed-heading" className="section-title">🔥 Mais Visualizados</h2>
      <div className="most-viewed-strip" role="list">
        {items.map((car) => (
          <div
            key={car.id}
            className="most-viewed-item"
            role="listitem"
            tabIndex={0}
            aria-label={`${car.name}, ${car.view_count} visualizações`}
            onClick={() => onSelect(car)}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onSelect(car)}
          >
            {car.image_url ? (
              <img src={car.image_url} alt={car.name} loading="lazy" />
            ) : (
              <div style={{ aspectRatio: "1/1", background: "#f0f0f0", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "2rem" }}>🏎️</div>
            )}
            <p className="most-viewed-item__label">{car.name}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Main App
// ---------------------------------------------------------------------------

export default function App() {
  const [cars, setCars] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [years, setYears] = useState([]);
  const [seriesList, setSeriesList] = useState([]);

  const [selectedYear, setSelectedYear] = useState("");
  const [selectedSeries, setSelectedSeries] = useState("");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [page, setPage] = useState(0);

  const [selectedCar, setSelectedCar] = useState(null);

  // Debounce search input
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 350);
    return () => clearTimeout(t);
  }, [search]);

  // Reset page when filters change
  useEffect(() => { setPage(0); }, [selectedYear, selectedSeries, debouncedSearch]);

  // Load filter metadata
  useEffect(() => {
    apiFetch("/years").then((d) => setYears(d.years)).catch(() => {});
    apiFetch("/series").then((d) => setSeriesList(d.series)).catch(() => {});
  }, []);

  // Load cars
  useEffect(() => {
    setLoading(true);
    setError(null);
    apiFetch(
      buildCarsUrl({
        year: selectedYear,
        series: selectedSeries,
        search: debouncedSearch,
        skip: page * PAGE_SIZE,
      })
    )
      .then((data) => {
        setCars(data.items);
        setTotal(data.total);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [selectedYear, selectedSeries, debouncedSearch, page]);

  const handleCardClick = useCallback(async (car) => {
    setSelectedCar(car);
    // Record view asynchronously
    try {
      const updated = await apiFetch(`/cars/${car.id}/view`, { method: "POST" });
      // Update car in list and in selected
      setCars((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
      setSelectedCar(updated);
    } catch (_) {}
  }, []);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <>
      {/* Header */}
      <header className="site-header">
        <span aria-hidden="true" style={{ fontSize: "1.4rem" }}>🏎️</span>
        <h1>HW Cotação Brasil</h1>
        <input
          className="search-input"
          type="search"
          placeholder="Buscar carrinho…"
          aria-label="Buscar carrinhos"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </header>

      <main className="container">
        {/* Most Viewed */}
        <MostViewedStrip onSelect={handleCardClick} />

        {/* Filters */}
        <div className="filters" role="search" aria-label="Filtros de carrinhos">
          <select
            aria-label="Filtrar por ano"
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            <option value="">Todos os anos</option>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>

          <select
            aria-label="Filtrar por série"
            value={selectedSeries}
            onChange={(e) => setSelectedSeries(e.target.value)}
          >
            <option value="">Todas as séries</option>
            {seriesList.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Error */}
        {error && (
          <div className="error-banner" role="alert">
            Erro ao carregar carrinhos: {error}
          </div>
        )}

        {/* Results heading */}
        <h2 className="section-title" aria-live="polite">
          {loading ? "Carregando…" : `${total} carrinho${total !== 1 ? "s" : ""}`}
        </h2>

        {/* Grid */}
        <section aria-label="Catálogo de carrinhos">
          <div className="cars-grid">
            {loading
              ? Array.from({ length: PAGE_SIZE }).map((_, i) => <SkeletonCard key={i} />)
              : cars.map((car) => (
                  <CarCard key={car.id} car={car} onClick={handleCardClick} />
                ))}
          </div>

          {!loading && cars.length === 0 && !error && (
            <p className="empty-state">Nenhum carrinho encontrado.</p>
          )}
        </section>

        {/* Pagination */}
        {totalPages > 1 && (
          <nav className="pagination" aria-label="Paginação">
            <button
              onClick={() => setPage(0)}
              disabled={page === 0}
              aria-label="Primeira página"
            >
              ««
            </button>
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              aria-label="Página anterior"
            >
              ‹ Anterior
            </button>
            <span className="current-page" aria-current="page">
              Página {page + 1} de {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              aria-label="Próxima página"
            >
              Próxima ›
            </button>
            <button
              onClick={() => setPage(totalPages - 1)}
              disabled={page >= totalPages - 1}
              aria-label="Última página"
            >
              »»
            </button>
          </nav>
        )}
      </main>

      {/* Modal */}
      {selectedCar && (
        <CarModal car={selectedCar} onClose={() => setSelectedCar(null)} />
      )}
    </>
  );
}
