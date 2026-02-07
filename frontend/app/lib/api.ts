const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ────────────────────────────────────────────────────────────────────

export interface CountryMood {
  country_code: string;
  country_name: string;
  mood_score: number;
  mood_label: string;
  color_code: string;
  valence: number | null;
  energy: number | null;
  danceability: number | null;
  acousticness: number | null;
  top_genre: string | null;
  top_track: string | null;
  news_sentiment: number | null;
  date: string;
}

export interface GlobalMoodResponse {
  updated_at: string;
  countries: CountryMood[];
}

export interface MoodTrendPoint {
  date: string;
  mood_score: number;
  mood_label: string;
}

export interface CountryDetailResponse extends CountryMood {
  trend: MoodTrendPoint[];
  spike_active: boolean;
}

export interface Spike {
  id: number;
  country_code: string;
  detected_at: string;
  previous_label: string;
  new_label: string;
  delta: number;
  reason: string | null;
}

export interface SpikeListResponse {
  spikes: Spike[];
}

// ── Fetchers ─────────────────────────────────────────────────────────────────

async function fetcher<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${path}`);
  }
  return res.json();
}

export async function fetchGlobalMood(): Promise<GlobalMoodResponse> {
  return fetcher<GlobalMoodResponse>("/mood/global");
}

export async function fetchCountryDetail(
  countryCode: string
): Promise<CountryDetailResponse> {
  return fetcher<CountryDetailResponse>(
    `/mood/country/${countryCode.toUpperCase()}`
  );
}

export async function fetchSpikes(): Promise<SpikeListResponse> {
  return fetcher<SpikeListResponse>("/spikes");
}
