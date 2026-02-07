/**
 * Mock data for frontend development when backend is not available
 */

import type { CountryMood, GlobalMoodResponse, CountryDetailResponse, SpikeListResponse } from "./api";

// Sample country mood data with realistic values
const SAMPLE_COUNTRIES: CountryMood[] = [
    { country_code: "US", country_name: "United States", mood_score: 0.45, mood_label: "Happy", color_code: "#22c55e", valence: 0.72, energy: 0.68, danceability: 0.75, acousticness: 0.15, top_genre: "Pop", top_track: "Good Feeling - Flo Rida", news_sentiment: 0.3, date: new Date().toISOString() },
    { country_code: "GB", country_name: "United Kingdom", mood_score: 0.12, mood_label: "Calm", color_code: "#38bdf8", valence: 0.55, energy: 0.42, danceability: 0.48, acousticness: 0.55, top_genre: "Indie", top_track: "Lost in Yesterday - Tame Impala", news_sentiment: 0.1, date: new Date().toISOString() },
    { country_code: "DE", country_name: "Germany", mood_score: 0.28, mood_label: "Happy", color_code: "#22c55e", valence: 0.65, energy: 0.55, danceability: 0.62, acousticness: 0.25, top_genre: "Electronic", top_track: "Levels - Avicii", news_sentiment: 0.2, date: new Date().toISOString() },
    { country_code: "FR", country_name: "France", mood_score: 0.05, mood_label: "Calm", color_code: "#38bdf8", valence: 0.52, energy: 0.38, danceability: 0.45, acousticness: 0.65, top_genre: "French Pop", top_track: "Dernière Danse - Indila", news_sentiment: 0.0, date: new Date().toISOString() },
    { country_code: "JP", country_name: "Japan", mood_score: 0.18, mood_label: "Calm", color_code: "#38bdf8", valence: 0.58, energy: 0.45, danceability: 0.52, acousticness: 0.42, top_genre: "J-Pop", top_track: "Lemon - Kenshi Yonezu", news_sentiment: 0.15, date: new Date().toISOString() },
    { country_code: "BR", country_name: "Brazil", mood_score: 0.62, mood_label: "Happy", color_code: "#22c55e", valence: 0.82, energy: 0.78, danceability: 0.88, acousticness: 0.12, top_genre: "Funk Carioca", top_track: "Vai Malandra - Anitta", news_sentiment: 0.4, date: new Date().toISOString() },
    { country_code: "AU", country_name: "Australia", mood_score: 0.35, mood_label: "Happy", color_code: "#22c55e", valence: 0.68, energy: 0.62, danceability: 0.65, acousticness: 0.22, top_genre: "Indie Rock", top_track: "Electric Feel - MGMT", news_sentiment: 0.25, date: new Date().toISOString() },
    { country_code: "CA", country_name: "Canada", mood_score: 0.22, mood_label: "Calm", color_code: "#38bdf8", valence: 0.58, energy: 0.48, danceability: 0.55, acousticness: 0.35, top_genre: "Alternative", top_track: "Blinding Lights - The Weeknd", news_sentiment: 0.18, date: new Date().toISOString() },
    { country_code: "MX", country_name: "Mexico", mood_score: 0.48, mood_label: "Happy", color_code: "#22c55e", valence: 0.75, energy: 0.72, danceability: 0.78, acousticness: 0.18, top_genre: "Reggaeton", top_track: "La Bicicleta - Shakira", news_sentiment: 0.35, date: new Date().toISOString() },
    { country_code: "ES", country_name: "Spain", mood_score: 0.42, mood_label: "Happy", color_code: "#22c55e", valence: 0.70, energy: 0.65, danceability: 0.72, acousticness: 0.20, top_genre: "Latin Pop", top_track: "Despacito - Luis Fonsi", news_sentiment: 0.3, date: new Date().toISOString() },
    { country_code: "IT", country_name: "Italy", mood_score: 0.15, mood_label: "Calm", color_code: "#38bdf8", valence: 0.55, energy: 0.45, danceability: 0.50, acousticness: 0.45, top_genre: "Italian Pop", top_track: "Soldi - Mahmood", news_sentiment: 0.1, date: new Date().toISOString() },
    { country_code: "RU", country_name: "Russia", mood_score: -0.25, mood_label: "Sad", color_code: "#8b5cf6", valence: 0.35, energy: 0.42, danceability: 0.38, acousticness: 0.55, top_genre: "Russian Pop", top_track: "Mood - Rauf & Faik", news_sentiment: -0.2, date: new Date().toISOString() },
    { country_code: "CN", country_name: "China", mood_score: 0.08, mood_label: "Calm", color_code: "#38bdf8", valence: 0.52, energy: 0.48, danceability: 0.45, acousticness: 0.42, top_genre: "Mandopop", top_track: "Love Scenario - iKON", news_sentiment: 0.05, date: new Date().toISOString() },
    { country_code: "IN", country_name: "India", mood_score: 0.38, mood_label: "Happy", color_code: "#22c55e", valence: 0.68, energy: 0.65, danceability: 0.70, acousticness: 0.25, top_genre: "Bollywood", top_track: "Jai Ho - A.R. Rahman", news_sentiment: 0.28, date: new Date().toISOString() },
    { country_code: "KR", country_name: "South Korea", mood_score: 0.52, mood_label: "Happy", color_code: "#22c55e", valence: 0.75, energy: 0.72, danceability: 0.82, acousticness: 0.15, top_genre: "K-Pop", top_track: "Dynamite - BTS", news_sentiment: 0.4, date: new Date().toISOString() },
    { country_code: "ZA", country_name: "South Africa", mood_score: 0.32, mood_label: "Happy", color_code: "#22c55e", valence: 0.65, energy: 0.60, danceability: 0.68, acousticness: 0.28, top_genre: "Afrobeats", top_track: "Jerusalema - Master KG", news_sentiment: 0.22, date: new Date().toISOString() },
    { country_code: "AR", country_name: "Argentina", mood_score: -0.15, mood_label: "Anxious", color_code: "#f97316", valence: 0.42, energy: 0.58, danceability: 0.55, acousticness: 0.32, top_genre: "Cumbia", top_track: "Tutu - Camilo", news_sentiment: -0.1, date: new Date().toISOString() },
    { country_code: "EG", country_name: "Egypt", mood_score: -0.08, mood_label: "Anxious", color_code: "#f97316", valence: 0.45, energy: 0.52, danceability: 0.48, acousticness: 0.38, top_genre: "Arabic Pop", top_track: "Bahebak - Amr Diab", news_sentiment: -0.05, date: new Date().toISOString() },
    { country_code: "NG", country_name: "Nigeria", mood_score: 0.58, mood_label: "Happy", color_code: "#22c55e", valence: 0.78, energy: 0.75, danceability: 0.85, acousticness: 0.12, top_genre: "Afrobeats", top_track: "Essence - Wizkid", news_sentiment: 0.42, date: new Date().toISOString() },
    { country_code: "SE", country_name: "Sweden", mood_score: 0.25, mood_label: "Calm", color_code: "#38bdf8", valence: 0.58, energy: 0.50, danceability: 0.55, acousticness: 0.40, top_genre: "Pop", top_track: "Dancing Queen - ABBA", news_sentiment: 0.2, date: new Date().toISOString() },
    { country_code: "NO", country_name: "Norway", mood_score: 0.20, mood_label: "Calm", color_code: "#38bdf8", valence: 0.55, energy: 0.48, danceability: 0.52, acousticness: 0.45, top_genre: "Electronic", top_track: "Take On Me - a-ha", news_sentiment: 0.15, date: new Date().toISOString() },
    { country_code: "PL", country_name: "Poland", mood_score: -0.35, mood_label: "Sad", color_code: "#8b5cf6", valence: 0.38, energy: 0.45, danceability: 0.42, acousticness: 0.48, top_genre: "Pop", top_track: "Nieznajomy - Dawid Podsiadło", news_sentiment: -0.3, date: new Date().toISOString() },
    { country_code: "TR", country_name: "Turkey", mood_score: -0.12, mood_label: "Anxious", color_code: "#f97316", valence: 0.45, energy: 0.55, danceability: 0.50, acousticness: 0.35, top_genre: "Turkish Pop", top_track: "Yalnızlık - Tarkan", news_sentiment: -0.08, date: new Date().toISOString() },
    { country_code: "SA", country_name: "Saudi Arabia", mood_score: 0.10, mood_label: "Calm", color_code: "#38bdf8", valence: 0.52, energy: 0.45, danceability: 0.48, acousticness: 0.42, top_genre: "Arabic Pop", top_track: "3 Daqat - Abu", news_sentiment: 0.08, date: new Date().toISOString() },
    { country_code: "AE", country_name: "United Arab Emirates", mood_score: 0.30, mood_label: "Happy", color_code: "#22c55e", valence: 0.62, energy: 0.58, danceability: 0.60, acousticness: 0.28, top_genre: "International Pop", top_track: "Habibi - DJ Snake", news_sentiment: 0.25, date: new Date().toISOString() },
    { country_code: "TH", country_name: "Thailand", mood_score: 0.42, mood_label: "Happy", color_code: "#22c55e", valence: 0.68, energy: 0.62, danceability: 0.65, acousticness: 0.25, top_genre: "T-Pop", top_track: "How You Like That - BLACKPINK", news_sentiment: 0.32, date: new Date().toISOString() },
    { country_code: "ID", country_name: "Indonesia", mood_score: 0.35, mood_label: "Happy", color_code: "#22c55e", valence: 0.65, energy: 0.58, danceability: 0.62, acousticness: 0.30, top_genre: "Pop", top_track: "Ojo Dibandingke - Denny Caknan", news_sentiment: 0.28, date: new Date().toISOString() },
    { country_code: "PH", country_name: "Philippines", mood_score: 0.48, mood_label: "Happy", color_code: "#22c55e", valence: 0.72, energy: 0.65, danceability: 0.70, acousticness: 0.22, top_genre: "OPM", top_track: "Tahanan - Adie", news_sentiment: 0.35, date: new Date().toISOString() },
    { country_code: "VN", country_name: "Vietnam", mood_score: 0.28, mood_label: "Calm", color_code: "#38bdf8", valence: 0.58, energy: 0.52, danceability: 0.55, acousticness: 0.38, top_genre: "V-Pop", top_track: "See Tình - Hoàng Thùy Linh", news_sentiment: 0.22, date: new Date().toISOString() },
    { country_code: "UA", country_name: "Ukraine", mood_score: -0.55, mood_label: "Angry", color_code: "#ef4444", valence: 0.25, energy: 0.65, danceability: 0.35, acousticness: 0.42, top_genre: "Ukrainian Pop", top_track: "Stefania - Kalush Orchestra", news_sentiment: -0.6, date: new Date().toISOString() },
];

// Generate 7-day trend data
function generateTrend(baseScore: number): { date: string; mood_score: number; mood_label: string }[] {
    const trend = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const variance = (Math.random() - 0.5) * 0.3;
        const score = Math.max(-1, Math.min(1, baseScore + variance));
        let label = "Calm";
        if (score >= 0.3) label = "Happy";
        else if (score >= 0) label = "Calm";
        else if (score >= -0.3) label = "Anxious";
        else if (score >= -0.6) label = "Sad";
        else label = "Angry";

        trend.push({
            date: date.toISOString().split("T")[0],
            mood_score: score,
            mood_label: label,
        });
    }
    return trend;
}

// Mock API responses
export const mockGlobalMood: GlobalMoodResponse = {
    updated_at: new Date().toISOString(),
    countries: SAMPLE_COUNTRIES,
};

export function getMockCountryDetail(countryCode: string): CountryDetailResponse | null {
    const country = SAMPLE_COUNTRIES.find(c => c.country_code === countryCode);
    if (!country) return null;

    return {
        ...country,
        trend: generateTrend(country.mood_score),
        spike_active: country.mood_score < -0.4 || Math.random() > 0.85,
    };
}

export const mockSpikes: SpikeListResponse = {
    spikes: [
        {
            id: 1,
            country_code: "UA",
            detected_at: new Date().toISOString(),
            previous_label: "Sad",
            new_label: "Angry",
            delta: -0.25,
            reason: "Ongoing regional tensions",
        },
        {
            id: 2,
            country_code: "AR",
            detected_at: new Date(Date.now() - 86400000).toISOString(),
            previous_label: "Calm",
            new_label: "Anxious",
            delta: -0.22,
            reason: "Economic uncertainty",
        },
        {
            id: 3,
            country_code: "BR",
            detected_at: new Date(Date.now() - 172800000).toISOString(),
            previous_label: "Calm",
            new_label: "Happy",
            delta: 0.35,
            reason: "Carnival season celebrations",
        },
    ],
};
